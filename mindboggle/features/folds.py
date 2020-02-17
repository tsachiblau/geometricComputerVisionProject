#!/usr/bin/env python
"""
Functions to extract surface folds.

Authors:
    - Arno Klein, 2012-2016  (arno@mindboggle.info)  http://binarybottle.com

Copyright 2016,  Mindboggle team (http://mindboggle.info), Apache v2.0 License

"""


def find_depth_threshold(depth_file, min_vertices=10000, verbose=False):
    """
    Find depth threshold to extract folds from a triangular surface mesh.

    Steps ::
        1. Compute histogram of depth measures.
        2. Define a depth threshold and find the deepest vertices.
           To extract an initial set of deep vertices from the surface mesh,
           we anticipate that there will be a rapidly decreasing distribution
           of low depth values (on the outer surface) with a long tail
           of higher depth values (in the folds), so we smooth the histogram's
           bin values, convolve to compute slopes, and find the depth value
           for the first bin with slope = 0. This is our threshold.

    Parameters
    ----------
    depth_file : string
        surface mesh file in VTK format with faces and depth scalar values
    min_vertices : integer
        minimum number of vertices
    verbose : bool
        print statements?

    Returns
    -------
    depth_threshold :  float
        threshold defining the minimum depth for vertices to be in a fold
    bins :  list of integers
        histogram bins: each is the number of vertices within a range of depth values
    bin_edges :  list of floats
        histogram bin edge values defining the bin ranges of depth values

    Examples
    --------
    >>> import numpy as np
    >>> from mindboggle.features.folds import find_depth_threshold
    >>> from mindboggle.mio.fetch_data import prep_tests
    >>> urls, fetch_data = prep_tests()
    >>> depth_file = fetch_data(urls['left_travel_depth'], '', '.vtk')
    >>> min_vertices = 10000
    >>> verbose = False
    >>> depth_threshold, bins, bin_edges = find_depth_threshold(depth_file,
    ...     min_vertices, verbose)
    >>> np.float("{0:.{1}f}".format(depth_threshold, 5))
    2.36089

    View threshold histogram plots (skip test):

    >>> def vis():
    ...     import numpy as np
    ...     import pylab
    ...     from scipy.ndimage.filters import gaussian_filter1d
    ...     from mindboggle.mio.vtks import read_scalars
    ...     # Plot histogram and depth threshold:
    ...     depths, name = read_scalars(depth_file)
    ...     nbins = np.round(len(depths) / 100.0)
    ...     a,b,c = pylab.hist(depths, bins=nbins)
    ...     pylab.plot(depth_threshold * np.ones((100,1)),
    ...                np.linspace(0, max(bins), 100), 'r.')
    ...     pylab.title('Histogram of depth values with threshold')
    ...     pylab.xlabel('Depth')
    ...     pylab.ylabel('Number of vertices')
    ...     pylab.show()
    ...     # Plot smoothed histogram:
    ...     bins_smooth = gaussian_filter1d(bins.tolist(), 5)
    ...     pylab.plot(list(range(len(bins))), bins, '.',
    ...                list(range(len(bins))), bins_smooth,'-')
    ...     pylab.title('Smoothed histogram of depth values')
    ...     pylab.show()
    >>> vis() # doctest: +SKIP

    """
    import numpy as np
    from scipy.ndimage.filters import gaussian_filter1d

    from mindboggle.mio.vtks import read_vtk

    # ------------------------------------------------------------------------
    # Load depth values for all vertices:
    # ------------------------------------------------------------------------
    points, indices, lines, faces, depths, scalar_names, npoints, \
        input_vtk = read_vtk(depth_file, return_first=True, return_array=True)

    # ------------------------------------------------------------------------
    # Compute histogram of depth measures:
    # ------------------------------------------------------------------------
    if npoints > min_vertices:
        nbins = np.int(np.round(npoints / 100.0))
    else:
        raise IOError("  Expecting at least {0} vertices to create "
                      "depth histogram".format(min_vertices))
    bins, bin_edges = np.histogram(depths, bins=nbins)

    # ------------------------------------------------------------------------
    # Anticipating that there will be a rapidly decreasing distribution
    # of low depth values (on the outer surface) with a long tail of higher
    # depth values (in the folds), smooth the bin values (Gaussian), convolve
    # to compute slopes, and find the depth for the first bin with slope = 0.
    # ------------------------------------------------------------------------
    bins_smooth = gaussian_filter1d(bins.tolist(), 5)
    window = [-1, 0, 1]
    bin_slopes = np.convolve(bins_smooth, window, mode='same') / \
                 (len(window) - 1)
    ibins0 = np.where(bin_slopes == 0)[0]
    if ibins0.shape:
        depth_threshold = bin_edges[ibins0[0]]
    else:
        depth_threshold = np.median(depths)

    # Print statement:
    if verbose:
        print('  Depth threshold: {0}'.format(depth_threshold))

    return depth_threshold, bins, bin_edges


