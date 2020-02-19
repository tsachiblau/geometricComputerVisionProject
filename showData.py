import numpy as np

import matplotlib
matplotlib.use('TkAgg')
import mpl_toolkits.mplot3d as a3
import matplotlib.pyplot as plt




def showData(vertex, all_body_polygons, small_body_polygons, selected_vertices, num_of_iter):

    x = vertex[:, 0]
    y = vertex[:, 1]
    z = vertex[:, 2]

    #normalize
    global_min = min(np.min(x), np.min(y), np.min(z))
    global_max = max(np.max(x), np.max(y), np.max(z))

    # create plot
    ax = a3.Axes3D(plt.figure())
    ax.set_xlim([global_min, global_max])
    ax.set_ylim([global_min, global_max])
    ax.set_zlim([global_min, global_max])
    ax.grid(None)
    ax.axis('off')

    #show all body
    showPolygons(ax, vertex, all_body_polygons, np.array([0, 0, 1]))

    #show small body
    if small_body_polygons is not None:
        showPolygons(ax, vertex, small_body_polygons,  np.array([0, 1, 0]))

    th_of_vertex = 0
    for v_i in range(np.shape(selected_vertices)[0]):
        if selected_vertices[v_i] > th_of_vertex:
            ax.scatter(x[v_i], y[v_i], z[v_i], c = np.array([1, 0, 0]))
    i_num_of_points = np.sum( np.array(selected_vertices) > th_of_vertex)
    ax.set_title('num of iter ' + str(num_of_iter) + '    num of points: ' + str(i_num_of_points))
    plt.show()




def showEigenValues(vertex, all_body_polygons, color):

    x = vertex[:, 0]
    y = vertex[:, 1]
    z = vertex[:, 2]

    #normalize
    global_min = min(np.min(x), np.min(y), np.min(z))
    global_max = max(np.max(x), np.max(y), np.max(z))

    # create plot
    ax = a3.Axes3D(plt.figure())
    ax.set_xlim([global_min, global_max])
    ax.set_ylim([global_min, global_max])
    ax.set_zlim([global_min, global_max])
    ax.grid(None)
    ax.axis('off')

    #show all body
    showPolygons(ax, vertex, all_body_polygons, color)
    plt.show()



def showPolygons(ax, vertex, polygons, face_color):


    x = vertex[:, 0]
    y = vertex[:, 1]
    z = vertex[:, 2]

    #normalize
    global_min = min(np.min(x), np.min(y), np.min(z))
    global_max = max(np.max(x), np.max(y), np.max(z))

    #color normalization
    if np.shape(face_color)[0] > 3:
        min_face_color = np.min(face_color)
        normalize_face_color = np.max(face_color) - min_face_color



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

        try:
            if np.shape(face_color)[0] <= 3:
                color_val = face_color
            else:
                tmp_val = ((face_color[idx_p1] + face_color[idx_p2] + face_color[idx_p3]) / 3 ) - min_face_color
                one_color_val = np.float( tmp_val / normalize_face_color )
                color_val = plt.cm.hot( np.clip(one_color_val, one_color_val, one_color_val) )

            tri.set_facecolor(color_val)


        except:
            print("There is a problem is showData funciton!")

        ax.add_collection3d(tri)
