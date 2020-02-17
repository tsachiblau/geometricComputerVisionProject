import numpy as np
from isMember import isMember
from removeIndexFromVector import removeIndexFromVector

def getSmallBody(polygons, num_of_polygons_in_small_model, seed):
    
    num_of_polygons = np.shape(polygons)[0]
    np.random.seed(seed) # remove in run time/

    #get seed point
    seed_polygon = np.random.randint(1, num_of_polygons - 2) # we sont include the end and beginnig of the vector

    #idx of all polygons
    list_of_all_polygons = list(range(num_of_polygons))

    #remove the seed
    remove_idx = seed_polygon
    list_of_all_polygons = removeIndexFromVector(list_of_all_polygons, remove_idx)

    #list of small polygon
    list_of_small_body = [seed_polygon]
    list_of_small_body_vertex = list(np.int16(polygons[seed_polygon, :]))



    for i in range(num_of_polygons_in_small_model):

        relevant_idx = isMember(polygons[list_of_all_polygons, :], list_of_small_body_vertex)
        relevant_idx = np.sum(relevant_idx, 1)
        max_val = np.max(relevant_idx)
        relevant_idx = relevant_idx == max_val
        relevant_idx = np.where(relevant_idx)[0]

        idx_from_list_of_polygons = relevant_idx[0]
        idx_of_polygon = list_of_all_polygons[ idx_from_list_of_polygons ]
        vertex_of_new_poly = np.int16(polygons[idx_of_polygon, :])

        #concat to small body 
        list_of_small_body = list_of_small_body + [ idx_of_polygon ]
        list_of_small_body_vertex = list_of_small_body_vertex + list(vertex_of_new_poly)

        #remove from list
        list_of_all_polygons = removeIndexFromVector(list_of_all_polygons, idx_from_list_of_polygons)


    small_body_polygons = polygons[list_of_small_body, :]
    
    return small_body_polygons