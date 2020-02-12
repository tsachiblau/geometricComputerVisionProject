import numpy as np
import mpl_toolkits.mplot3d as a3
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from isMember import isMember

def removeListOfIndexFromVector(vector, idx):

    vector = np.array(vector)
    keep_vector = list( range(np.shape(vector)[0]) )
    idx_to_remove = isMember(keep_vector, idx)
    idx_to_keep = np.int16(np.where(idx_to_remove == 0)).flatten()
    vector = [vector[ idx_to_keep[i] ] for i in range(np.shape(idx_to_keep)[0])]

    return vector
