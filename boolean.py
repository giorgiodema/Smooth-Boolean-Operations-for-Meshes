import pymesh
import numpy as np
import skimage
from typing import Tuple,List


def _computeAABB(meshes:List[pymesh.Mesh])->Tuple[int]:
    v = meshes[0].vertices
    for m in meshes[1:]:
        v = np.concatenate([v,m.vertices],axis=0)
    minx = np.min(v[:,0])
    maxx = np.max(v[:,0])
    miny = np.min(v[:,1])
    maxy = np.max(v[:,1])
    minz = np.min(v[:,2])
    maxz = np.max(v[:,2])
    return (minx,maxx,miny,maxy,minz,maxz)

def _makeSDFGrid(m:pymesh.Mesh,resolution:int,aabb:Tuple[int])->np.ndarray:
    ox = 10.0 * (aabb[1]-aabb[0])/resolution
    oy = 10.0 * (aabb[3]-aabb[2])/resolution
    oz = 10.0 * (aabb[5]-aabb[4])/resolution
    x = np.linspace(aabb[0]-ox,aabb[1]+ox,resolution)
    y = np.linspace(aabb[2]-oy,aabb[3]+oy,resolution)
    z = np.linspace(aabb[4]-oz,aabb[5]+oz,resolution)
    points = np.zeros((resolution**3,3))
    for i in range(resolution):
        for j in range(resolution):
            for k in range(resolution):
                points[i*resolution**2 + j*resolution + k] = np.asarray([x[i],y[j],z[k]])
    sdf,_,_,_ = pymesh.signed_distance_to_mesh(m,points)
    sdf = np.reshape(sdf,(resolution,resolution,resolution))
    return sdf,points


def _smoothUnion(sdf1:np.ndarray,sdf2:np.ndarray,smoothness:float)->np.ndarray:
    h = np.clip(0.5 + 0.5*(sdf2-sdf1)/smoothness,0.,1.)
    interp = sdf2 * (1. - h) + sdf1 * h
    res = interp - smoothness * h * (1.-h)
    return res

def smoothUnion(m1:pymesh.Mesh,m2:pymesh.Mesh,smoothness:float,resolution:float)->pymesh.Mesh:
    aabb = _computeAABB([m1,m2])
    sdf1,_ = _makeSDFGrid(m1,resolution,aabb)
    sdf2,_ = _makeSDFGrid(m2,resolution,aabb)
    sdf = _smoothUnion(sdf1,sdf2,smoothness)
    ox = 10.0 * (aabb[1]-aabb[0])/resolution
    oy = 10.0 * (aabb[3]-aabb[2])/resolution
    oz = 10.0 * (aabb[5]-aabb[4])/resolution
    spacing = (
        (aabb[1]-aabb[0] + 2*ox)/resolution,
        (aabb[3]-aabb[2] + 2*oy)/resolution,
        (aabb[5]-aabb[4] + 2*oz)/resolution
    )
    verts,faces,_,_ = skimage.measure.marching_cubes(sdf,level=0.,spacing=spacing)
    mesh = pymesh.form_mesh(verts,faces)
    return mesh

def union(m1:pymesh.Mesh,m2:pymesh.Mesh,resolution:float)->pymesh.Mesh:
    aabb = _computeAABB([m1,m2])
    sdf1,_ = _makeSDFGrid(m1,resolution,aabb)
    sdf2,_ = _makeSDFGrid(m2,resolution,aabb)
    sdf = np.minimum(sdf1,sdf2)
    ox = 10.0 * (aabb[1]-aabb[0])/resolution
    oy = 10.0 * (aabb[3]-aabb[2])/resolution
    oz = 10.0 * (aabb[5]-aabb[4])/resolution
    spacing = (
        (aabb[1]-aabb[0]+2*ox)/resolution,
        (aabb[3]-aabb[2]+2*oy)/resolution,
        (aabb[5]-aabb[4]+2*oz)/resolution
    )
    verts,faces,_,_ = skimage.measure.marching_cubes(sdf,level=0.,spacing=spacing)
    mesh = pymesh.form_mesh(verts,faces)
    return mesh



if __name__=="__main__":
    import matplotlib.pyplot as plt

    TEST = 1

    if TEST == 0:
        m1 = pymesh.load_mesh("monkey.obj")
        m2 = pymesh.load_mesh("monkey.obj")
        m2 = pymesh.form_mesh(m2.vertices + [[1.0,0.,0.]],m2.faces)
        u = union(m1,m2,128)
        su = smoothUnion(m1,m2,0.2,128)
        pymesh.save_mesh("tmp/01u.obj",u)
        pymesh.save_mesh("tmp/01su.obj",su)

    if TEST == 1:
        m1 = pymesh.load_mesh("sphere.obj")
        m2 = pymesh.load_mesh("cube.obj")
        m2 = pymesh.form_mesh(m2.vertices + [[1.0,0.,0.]],m2.faces)
        u = union(m1,m2,128)
        su = smoothUnion(m1,m2,0.2,128)
        pymesh.save_mesh("tmp/02u.obj",u)
        pymesh.save_mesh("tmp/02su.obj",su)  

    if TEST == 10:
        res = 64
        m = pymesh.load_mesh("cube.obj")
        aabb = _computeAABB([m])
        sdists,points = _makeSDFGrid(m,res,aabb)
        sdists = np.reshape(sdists,(res**3,1))
        surface = points[np.abs(sdists[:,0])<=0.1]
        # Create a new matplotlib figure and its axes
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        # Scatter plot
        ax.scatter(surface[:,0], surface[:,1], surface[:,2])
        # Set labels for axes
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')
        # Show the plot
        plt.show()

    if TEST == 12:
        res = 128
        m = pymesh.load_mesh("cube.obj")
        aabb = _computeAABB([m])
        sdf,points = _makeSDFGrid(m,res,aabb)
        spacing = (
            (aabb[1]-aabb[0])/res,
            (aabb[3]-aabb[2])/res,
            (aabb[5]-aabb[4])/res
        )
        level = 0.5 * (sdf.min() + sdf.max())
        verts,faces,_,_ = skimage.measure.marching_cubes(sdf,level=0.0,spacing=spacing)
        mesh = pymesh.form_mesh(verts,faces)
        pymesh.save_mesh("tmp/cube_rec.obj",mesh)

    if TEST == 13:
        res = 128
        m = pymesh.load_mesh("bunny_big.obj")
        aabb = _computeAABB([m])
        sdf,points = _makeSDFGrid(m,res,aabb)
        plt.imshow(sdf[:,:,res//2],cmap="viridis")
        plt.colorbar()
        plt.show()