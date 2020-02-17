import numpy as np

def isMember(A, B):

    A = np.int16(A)
    B = np.int16(B)
    res = np.zeros_like(A)
    
    for i in range(np.shape(A)[1]):
        tmp_sum = 0
        for b in B:
            tmp_sum += np.int16(A[:, i] == b)
        res[:, i] = tmp_sum
    return res
