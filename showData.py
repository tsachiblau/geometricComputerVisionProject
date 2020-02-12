import numpy as np
import mpl_toolkits.mplot3d as a3
import matplotlib.colors as colors
import matplotlib.pyplot as plt

def showData(vertex, polygons):
    x = vertex[:, 0]
    y = vertex[:, 1]
    z = vertex[:, 2]

    #normalize
    global_min = min(np.min(x), np.min(y), np.min(z))
    global_max = max(np.max(x), np.max(y), np.max(z))
    ax = a3.Axes3D(plt.figure())
    ax.set_xlim([global_min, global_max])
    ax.set_ylim([global_min, global_max])
    ax.set_zlim([global_min, global_max])
    ax.grid(None)
    ax.axis('off')

    #draw all polygons
    for i in range(np.shape(polygons)[0]):
        vertex = np.int16(polygons[i, :]) 
        vtx = [[x[vertex[0]], y[vertex[0]], z[vertex[0]]],\
               [x[vertex[1]], y[vertex[1]], z[vertex[1]]],\
               [x[vertex[2]], y[vertex[2]], z[vertex[2]]]]
        tri = a3.art3d.Poly3DCollection([vtx])
        tri.set_edgecolor('k')
        ax.add_collection3d(tri)

    plt.show()
