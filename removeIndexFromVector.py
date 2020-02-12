import numpy as np
import mpl_toolkits.mplot3d as a3
import matplotlib.colors as colors
import matplotlib.pyplot as plt

def removeIndexFromVector(vector, idx):
    
    
    if idx == 0:
        vector = vector[1:]
        return vector   
    
    if idx == np.shape(vector)[0] - 1:
        vector = vector[: np.shape(vector)[0]]
        return vector
    
    vector = vector[: idx] + vector[idx + 1:]
    return vector
