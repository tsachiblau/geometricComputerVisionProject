import numpy as np
from dataLoader import dataLoader
from showData import showData
from getSmallBody import getSmallBody

#load data
file_path1 = './dataset/dog0.vert'
file_path2 = './dataset/dog0.tri'
[ver, polygons] = dataLoader(file_path1, file_path2)

#fit for idx of vertex
polygons = polygons - 1

#show data
showData(ver, polygons)

#get part of the body

num_of_polygons_in_small_model = 1000

seed = 10
small_body_polygons = getSmallBody(polygons, num_of_polygons_in_small_model, seed)

#show data
showData(ver, small_body_polygons)
