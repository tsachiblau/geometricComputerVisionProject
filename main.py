import numpy as np
from dataLoader import dataLoader
from showData import showData
from getSmallBody import getSmallBody
from prepreForLaplacian import prepreForLaplacian
from mindboggle.shapes.laplace_beltrami import computeAB
from mindboggle.shapes.laplace_beltrami import fem_laplacian
from findOptimalV import findOptimalV
from showData import showEigenValues
from scipy.sparse.linalg import inv
from scipy import sparse
import os.path
from os import path


#load data
file_path = './dataset/dog0'
file_path1 = file_path + '.vert'
file_path2 = file_path + '.tri'
[ver, polygons] = dataLoader(file_path1, file_path2)

#fit for idx of vertex
polygons = polygons - 1

#get part of the body
num_of_polygons_in_small_model = 1000
seed = 5
small_body_path = './small_body_data_' + str(num_of_polygons_in_small_model) + '_seed_' + str(seed)

if not path.exists(small_body_path + '.npy'):
    small_body_polygons = getSmallBody(polygons, num_of_polygons_in_small_model, seed)
    np.save(small_body_path, small_body_polygons)
else:
    small_body_polygons = np.load(small_body_path + '.npy')

#clac laplacian
number_of_eigen_values_y = 20
ver_laplace_x, polygons_laplace_x = prepreForLaplacian(ver, polygons)
ver_laplace_y, polygons_laplace_y = prepreForLaplacian(ver, small_body_polygons)

eigen_values_x, eigen_vectors_x = fem_laplacian(ver_laplace_x, polygons_laplace_x, spectrum_size = number_of_eigen_values_y)
eigen_values_y, eigen_vectors_y = fem_laplacian(ver_laplace_y, polygons_laplace_y, spectrum_size = number_of_eigen_values_y)
A, B = computeAB(ver_laplace_x, polygons_laplace_x)
B_inv = inv(B)
laplacian = sparse.csr_matrix.multiply(B_inv, A)

#show eigenvalue
# first_func = np.sum(eigen_vectors_x[:, 10:11], 1)
# res_func = first_func
# showEigenValues(ver, polygons, res_func)

tau = (10 * eigen_values_y[-1])
initial_v = np.ones( np.shape(ver_laplace_x)[0] ) * 1
num_of_iter = 1000
v = findOptimalV(laplacian, eigen_values_x, initial_v, eigen_values_y, eigen_vectors_x, tau / 2, num_of_iter)
showData(ver, all_body_polygons = polygons, small_body_polygons = small_body_polygons, selected_vertices = v, num_of_iter = num_of_iter)
