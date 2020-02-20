import numpy as np
from scipy import sparse
from io import StringIO
from os import path
from getSmallBody import getSmallBody
from showData import showData

def loadData(file_path):
    # file name
    file_path1 = file_path + '.vert'
    file_path2 = file_path + '.tri'
    [ver, polygons] = dataLoader(file_path1, file_path2)

    # fit for idx of vertex, should start at 0 and not at 1
    polygons = polygons - 1

    # get part of the body
    num_of_polygons_in_small_model = 1000
    seed = 1
    # name for the file that we will save
    small_body_path = './small_body_data_' + str(num_of_polygons_in_small_model) + '_seed_' + str(seed)

    # if file does not exist create it
    if not path.exists(small_body_path + '.npy'):
        small_body_polygons = getSmallBody(polygons, num_of_polygons_in_small_model, seed)
        np.save(small_body_path, small_body_polygons)
    else:
        small_body_polygons = np.load(small_body_path + '.npy')

    # initial_v = np.ones(3400)
    # showData(ver, all_body_polygons=polygons, small_body_polygons=small_body_polygons, selected_vertices=initial_v[:] * 0)

    small_body_file_path = file_path + '_small_body'
    if not path.exists(small_body_file_path + '.tri'):
        np.savetxt(small_body_file_path + '.tri', small_body_polygons)
    if not path.exists(small_body_file_path + '.vert'):
        np.savetxt(small_body_file_path + '.vert', ver)

    #########################################################################################################
    ############################################# get laplacian #############################################
    #########################################################################################################

    tmp_path = file_path + '_laplacian_W.txt'
    if not path.exists(tmp_path):
        print("There is no laplacian for whole body")
        exit()
    else:
        f = open(tmp_path, 'r')
        laplacian_X_W = np.loadtxt(StringIO(f.read()))
        sparse_laplacian_X_W = sparse.csr_matrix(laplacian_X_W)

    tmp_path = file_path + '_laplacian_A.txt'
    if not path.exists(tmp_path):
        print("There is no laplacian for whole body")
        exit()
    else:
        f = open(tmp_path, 'r')
        laplacian_X_A = np.loadtxt(StringIO(f.read()))
        sparse_laplacian_X_A = sparse.csr_matrix(laplacian_X_A)

    small_body_laplacian_file_path = file_path + '_small_body'
    tmp_path = small_body_laplacian_file_path + '_laplacian_W.txt'
    if not path.exists(tmp_path):
        print("There is no laplacian for whole body")
        exit()
    else:
        f = open(tmp_path, 'r')
        laplacian_Y_W = np.loadtxt(StringIO(f.read()))
        sparse_laplacian_Y_W = sparse.csr_matrix(laplacian_Y_W)

    tmp_path = small_body_laplacian_file_path + '_laplacian_A.txt'
    if not path.exists(tmp_path):
        print("There is no laplacian for whole body")
        exit()
    else:
        f = open(tmp_path, 'r')
        laplacian_Y_A = np.loadtxt(StringIO(f.read()))
        sparse_laplacian_Y_A = sparse.csr_matrix(laplacian_Y_A)

    tmp_path = small_body_laplacian_file_path + '_laplacian_A_inv.txt'
    if not path.exists(tmp_path):
        print("There is no laplacian for whole body")
        exit()
    else:
        f = open(tmp_path, 'r')
        laplacian_Y_A_inv = np.loadtxt(StringIO(f.read()))
        sparse_laplacian_Y_A_inv = sparse.csr_matrix(laplacian_Y_A_inv)



    return polygons, small_body_polygons, ver,\
           sparse_laplacian_X_W, sparse_laplacian_X_A,\
           sparse_laplacian_Y_W, sparse_laplacian_Y_A, sparse_laplacian_Y_A_inv




def dataLoader(ver_path, tri_path):
    f = open(tri_path, 'r') 
    polygons = np.loadtxt(StringIO(f.read()))
    print('number of polygons: ' + str(np.shape(polygons)) )

    f = open(ver_path, 'r') 
    ver = np.loadtxt(StringIO(f.read()))
    print('number of vertices: ' + str(np.shape(ver)) )
    
    return [ver, polygons]


