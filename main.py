import numpy as np
from dataLoader import loadData
from showData import showData
from mindboggle.shapes.laplace_beltrami import computeAB
from mindboggle.shapes.laplace_beltrami import fem_laplacian
from findOptimalV import findOptimalV
from scipy.sparse.linalg import eigsh
from showData import showEigenValues
import matplotlib.pyplot as plt


#########################################################################################################
############################################### load data ###############################################
#########################################################################################################

file_path = './dataset/dog0'
polygons, small_body_polygons, ver,\
sparse_laplacian_X_W, sparse_laplacian_X_A,\
sparse_laplacian_Y_W, sparse_laplacian_Y_A, sparse_laplacian_Y_A_inv = loadData(file_path)

#########################################################################################################
############################################# get laplacian #############################################
#########################################################################################################
number_of_eigen_values_y = 10
eigenvalues_X, eigenvectors_X = eigsh(sparse_laplacian_X_W, k = number_of_eigen_values_y, M=sparse_laplacian_X_A, sigma=-0.01)
eigenvalues_Y, eigenvectors_Y = eigsh(sparse_laplacian_Y_A_inv.dot(sparse_laplacian_Y_W), k = number_of_eigen_values_y, sigma=-0.01)

initial_v = np.ones( np.shape(eigenvectors_X)[0] ) * 1
num_of_iter = 10000

#########################################################################################################
################################################ visualization ##########################################
#########################################################################################################
# #show the part
# showData(ver, all_body_polygons = polygons, small_body_polygons = small_body_polygons, selected_vertices = initial_v[:] * 0)
#
# #show eigenvalue
# showEigenValues(ver, polygons, eigenvectors_X, eigenvalues_X)

# #show eigenvalue graph
plt.figure()
plt.plot(np.array(range(np.shape(eigenvalues_X)[0])), eigenvalues_X)
plt.plot(np.array(range(np.shape(eigenvalues_Y)[0])), eigenvalues_Y)
plt.legend(['all shape', 'part shape'])
plt.show(block = False)


#########################################################################################################
################################################### calc V ##############################################
#########################################################################################################
tau = (10 * eigenvectors_Y[number_of_eigen_values_y - 1])
initial_v = np.ones( np.shape(ver)[0] ) * 1
v = findOptimalV(sparse_laplacian_X_W, sparse_laplacian_X_A, initial_v, eigenvectors_Y, tau / 2, num_of_iter)

#########################################################################################################
################################################# show res ##############################################
#########################################################################################################
showData(ver, all_body_polygons = polygons, small_body_polygons = small_body_polygons, selected_vertices = v, num_of_iter = num_of_iter)
