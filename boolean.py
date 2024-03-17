import pymesh
import numpy as np
import skimage
from typing import Tuple,List

##
#   Auxiliary functions
##
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

def _makeSDFGrid(m:pymesh.Mesh,resolution:int,aabb:Tuple[int],pad:float=0.0)->np.ndarray:
    ox = pad * (aabb[1]-aabb[0])/resolution
    oy = pad * (aabb[3]-aabb[2])/resolution
    oz = pad * (aabb[5]-aabb[4])/resolution
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

def _smoothSubtraction(sdf1:np.ndarray,sdf2:np.ndarray,smoothness:float)->np.ndarray:
    h = np.clip(0.5 - 0.5*(sdf2+sdf1)/smoothness,0.,1.)
    interp = sdf2 * (1. - h) - sdf1 * h
    res = interp + smoothness * h * (1.-h)
    return res

def _smoothIntersection(sdf1:np.ndarray,sdf2:np.ndarray,smoothness:float)->np.ndarray:
    h = np.clip(0.5 - 0.5*(sdf2-sdf1)/smoothness,0.,1.)
    interp = sdf2 * (1. - h) + sdf1 * h
    res = interp + smoothness * h * (1.-h)
    return res

##
# Non Smooth Boolean Operations
##
def union(m1:pymesh.Mesh,m2:pymesh.Mesh,resolution:int,pad:float=1.0)->pymesh.Mesh:
    """
    Compute the union between two meshes
    Parameters:
    m1 (pymesh.Mesh): The first operand
    m2 (pymesh.Mesh): The second operand
    resolution (int): The resolution of the volumetric grid
    pad (float): Add padding to the original grid

    Returns:
    pymesh.Mesh: The result of the boolean operation
    """
    aabb = _computeAABB([m1,m2])
    sdf1,_ = _makeSDFGrid(m1,resolution,aabb,pad=pad)
    sdf2,_ = _makeSDFGrid(m2,resolution,aabb,pad=pad)
    sdf = np.minimum(sdf1,sdf2)
    ox = pad * (aabb[1]-aabb[0])/resolution
    oy = pad * (aabb[3]-aabb[2])/resolution
    oz = pad * (aabb[5]-aabb[4])/resolution
    spacing = (
        (aabb[1]-aabb[0]+2*ox)/resolution,
        (aabb[3]-aabb[2]+2*oy)/resolution,
        (aabb[5]-aabb[4]+2*oz)/resolution
    )
    verts,faces,_,_ = skimage.measure.marching_cubes(sdf,level=0.,spacing=spacing)
    mesh = pymesh.form_mesh(verts,faces)
    return mesh

def subtraction(m1:pymesh.Mesh,m2:pymesh.Mesh,resolution:int,pad:float=1.0)->pymesh.Mesh:
    """
    Compute the difference between two meshes (m2 - m1)
    Parameters:
    m1 (pymesh.Mesh): The first operand
    m2 (pymesh.Mesh): The second operand
    resolution (int): The resolution of the volumetric grid
    pad (float): Add padding to the original grid

    Returns:
    pymesh.Mesh: The result of the boolean operation
    """
    aabb = _computeAABB([m1,m2])
    sdf1,_ = _makeSDFGrid(m1,resolution,aabb,pad=pad)
    sdf2,_ = _makeSDFGrid(m2,resolution,aabb,pad=pad)
    sdf = np.maximum(-sdf1,sdf2)
    ox = pad * (aabb[1]-aabb[0])/resolution
    oy = pad * (aabb[3]-aabb[2])/resolution
    oz = pad * (aabb[5]-aabb[4])/resolution
    spacing = (
        (aabb[1]-aabb[0]+2*ox)/resolution,
        (aabb[3]-aabb[2]+2*oy)/resolution,
        (aabb[5]-aabb[4]+2*oz)/resolution
    )
    verts,faces,_,_ = skimage.measure.marching_cubes(sdf,level=0.,spacing=spacing)
    mesh = pymesh.form_mesh(verts,faces)
    return mesh

def intersection(m1:pymesh.Mesh,m2:pymesh.Mesh,resolution:int,pad:float=1.0)->pymesh.Mesh:
    """
    Compute the intersection between two meshes
    Parameters:
    m1 (pymesh.Mesh): The first operand
    m2 (pymesh.Mesh): The second operand
    resolution (int): The resolution of the volumetric grid
    pad (float): Add padding to the original grid

    Returns:
    pymesh.Mesh: The result of the boolean operation
    """
    aabb = _computeAABB([m1,m2])
    sdf1,_ = _makeSDFGrid(m1,resolution,aabb,pad=pad)
    sdf2,_ = _makeSDFGrid(m2,resolution,aabb,pad=pad)
    sdf = np.maximum(sdf1,sdf2)
    ox = pad * (aabb[1]-aabb[0])/resolution
    oy = pad * (aabb[3]-aabb[2])/resolution
    oz = pad * (aabb[5]-aabb[4])/resolution
    spacing = (
        (aabb[1]-aabb[0]+2*ox)/resolution,
        (aabb[3]-aabb[2]+2*oy)/resolution,
        (aabb[5]-aabb[4]+2*oz)/resolution
    )
    verts,faces,_,_ = skimage.measure.marching_cubes(sdf,level=0.,spacing=spacing)
    mesh = pymesh.form_mesh(verts,faces)
    return mesh

