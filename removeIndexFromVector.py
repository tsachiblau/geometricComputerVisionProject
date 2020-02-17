import numpy as np

def removeIndexFromVector(vector, idx):
    
    
    if idx == 0:
        vector = vector[1:]
        return vector   
    
    if idx == np.shape(vector)[0] - 1:
        vector = vector[: np.shape(vector)[0]]
        return vector
    
    vector = vector[: idx] + vector[idx + 1:]
    return vector
