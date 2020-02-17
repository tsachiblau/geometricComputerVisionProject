#!/usr/bin/env python
"""
Compute (fundus) likelihood values that highlight deep and highly curved
portions of a surface mesh.

Compute likelihood values for a VTK surface mesh:

compute_likelihood():
    Compute likelihood values for a given VTK surface mesh.
    This is run after training on the distributions of depth and curvature
    values across multiple VTK surface mesh files in the functions below.

Learn distributions from training data (see Examples below):

estimate_depth_curvature_distributions():
    Estimate distribution means, sigmas (standard deviations), and weights
    for VTK surface mesh depth and curvature scalars along and outside
    sulcus label borders within folds (as defined by a labeling protocol).

estimate_depth_curvature_distributions() calls the following functions:

concatenate_sulcus_scalars():
    Prepare data for estimating scalar distributions along and outside fundi.
    Extract (e.g., depth, curvature) scalar values in folds, along sulcus
    label boundaries as well as outside the sulcus label boundaries.
    Concatenate these scalar values across multiple files.

fit_normals_to_histogram():
    This Estimation-Maximization method returns estimated means, sigmas
    (standard deviations) and weights from a distribution of values.


Authors:
Yrjo Hame, 2012-2013  .  yrjo.hame@gmail.com
Arno Klein, 2012-2016  .  arno@mindboggle.info  .  www.binarybottle.com

Copyright 2016,  Mindboggle team (http://mindboggle.info), Apache v2.0 License

"""