def extract_folds(depth_file, depth_threshold=2, min_fold_size=50,
                  save_file=False, output_file='', background_value=-1,
                  verbose=False):
    """
    Use depth threshold to extract folds from a triangular surface mesh.

    A fold is a group of connected, deep vertices. To extract folds,
    a depth threshold is used to segment deep vertices of the surface mesh.
    We have observed in the histograms of travel depth measures of cortical
    surfaces that there is a rapidly decreasing distribution of low depth
    values (corresponding to the outer surface, or gyral crowns) with a
    long tail of higher depth values (corresponding to the folds).

    The find_depth_threshold function therefore computes a histogram of
    travel depth measures, smooths the histogram's bin values, convolves
    to compute slopes, and finds the depth value for the first bin with
    zero slope. The extract_folds function uses this depth value, segments
    deep vertices, and removes extremely small folds (empirically set at 50
    vertices or fewer out of a total mesh size of over 100,000 vertices).

    Steps ::
        1. Segment deep vertices as an initial set of folds.
        2. Remove small folds.
        3. Renumber folds.

    Note ::
        Removed option: Find and fill holes in the folds:
        Folds could have holes in areas shallower than the depth threshold.
        Calling fill_holes() could accidentally include very shallow areas
        (in an annulus-shaped fold, for example).
        However, we could include the argument exclude_range to check for
        any values from zero to min_hole_depth; holes would not be filled
        if they were to contain values within this range.

    Parameters
    ----------
    depth_file : string
        surface mesh file in VTK format with faces and depth scalar values
    depth_threshold :  float
        threshold defining the minimum depth for vertices to be in a fold
    min_fold_size : integer
        minimum fold size (number of vertices)
    save_file : bool
        save output VTK file?
    output_file : string
        name of output file in VTK format
    background_value : integer or float
        background value
    verbose : bool
        print statements?

    Returns
    -------
    folds : list of integers
        fold numbers for all vertices (-1 for non-fold vertices)
    n_folds :  int
        number of folds
    folds_file : string (if save_file)
        name of output VTK file with fold IDs (-1 for non-fold vertices)

    Examples
    --------
    >>> from mindboggle.features.folds import extract_folds
    >>> from mindboggle.mio.fetch_data import prep_tests
    >>> urls, fetch_data = prep_tests()
    >>> depth_file = fetch_data(urls['left_travel_depth'], '', '.vtk')
    >>> depth_threshold = 2.36089
    >>> min_fold_size = 50
    >>> save_file = True
    >>> output_file = 'extract_folds.vtk'
    >>> background_value = -1
    >>> verbose = False
    >>> folds, n_folds, folds_file = extract_folds(depth_file,
    ...     depth_threshold, min_fold_size, save_file, output_file,
    ...     background_value, verbose)
    >>> n_folds
    33
    >>> lens = [len([x for x in folds if x == y]) for y in range(n_folds)]
    >>> lens[0:10]
    [726, 67241, 2750, 5799, 1151, 6360, 1001, 505, 228, 198]

    View folds (skip test):

    >>> from mindboggle.mio.plots import plot_surfaces # doctest: +SKIP
    >>> plot_surfaces('extract_folds.vtk') # doctest: +SKIP

    View folds without background (skip test):

    >>> from mindboggle.mio.plots import plot_surfaces # doctest: +SKIP
    >>> from mindboggle.mio.vtks import rewrite_scalars # doctest: +SKIP
    >>> rewrite_scalars(depth_file, 'extract_folds_no_background.vtk', folds,
    ...     'just_folds', folds, -1) # doctest: +SKIP
    >>> plot_surfaces('extract_folds_no_background.vtk') # doctest: +SKIP

    """
    import os
    import numpy as np
    from time import time

    from mindboggle.mio.vtks import rewrite_scalars, read_vtk
    from mindboggle.guts.mesh import find_neighbors
    from mindboggle.guts.segment import segment_regions

    if verbose:
        print("Extract folds in surface mesh")
        t0 = time()

    # ------------------------------------------------------------------------
    # Load depth values for all vertices
    # ------------------------------------------------------------------------
    points, indices, lines, faces, depths, scalar_names, npoints, \
        input_vtk = read_vtk(depth_file, return_first=True, return_array=True)

    # ------------------------------------------------------------------------
    # Find the deepest vertices
    # ------------------------------------------------------------------------
    indices_deep = [i for i,x in enumerate(depths) if x >= depth_threshold]
    if indices_deep:

        # --------------------------------------------------------------------
        # Find neighbors for each vertex
        # --------------------------------------------------------------------
        neighbor_lists = find_neighbors(faces, npoints)

        # --------------------------------------------------------------------
        # Segment deep vertices as an initial set of folds
        # --------------------------------------------------------------------
        if verbose:
            print("  Segment vertices deeper than {0:.2f} as folds".format(depth_threshold))
            t1 = time()
        folds = segment_regions(indices_deep, neighbor_lists, 1, [], False,
                                False, [], [], [], '', background_value, False)
        if verbose:
            print('  ...Segmented folds ({0:.2f} seconds)'.format(time() - t1))

        # --------------------------------------------------------------------
        # Remove small folds
        # --------------------------------------------------------------------
        if min_fold_size > 1:
            if verbose:
                print('  Remove folds smaller than {0}'.format(min_fold_size))
            unique_folds = [x for x in np.unique(folds)
                            if x != background_value]
            for nfold in unique_folds:
                indices_fold = [i for i,x in enumerate(folds) if x == nfold]
                if len(indices_fold) < min_fold_size:
                    folds[indices_fold] = background_value

        # --------------------------------------------------------------------
        # Find and fill holes in the folds
        # Note: Surfaces surrounded by folds can be mistaken for holes,
        #       so exclude_range includes outer surface values close to zero.
        # --------------------------------------------------------------------
        # folds = fill_holes(folds, neighbor_lists, values=depths,
        #                    exclude_range=[0, min_hole_depth])

        # --------------------------------------------------------------------
        # Renumber folds so they are sequential.
        # NOTE: All vertices are included (-1 for non-fold vertices).
        # --------------------------------------------------------------------
        renumber_folds = background_value * np.ones(npoints)
        fold_numbers = [x for x in np.unique(folds) if x != background_value]
        for i_fold, n_fold in enumerate(fold_numbers):
            fold_indices = [i for i,x in enumerate(folds) if x == n_fold]
            renumber_folds[fold_indices] = i_fold
        folds = renumber_folds
        folds = [int(x) for x in folds]
        n_folds = i_fold + 1

        # Print statement
        if verbose:
            print('  ...Extracted {0} folds ({1:.2f} seconds)'.
                  format(n_folds, time() - t0))
    else:
        if verbose:
            print('  No deep vertices')

    # ------------------------------------------------------------------------
    # Return folds, number of folds, file name
    # ------------------------------------------------------------------------
    if save_file:

        if output_file:
            folds_file = output_file
        else:
            folds_file = os.path.join(os.getcwd(), 'folds.vtk')
        rewrite_scalars(depth_file, folds_file, folds, 'folds', [],
                        background_value)

        if not os.path.exists(folds_file):
            raise IOError(folds_file + " not found")

    else:
        folds_file = None

    return folds, n_folds, folds_file


