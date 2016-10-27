# (c) 2016 Gregor Mitscha-Baude
"PNPS solvers and visualization for pugh pore"

import dolfin
import nanopores as nano
import nanopores.geometries.pughpore as pughpore
import nanopores.physics.simplepnps as simplepnps
import nanopores.tools.solvers as solvers

default = nano.Params(
geop = nano.Params(
    dim = 3,
    R = pughpore.params["R"],
    H = pughpore.params["H"],
    x0 = pughpore.params["x0"],
    rMolecule = pughpore.params["rMolecule"],
),
physp = nano.Params(
    Qmol = 6., # charge of trypsin at pH 8.
    bulkcon = 1000.,
    dnaqsdamp = .5,
    bV = -0.1,
    rDPore = 1.,
),
solverp = nano.Params(
    h = 2.,
    frac = 0.2,
    Nmax = 6e5,  
    imax = 30,
    tol = 1e-2,
    cheapest = False,
    stokesiter = True
))
defaultp = default.geop | default.physp

class Setup(solvers.Setup):
    default = default
                    
    def init_geo(self):
        if self.geop.dim == 3:
            geo = pughpore.get_geo(self.solverp.h, **self.geop)
            molec = nano.curved.Sphere(geo.params["rMolecule"],
                                       geo.params["x0"])
        if self.geop.dim == 2:
            geo = pughpore.get_geo_cyl(self.solverp.h, **self.geop)
            molec = nano.curved.Circle(geo.params["rMolecule"],
                                       geo.params["x0"])
        geo.curved = dict(moleculeb = molec.snap)
        self.geo = geo
        
    def init_phys(self):
        cyl = self.geop.dim == 2
        self.phys = nano.Physics("pore_mol", self.geo, cyl=cyl, **self.physp)
        
class Plotter(object):
    def __init__(self, setup):
        self.geo = setup.geo
        self.dim = setup.phys.dim
        if self.dim == 3:
            R, H = self.geo.params["R"], self.geo.params["H"]
            self.mesh2D = nano.RectangleMesh([-R,-H/2.], [R, H/2.],
                                         int(4*R), int(2*H))
    def plot(self, u, title="u"):
        if self.dim == 3:
            nano.plot_cross(u, self.mesh2D, title=title, key=title)
        elif self.dim == 2:
            dolfin.plot(u, title=title, key=title)
        
    def plot_vector(self, u, title="u"):
        if self.dim == 3:
            nano.plot_cross_vector(u, self.mesh2D, title=title, key=title)
        elif self.dim == 2:
            dolfin.plot(u, title=title, key=title)
    
def solve(setup, visualize=False):
    geo, phys, solverp = setup.geo, setup.phys, setup.solverp
    if visualize:
        plotter = Plotter(setup)
    set_sideBCs(phys, setup.geop, setup.physp)
    if geo.mesh.num_cells() < solverp.Nmax:
        pb = prerefine(setup, visualize)
    else:
        pb = None
    
    it = phys.dim==3
    pnps = simplepnps.PNPSFixedPointbV(geo, phys, ipicard=solverp.imax,
               verbose=True, tolnewton=solverp.tol, #taylorhood=True,
               stokesiter=(it and solverp.stokesiter), iterative=it,
               cyl=phys.cyl)          
    
    print "Number of cells:", geo.mesh.num_cells()
    print "DOFs:", pnps.dofs()
    dolfin.tic()
    for i in pnps.fixedpoint(ipnp=5):
        if visualize:
            v, cp, cm, u, p = pnps.solutions()
            plotter.plot(v, "potential")
    print "CPU time (solve): %.3g s" %(dolfin.toc(),)
    return pb, pnps

def get_forces(setup, pnps):
    forces = pnps.evaluate(setup.phys.CurrentPNPS)
    forces.update(pnps.evaluate(setup.phys.ForcesPNPS))
    return forces
      
