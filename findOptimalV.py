import scipy
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt


def loss(t_sigma_x, t_v, t_eigen_values_y, tau):

    t_tanh = tf.math.tanh(t_v)
    t_tanh_add = tf.add(t_tanh, 1)
    t_tanh_normalize = tf.multiply(t_tanh_add, tau)

    #diag v
    t_diag_v = tf.linalg.tensor_diag( t_tanh_normalize )

    #add v to cov
    t_sum = tf.add(t_sigma_x, t_diag_v)

    #get eignevalues
    t_eigenvalues = tf.linalg.eigvalsh( t_sum )

    #get num_of_eigenvalues of eigenvalues
    num_of_eigenvalues = t_eigen_values_y.get_shape().dims[0]
    t_cut_eigen_values = t_eigenvalues[0 : num_of_eigenvalues ]


    t_eigen_values_y_inv = tf.divide( tf.ones(num_of_eigenvalues, dtype=tf.dtypes.float64), t_eigen_values_y )##################################

    t_sub = tf.subtract(t_cut_eigen_values, t_eigen_values_y, )
    t_normalize = tf.math.multiply(t_sub, tf.cast(t_eigen_values_y_inv, tf.float64) )
    t_norm = tf.tensordot(t_normalize, t_normalize, axes=1)

    return t_norm



def step(t_sigma_x, t_v, t_eigen_values_y, tau, lr = 1e-4):
    with tf.GradientTape() as tape:
        v_loss = loss(t_sigma_x, t_v, t_eigen_values_y, tau)

    t_v_gradient = tape.gradient(v_loss, t_v)

    # Update variables
    t_v.assign_sub(t_v_gradient * lr)

    return v_loss, t_v_gradient





def findOptimalV(sigma_x, eigen_value_x, v, eigen_value_y, eigen_vectors_x, tau, num_of_iter = 2):

    #arrange sigma_x
    if isinstance( sigma_x, scipy.sparse.csr.csr_matrix ):
        sigma_x = sigma_x.todense()

    # Setup a stochastic gradient descent optimizer
    opt = tf.keras.optimizers.SGD(learning_rate= 1e-6)
    # opt = tf.keras.optimizers.Adadelta(learning_rate= 1e-4, rho = 0.999)

    # Define loss function and variables to optimize
    t_v = tf.Variable(v, trainable = True)
    t_sigma_x = tf.Variable(sigma_x)
    t_eigen_values_y = tf.Variable(eigen_value_y)

    loss_error = []
    plt.figure()
    plt.show(block = False)

    lr = 1e-5

    # Optimize for a fixed number of steps
    for i in range(num_of_iter):
        print('iter: ' + str(i) + '/' + str(num_of_iter))
        try:
            # opt.minimize(loss_fn, var_list)

            ms_error, t_v_gradient = step(t_sigma_x, t_v, t_eigen_values_y, tau, lr = lr)
            loss_error.append(ms_error)

            if np.mod(i, 10) == 0:
                plt.clf()
                plt.subplot(3, 1, 1)
                plt.plot(np.array(range(np.shape(loss_error)[0])), loss_error)
                plt.subplot(3, 1, 2)
                tmpx = np.array( range(t_v.shape[0]) )
                tmpy = np.array( tf.keras.backend.eval(t_v) )
                plt.scatter( tmpx, tmpy, facecolors = 'b')
                plt.title('num of vertices' + str(np.sum( tmpy > 0 )))
                plt.subplot(3, 1, 3)
                tmpx = np.array( range(t_v_gradient.shape[0]) )
                tmpy = np.array( tf.keras.backend.eval(t_v_gradient) )
                plt.scatter( tmpx, tmpy, facecolors = 'b')
                plt.draw()
                plt.pause(0.001)
                print('    current error is: ' + str(ms_error))

        except:
            print('there is an error in the optimization')
            break

    v = tf.keras.backend.eval(t_v)
    return v