def compute_likelihood(trained_file, depth_file, curvature_file, folds,
                       save_file=False, background_value=-1):
    """
    Compute likelihoods based on input values, folds, estimated parameters.

    Compute likelihood values for a given VTK surface mesh file, after
    training on distributions of depth and curvature values from multiple
    files.

    Parameters
    ----------
    trained_file : pickle compressed file
        depth_border, curv_border, depth_nonborder, and curv_nonborder are
        dictionaries containing lists of floats
        (estimates of depth or curvature means, sigmas, and weights
        trained on fold vertices either on or off sulcus label borders)
    depth_file : string
        VTK surface mesh file with depth values in [0,1] for all vertices
    curvature_file : string
        VTK surface mesh file with curvature values in [-1,1] for all vertices
    folds : list of integers
        fold number for all vertices (-1 for non-fold vertices)
    save_file : bool
        save output VTK file?
    background_value : integer or float
        background value

    Returns
    -------
    likelihoods : list of floats
        likelihood values for all vertices (0 for non-fold vertices)
    likelihoods_file : string (if save_file)
        name of output VTK file with likelihood scalars
        (-1 for non-fold vertices)

    Notes
    -----
    The depth_curv_border_nonborder_parameters.pkl file needs to be updated.

    Examples
    --------
    >>> from mindboggle.mio.vtks import read_scalars
    >>> from mindboggle.shapes.likelihood import compute_likelihood
    >>> from mindboggle.mio.fetch_data import prep_tests
    >>> urls, fetch_data = prep_tests()
    >>> depth_file = fetch_data(urls['left_travel_depth'], '', '.vtk')
    >>> curvature_file = fetch_data(urls['left_mean_curvature'], '', '.vtk')
    >>> folds_file = fetch_data(urls['left_folds'], '', '.vtk')
    >>> trained_file = fetch_data(urls[
    ...     'depth_curv_border_nonborder_parameters'], '', '.pkl') # doctest: +SKIP
    >>> folds, name = read_scalars(folds_file)
    >>> save_file = True
    >>> background_value = -1
    >>> likelihoods, likelihoods_file = compute_likelihood(trained_file,
    ...     depth_file, curvature_file, folds, save_file, background_value) # doctest: +SKIP

    View result (skip test):

    >>> from mindboggle.mio.plots import plot_surfaces # doctest: +SKIP
    >>> plot_surfaces('likelihoods.vtk', folds_file) # doctest: +SKIP

    """
    import os
    import numpy as np
    from math import pi
    import pickle
    from io import open

    from mindboggle.mio.vtks import read_scalars, rewrite_scalars

    # Initialize variables:
    tiny = 0.000000001
    L = np.zeros(len(folds))
    probs_border = np.zeros(len(folds))
    probs_nonborder = np.zeros(len(folds))

    # Load estimated depth and curvature distribution parameters:
    depth_border, curv_border, depth_nonborder, \
        curv_nonborder = pickle.load(open(trained_file, "rb"))

    # Load depths, curvatures:
    depths, name = read_scalars(depth_file, True, True)
    curvatures, name = read_scalars(curvature_file, True, True)

    # Prep for below:
    n = 2
    twopiexp = (2*pi)**(n/2)
    border_sigmas = depth_border['sigmas'] * curv_border['sigmas']
    nonborder_sigmas = depth_nonborder['sigmas'] * curv_nonborder['sigmas']
    norm_border = 1 / (twopiexp * border_sigmas + tiny)
    norm_nonborder = 1 / (twopiexp * nonborder_sigmas + tiny)
    I = [i for i,x in enumerate(folds) if x != background_value]

    N = depth_border['sigmas'].shape[0]
    for j in range(N):

        # Border:
        expB = depth_border['weights'][j] * \
            ((depths[I]-depth_border['means'][j])**2) / \
            depth_border['sigmas'][j]**2
        expB += curv_border['weights'][j] * \
            ((curvatures[I]-curv_border['means'][j])**2) / \
            curv_border['sigmas'][j]**2
        expB = -expB / 2
        probs_border[I] = probs_border[I] + norm_border[j] * np.exp(expB)

        # Non-border:
        expNB = depth_nonborder['weights'][j] * \
            ((depths[I]-depth_nonborder['means'][j])**2) / \
            depth_nonborder['sigmas'][j]**2
        expNB += curv_nonborder['weights'][j] * \
            ((curvatures[I]-curv_nonborder['means'][j])**2) / \
            curv_nonborder['sigmas'][j]**2
        expNB = -expNB / 2
        probs_nonborder[I] = probs_nonborder[I] + \
                             norm_nonborder[j] * np.exp(expNB)

    likelihoods = probs_border / (probs_nonborder + probs_border + tiny)
    likelihoods = likelihoods.tolist()

    # ------------------------------------------------------------------------
    # Return likelihoods and output file name
    # ------------------------------------------------------------------------
    if save_file:

        likelihoods_file = os.path.join(os.getcwd(), 'likelihoods.vtk')
        rewrite_scalars(depth_file, likelihoods_file, likelihoods,
                        'likelihoods', likelihoods, background_value)
        if not os.path.exists(likelihoods_file):
            raise IOError(likelihoods_file + " not found")

    else:
        likelihoods_file = None

    return likelihoods, likelihoods_file


