import numpy as np

def prepreForLaplacian(ver, polygons):

    ver_list = [[np.int16(ver[i, 0]), np.int16(ver[i, 1]), np.int16(ver[i, 2])] for i in range(np.shape(ver)[0])]
    polygons_list = [ list(np.int16(polygons[i, :]))  for i in range(np.shape(polygons)[0]) ]

    return ver_list, polygons_list