##
# Smooth Boolean Operations
##
def smoothUnion(m1:pymesh.Mesh,m2:pymesh.Mesh,smoothness:float,resolution:int,pad:float=10.0)->pymesh.Mesh:
    """
    Compute the smooth union between two meshes
    Parameters:
    m1 (pymesh.Mesh): The first operand
    m2 (pymesh.Mesh): The second operand
    smoothness (float): The amount of smoothness in actual distance units
    resolution (int): The resolution of the volumetric grid
    pad (float): Add padding to the original grid

    Returns:
    pymesh.Mesh: The result of the boolean operation
    """
    aabb = _computeAABB([m1,m2])
    sdf1,_ = _makeSDFGrid(m1,resolution,aabb,pad=pad)
    sdf2,_ = _makeSDFGrid(m2,resolution,aabb,pad=pad)
    sdf = _smoothUnion(sdf1,sdf2,smoothness)
    ox = pad * (aabb[1]-aabb[0])/resolution
    oy = pad * (aabb[3]-aabb[2])/resolution
    oz = pad * (aabb[5]-aabb[4])/resolution
    spacing = (
        (aabb[1]-aabb[0] + 2*ox)/resolution,
        (aabb[3]-aabb[2] + 2*oy)/resolution,
        (aabb[5]-aabb[4] + 2*oz)/resolution
    )
    verts,faces,_,_ = skimage.measure.marching_cubes(sdf,level=0.,spacing=spacing)
    mesh = pymesh.form_mesh(verts,faces)
    return mesh

def smoothSubtraction(m1:pymesh.Mesh,m2:pymesh.Mesh,smoothness:float,resolution:int,pad:float=10.0)->pymesh.Mesh:
    """
    Compute the smooth difference between two meshes
    Parameters:
    m1 (pymesh.Mesh): The first operand
    m2 (pymesh.Mesh): The second operand
    smoothness (float): The amount of smoothness in actual distance units
    resolution (int): The resolution of the volumetric grid
    pad (float): Add padding to the original grid

    Returns:
    pymesh.Mesh: The result of the boolean operation
    """
    aabb = _computeAABB([m1,m2])
    sdf1,_ = _makeSDFGrid(m1,resolution,aabb,pad=pad)
    sdf2,_ = _makeSDFGrid(m2,resolution,aabb,pad=pad)
    sdf = _smoothSubtraction(sdf1,sdf2,smoothness)
    ox = pad * (aabb[1]-aabb[0])/resolution
    oy = pad * (aabb[3]-aabb[2])/resolution
    oz = pad * (aabb[5]-aabb[4])/resolution
    spacing = (
        (aabb[1]-aabb[0] + 2*ox)/resolution,
        (aabb[3]-aabb[2] + 2*oy)/resolution,
        (aabb[5]-aabb[4] + 2*oz)/resolution
    )
    verts,faces,_,_ = skimage.measure.marching_cubes(sdf,level=0.,spacing=spacing)
    mesh = pymesh.form_mesh(verts,faces)
    return mesh

def smoothIntersection(m1:pymesh.Mesh,m2:pymesh.Mesh,smoothness:float,resolution:int,pad:float=10.0)->pymesh.Mesh:
    """
    Compute the smooth intersection between two meshes
    Parameters:
    m1 (pymesh.Mesh): The first operand
    m2 (pymesh.Mesh): The second operand
    smoothness (float): The amount of smoothness in actual distance units
    resolution (int): The resolution of the volumetric grid
    pad (float): Add padding to the original grid

    Returns:
    pymesh.Mesh: The result of the boolean operation
    """
    aabb = _computeAABB([m1,m2])
    sdf1,_ = _makeSDFGrid(m1,resolution,aabb,pad=pad)
    sdf2,_ = _makeSDFGrid(m2,resolution,aabb,pad=pad)
    sdf = _smoothIntersection(sdf1,sdf2,smoothness)
    ox = pad * (aabb[1]-aabb[0])/resolution
    oy = pad * (aabb[3]-aabb[2])/resolution
    oz = pad * (aabb[5]-aabb[4])/resolution
    spacing = (
        (aabb[1]-aabb[0] + 2*ox)/resolution,
        (aabb[3]-aabb[2] + 2*oy)/resolution,
        (aabb[5]-aabb[4] + 2*oz)/resolution
    )
    verts,faces,_,_ = skimage.measure.marching_cubes(sdf,level=0.,spacing=spacing)
    mesh = pymesh.form_mesh(verts,faces)
    return mesh

def round(m:pymesh.Mesh,roundness:float,resolution:int,pad:float=10.0)->pymesh.Mesh:
    """
    Compute a rounded version of the original mesh
    Parameters:
    m (pymesh.Mesh): The input mesh
    roundness (float): The amount of roundness in actual distance units
    resolution (int): The resolution of the volumetric grid
    pad (float): Add padding to the original grid

    Returns:
    pymesh.Mesh: The rounded mesh
    """
    aabb = _computeAABB([m])
    sdf,_ = _makeSDFGrid(m,resolution,aabb,pad)
    ox = pad * (aabb[1]-aabb[0])/resolution
    oy = pad * (aabb[3]-aabb[2])/resolution
    oz = pad * (aabb[5]-aabb[4])/resolution
    spacing = (
        (aabb[1]-aabb[0] + 2*ox)/resolution,
        (aabb[3]-aabb[2] + 2*oy)/resolution,
        (aabb[5]-aabb[4] + 2*oz)/resolution
    )
    verts,faces,_,_ = skimage.measure.marching_cubes(sdf,level=roundness,spacing=spacing)
    mesh = pymesh.form_mesh(verts,faces)
    return mesh