def estimate_distribution(scalar_files, scalar_range, fold_files, label_files,
                          background_value=-1, verbose=False):
    """
    Estimate sulcus label border scalar distributions from VTK files.

    Learn distributions from training data (different surface meshes).
    Estimate distribution means, sigmas (standard deviations), and weights
    for VTK surface mesh scalars (e.g., depth, curvature) along and outside
    sulcus label borders within folds.

    Note : The number of classes, k, is currently hard-coded.

    Parameters
    ----------
    scalar_files : list of strings
        names of VTK files with scalar values for all surface vertices
    scalar_range : list of floats
        range of values to estimate distribution
    fold_files : list of strings
        names of VTK files with fold numbers for scalar values
    label_files : list of strings
        names of VTK files with label numbers for scalar values
    background_value : integer or float
        background value
    verbose : bool
        print statements?

    Returns
    -------
    border_parameters : dictionary containing lists of floats
        means, sigmas, weights
    nonborder_parameters : dictionary containing lists of floats
        means, sigmas, weights

    Examples
    --------
    >>> import numpy as np
    >>> import pickle
    >>> from mindboggle.shapes.likelihood import estimate_distribution
    >>> from mindboggle.mio.fetch_data import prep_tests
    >>> # Train on a single surface mesh (using FreeSurfer vs. manual labels):
    >>> urls, fetch_data = prep_tests()
    >>> depth_file = fetch_data(urls['left_travel_depth'], '', '.vtk')
    >>> curv_file = fetch_data(urls['left_mean_curvature'], '', '.vtk')
    >>> folds_file = fetch_data(urls['left_folds'], '', '.vtk')
    >>> labels_file = fetch_data(urls['left_freesurfer_labels'], '', '.vtk')
    >>> depth_files = [depth_file]
    >>> curv_files = [curv_file]
    >>> fold_files = [folds_file]
    >>> label_files = [labels_file]
    >>> #
    >>> # # Train on many Mindboggle-101 surface meshes:
    >>> # import os
    >>> # mindboggle_path = '../../Mindboggle101_mindboggle_results'
    >>> # label_path = os.environ['SUBJECTS_DIR']
    >>> # x_path = os.path.join(os.environ['MINDBOGGLE'], 'x')
    >>> # atlas_list_file = os.path.join(x_path, 'mindboggle101_atlases.txt')
    >>> # depth_files = []
    >>> # curv_files = []
    >>> # fold_files = []
    >>> # label_files = []
    >>> # for atlas in atlas_list:
    >>> #  if 'OASIS' in atlas or 'NKI' in atlas or 'MMRR-21' in atlas:
    >>> #   print(atlas)
    >>> #   for h in ['lh','rh']:
    >>> #     depth_file = os.path.join(mindboggle_path, 'shapes',
    >>> #         '_hemi_'+h+'_subject_'+atlas, h+'.pial.travel_depth.vtk')
    >>> #     curv_file = os.path.join(mindboggle_path, 'shapes',
    >>> #         '_hemi_'+h+'_subject_'+atlas, h+'.pial.mean_curvature.vtk')
    >>> #     folds_file = os.path.join(mindboggle_path, 'features',
    >>> #         '_hemi_'+h+'_subject_'+atlas, 'folds.vtk')
    >>> #     labels_file = os.path.join(label_path, atlas, 'label',
    >>> #         h+'.labels.DKT25.manual.vtk')
    >>> #     depth_files.append(depth_file)
    >>> #     curv_files.append(curv_file)
    >>> #     fold_files.append(folds_file)
    >>> #     label_files.append(labels_file)
    >>> #
    >>> scalar_files = depth_files
    >>> scalar_range = np.linspace(0, 1, 51, endpoint=True) # (0 to 1 by 0.02)
    >>> background_value = -1
    >>> verbose = False
    >>> depth_border, depth_nonborder = estimate_distribution(scalar_files,
    ...     scalar_range, fold_files, label_files, background_value, verbose)
    >>> scalar_files = curv_files
    >>> scalar_range = np.linspace(-1, 1, 101, endpoint=True) # (-1 to 1 by 0.02)
    >>> curv_border, curv_nonborder = estimate_distribution(scalar_files,
    ...     scalar_range, fold_files, label_files, verbose)
    >>> [np.float("{0:.{1}f}".format(x, 5)) for x in depth_border['means']]
    [13.0869, 0.0, 0.0]
    >>> [np.float("{0:.{1}f}".format(x, 5)) for x in depth_nonborder['means']]
    [14.59311, 6.16008, 0.0]
    >>> [np.float("{0:.{1}f}".format(x, 5)) for x in curv_border['means']]
    [3.06449, -0.76109, -3.43184]
    >>> [np.float("{0:.{1}f}".format(x, 5)) for x in curv_nonborder['means']]
    [0.62236, -1.55192, -5.19359]
    >>> pickle.dump([depth_border, curv_border, depth_nonborder, curv_nonborder],
    ...     open("depth_curv_border_nonborder_parameters.pkl", "wb"))

    """
    from mindboggle.shapes.likelihood import concatenate_sulcus_scalars, \
        fit_normals_to_histogram

    if not scalar_files or not fold_files or not label_files:
        raise IOError("Input file lists cannot be empty.")

    # Concatenate scalars across multiple training files:
    border_scalars, nonborder_scalars = concatenate_sulcus_scalars(scalar_files,
        fold_files, label_files, background_value)

    # Estimate distribution parameters:
    border_means, border_sigmas, \
        border_weights = fit_normals_to_histogram(border_scalars,
                                                  scalar_range, verbose)
    nonborder_means, nonborder_sigmas, \
        nonborder_weights = fit_normals_to_histogram(nonborder_scalars,
                                                     scalar_range, verbose)

    # Store outputs in dictionaries:
    border_parameters = {
        'means': border_means,
        'sigmas': border_sigmas,
        'weights': border_weights
    }
    nonborder_parameters = {
        'means': nonborder_means,
        'sigmas': nonborder_sigmas,
        'weights': nonborder_weights
    }

    return border_parameters, nonborder_parameters


