#!/usr/bin/python
"""
Compute the Zernike moments of a collection of points.


Authors:
    - Arthur Mikhno, 2013, Columbia University (original MATLAB code)
    - Brian Rossa, 2013, Tank Think Labs, LLC (port to Python)
    - Arno Klein, 2013  (arno@mindboggle.info)  http://binarybottle.com

Copyright 2013,  Mindboggle team (http://mindboggle.info), Apache v2.0 License

"""


def zernike_moments(points, faces, order=10, scale_input=True,
                    decimate_fraction=0, decimate_smooth=0, verbose=False):
    """
    Compute the Zernike moments of a surface patch of points and faces.

    Optionally decimate the input mesh.

    Note::
      Decimation sometimes leads to an error of "Segmentation fault: 11"
      (Twins-2-1 left label 14 gives such an error only when decimated.)

    Parameters
    ----------
    points : list of lists of 3 floats
        x,y,z coordinates for each vertex
    faces : list of lists of 3 integers
        each list contains indices to vertices that form a triangle on a mesh
    order : integer
        order of the moments being calculated
    scale_input : bool
        translate and scale each object so it is bounded by a unit sphere?
        (this is the expected input to zernike_moments())
    decimate_fraction : float
        fraction of mesh faces to remove for decimation (0 for no decimation)
    decimate_smooth : integer
        number of smoothing steps for decimation
    verbose : bool
        print statements?

    Returns
    -------
    descriptors : list of floats
        Zernike descriptors

    Examples
    --------
    >>> # Example 1: simple cube (decimation results in a Segmentation Fault):
    >>> import numpy as np
    >>> from mindboggle.shapes.zernike.zernike import zernike_moments
    >>> points = [[0,0,0], [1,0,0], [0,0,1], [0,1,1],
    ...           [1,0,1], [0,1,0], [1,1,1], [1,1,0]]
    >>> faces = [[0,2,4], [0,1,4], [2,3,4], [3,4,5], [3,5,6], [0,1,7]]
    >>> order = 3
    >>> scale_input = True
    >>> decimate_fraction = 0
    >>> decimate_smooth = 0
    >>> verbose = False
    >>> descriptors = zernike_moments(points, faces, order, scale_input,
    ...     decimate_fraction, decimate_smooth, verbose)
    >>> [np.float("{0:.{1}f}".format(x, 5)) for x in descriptors]
    [0.09189, 0.09357, 0.04309, 0.06466, 0.0382, 0.04138]

    Example 2: Twins-2-1 left postcentral pial surface -- NO decimation:
               (zernike_moments took 142 seconds for order = 3 with no decimation)

    >>> from mindboggle.shapes.zernike.zernike import zernike_moments
    >>> from mindboggle.mio.vtks import read_vtk
    >>> from mindboggle.guts.mesh import keep_faces
    >>> from mindboggle.mio.fetch_data import prep_tests
    >>> urls, fetch_data = prep_tests()
    >>> label_file = fetch_data(urls['left_freesurfer_labels'], '', '.vtk')
    >>> points, f1,f2, faces, labels, f3,f4,f5 = read_vtk(label_file)
    >>> I22 = [i for i,x in enumerate(labels) if x==1022] # postcentral
    >>> faces = keep_faces(faces, I22)
    >>> order = 3
    >>> scale_input = True
    >>> decimate_fraction = 0
    >>> decimate_smooth = 0
    >>> verbose = False
    >>> descriptors = zernike_moments(points, faces, order, scale_input,
    ...     decimate_fraction, decimate_smooth, verbose)
    >>> [np.float("{0:.{1}f}".format(x, 5)) for x in descriptors]
    [0.00471, 0.0084, 0.00295, 0.00762, 0.0014, 0.00076]

    Example 3: left postcentral + pars triangularis pial surfaces:

    >>> from mindboggle.mio.vtks import read_vtk, write_vtk
    >>> points, f1,f2, faces, labels, f3,f4,f5 = read_vtk(label_file)
    >>> I20 = [i for i,x in enumerate(labels) if x==1020] # pars triangularis
    >>> I22 = [i for i,x in enumerate(labels) if x==1022] # postcentral
    >>> I22.extend(I20)
    >>> faces = keep_faces(faces, I22)
    >>> order = 3
    >>> scale_input = True
    >>> decimate_fraction = 0
    >>> decimate_smooth = 0
    >>> verbose = False
    >>> descriptors = zernike_moments(points, faces, order, scale_input,
    ...     decimate_fraction, decimate_smooth, verbose)
    >>> [np.float("{0:.{1}f}".format(x, 5)) for x in descriptors]
    [0.00586, 0.00973, 0.00322, 0.00818, 0.0013, 0.00131]

    View both segments (skip test):

    >>> from mindboggle.mio.plots import plot_surfaces # doctest: +SKIP
    >>> from mindboggle.mio.vtks import rewrite_scalars # doctest: +SKIP
    >>> scalars = -1 * np.ones(np.shape(labels)) # doctest: +SKIP
    >>> scalars[I22] = 1 # doctest: +SKIP
    >>> rewrite_scalars(label_file, 'test_two_labels.vtk', scalars,
    ...                 'two_labels', scalars) # doctest: +SKIP
    >>> plot_surfaces(vtk_file) # doctest: +SKIP

    """
    import numpy as np

    from mindboggle.guts.mesh import reindex_faces_0to1
    from mindboggle.guts.mesh import decimate
    from mindboggle.shapes.zernike.pipelines import DefaultPipeline as Pipeline

    # Convert 0-indices (Python) to 1-indices (Matlab) for all face indices:
    index1 = False  # already done elsewhere in the code
    if index1:
        faces = reindex_faces_0to1(faces)

    # Convert lists to numpy arrays:
    if isinstance(points, list):
        points = np.array(points)
    if isinstance(faces, list):
        faces = np.array(faces)

    # ------------------------------------------------------------------------
    # Translate all points so that they are centered at their mean,
    # and scale them so that they are bounded by a unit sphere:
    # ------------------------------------------------------------------------
    if scale_input:
        center = np.mean(points, axis=0)
        points = points - center
        maxd = np.max(np.sqrt(np.sum(points**2, axis=1)))
        points /= maxd

    # ------------------------------------------------------------------------
    # Decimate surface:
    # ------------------------------------------------------------------------
    if 0 < decimate_fraction < 1:
        points, faces, u1,u2 = decimate(points, faces,
            decimate_fraction, decimate_smooth, [], save_vtk=False)

        # Convert lists to numpy arrays:
        points = np.array(points)
        faces = np.array(faces)

    # ------------------------------------------------------------------------
    # Multiprocessor pipeline:
    # ------------------------------------------------------------------------
    pl = Pipeline()

    # ------------------------------------------------------------------------
    # Geometric moments:
    # ------------------------------------------------------------------------
    G = pl.geometric_moments_exact(points, faces, order)

    # ------------------------------------------------------------------------
    # ------------------------------------------------------------------------
    Z = pl.zernike(G, order)

    # ------------------------------------------------------------------------
    # Extract Zernike descriptors:
    # ------------------------------------------------------------------------
    descriptors = pl.feature_extraction(Z, order).tolist()

    if verbose:
        print("Zernike moments: {0}".format(descriptors))

    return descriptors


