import numpy as np
from io import StringIO


def dataLoader(ver_path, tri_path):
    f = open(tri_path, 'r') 
    polygons = np.loadtxt(StringIO(f.read()))
    print('number of polygons: ' + str(np.shape(polygons)) )

    f = open(ver_path, 'r') 
    ver = np.loadtxt(StringIO(f.read()))
    print('number of vertices: ' + str(np.shape(ver)) )
    
    return [ver, polygons]