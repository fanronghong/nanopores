from nanopores.tools import fields
from nanopores.tools.interpolation import harmonic_interpolation
import dolfin
from nanopores.models.pughpore import Plotter
import nanopores.geometries.pughpore as pughpore
import folders
params=dict(bulkcon=1000.)
data=fields.get_fields("pugh",**params)
x=data["x"]
Fel=data["Fel"]
Fdrag=data["Fdrag"]
J=data["J"]
F=data["F"]

xq=list(x)
Felq=list(Fel)
Fdragq=list(Fdrag)
Jq=list(J)
Fq=list(F)
# diagonal mirror
for i in range(len(x)):
    if x[i][0]!=x[i][1]:
        xq.append([x[i][1],x[i][0],x[i][2]])
        Felq.append([Fel[i][1],Fel[i][0],Fel[i][2]])
        Fdragq.append([Fdrag[i][1],Fdrag[i][0],Fdrag[i][2]])
        Fq.append([F[i][1],F[i][0],F[i][2]])
        Jq.append(J[i])
xh=list(xq)
Felh=list(Felq)
Fdragh=list(Fdragq)
Jh=list(Jq)
Fh=list(Fq)
# left-right mirror
for i in range(len(xq)):
    if not (xq[i][0]==0. and xq[i][1]==0.):
        xh.append([-xq[i][0],xq[i][1],xq[i][2]])
        Felh.append([-Felq[i][0],Felq[i][1],Felq[i][2]])
        Fdragh.append([-Fdragq[i][0],Fdragq[i][1],Fdragq[i][2]])
        Fh.append([-Fq[i][0],Fq[i][1],Fq[i][2]])
        Jh.append(Jq[i])
xf=list(xh)
Felf=list(Felh)
Fdragf=list(Fdragh)
Jf=list(Jh)
Ff=list(Fh)
# top-bottom mirror
for i in range(len(xh)):
    if not (xh[i][0]==0. and xh[i][1]==0.):
        xf.append([xh[i][0],-xh[i][1],xh[i][2]])
        Felf.append([Felh[i][0],-Felh[i][1],Felh[i][2]])
        Fdragf.append([Fdragh[i][0],-Fdragh[i][1],Fdragh[i][2]])
        Ff.append([Fh[i][0],-Fh[i][1],Fh[i][2]])
        Jf.append(Jh[i])
len=len(xf)
h=2.
#shift all points up a little bit to ensure that they are in elements and not on facets
eps=1e-2
for i in range(len):
    xf[i][2]+=eps
Fx_=[Ff[i][0] for i in range(len)]
Fy_=[Ff[i][1] for i in range(len)]
Fz_=[Ff[i][2] for i in range(len)]
Felx_=[Felf[i][0] for i in range(len)]
Fely_=[Felf[i][1] for i in range(len)]
Felz_=[Felf[i][2] for i in range(len)]
Fdragx_=[Fdragf[i][0] for i in range(len)]
Fdragy_=[Fdragf[i][1] for i in range(len)]
Fdragz_=[Fdragf[i][2] for i in range(len)]



domain = pughpore.get_domain(h, x0=None)
domain.write_gmsh_code(h)
domain.insert_points(xf,h)
geo=domain.code_to_mesh()
mesh=geo.mesh
Fdragz = harmonic_interpolation(geo,xf,Fdragz_)
Plotter().plot(Fdragz)
dolfin.interactive()