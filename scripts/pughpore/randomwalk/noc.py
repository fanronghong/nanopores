from math import exp, factorial, pow
import matplotlib
matplotlib.use("Agg")
from matplotlib import gridspec
import matplotlib.pyplot as plt
import numpy as np
import os
import nanopores.tools.fields as f
HOME = os.path.expanduser("~")
PAPERDIR = os.path.join(HOME, "papers", "paper-howorka")
FIGDIR = os.path.join(PAPERDIR, "figures", "")
DATADIR = os.path.join(HOME,"Dropbox", "nanopores", "fields")
f.set_dir(DATADIR)

hpore=46.
#fieldsname='number_of_collisions_all'
fieldsname='number_of_collisions'
params=dict(avgbind1=2e7,avgbind2=3e4,P_bind1=0.,P_bind2=0.,z0=23.) # old one interval lengths(4,8,13)
#params=dict(avgbind1=23e6,avgbind2=3e4,P_bind1=0*0.035,P_bind2=0*3e-1,z0=hpore/2.+0.) # for binding everywhere

data=f.get_fields(fieldsname,**params)
data2=f.get_fields(fieldsname+'2',**params)
data3=f.get_fields(fieldsname+'3',**params)
Nc=np.array(data["Nc"])
Nc2=np.array(data2["Nc"])
Nc3=np.array(data3["Nc"])
lam=np.mean(Nc)
lam2=np.mean(Nc2)
lam3=np.mean(Nc3)
k=np.arange(0,21)
def P(k):
    return pow(lam,k)/(factorial(k))*exp(-lam)
P=np.array([P(x) for x in k])
def P2(k):
    return pow(lam2,k)/(factorial(k))*exp(-lam2)
P2=np.array([P2(x) for x in k])
def P3(k):
    return pow(lam3,k)/(factorial(k))*exp(-lam3)
P3=np.array([P3(x) for x in k])

color1 = 'blue'
color2 = 'green'
color3 = 'red'
alpha=.25
s=30.

plt.figure(figsize=(5,4),dpi=80)
#gs = gridspec.GridSpec(1,2,width_ratios=[1,1])
#gs.update(wspace=0.,hspace=0.)

#plt1=plt.subplot(gs[0])
plt.hist(Nc,bins=19,normed=1,alpha=alpha,color=color1,histtype='bar',align='left')
len3 = plt.scatter(k,P,color=color1,s=s)

plt.hist(Nc2,13,normed=1,alpha=alpha,color=color2,histtype='bar',align='left')
len2 = plt.scatter(k,P2,color=color2,s=s)

plt.hist(Nc3,8,normed=1,alpha=alpha,color=color3,histtype='bar',align='left')
len1 = plt.scatter(k,P3,color=color3,s=s)
ax=plt.gca()

xlim=[-.5,16.]
ylim=[0.,.40]
xticks=np.arange(0.,17.,2.)
yticks=np.arange(0.,.5,.1)
ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.set_xticks(xticks)
ax.set_yticks(yticks)

ax.legend([len1,len2,len3],['length 3nm','length 8nm','length 14nm'],frameon=False)
ax.set_xlabel('binding attempts')
ax.set_ylabel('relative frequency/probability')


#plt2=plt.subplot(gs[1])
#plt2.plot([3.,8.,14.],[lam3,lam2,lam])
#plt2.scatter([14.],[lam], color=color1,s=100,marker='s')
#plt2.scatter([8.0],[lam2],color=color2,s=100,marker='s')
#plt2.scatter([3.0],[lam3],color=color3,s=100,marker='s')
#plt2.set_xlabel('length of binding site [nm]')
#plt2.set_ylabel('mean binding attempts')


plt.tight_layout()
plt.savefig('attempts.pdf')
#plt.show()