def prerefine(setup, visualize=False):
    geo, phys, p = setup.geo, setup.phys, setup.solverp
    dolfin.tic()
    if setup.geop.x0 is None:
        goal = phys.CurrentPB
    else:
        goal = lambda v: phys.CurrentPB(v) + phys.Fbare(v, phys.dim-1)
    pb = simplepnps.SimpleLinearPBGO(geo, phys, goal=goal, cheapest=p.cheapest)
    
    for i in pb.adaptive_loop(p.Nmax, p.frac, verbose=True):
        if visualize:
            if phys.dim==3:
                nano.plot_sliced_mesh(geo, title="adapted mesh", key="b",
                                      elevate=-90. if i==1 else 0.)
                #dolfin.plot(geo.submesh("solid"), key="b",
                #            title="adapted solid mesh")
            if phys.dim==2:
                dolfin.plot(geo.boundaries, key="b", title="adapted mesh",
                            scalarbar=False)
    print "CPU time (PB): %.3g s" %(dolfin.toc(),)
    return pb    

def solve1D(geop, physp):
    geo = pughpore.get_geo1D(lc=.001, **geop)
    phys = nano.Physics("pore", geo, **physp)
    pnp = nano.solve_pde(simplepnps.SimplePNPProblem, geo, phys)
    return geo, pnp
    
def visualize1D(geo, pnp):
    v, cp, cm = pnp.solutions()
    h = geo.params["H"]
    nano.plot1D({"potential": v}, (-h/2, h/2, 1001),
                "x", dim=1, axlabels=("z [nm]", "potential [V]"))
    nano.plot1D({"c+": cp, "c-":cm},  (-h/2, h/2, 1001),
                "x", dim=1, axlabels=("z [nm]", "concentrations [mol/m^3]"))
                
class u1D(dolfin.Expression):
    def __init__(self, u, damping=1.):
        self.u = u
        self.damping = damping
        dolfin.Expression.__init__(self)
        
    def damp(self, scalar):
        self.damping *= scalar

    def eval(self, value, x):
        dim = x.shape[0]
        value[0] = self.damping*self.u(x[dim-1])
        
def set_sideBCs(phys, geop, physp):
    geo, pnp = solve1D(geop, physp)
    v, cp, cm = pnp.solutions()
    phys.v0["sideb"] = u1D(v)
    phys.cp0["sideb"] = u1D(cp)
    phys.cm0["sideb"] = u1D(cm)
    
def join_dicts(list):
    "[{'F':1.0}, {'F':2.0}, ...] --> {'F':[1.0, 2.0, ...]}"
    return {key:[dic[key] for dic in list] for key in list[0]}
    
# evaluate finite-size model for a a number of x positions
@solvers.cache_forcefield("pugh", defaultp)
def F_explicit(X, **params):
    _params = dict(defaultp, **params)
    values = []
    for x0 in X:
        setup = Setup(x0=x0, **_params)
        pb, pnps = solve(setup, False)
        values.append(get_forces(setup, pnps))
    return join_dicts(values)

        
# TODO
## evaluate point-size model for a number of z positions
#def F_implicit3D(Z, **params):
#    geo, phys = setup2D(z0=None, **params)
#    pb, pnps = solve2D(geo, phys, **params)
#    values = [pnps.zforces_implicit(z0) for z0 in Z]
#    F, Fel, Fdrag = tuple(zip(*values))
#    return F, Fel, Fdrag
#
## get discrete force fields from point-size model
#def F_field_implicit3D(**params):
#    params["z0"] = None
#    geo, phys = setup2D(**params)
#    pb, pnps = solve2D(geo, phys, **params)
#    (v, cp, cm, u, p) = pnps.solutions()
#    F, Fel, Fdrag = phys.Forces(v, u)
#    return F, Fel, Fdrag
    
if __name__ == "__main__":
    setup = Setup(h=1., Nmax=2e6, dim=3) #, x0=None)
    _, pnps = solve(setup, True)
    print get_forces(setup, pnps)
    
    plotter = Plotter(setup)
    v, cp, cm, u, p = pnps.solutions()
    plotter.plot_vector(u, "velocity")
    plotter.plot(cm, "cm")
    plotter.plot(cp, "cp")
    plotter.plot(p, "p")
    dolfin.interactive()
    