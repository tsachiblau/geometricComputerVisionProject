import numpy as np
import mpl_toolkits.mplot3d as a3
import matplotlib.colors as colors
import matplotlib.pyplot as plt

def showData(vertex, polygons, face_color = None):

    if face_color is not None:
        # face_color = face_color.todense()
        min_face_color = np.min(face_color)
        normalize_face_color = np.max(face_color) - min_face_color

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
        idx_p1 = vertex[0]
        idx_p2 = vertex[1]
        idx_p3 = vertex[2]
        l1 = [x[idx_p1], y[idx_p1], z[idx_p1]]
        l2 = [x[idx_p2], y[idx_p2], z[idx_p2]]
        l3 = [x[idx_p3], y[idx_p3], z[idx_p3]]
        vtx = [l1, l2, l3]

        tri = a3.art3d.Poly3DCollection([vtx])
        #tri.set_edgecolor('k')
        if face_color is not None:
            try:
                tmp_val = ((face_color[idx_p1] + face_color[idx_p2] + face_color[idx_p3]) / 3 ) - min_face_color
                color_val = np.float( tmp_val / normalize_face_color )
                print(color_val)
                tri.set_facecolor([color_val, color_val, color_val])
            except:
                print("There is a problem is showData funciton!")
        else:
            tri.set_facecolor([1, 1, 1])

        ax.add_collection3d(tri)

    plt.show()
