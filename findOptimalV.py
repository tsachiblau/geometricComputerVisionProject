import numpy as np
import mpl_toolkits.mplot3d as a3
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import scipy
import tensorflow as tf


@tf.function
def f(t_sigma_x, t_v, t_eigen_values_y, tau):

    t_tanh = tf.math.tanh(t_v)
    t_tanh_add = tf.add(t_v, 1)
    t_tanh_normalize = tf.multiply(t_v, tau)

    #diag v
    t_diag_v = tf.linalg.tensor_diag( t_tanh_normalize )

    #add v to cov
    t_sum = tf.add(t_sigma_x, t_diag_v)

    #get eignevalues
    t_eigenvalues = tf.linalg.eigvalsh( t_sum )

    #get num_of_eigenvalues of eigenvalues
    num_of_eigenvalues = t_eigen_values_y.get_shape().dims[0]
    t_cut_eigen_values = t_eigenvalues[0 : num_of_eigenvalues ]


    t_eigen_values_y_inv = tf.divide( tf.ones(num_of_eigenvalues, dtype=tf.dtypes.float64), t_eigen_values_y )

    t_sub = tf.subtract(t_cut_eigen_values, t_eigen_values_y, )
    t_normalize = tf.math.multiply(t_sub, tf.cast(t_eigen_values_y_inv, tf.float64) )
    t_norm = tf.tensordot(t_normalize, t_normalize, axes=1)

    return t_norm


def findOptimalV(sigma_x, eigen_value_x, v, eigen_value_y, eigen_vectors_x, tau, num_of_iter = 2):

    #arrange sigma_x
    if isinstance( sigma_x, scipy.sparse.csr.csr_matrix ):
        sigma_x = sigma_x.todense()

    # Input data

    # Setup a stochastic gradient descent optimizer
    opt = tf.keras.optimizers.SGD(learning_rate=0.01)
    # Define loss function and variables to optimize
    t_v = tf.Variable(v)
    t_sigma_x = tf.Variable(sigma_x)
    t_eigen_values_y = tf.Variable(eigen_value_y)

    loss_fn = lambda: f(t_sigma_x, t_v, t_eigen_values_y, tau)

    var_list = [t_v]
    # Optimize for a fixed number of steps
    for _ in range(num_of_iter):
        opt.minimize(loss_fn, var_list)
        print(t_v)

    v = tf.keras.backend.eval(t_v)
    return v