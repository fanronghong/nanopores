# this works with geo_params_old
from nanopores import *
from dolfin import *

geo_name = "H_geo"
nm = 1e-9
z0 = 7.5*nm

geo_params = dict(
#x0 = None,
x0 = [0.,0.,z0],
#x0 = [0., 0., -8.372*nm],
rMolecule = 0.4*nm,
#lcMolecule = nm*0.1,
moleculeblayer = True,
boxfields = True,
#Rx = 300*nm,
#Ry = 30*nm,
)

phys_params = dict(
Membraneqs = -0.0,
#bV = .1,
Qmol = -1.*qq,
bulkcon = 3e2,
#lowerpbias = .01,
#lowermbias = -.01,
dnaqsdamp = 0.1,
bulkconFluo = 10e-3, # bulk concentration of fluorophore [mol/m**3]
hReservoir = 1e-8, # height of cylindrical upper reservoir [m]
#applylowerqs = True,
couplebVtoQmol = True,
bV0 = 0.01,
)

meshgen_dict = generate_mesh(.9, geo_name, **geo_params)
geo = geo_from_name(geo_name, **geo_params)
phys = Physics("pore_molecule", geo, **phys_params)
print phys.charge

plot(geo.mesh)
#plot(geo.pwconst("initial_ions"))
#plot(geo.pwconst("permittivity"))
#interactive()
#exit()

if geo.parameter("x0") is None:
    exec("from nanopores.geometries.%s.subdomains import synonymes" %geo_name)
    geo.import_synonymes({"moleculeb":set()})
    geo.import_synonymes(synonymes)

IllposedNonlinearSolver.newtondamp = 1.

PNPSAxisym.imax = 50
PNPSAxisym.tolnewton = 1e-2
PNPSAxisym.alwaysstokes = True
#PNPProblemAxisym.k = 2
PNPProblemAxisym.method["iterative"] = False
PNPProblemAxisym.method["kparams"]["monitor_convergence"] = False

#pb = LinearPBAxisym(geo, phys)
goal = (lambda v : phys.Fbare(v, 1)) if geo.parameter("x0") else (lambda v : phys.CurrentPB(v))
#goal = (lambda v : phys.Fbare(v, 1) + phys.CurrentPB(v)) if geo.parameter("x0") else (lambda v : phys.CurrentPB(v))
#goal = lambda v : phys.CurrentPB(v)
pb = LinearPBAxisymGoalOriented(geo, phys, goal=goal)

pb.maxcells = 1e4
pb.marking_fraction = 0.5
pb.solve(refinement=True)

geo = pb.geo
v0 = pb.solution

#plot_on_sub(v0, geo, "pore", expr=-grad(v0)[1], title="E")

#pnps = PNPSAxisym(geo, phys)
pnps = PNPSAxisym(geo, phys, v0=v0)
pnps.maxcells = 20e4
pnps.marking_fraction = 0.5
#pnps.solvers.pop("Stokes")
refine = False #True
pnps.solve(refinement=refine, print_functionals=True)
pnps.print_results()

(v,cp,cm,u,p) = pnps.solutions(deepcopy=True)
I = pnps.get_functionals()["Javgbtm"]
Ry = geo.params["Ry"]
V = v([0.0, -Ry]) - v([0.0, Ry])

for est in pnps.estimators.values():
    if refine: est.plot(rate=-0.5)
    #else: est.plot()

#print "Convergence rates:\n",pnps.estimators["h1"].rates()

#plot_on_sub(v, geo, "pore", expr=-grad(v), title="E")
#interactive()

print
print "I (current through pore center):",I,"[pA]"
print "V (transmembrane potential):",V,"[V]"
print "conductance I/V:",I/V,"[pS]"

l1 = 10*nm
cmdiff = cm([10*nm, -l1]) - cm([10*nm, l1])
print "cm difference across membrane:",cmdiff,"[mol/m**3]"

print "u(0) = ",u(0.,0.)

if geo.params["x0"] is None:
    r = geo.params["rMolecule"]
    R = geo.params["r0"]
    Fel0 = 1e12*phys_params["Qmol"]*(v([0.,z0-r])-v([0.,z0+r]))/(2.*r)
    Fdrag0 = 1e12*6*pi*eta*r*u([0.,z0])[1]*exp(2.*r/(R-r))
    print "Fbare (theory) [pN]:", Fel0
    print "Fdrag (theory) [pN]:", Fdrag0
    print "F [pN]:", Fdrag0 + Fel0
else:
    fs = pnps.get_functionals()
    Fdrag = fs["Fp1"] + fs["Fshear1"]
    Fel = fs["Fbarevol1"]
    print "phys.Fbare [pN]:",1e12*assemble(phys.Fbare(v, 1))
    print "Fbare [pN]:", Fel
    print "Fdrag [pN]:", Fdrag
    print "F [pN]:", Fdrag + Fel

print "hmin [nm]: ", geo.mesh.hmin()*1e9
#plot(pnps.geo.mesh)
#interactive()
pb.estimators["err"].plot(rate=-1.)
pb.visualize()
pnps.visualize()
