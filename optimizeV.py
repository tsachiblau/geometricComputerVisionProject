import numpy as np
import mpl_toolkits.mplot3d as a3
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from isMember import isMember
from removeIndexFromVector import removeIndexFromVector
from scipy.sparse.linalg import eigsh, lobpcg
from scipy.sparse import diags
import tensorflow as tf

def optimizeV(t_x, eigen_value_y, t_v):

    opt = tf.keras.optimizers.SGD(learning_rate=0.1)
    opt_op = opt.minimize(t_v, var_list=[tf.vat_v])
    opt_op.run()
    # In eager mode, simply call minimize to update the list of variables.
    opt.minimize(t_x, var_list=[t_v])