def zernike_moments_per_label(vtk_file, order=10, exclude_labels=[-1],
                              scale_input=True, decimate_fraction=0,
                              decimate_smooth=25, verbose=False):
    """
    Compute the Zernike moments per labeled region in a file.

    Optionally decimate the input mesh.

    Parameters
    ----------
    vtk_file : string
        name of VTK surface mesh file containing index scalars (labels)
    order : integer
        number of moments to compute
    exclude_labels : list of integers
        labels to be excluded
    scale_input : bool
        translate and scale each object so it is bounded by a unit sphere?
        (this is the expected input to zernike_moments())
    decimate_fraction : float
        fraction of mesh faces to remove for decimation (1 for no decimation)
    decimate_smooth : integer
        number of smoothing steps for decimation
    verbose : bool
        print statements?

    Returns
    -------
    descriptors_lists : list of lists of floats
        Zernike descriptors per label
    label_list : list of integers
        list of unique labels for which moments are computed

    Examples
    --------
    >>> # Zernike moments per label of a FreeSurfer-labeled left cortex.
    >>> # Uncomment "if label==22:" below to run example
    >>> # for left postcentral (22) pial surface:
    >>> import numpy as np
    >>> from mindboggle.shapes.zernike.zernike import zernike_moments_per_label
    >>> from mindboggle.mio.fetch_data import prep_tests
    >>> urls, fetch_data = prep_tests()
    >>> vtk_file = fetch_data(urls['left_freesurfer_labels'], '', '.vtk')
    >>> order = 3
    >>> exclude_labels = [-1]
    >>> scale_input = True
    >>> verbose = False
    >>> descriptors_lists, label_list = zernike_moments_per_label(vtk_file,
    ...     order, exclude_labels, scale_input, verbose)
    >>> label_list[0:10]
    [999, 1001, 1002, 1003, 1005, 1006, 1007, 1008, 1009, 1010]
    >>> [np.float("{0:.{1}f}".format(x, 5)) for x in descriptors_lists[0]]
    [0.00587, 0.01143, 0.0031, 0.00881, 0.00107, 0.00041]
    >>> [np.float("{0:.{1}f}".format(x, 5)) for x in descriptors_lists[1]]
    [4e-05, 9e-05, 3e-05, 9e-05, 2e-05, 1e-05]
    >>> [np.float("{0:.{1}f}".format(x, 5)) for x in descriptors_lists[2]]
    [0.00144, 0.00232, 0.00128, 0.00304, 0.00084, 0.00051]
    >>> [np.float("{0:.{1}f}".format(x, 5)) for x in descriptors_lists[3]]
    [0.00393, 0.006, 0.00371, 0.00852, 0.00251, 0.00153]
    >>> [np.float("{0:.{1}f}".format(x, 5)) for x in descriptors_lists[4]]
    [0.00043, 0.0003, 0.00095, 0.00051, 0.00115, 0.00116]

    """
    import numpy as np
    from mindboggle.mio.vtks import read_vtk
    from mindboggle.guts.mesh import keep_faces
    from mindboggle.shapes.zernike.zernike import zernike_moments

    min_points_faces = 4

    # ------------------------------------------------------------------------
    # Read VTK surface mesh file:
    # ------------------------------------------------------------------------
    points, indices, lines, faces, labels, scalar_names, npoints, \
            input_vtk = read_vtk(vtk_file)

    # ------------------------------------------------------------------------
    # Loop through labeled regions:
    # ------------------------------------------------------------------------
    ulabels = [x for x in np.unique(labels) if x not in exclude_labels]
    label_list = []
    descriptors_lists = []
    for label in ulabels:
      #if label == 1022:  # 22:
      #    print("DEBUG: COMPUTE FOR ONLY ONE LABEL")

        # --------------------------------------------------------------------
        # Determine the indices per label:
        # --------------------------------------------------------------------
        Ilabel = [i for i,x in enumerate(labels) if x == label]
        if verbose:
          print('  {0} vertices for label {1}'.format(len(Ilabel), label))

        if len(Ilabel) > min_points_faces:

            # ----------------------------------------------------------------
            # Remove background faces:
            # ----------------------------------------------------------------
            pick_faces = keep_faces(faces, Ilabel)
            if len(pick_faces) > min_points_faces:

                # ------------------------------------------------------------
                # Compute Zernike moments for the label:
                # ------------------------------------------------------------
                descriptors = zernike_moments(points, pick_faces,
                                              order, scale_input,
                                              decimate_fraction,
                                              decimate_smooth, verbose)

                # ------------------------------------------------------------
                # Append to a list of lists of spectra:
                # ------------------------------------------------------------
                descriptors_lists.append(descriptors)
                label_list.append(label)

    return descriptors_lists, label_list


# ============================================================================
# Doctests
# ============================================================================
if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)  # py.test --doctest-modules