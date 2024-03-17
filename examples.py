import pymesh
import boolean

m1 = pymesh.load_mesh("data/box_1.obj")
m2 = pymesh.load_mesh("data/sphere_1.obj")

# Basic union
u = boolean.union(m2, m1, resolution=128)

# Smooth unions with varying smoothness
su1 = boolean.smoothUnion(m2,m1,smoothness=0.4,resolution=128,pad=10)
su2 = boolean.smoothUnion(m2,m1,smoothness=0.8,resolution=128,pad=10)

pymesh.save_mesh("tmp/u.obj",u)
pymesh.save_mesh("tmp/su1.obj",su1)
pymesh.save_mesh("tmp/su2.obj",su2)

# Basic difference
d = boolean.subtraction(m2,m1,resolution=128)

# Smooth differences with varying smoothness
sd1 = boolean.smoothSubtraction(m2,m1,smoothness=0.4,resolution=128,pad=10)
sd2 = boolean.smoothSubtraction(m2,m1,smoothness=0.8,resolution=128,pad=10)

pymesh.save_mesh("tmp/d.obj",d)
pymesh.save_mesh("tmp/sd1.obj",sd1)
pymesh.save_mesh("tmp/sd2.obj",sd2)

# Basic intersection
i = boolean.intersection(m2,m1,resolution=128)

# Smooth intersections with varying smoothness
si1 = boolean.smoothIntersection(m2,m1,smoothness=0.4,resolution=128,pad=10)
si2 = boolean.smoothIntersection(m2,m1,smoothness=0.8,resolution=128,pad=10)

pymesh.save_mesh("tmp/i.obj",i)
pymesh.save_mesh("tmp/si1.obj",si1)
pymesh.save_mesh("tmp/si2.obj",si2)


bunny = pymesh.load_mesh("data/bunny.obj")

# rounding with varying roundness
r1 = boolean.round(bunny,roundness=0.1,resolution=128,pad=20.)
r2 = boolean.round(bunny,roundness=0.2,resolution=128,pad=25.)

pymesh.save_mesh("tmp/r1.obj",r1)
pymesh.save_mesh("tmp/r2.obj",r2)


bunny1 = pymesh.load_mesh("data/bunny_1.obj")

# boolean operation on non watertight mesh
nw = boolean.subtraction(bunny1,m1,resolution=128)

pymesh.save_mesh("tmp/nw.obj",nw)