def concatenate_sulcus_scalars(scalar_files, fold_files, label_files,
                               background_value=-1):
    """
    Prepare data for estimating scalar distributions along and outside fundi.

    Extract (e.g., depth, curvature) scalar values in folds, along sulcus
    label boundaries as well as outside the sulcus label boundaries.
    Concatenate these scalar values across multiple files.

    Parameters
    ----------
    scalar_files : list of strings
        names of surface mesh VTK files with scalar values to concatenate
    fold_files : list of strings (corr. to each list in scalar_files)
        VTK files with fold numbers as scalars (-1 for non-fold vertices)
    label_files : list of strings (corr. to fold_files)
        VTK files with label numbers (-1 for unlabeled vertices)
    background_value : integer or float
        background value

    Returns
    -------
    border_scalars : list of floats
        concatenated scalar values within folds along sulcus label boundaries
    nonborder_scalars : list of floats
        concatenated scalar values within folds outside sulcus label boundaries

    Examples
    --------
    >>> # Concatenate (duplicate) depth scalars:
    >>> import numpy as np
    >>> from mindboggle.shapes.likelihood import concatenate_sulcus_scalars
    >>> from mindboggle.mio.fetch_data import prep_tests
    >>> urls, fetch_data = prep_tests()
    >>> depth_file = fetch_data(urls['left_travel_depth'], '', '.vtk')
    >>> labels_file = fetch_data(urls['left_freesurfer_labels'], '', '.vtk')
    >>> folds_file = fetch_data(urls['left_folds'], '', '.vtk')
    >>> scalar_files = [depth_file, depth_file]
    >>> fold_files = [folds_file, folds_file]
    >>> label_files = [labels_file, labels_file]
    >>> background_value = -1
    >>> border, nonborder = concatenate_sulcus_scalars(scalar_files,
    ...     fold_files, label_files, background_value)
    >>> [np.float("{0:.{1}f}".format(x, 5)) for x in border[0:5]]
    [3.48284, 2.57157, 4.27596, 4.56549, 3.84881]
    >>> [np.float("{0:.{1}f}".format(x, 5)) for x in nonborder[0:5]]
    [2.87204, 2.89388, 3.55364, 2.81681, 3.70736]

    """
    import numpy as np

    from mindboggle.mio.vtks import read_scalars
    from mindboggle.guts.mesh import find_neighbors_from_file
    from mindboggle.guts.segment import extract_borders
    from mindboggle.mio.labels import DKTprotocol

    dkt = DKTprotocol()

    # Prepare (non-unique) list of sulcus label pairs:
    protocol_label_pairs = [x for lst in dkt.sulcus_label_pair_lists
                            for x in lst]

    border_scalars = []
    nonborder_scalars = []

    # Loop through files with the scalar values:
    for ifile, scalar_file in enumerate(scalar_files):
        #print(scalar_file)

        # Load scalars, folds, and labels:
        folds_file = fold_files[ifile]
        labels_file = label_files[ifile]
        scalars, name = read_scalars(scalar_file, True, True)
        if scalars.shape:
            folds, name = read_scalars(folds_file)
            labels, name = read_scalars(labels_file)
            indices_folds = [i for i,x in enumerate(folds)
                             if x != background_value]
            neighbor_lists = find_neighbors_from_file(labels_file)

            # Find all label border pairs within the folds:
            indices_label_pairs, label_pairs, unique_pairs = extract_borders(
                indices_folds, labels, neighbor_lists, ignore_values=[-1],
                return_label_pairs=True)
            indices_label_pairs = np.array(indices_label_pairs)

            # Find vertices with label pairs in the sulcus labeling protocol:
            Ipairs_in_protocol = [i for i,x in enumerate(label_pairs)
                                  if x in protocol_label_pairs]
            indices_label_pairs = indices_label_pairs[Ipairs_in_protocol]
            indices_outside_pairs = list(frozenset(indices_folds).difference(
                indices_label_pairs))

            # Store scalar values in folds along label border pairs:
            border_scalars.extend(scalars[indices_label_pairs].tolist())

            # Store scalar values in folds outside label border pairs:
            nonborder_scalars.extend(scalars[indices_outside_pairs].tolist())

    return border_scalars, nonborder_scalars


