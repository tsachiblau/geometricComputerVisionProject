import numpy as np
import mpl_toolkits.mplot3d as a3
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from isMember import isMember
from removeIndexFromVector import removeIndexFromVector
from scipy.sparse.linalg import eigsh, lobpcg
import scipy
import tensorflow as tf

def buildGraph(sigma_x, v, initial_x, eigen_value_y):

    t_v = tf.Variable(v)
    t_diag_v = tf.linalg.tensor_diag( t_v )
    if isinstance( sigma_x, scipy.sparse.csr.csr_matrix ):
        sigma_x = sigma_x.todense()
    t_sigma_x = tf.constant( sigma_x, dtype=None, shape=None, name='Const' )
    t_sum = tf.add(t_sigma_x, t_diag_v)
    t_eigenvalues = tf.linalg.eigvalsh( t_sum )
    t_cut_eigen_values = t_eigenvalues[0 : np.shape(eigen_value_y)[0] ]
    t_eigen_values_y = tf.constant( eigen_value_y, dtype=None, shape=None, name='Const' )
    t_eigen_values_y_inv = tf.constant( 1 / np.array(eigen_value_y), dtype=None, shape=None, name='Const' )

    t_sub = tf.subtract(t_cut_eigen_values, t_eigen_values_y)
    t_normalize = tf.math.multiply(t_sub, t_eigen_values_y_inv)
    t_norm = tf.tensordot(t_normalize, t_normalize, axes=1)
    return t_norm, t_v


