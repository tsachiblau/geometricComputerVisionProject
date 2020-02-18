import numpy as np
from dataLoader import dataLoader
from showData import showData
from getSmallBody import getSmallBody
from prepreForLaplacian import prepreForLaplacian
from mindboggle.shapes.laplace_beltrami import computeAB
from mindboggle.shapes.laplace_beltrami import fem_laplacian
from findOptimalV import findOptimalV



#load data
file_path1 = './dataset/dog0.vert'
file_path2 = './dataset/dog0.tri'
[ver, polygons] = dataLoader(file_path1, file_path2)

#fit for idx of vertex
polygons = polygons - 1

#show data
# showData(ver, polygons)

#get part of the body

num_of_polygons_in_small_model = 300

seed = 10
small_body_polygons = getSmallBody(polygons, num_of_polygons_in_small_model, seed)

#show data
# showData(ver, small_body_polygons)

#clac laplacian
number_of_eigen_values_y = 20
ver_laplace_x, polygons_laplace_x = prepreForLaplacian(ver, polygons)
ver_laplace_y, polygons_laplace_y = prepreForLaplacian(ver, small_body_polygons)

eigen_values_x, eigen_vectors_x =  fem_laplacian(ver_laplace_x, polygons_laplace_x, spectrum_size = number_of_eigen_values_y)
eigen_values_y, eigen_vectors_y =  fem_laplacian(ver_laplace_y, polygons_laplace_y, spectrum_size = number_of_eigen_values_y)
laplacianA, laplacianB = computeAB(ver_laplace_x, polygons_laplace_x)

#first_func = np.sum(eigen_vectors_x[:, 50:48], 1)
#res_func = first_func
#showData(ver, polygons, res_func)


initial_v = np.ones( np.shape(ver_laplace_x)[0] ) * 0
num_of_iter = 90
tau = (10 * eigen_values_y[-1]) / 2
v = findOptimalV(laplacianA, eigen_values_x, initial_v, eigen_values_y, eigen_vectors_x, tau, num_of_iter)
showData(ver, all_body_polygons = polygons, small_body_polygons = small_body_polygons, selected_vertices = v, num_of_iter = num_of_iter)