def fit_normals_to_histogram(data, x, verbose=False):
    """
    This Estimation-Maximization method returns estimated means, sigmas
    (standard deviations) and weights, each of length k (number of classes).

    Parameters
    ----------
    data : list of floats
        data to estimate distribution means, sigmas, and weights
    x : list of floats
        range of values used to initialize distribution means and sigmas

    Returns
    -------
    means : list of floats
        estimated mean for each class
    sigmas : list of floats
        estimated standard deviation for each class
    weights : list of floats
        weight for each class
    verbose : bool
        print statements?

    Examples
    --------
    >>> import numpy as np
    >>> from mindboggle.shapes.likelihood import fit_normals_to_histogram
    >>> from mindboggle.mio.vtks import read_scalars
    >>> from mindboggle.mio.fetch_data import prep_tests
    >>> urls, fetch_data = prep_tests()
    >>> depth_file = fetch_data(urls['left_travel_depth'], '', '.vtk')
    >>> scalars, name = read_scalars(depth_file)
    >>> x = np.linspace(0, 1, 51, endpoint=True)
    >>> verbose = False
    >>> means, sigmas, weights = fit_normals_to_histogram(scalars, x, verbose)
    >>> [np.float("{0:.{1}f}".format(x, 5)) for x in means]
    [13.38742, 3.90712, 0.10946]
    >>> [np.float("{0:.{1}f}".format(x, 5)) for x in sigmas]
    [5.80721, 2.58297, 0.10209]
    >>> [np.float("{0:.{1}f}".format(x, 5)) for x in weights]
    [0.43959, 0.39286, 0.16755]

    """
    import numpy as np
    from math import pi

    # Initialize variables:
    k = 3
    tiny = 0.000000001
    probs = np.zeros((len(data), k))
    W = np.zeros((len(data), k))
    means = np.zeros(k)
    sigmas = np.zeros(k)
    weights = np.zeros(k)

    # Initialize distribution means and sigmas:
    rangex = max(x) - min(x)
    for i in range(1, k + 1):
        means[i-1] = max(x) - rangex/2 - 0.2 * rangex * (i - k/2)
        sigmas[i-1] = 0.2

    if verbose:
        print('Fitting normals to histograms...')

    # Iteratively compute probabilities, weights, means and sigmas:
    iter = 0
    while iter < 25:
        iter += 1

        for i in range(k):
            m1 = 1 / (sigmas[i] * np.sqrt(2*pi) + tiny)
            m2 = -((data-means[i])**2) / (2 *(sigmas[i]**2) + tiny)
            probs[:,i] = m1 * np.exp(m2)

        for i in range(k):
            W[:,i] = probs[:,i] / (np.sum(probs, axis=1) + tiny)

        for i in range(k):
            n1 = sum(W[:,i] * (data - means[i])**2)
            d1 = sum(W[:,i]) + tiny
            sigmas[i] =  np.sqrt(n1 / d1)
            means[i] = sum(W[:,i] * data) / d1

        if verbose:
            print('    means: {0}; sigmas: {1}'.format(means, sigmas))

    for i in range(k):
        weights[i] = sum(W[:,i]) / (np.sum(W) + tiny)

    if verbose:
        print('    weights: {0}'.format(weights))

    return means, sigmas, weights


# ============================================================================
# Doctests
# ============================================================================
if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)  # py.test --doctest-modules