# def extract_subfolds(depth_file, folds, min_size=10, depth_factor=0.25,
#                      depth_ratio=0.1, tolerance=0.01, save_file=False,
#                      background_value=-1, verbose=False):
#     """
#     Use depth to segment folds into subfolds in a triangular surface mesh.
#
#     Note ::
#
#         The function extract_sulci() performs about the same whether folds
#         or subfolds are used as input.  The latter leads to some loss of
#         small subfolds and possibly holes for small subfolds in the middle
#         of other subfolds.
#
#     Note about the watershed() function:
#     The watershed() function performs individual seed growing from deep seeds,
#     repeats segmentation from the resulting seeds until each seed's segment
#     touches a boundary. The function segment() fills in the rest. Finally
#     segments are joined if their seeds are too close to each other.
#     Despite these precautions, the order of seed selection in segment() could
#     possibly influence the resulting borders between adjoining segments.
#     [The propagate() function is slower and insensitive to depth,
#      but is not biased by seed order.]
#
#     Parameters
#     ----------
#     depth_file : string
#         surface mesh file in VTK format with faces and depth scalar values
#     folds : list of integers
#         fold numbers for all vertices (-1 for non-fold vertices)
#     min_size : integer
#         minimum number of vertices for a subfold
#     depth_factor : float
#         watershed() depth_factor:
#         factor to determine whether to merge two neighboring watershed
#         catchment basins -- they are merged if the Euclidean distance between
#         their basin seeds is less than this fraction of the maximum Euclidean
#         distance between points having minimum and maximum depths
#     depth_ratio : float
#         watershed() depth_ratio:
#         the minimum fraction of depth for a neighboring shallower
#         watershed catchment basin (otherwise merged with the deeper basin)
#     tolerance : float
#         watershed() tolerance:
#         tolerance for detecting differences in depth between vertices
#     save_file : bool
#         save output VTK file?
#     background_value : integer or float
#         background value
#     verbose : bool
#         verbose output?
#
#     Returns
#     -------
#     subfolds : list of integers
#         fold numbers for all vertices (-1 for non-fold vertices)
#     n_subfolds :  int
#         number of subfolds
#     subfolds_file : string (if save_file)
#         name of output VTK file with fold IDs (-1 for non-fold vertices)
#
#     Examples
#     --------
#     >>> import os
#     >>> from mindboggle.mio.vtks import read_scalars, rewrite_scalars
#     >>> from mindboggle.guts.mesh import find_neighbors_from_file
#     >>> from mindboggle.features.folds import extract_subfolds
#     >>> from mindboggle.mio.plots import plot_surfaces
#     >>> path = os.environ['MINDBOGGLE_DATA']
#     >>> depth_file = os.path.join(path, 'shapes', 'left_cortical_surface',
#     ...     'travel_depth.vtk')
#     >>> folds_file = os.path.join(path, 'features', 'left_cortical_surface',
#     ...     'folds.vtk')
#     >>> folds, name = read_scalars(folds_file)
#     >>> min_size = 10
#     >>> depth_factor = 0.5
#     >>> depth_ratio = 0.1
#     >>> tolerance = 0.01
#     >>> save_file = False
#     >>> background_value = -1
#     >>> verbose = False
#     >>> subfolds, n_subfolds, subfolds_file = extract_subfolds(depth_file,
#     ...     folds, min_size, depth_factor, depth_ratio, tolerance, save_file,
#     ...     background_value, verbose)
#     >>> n_subfolds
#     288
#     >>> [len([x for x in subfolds if x == y]) for y in range(n_subfolds)]  # doctest: +ELLIPSIS
#     [3406, 31, 678, 1208, 1241, 30,, ...,  93, 107, 68, 90, 131, 71]
#     >>>
#     >>> # View:
#     >>> def vis():
#     ...     rewrite_scalars(depth_file, 'subfolds.vtk', subfolds, 'subfolds',
#     ...                     subfolds)
#     ...     plot_surfaces('subfolds.vtk')
#     >>> vis() # doctest: +SKIP
#
#     """
#     import os
#     import numpy as np
#     from time import time
#     from mindboggle.mio.vtks import rewrite_scalars, read_vtk
#     from mindboggle.guts.mesh import find_neighbors
#     from mindboggle.guts.segment import watershed
#
#     if verbose:
#         print("Segment folds into subfolds")
#         t0 = time()
#
#     # ------------------------------------------------------------------------
#     # Load depth values for all vertices
#     # ------------------------------------------------------------------------
#     points, indices, lines, faces, depths, scalar_names, npoints, \
#         input_vtk = read_vtk(depth_file, return_first=True, return_array=True)
#
#     # ------------------------------------------------------------------------
#     # Find neighbors for each vertex
#     # ------------------------------------------------------------------------
#     neighbor_lists = find_neighbors(faces, npoints)
#
#     # ------------------------------------------------------------------------
#     # Segment folds into "watershed basins"
#     # ------------------------------------------------------------------------
#     indices_folds = [i for i,x in enumerate(folds) if x != -1]
#     subfolds, seed_indices = watershed(depths, points, indices_folds,
#                                        neighbor_lists, min_size,
#                                        depth_factor=0.25, depth_ratio=0.1,
#                                        tolerance=0.01, regrow=True,
#                                        background_value=background_value,
#                                        verbose=False)
#
#     # Print statement
#     n_subfolds = len([x for x in np.unique(subfolds) if x != -1])
#     if verbose:
#         print('  Extracted {0} subfolds ({1:.2f} seconds)'.
#               format(n_subfolds, time() - t0))
#
#     # ------------------------------------------------------------------------
#     # Return subfolds, number of subfolds, file name
#     # ------------------------------------------------------------------------
#     if save_file:
#         subfolds_file = os.path.join(os.getcwd(), 'subfolds.vtk')
#         rewrite_scalars(depth_file, subfolds_file,
#                         subfolds, 'subfolds', subfolds)
#
#         if not os.path.exists(subfolds_file):
#             raise IOError(subfolds_file + " not found")
#
#     else:
#         subfolds_file = None
#
#     return subfolds, n_subfolds, subfolds_file


# ============================================================================
# Doctests
# ============================================================================
if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)  # py.test --doctest-modules