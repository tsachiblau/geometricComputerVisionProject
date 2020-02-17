#!/usr/bin/env python
"""
Functions related to reading and writing VTK format files.

Authors:
    - Forrest Sheng Bao, 2012-2013  (forrest.bao@gmail.com)  http://fsbao.net
    - Arno Klein, 2012-2016  (arno@mindboggle.info)  http://binarybottle.com
    - Oliver Hinds, 2013 (ohinds@gmail.com)
    - Daniel Haehn, 2013 (daniel.haehn@childrens.harvard.edu)

Copyright 2016,  Mindboggle team (http://mindboggle.info), Apache v2.0 License

"""


def read_vertices(filename):
    """
    Load VERTICES segment from a VTK file (actually indices to vertices).

    Parameters
    ----------
    filename : string
        The path/filename of a VTK format file.

    Returns
    -------
    indices : a list of integers
        Each element is an integer defined in the VTK file's VERTICES segment.
        The integer is an index referring to a point defined in the
        POINTS segment of the VTK file.

    Notes ::

        -- Not currently in use by Mindboggle.

        We assume that the VERTICES segment is organized as one line,
        the first column of which is the number of vertices.
        Vertices here are as vertices in VTK terminology.
        It may not be the vertices in your 3-D surface.

    Examples
    --------
    >>> from mindboggle.mio.vtks import read_vertices
    >>> from mindboggle.mio.fetch_data import prep_tests
    >>> urls, fetch_data = prep_tests()
    >>> depth_file = fetch_data(urls['left_travel_depth'], '', '.vtk')
    >>> indices = read_vertices(depth_file) # doctest: +SKIP

    """
    import vtk

    Reader = vtk.vtkDataSetReader()
    Reader.SetFileName(filename)
    Reader.Update()

    Data = Reader.GetOutput()

    Vrts = Data.GetVerts()
    indices = [Vrts.GetData().GetValue(i) for i in range(1, Vrts.GetSize())]

    return indices


def read_lines(filename):
    """
    Load LINES from a VTK file, along with the scalar values.

    The line that extracts vertices from a VTK
    iterates from 1 to Vrts.GetSize(), rather than from 0.

    Not currently in use by Mindboggle.
    This was intended for use with the fundus line extraction algorithm.

    Parameters
    ----------
    filename : string
        the path/filename of a VTK format file

    Returns
    -------
    lines : list of 2-tuple of integers
        each element is a 2-tuple of IDs (i.e., indices) of two points
        defined in the POINTS section of the VTK file
    scalars : list of floats
        each element is a scalar value corresponding to a vertex

    Examples
    --------
    >>> from mindboggle.mio.vtks import read_lines
    >>> from mindboggle.mio.fetch_data import prep_tests
    >>> urls, fetch_data = prep_tests()
    >>> fundus_file = fetch_data(urls['left_fundus_per_fold'], '', '.vtk')
    >>> lines, scalars  = read_lines(fundus_file) # doctest: +SKIP

    """
    import vtk

    Reader = vtk.vtkDataSetReader()
    Reader.SetFileName(filename)
    Reader.Update()

    Data = Reader.GetOutput()
    Lns = Data.GetLines()

    lines  = [[Lns.GetData().GetValue(j) for j in range(i*3+1, i*3+3) ]
              for i in range(Data.GetNumberOfLines())]

    PointData = Data.GetPointData()
    print("There are {0} scalars in file {1}".format(
        Reader.GetNumberOfscalarsInFile(), filename))
    print("Loading the scalar {0}".format(Reader.GetScalarsNameInFile(0)))
    ScalarsArray = PointData.GetArray(Reader.GetScalarsNameInFile(0))
    scalars = [ScalarsArray.GetValue(i)
               for i in range(0, ScalarsArray.GetDataSize())]

    return lines, scalars


def read_points(filename):
    """
    Load points of a VTK surface file.

    Not currently in use by Mindboggle.

    Parameters
    ----------
    filename : string
        path/filename of a VTK format file

    Returns
    -------
    points : list of lists of floats
        each element is a list of 3-D coordinates of a surface mesh vertex

    Examples
    --------
    >>> import numpy as np
    >>> from mindboggle.mio.vtks import read_points
    >>> from mindboggle.mio.fetch_data import prep_tests
    >>> urls, fetch_data = prep_tests()
    >>> depth_file = fetch_data(urls['left_travel_depth'], '', '.vtk')
    >>> points  = read_points(depth_file)
    >>> print(np.array_str(np.array(points[0:5]),
    ...       precision=5, suppress_small=True))
    [[-13.7924  -76.0973   -2.57594]
     [-14.2225  -76.2362   -2.73425]
     [-14.9617  -76.2497   -2.62924]
     [-12.4807  -76.1401   -3.98634]
     [-13.3426  -76.1914   -3.3657 ]]

    """
    import vtk

    Reader = vtk.vtkDataSetReader()
    Reader.SetFileName(filename)
    Reader.ReadAllScalarsOn()  # Activate the reading of all scalars
    Reader.Update()

    Data = Reader.GetOutput()
    points = [list(Data.GetPoint(point_id))
              for point_id in range(Data.GetNumberOfPoints())]

    return points


def read_faces_points(filename):
    """
    Load points and faces of a VTK surface file.

    Parameters
    ----------
    filename : string
        path/filename of a VTK format file

    Returns
    -------
    faces : list of lists of integers
        each element is list of 3 indices of vertices that form a face
        on a surface mesh
    points : list of lists of floats
        each element is a list of 3-D coordinates of a surface mesh vertex
    npoints : integer
        number of points

    Examples
    --------
    >>> import numpy as np
    >>> from mindboggle.mio.vtks import read_faces_points
    >>> from mindboggle.mio.fetch_data import prep_tests
    >>> urls, fetch_data = prep_tests()
    >>> depth_file = fetch_data(urls['left_travel_depth'], '', '.vtk')
    >>> faces, points, npoints  = read_faces_points(depth_file)
    >>> npoints
    145069
    >>> faces[0:5]
    [[0, 1, 4], [5, 4, 1], [0, 48, 49], [0, 49, 1], [0, 4, 48]]
    >>> print(np.array_str(np.array(points[0:5]),
    ...       precision=5, suppress_small=True))
    [[-13.7924  -76.0973   -2.57594]
     [-14.2225  -76.2362   -2.73425]
     [-14.9617  -76.2497   -2.62924]
     [-12.4807  -76.1401   -3.98634]
     [-13.3426  -76.1914   -3.3657 ]]

    """
    import vtk

    Reader = vtk.vtkDataSetReader()
    Reader.SetFileName(filename)
    Reader.ReadAllScalarsOn()  # Activate the reading of all scalars
    Reader.Update()

    Data = Reader.GetOutput()
    points = [list(Data.GetPoint(point_id))
              for point_id in range(Data.GetNumberOfPoints())]
    npoints = len(points)

    if Data.GetNumberOfPolys() > 0:
        faces = [[int(Data.GetPolys().GetData().GetValue(j))
                  for j in range(i*4 + 1, i*4 + 4)]
                  for i in range(Data.GetPolys().GetNumberOfCells())]
    else:
        faces = []

    return faces, points, npoints


def read_scalars(filename, return_first=True, return_array=False):
    """
    Load all scalar lookup tables from a VTK file.

    Parameters
    ----------
    filename : string
        The path/filename of a VTK format file.
    return_first : bool
        Return only the first list of scalar values?
    return_array : bool (only if return_first)
        Return first list of scalars as a numpy array?

    Returns
    -------
    scalars : list of lists of integers or floats
        each element is a list of scalar values for the vertices of a mesh
    scalar_name(s) : list of strings
        each element is the name of a lookup table

    Examples
    --------
    >>> import numpy as np
    >>> from mindboggle.mio.vtks import read_scalars
    >>> from mindboggle.mio.fetch_data import prep_tests
    >>> urls, fetch_data = prep_tests()
    >>> depth_file = fetch_data(urls['left_travel_depth'], '', '.vtk')
    >>> depths, name = read_scalars(depth_file)
    >>> name
    'scalars'
    >>> [np.float("{0:.{1}f}".format(x, 5)) for x in depths[0:5]]
    [0.02026, 0.06009, 0.12859, 0.04564, 0.00774]

    """
    #import os
    import vtk
    if return_first and return_array:
        import numpy as np

    Reader = vtk.vtkDataSetReader()
    Reader.SetFileName(filename)
    Reader.ReadAllScalarsOn()  # Activate the reading of all scalars
    Reader.Update()
    Data = Reader.GetOutput()
    PointData = Data.GetPointData()

    scalars = []
    scalar_names = []
    if Reader.GetNumberOfScalarsInFile() > 0:
        for scalar_index in range(Reader.GetNumberOfScalarsInFile()):
            scalar_name = Reader.GetScalarsNameInFile(scalar_index)

            #n_scalars = scalar_index + 1
            #if n_scalars == 1:
            #    print("Load \"{0}\" scalars from {1}".
            #          format(scalar_name, os.path.basename(filename)))
            #else:
            #    print("Load \"{0}\" (of {1} scalars) from {2}".
            #          format(scalar_name, n_scalars,
            #                 os.path.basename(filename)))

            scalar_array = PointData.GetArray(scalar_name)
            scalar = [scalar_array.GetValue(i)
                      for i in range(scalar_array.GetDataSize())]
            scalars.append(scalar)
            scalar_names.append(scalar_name)

    if return_first:
        if scalars:
            scalars = scalars[0]
        if return_array:
            scalars = np.array(scalars)
        if scalar_names:
            scalar_names = scalar_names[0]
        else:
            scalar_names = ''

    return scalars, scalar_names


def read_vtk(input_vtk, return_first=True, return_array=False):
    """
    Load faces, lines, indices, points, #points,
    and all scalar lookup tables from a VTK file.

    Note ::

        1. This supports copying lines, vertices (indices of points),
           and triangular faces from one surface to another.
        2. We assume that all vertices are written in one line
           in the VERTICES segment.

    Parameters
    ----------
    input_vtk : string
        path/filename of a VTK format file
    return_first : bool
        Return only the first list of scalar values?
    return_array : bool (only if return_first)
        Return first list of scalars as a numpy array?

    Returns
    -------
    points :  list of 3-tuples of floats
        each element has 3 numbers representing the coordinates of the points
    indices : list of integers
        indices of vertices
    lines : list of 2-tuples of integers
        each element is an edge on the mesh, consisting of 2 integers
        representing the 2 vertices of the edge
    faces : list of lists of integers
        each element is list of 3 indices of vertices that form a face
        on a surface mesh
    scalars : list or list of lists of floats or integers
        scalar values for the vertices of a mesh
    scalar_names : string or list of strings
        name(s) of lookup table(s)
    npoints : int
        number of vertices in the mesh
    input_vtk : string
        path/filename of the input VTK format file

    Examples
    --------
    >>> import numpy as np
    >>> from mindboggle.mio.vtks import read_vtk
    >>> from mindboggle.mio.fetch_data import prep_tests
    >>> urls, fetch_data = prep_tests()
    >>> depth_file = fetch_data(urls['left_travel_depth'], '', '.vtk')
    >>> points, indices, lines, faces, scalars, scalar_names, npoints, input_vtk = read_vtk(depth_file)
    >>> npoints
    145069
    >>> print(np.array_str(np.array(points[0:5]),
    ...       precision=5, suppress_small=True))
    [[-13.7924  -76.0973   -2.57594]
     [-14.2225  -76.2362   -2.73425]
     [-14.9617  -76.2497   -2.62924]
     [-12.4807  -76.1401   -3.98634]
     [-13.3426  -76.1914   -3.3657 ]]
    >>> [np.float("{0:.{1}f}".format(x, 5)) for x in scalars[0:5]]
    [0.02026, 0.06009, 0.12859, 0.04564, 0.00774]
    >>> faces[0:5]
    [[0, 1, 4], [5, 4, 1], [0, 48, 49], [0, 49, 1], [0, 4, 48]]

    """
    #import os
    import vtk
    if return_first and return_array:
        import numpy as np

    Reader = vtk.vtkDataSetReader()
    Reader.SetFileName(input_vtk)
    Reader.ReadAllScalarsOn()  # Activate the reading of all scalars
    Reader.Update()

    Data = Reader.GetOutput()
    PointData = Data.GetPointData()
    points = [list(Data.GetPoint(point_id))
              for point_id in range(0, Data.GetNumberOfPoints())]
    npoints = len(points)

    if Data.GetNumberOfPolys() > 0:
        faces = [[int(Data.GetPolys().GetData().GetValue(j))
                  for j in range(i*4 + 1, i*4 + 4)]
                  for i in range(Data.GetPolys().GetNumberOfCells())]
    else:
        faces = []

    if Data.GetNumberOfLines() > 0:
        lines  = [[Data.GetLines().GetData().GetValue(j)
                   for j in range(i*3+1, i*3+3) ]
                   for i in range(Data.GetNumberOfLines())]
    else:
        lines = []

    if Data.GetNumberOfVerts() > 0:
       indices = [Data.GetVerts().GetData().GetValue(i)
                  for i in range(1, Data.GetVerts().GetSize() )]
    else:
       indices = []

    scalars = []
    scalar_names = []

    if Reader.GetNumberOfScalarsInFile() > 0:
        for scalar_index in range(Reader.GetNumberOfScalarsInFile()):
            scalar_name = Reader.GetScalarsNameInFile(scalar_index)

            #n_scalars = scalar_index + 1
            #if n_scalars == 1:
            #    print("Load \"{0}\" scalars from {1}".
            #          format(scalar_name, os.path.basename(input_vtk)))
            #else:
            #    print("Load \"{0}\" (of {1} scalars) from {2}".
            #          format(scalar_name, n_scalars,
            #                 os.path.basename(input_vtk)))

            scalar_array = PointData.GetArray(scalar_name)
            if scalar_array:
                scalar = [scalar_array.GetValue(i)
                          for i in range(scalar_array.GetDataSize())]
                scalars.append(scalar)
                scalar_names.append(scalar_name)

    if return_first:
        if scalars:
            scalars = scalars[0]
        if return_array:
            scalars = np.array(scalars)
        if scalar_names:
            scalar_names = scalar_names[0]
        else:
            scalar_names = ''

    return points, indices, lines, faces, scalars, scalar_names, \
           npoints, input_vtk


def write_header(Fp, Header='# vtk DataFile Version 2.0',
                     Title='Generated by Mindboggle (www.mindboggle.info)',
                     fileType='ASCII', dataType='POLYDATA'):
    """
    Write header information for a VTK-format file::

        # vtk DataFile Version 2.0
        Generated by Mindboggle (www.mindboggle.info)
        ASCII
        DATASET POLYDATA

    This part matches three things in the VTK 4.2 File Formats doc:
      - Part 1: Header
      - Part 2: Title (256 characters maximum, ending with newline character)
      - Part 3: Data type, either ASCII or BINARY
      - Part 4: Geometry/topology. dataType is one of:
          - STRUCTURED_POINTS
          - STRUCTURED_GRID
          - UNSTRUCTURED_GRID
          - POLYDATA
          - RECTILINEAR_GRID
          - FIELD

    """

    Fp.write('{0}\n{1}\n{2}\nDATASET {3}\n'.format(Header, Title, fileType,
                                                   dataType))


def write_points(Fp, points, dataType="float"):
    """
    Write coordinates of points, the POINTS section in DATASET POLYDATA::

        POINTS 150991 float
        -7.62268877029 -81.2403945923 -1.44539153576
        ...

    Indices are 0-offset. Thus the first point is point id 0::

        POINTS n dataType
        p0x p0y p0z
        ...
        p(n-1)x p(n-1)y p(n-1)z

    """
    import numpy as np

    Fp.write('POINTS {0} {1}\n'.format(len(points), dataType))

    n = np.shape(points)[1]
    for point in points:
        if n == 3:
            [R, A, S] = point
            Fp.write('{0} {1} {2}\n'.format(R, A, S))
        elif n == 2:
            [R, A] = point
            Fp.write('{0} {1}\n'.format(R, A))
        else:
            raise IOError('Unrecognized number of coordinates per point')


def write_faces(Fp, faces):
    """
    Write indices to vertices forming triangular meshes or lines,
    the POLYGONS section in DATASET POLYDATA section:

        POLYGONS 301978 1207912
        3 0 1 4
        ...

    """
    import numpy as np

    n = np.shape(faces)[1]
    if n == 3:
        face_name = 'POLYGONS '
        Fp.write('{0} {1} {2}\n'.format(face_name, len(faces),
                 len(faces) * (n + 1)))
    elif n == 2:
        face_name = 'LINES '
        Fp.write('{0} {1} {2}\n'.format(face_name, len(faces),
                 len(faces) * (n + 1)))
    else:
        raise IOError('Unrecognized number of vertices per face')

    for face in faces:
        if n == 3:
            [V0, V1, V2] = face
            Fp.write('{0} {1} {2} {3}\n'.format(n, V0, V1, V2))
        elif n == 2:
            [V0, V1] = face
            Fp.write('{0} {1} {2}\n'.format(n, V0, V1))


def write_lines(Fp, lines):
    """
    Save connected line segments to a VTK file.

    Parameters
    ----------
    Fp : pointer to a file
        pointer to the file to write lines
    lines : list of 2-tuples of integers
        each element is an edge on the mesh, consisting of 2 integers
        representing the 2 vertices of the edge
    """

    write_faces(Fp, lines)


def write_vertices(Fp, indices):
    """
    Write indices to vertices, the VERTICES section
    in the DATASET POLYDATA section::

        VERTICES 140200 420600
        3 130239 2779 10523
        ...

    Indices are 0-offset. Thus the first point is point id 0::

        VERTICES n size
        numPoints0 i0 j0 k0
        ...
        numPoints_[n-1] i_[n-1] j_[n-1] k_[n-1]

    Note::

        Currently we write all vertices in one line.

    """

    Fp.write('VERTICES {0} {1}\n{2} '.format(
             1, len(indices) + 1, len(indices)))
    [Fp.write('{0} '.format(i)) for i in indices]
    Fp.write('\n')


def write_scalars(Fp, scalars, scalar_name, begin_scalars=True,
                  scalar_type='float'):
    """
    Write per-VERTEX values as a scalar lookup table into a VTK file::

        POINT_DATA 150991
        SCALARS Max_(majority_labels) int 
        LOOKUP_TABLE default
        11 
        11 
        11 
        11 
        .
        .
        .

    Parameters
    ----------
    Fp : string
        name of VTK surface mesh file
    scalars :  list of integers or floats
        scalar values, one per vertex of mesh
    scalar_name : string
        name for scalars (use unbroken string)
    begin_scalars : bool
        True if the first vertex lookup table in a VTK file
    scalar_type : string
        type of scalars ('float' or 'int')

    """

    if begin_scalars:
        Fp.write('POINT_DATA {0}\n'.format(len(scalars)))
    Fp.write('SCALARS {0} {1}\n'.format(scalar_name, scalar_type))
    Fp.write('LOOKUP_TABLE {0}\n'.format(scalar_name))
    for Value in scalars:
        Fp.write('{0}\n'.format(Value))
    Fp.write('\n')


def write_vtk(output_vtk, points, indices=[], lines=[], faces=[],
              scalars=[], scalar_names=['scalars'], scalar_type='float'):
    """
    Save lists of scalars into the lookup table of a VTK-format file.

    Scalar definition includes specification of a lookup table.
    The definition of a lookup table is optional. If not specified,
    the default VTK table will be used (and tableName should be "default").

    SCALARS dataName dataType numComp
    LOOKUP_TABLE tableName

    Parameters
    ----------
    output_vtk : string
        path of the output VTK file
    points :  list of 3-tuples of floats
        each element has 3 numbers representing the coordinates of the points
    indices : list of integers
        indices of vertices
    lines : list of 2-tuples of integers
        Each element is an edge on the mesh, consisting of 2 integers
        representing the 2 vertices of the edge
    faces : list of 3-tuples of integers
        indices to the three vertices of a face on the mesh
    scalars : list of floats, or list of lists of floats;
        each list (lookup table) contains values assigned to the vertices
    scalar_names : string or list of strings
        each element is the name of a scalar list (lookup table)
    scalar_type : string
        type of scalars ('float' or 'int')

    Examples
    --------
    >>> # Toy example
    >>> import random, os
    >>> from mindboggle.mio.vtks import write_vtk
    >>> points = [[random.random() for i in [1,2,3]] for j in range(4)]
    >>> indices = [1,2,3,0]
    >>> lines = [[1,2],[3,4]]
    >>> faces = [[1,2,3],[0,1,3]]
    >>> #scalars = [[random.random() for i in range(4)] for j in [1,2]]
    >>> scalars = [[1,3,5,7],[2,4,6,8]]
    >>> scalar_names = ['curv','depth']
    >>> output_vtk = 'write_vtk_toy.vtk'
    >>> scalar_type = 'float'
    >>> write_vtk(output_vtk, points, indices, lines, faces, scalars,
    ...           scalar_names, scalar_type) # doctest: +SKIP

    View resulting vtk file (skip test):

    >>> from mindboggle.mio.plots import plot_surfaces # doctest: +SKIP
    >>> plot_surfaces(output_vtk) # doctest: +SKIP

    Write vtk file with depth values and view (skip plot in test):

    >>> from mindboggle.mio.vtks import read_vtk
    >>> from mindboggle.mio.fetch_data import prep_tests
    >>> urls, fetch_data = prep_tests()
    >>> input_vtk = fetch_data(urls['left_travel_depth'], '', '.vtk')
    >>> points, indices, lines, faces, scalars, scalar_names, npoints, input_vtk = read_vtk(input_vtk)
    >>> output_vtk = 'write_vtk.vtk'
    >>> scalar_type = 'float'
    >>> write_vtk(output_vtk, points, indices, lines, faces, scalars,
    ...           scalar_names, scalar_type)

    View resulting vtk file (skip test):

    >>> plot_surfaces(output_vtk) # doctest: +SKIP

    """
    import os
    import numpy as np
    from io import open

    from mindboggle.mio.vtks import write_header, write_points, \
        write_vertices, write_faces, write_scalars, scalars_checker

    # Convert numpy arrays to lists
    if isinstance(faces, np.ndarray):
        faces = faces.tolist()
    if isinstance(points, np.ndarray):
        points = points.tolist()

    output_vtk = os.path.join(os.getcwd(), output_vtk)

    Fp = open(output_vtk,'w', encoding="utf-8")
    write_header(Fp)
    write_points(Fp, points)
    if indices:
        write_vertices(Fp, indices)
    if lines:
        for i in range(0,len(lines)):
            lines[i] = [lines[i][0], lines[i][1]]
        write_faces(Fp, lines) # write_faces can write either lines or faces
    if faces:
        write_faces(Fp, faces)
    scalars, scalar_names = scalars_checker(scalars, scalar_names)
    if len(scalars):

        for i, scalar_list in enumerate(scalars):
            if i == 0:
                scalar_name = scalar_names[i]
                write_scalars(Fp, scalar_list, scalar_name,
                              begin_scalars=True, scalar_type=scalar_type)
            else:
                if len(scalar_names) < i + 1:
                    scalar_name = scalar_names[0]
                else:
                    scalar_name = scalar_names[i]
                write_scalars(Fp, scalar_list, scalar_name,
                              begin_scalars=False, scalar_type=scalar_type)
    Fp.close()

    if not os.path.exists(output_vtk):
        raise IOError(output_vtk + " not found")


def rewrite_scalars(input_vtk, output_vtk, new_scalars,
                    new_scalar_names=['scalars'], filter_scalars=[],
                    background_value=-1):
    """
    Load VTK format file and save a subset of scalars into a new file.

    Parameters
    ----------
    input_vtk : string
        input VTK file name
    output_vtk : string
        output VTK file name
    new_scalars : list of lists (or single list or numpy array) of N floats
        each list contains new values to assign to the vertices
    new_scalar_names : string or list of strings
        each element is the new name for the corresponding scalars
    filter_scalars : list or numpy array of N elements (optional)
        scalar values used to filter faces (foreground values retained)
    background_value : integer
        background value

    Examples
    --------
    >>> # Write vtk file with depth values on sulci
    >>> from mindboggle.mio.vtks import rewrite_scalars
    >>> from mindboggle.mio.vtks import read_scalars
    >>> from mindboggle.mio.fetch_data import prep_tests
    >>> urls, fetch_data = prep_tests()
    >>> input_vtk = fetch_data(urls['left_travel_depth'], '', '.vtk')
    >>> sulci_file = fetch_data(urls['left_sulci'], '', '.vtk')
    >>> output_vtk = 'rewrite_scalars.vtk'
    >>> curvs, name = read_scalars(input_vtk, True,True)
    >>> sulci, name = read_scalars(sulci_file)
    >>> new_scalars = [curvs, sulci]
    >>> new_scalar_names = ['curvs', 'sulci']
    >>> filter_scalars = sulci
    >>> background_value = -1
    >>> rewrite_scalars(input_vtk, output_vtk, new_scalars,
    ...     new_scalar_names, filter_scalars, background_value)

    View resulting vtk file (skip test):

    >>> from mindboggle.mio.plots import plot_surfaces
    >>> plot_surfaces(output_vtk) # doctest: +SKIP

    """
    import os
    import numpy as np
    from io import open

    from mindboggle.guts.mesh import keep_faces, reindex_faces_points
    from mindboggle.mio.vtks import write_header, write_points, \
        write_vertices, write_faces, write_scalars, read_vtk, scalars_checker

    # Convert numpy arrays to lists
    if isinstance(new_scalars, np.ndarray):
        new_scalars = new_scalars.tolist()
    if isinstance(filter_scalars, np.ndarray):
        filter_scalars = filter_scalars.tolist()

    # Output VTK file to current working directory
    output_vtk = os.path.join(os.getcwd(), output_vtk)

    # Load VTK file
    points, indices, lines, faces, scalars, scalar_names, npoints, \
        input_vtk = read_vtk(input_vtk)

    # Find indices to foreground values
    if filter_scalars:
        indices_keep = [i for i,x in enumerate(filter_scalars)
                        if x != background_value]
        #indices_remove = [i for i,x in enumerate(filter_scalars)
        #                  if x == background_value]
        # Remove surface faces whose three vertices are not all in indices
        faces = keep_faces(faces, indices_keep)
        faces, points, original_indices = reindex_faces_points(faces, points)

    # Write VTK file
    Fp = open(output_vtk,'w', encoding="utf-8")
    write_header(Fp)
    if points:
        write_points(Fp, points)
    if indices:
        write_vertices(Fp, indices)
    if faces:
        write_faces(Fp, faces)
    if new_scalars:
        new_scalars, new_scalar_names = scalars_checker(new_scalars,
                                                        new_scalar_names)

        # scalars_checker() returns a list of lists for scalars:
        for i, new_scalar_list in enumerate(new_scalars):
            if filter_scalars:
                new_scalar_list = np.array(new_scalar_list)[original_indices].\
                    tolist()
            #    for iremove in indices_remove:
            #        new_scalar_list[iremove] = background_value
            if np.ndim(new_scalar_list) == 1:
                scalar_type = type(new_scalar_list[0]).__name__
            elif np.ndim(new_scalar_list) == 2:
                scalar_type = type(new_scalar_list[0][0]).__name__
            else:
                raise IOError("Undefined scalar type!")
            if i == 0:
                new_scalar_name = new_scalar_names[0]
                write_scalars(Fp, new_scalar_list, new_scalar_name,
                              begin_scalars=True,
                              scalar_type=scalar_type)
            else:
                if len(new_scalar_names) < i + 1:
                    new_scalar_name = new_scalar_names[0]
                else:
                    new_scalar_name = new_scalar_names[i]
                write_scalars(Fp, new_scalar_list, new_scalar_name,
                              begin_scalars=False,
                              scalar_type=scalar_type)
    else:
        raise IOError('new_scalars is empty')

    Fp.close()

    if not os.path.exists(output_vtk):
        raise IOError(output_vtk + " not found")


def explode_scalars(input_indices_vtk, input_values_vtk='', output_stem='',
                    exclude_values=[-1], background_value=-1,
                    output_scalar_name='scalars',
                    remove_background_faces=True,
                    reindex=True, verbose=False):
    """
    Write out a separate VTK file for each integer (not in exclude_values)
    in (the first) scalar list of an input VTK file.
    Optionally write the values drawn from a second VTK file,
    remove background values, and reindex indices.

    Parameters
    ----------
    input_indices_vtk : string
        path of the input VTK file that contains indices as scalars
        (assumes that the scalars are a list of floats or integers)
    input_values_vtk : string
        path of the input VTK file that contains values as scalars
    output_stem : string
        path and stem of the output VTK file
    exclude_values : list or array
        values to exclude
    background_value : integer or float
        background value in output VTK files
    remove_background_faces : bool
        remove all faces whose three vertices are not all a given index?
    reindex : bool
        reindex all indices in faces?
    verbose : bool
        print statements?

    Returns
    -------
    output_files : list of strings
        paths to output VTK files

    Examples
    --------
    >>> # Example 1:  explode sulci with thickness values
    >>> import os
    >>> from mindboggle.mio.vtks import explode_scalars
    >>> from mindboggle.mio.fetch_data import prep_tests
    >>> urls, fetch_data = prep_tests()
    >>> input_indices_vtk = fetch_data(urls['left_sulci'], '', '.vtk')
    >>> input_values_vtk = fetch_data(urls['left_travel_depth'], '', '.vtk')
    >>> output_stem = 'explode_scalars_sulcus_depth'
    >>> exclude_values = [-1]
    >>> background_value = -1,
    >>> output_scalar_name = 'sulcus_depth'
    >>> remove_background_faces = True
    >>> reindex = True
    >>> verbose = False
    >>> output_files = explode_scalars(input_indices_vtk, input_values_vtk,
    ...     output_stem, exclude_values, background_value, output_scalar_name,
    ...     remove_background_faces, reindex, verbose)
    >>> os.path.basename(output_files[0])
    'explode_scalars_sulcus_depth1.vtk'

    View Example 1 results (skip test):

    >>> from mindboggle.mio.plots import plot_surfaces
    >>> plot_surfaces(output_stem + '1.vtk') # doctest: +SKIP

    Example 2:  explode labels

    >>> input_indices_vtk = fetch_data(urls['left_freesurfer_labels'], '', '.vtk')
    >>> input_values_vtk = ''
    >>> output_stem = 'explode_scalars_label'
    >>> output_scalar_name = 'labels'
    >>> output_files = explode_scalars(input_indices_vtk, input_values_vtk, 
    ...     output_stem, exclude_values, background_value, output_scalar_name,
    ...     remove_background_faces, reindex, verbose)
    >>> os.path.basename(output_files[0])
    'explode_scalars_label999.vtk'

    View Example 2 results (skip test):

    >>> from mindboggle.mio.plots import plot_surfaces
    >>> plot_surfaces(output_stem + '1.vtk') # doctest: +SKIP

    """
    import os
    import numpy as np
    from mindboggle.mio.vtks import read_scalars, read_vtk, write_vtk
    from mindboggle.guts.mesh import reindex_faces_points, keep_faces

    if not input_values_vtk:
        input_values_vtk = input_indices_vtk

    # Load VTK file:
    points, indices, lines, faces, scalars, scalar_names, npoints, \
        input_vtk = read_vtk(input_indices_vtk, True, True)
    if verbose:
        print("Explode the scalar list in {0}".
            format(os.path.basename(input_indices_vtk)))
    if input_values_vtk != input_indices_vtk:
        values, name = read_scalars(input_values_vtk, True, True)
        if verbose:
            print("Explode the scalar list of values in {0} "
                  "with the scalar list of indices in {1}".
                format(os.path.basename(input_values_vtk),
                       os.path.basename(input_indices_vtk)))
    else:
        values = np.copy(scalars)

    # Loop through unique (non-excluded) scalar values:
    unique_scalars = np.unique(scalars)
    if all(unique_scalars==np.round(unique_scalars)):
        unique_scalars = [int(x) for x in unique_scalars
                          if x not in exclude_values]
    else:
        unique_scalars = [x for x in unique_scalars
                          if x not in exclude_values]

    output_files =[]
    for scalar in unique_scalars:

        # Remove background (keep only faces with the scalar):
        if remove_background_faces:
            scalar_indices = [i for i,x in enumerate(scalars) if x == scalar]
            scalar_faces = keep_faces(faces, scalar_indices)
        else:
            scalar_faces = faces

        # Reindex:
        if reindex:
            scalar_faces, select_points, \
            o1 = reindex_faces_points(scalar_faces, points)
        else:
            select_points = points

        # Select values for each scalar:
        select_values = np.copy(values)
        select_values[scalars != scalar] = background_value

        if verbose:
            print("  Scalar {0}: {1} vertices".format(scalar,
                                                      len(select_points)))

        if len(select_points) > 0:
            # Write VTK file with scalar values (list of values):
            if np.ndim(select_values) == 1:
                scalar_type = type(select_values[0]).__name__
            elif np.ndim(select_values) == 2:
                scalar_type = type(select_values[0][0]).__name__
            else:
                if verbose:
                    raise IOError("Undefined scalar type!")
            output_vtk = os.path.join(os.getcwd(),
                                      output_stem + str(scalar) + '.vtk')
            write_vtk(output_vtk, select_points, indices, lines, scalar_faces,
                      select_values.tolist(), output_scalar_name,
                      scalar_type=scalar_type)

            output_files.append(output_vtk)

    return output_files


def explode_scalars_mindboggle(subject_path, output_path='',
                               pieces='labels', background_value=-1,
                               verbose=False):
    """
    Given the path to a subject's Mindboggle output data,
    break up each shape surface VTK file into separate VTK files,
    one for each label/sulcus index.

    Parameters
    ----------
    subject_path : string
        path to subject directory
    output_path : string
        output path/directory
    pieces : string
        name of structures to explode (e.g., 'labels', 'sulci')
    background_value : integer or float
        background value
    verbose : bool
        print statements?

    Examples
    --------
    >>> # Explode surface shape files by label values:
    >>> import os
    >>> from mindboggle.mio.vtks import explode_scalars_mindboggle
    >>> subject_path = '/Users/arno/mindboggled/Twins-2-1'
    >>> output_path = os.getcwd()
    >>> pieces = 'labels'
    >>> background_value = -1
    >>> verbose = False
    >>> explode_scalars_mindboggle(subject_path, output_path, pieces,
    ...                            background_value, verbose) # doctest: +SKIP

    View example result (skip test):

    >>> from mindboggle.mio.plots import plot_surfaces
    >>> plot_surfaces('left_exploded/travel_depth_1035.vtk') # doctest: +SKIP

    """
    import os
    from mindboggle.mio.vtks import explode_scalars

    if not os.path.exists(output_path):
        raise IOError("{0} does not exist".format(output_path))
    else:

        for side in ['left', 'right']:

            output_dir = os.path.join(output_path,
                                      side + '_exploded_' + pieces + '_vtks')
            if not os.path.exists(output_dir):
                if verbose:
                    print("Create missing output directory: {0}".
                          format(output_dir))
                os.mkdir(output_dir)
            if os.path.exists(output_dir):

                if pieces == 'labels':
                    File = os.path.join('labels',
                                        side + '_cortical_surface',
                                        'freesurfer_cortex_labels.vtk')
                elif pieces in ['sulci', 'fundus_per_sulcus', 'folds']:
                    File = os.path.join('features',
                                          side + '_cortical_surface',
                                          pieces + '.vtk')
                else:
                    raise IOError("Choose from: {'labels', 'sulci'}")
                                  #'fundus_per_sulcus', 'folds'}")

                labels_vtk = os.path.join(subject_path, File)
                shapes_path = os.path.join(subject_path, 'shapes',
                                           side + '_cortical_surface')
                shape_names = ['travel_depth',
                               'geodesic_depth',
                               'freesurfer_sulc',
                               'mean_curvature',
                               'freesurfer_curvature',
                               'freesurfer_thickness']

                for shape_name in shape_names:

                    shape_vtk = os.path.join(shapes_path, shape_name + '.vtk')

                    if verbose:
                        print("Explode {0} by {1} values from {2}").\
                            format(shape_vtk, pieces, labels_vtk)

                    output_files = explode_scalars(labels_vtk, shape_vtk,
                                    os.path.join(output_dir,
                                                 shape_name + '_'),
                                    [background_value], background_value,
                                    'scalars', True, True, False)

            else:
                raise IOError('Unable to make directory {0}'.format(output_dir))


def scalars_checker(scalars, scalar_names):
    """
    Check whether input scalars and scalar_names are in acceptable format.
    If not, reformat.

    Parameters
    ----------
    scalars : list of lists of floats (or single list or 1-/2-D array)
    scalar_names : string or list of strings

    Returns
    -------
    scalars : list of lists of floats or integers
    scalar_names : list of strings

    Examples
    --------
    >>> import numpy as np
    >>> from mindboggle.mio.vtks import scalars_checker
    >>> scalars_checker([[1,2],[3,4]], ["list1", "list2"])
    ([[1, 2], [3, 4]], ['list1', 'list2'])
    >>> scalars_checker([[1,2],[3,4]], "")
    ([[1, 2], [3, 4]], ['', ''])
    >>> scalars_checker([[1,2],[3,4]], ["list1", "list2", "list3"])
    ([[1, 2], [3, 4]], ['list1', 'list2', 'list3'])
    >>> scalars_checker([[1,2],[3,4]], "list1")
    ([[1, 2], [3, 4]], ['list1', 'list1'])
    >>> scalars_checker([1,2,3,4], ["123"])
    ([[1, 2, 3, 4]], ['123'])
    >>> scalars_checker(1, ["123"]) # doctest: +SKIP
    Error: scalars is neither a list nor a numpy array. # doctest: +SKIP
    >>> scalars_checker(np.array([1,2,3]), ["123"])
    ([[1, 2, 3]], ['123'])
    >>> scalars_checker(np.array([[1,2,3]]), ["123"])
    ([[1, 2, 3]], ['123'])
    >>> scalars_checker(np.array([[1,2,3],[4,5,6]]), ["123"])
    ([[1, 2, 3], [4, 5, 6]], ['123', '123'])
    >>> scalars_checker(np.array([[[1,2,3]]]), ["123"]) # doctest: +SKIP
    Error: Dimension of new_scalars is too high. # doctest: +SKIP
    >>> scalars_checker(np.array([np.array([0,7,9]),[1,2,3]]), ["123"])
    ([[0, 7, 9], [1, 2, 3]], ['123', '123'])

    Notes
    -----
    This function does not check all possible cases of scalars and
    scalar_names, but only those that are likely to occur when using Mindboggle.

    """
    import numpy as np

    # If not a list, convert to a list.
    if not isinstance(scalars, list):
        if isinstance(scalars, np.ndarray):
            if len(scalars.shape) < 2: # this is at most a 1-D array
                scalars = [scalars.tolist()]
            elif len(scalars.shape) == 2: # 2-D numpy array
                scalars = scalars.tolist()
            else:
                raise IOError("Error: Dimension of new_scalars is too high.")
        else:
            raise IOError("Error: scalars is neither a list nor a numpy array.")

    if scalars:

        # If the list contains integers or floats, put in a list.
        if isinstance(scalars[0], int) or isinstance(scalars[0], float):
            scalars = [scalars]
        # If the list contains all lists, accept format.
        elif all([isinstance(x, list) for x in scalars]):
            pass
        # If the list contains arrays (optionally lists), convert arrays to lists.
        elif all([isinstance(x, list) or isinstance(x, np.ndarray)
                  for x in scalars]):
            scalars2 = []
            for x in scalars:
                if isinstance(x, list):
                    scalars2.append(x)
                else:
                    scalars2.append(x.tolist())
            scalars = scalars2
        else:
            raise IOError("Error: scalars is a 1-D list containing unacceptable elements.")
            #print("scalars type is: {0}".format(type(scalars)))
            #print("scalars length is: {0}".format(len(scalars)))
            #print("scalars[0] type is: {0}".format(type(scalars[0])))

        # If scalar_names is a string, create a list containing
        # as many of this string as there are scalar lists.
        if isinstance(scalar_names, str):
            scalar_names = [scalar_names for x in scalars]
        elif isinstance(scalar_names, list):
            if len(scalar_names) < len(scalars):
                scalar_names = [scalar_names[0] for x in scalars]
            else:
                pass
        else:
            raise IOError("Error: scalar_names is neither a list nor a string")
    #else:
        #print("Warning: scalars is empty")

    return scalars, scalar_names


# def read_itk_transform_old(transform_file):
#     """
#     Read ITK transform file and output transform array.
#
#     ..ITK affine transform file format ::
#
#     #Insight Transform File V1.0
#     #Transform 0
#     Transform: MatrixOffsetTransformBase_double_3_3
#     Parameters: 0.90768 0.043529 0.0128917 -0.0454455 0.868937 0.406098 \
#     0.0179439 -0.430013 0.783074 -0.794889 -18.3346 -3.14767
#     FixedParameters: -0.60936 21.1593 10.6148
#
#     Parameters
#     ----------
#     transform_file : string
#         name of ITK affine transform file
#
#     Returns
#     -------
#     transform : numpy array
#         4x4 affine transform matrix
#     fixed_parameters : numpy array
#         FixedParameters vector
#
#     Examples
#     --------
#     >>> import os
#     >>> from mindboggle.mio.vtks import read_itk_transform_old
#     >>> transform_file = os.path.join('mri',
#     ...                               't1weighted_brain.MNI152Affine.txt') # doctest: +SKIP
#     >>> read_itk_transform_old(transform_file) # doctest: +SKIP
#     (array([[ 9.07680e-01, 4.35290e-02, 1.28917e-02, -7.94889e-01],
#     [ -4.54455e-02, 8.68937e-01, 4.06098e-01, -1.83346e+01],
#     [ 1.79439e-02, -4.30013e-01, 7.83074e-01, -3.14767e+00],
#     [ 0.00000e+00, 0.00000e+00, 0.00000e+00, 1.00000e+00]]),
#     [-0.60936, 21.1593, 10.6148])
#
#     """
#     import numpy as np
#     from io import open
#
#     transform = np.eye(4)
#
#     # Read ITK transform file
#     fid = open(transform_file, 'r')
#     affine_lines = fid.readlines()
#
#     affine = affine_lines[3]
#     affine = affine.split()
#     affine = [np.float(x) for x in affine[1::]]
#     affine = np.reshape(affine, (4,3))
#     linear_transform = affine[0:3,:]
#     translation = affine[3,:]
#     transform[0:3,0:3] = linear_transform
#     transform[0:3,3] = translation
#
#     fixed_parameters = affine_lines[4]
#     fixed_parameters = fixed_parameters.split()
#     fixed_parameters = [np.float(x) for x in fixed_parameters[1::]]
#
#     return transform, fixed_parameters
#
#
# def read_itk_transform(transform_file):
#     """
#     Read ITK transform file and output transform array.
#
#     Daniel Haehn's implementation: https://gist.github.com/haehn/5614966
#
#     ..ITK affine transform file format ::
#
#         #Insight Transform File V1.0
#         #Transform 0
#         Transform: MatrixOffsetTransformBase_double_3_3
#         Parameters: 0.90768 0.043529 0.0128917 -0.0454455 0.868937 0.406098 \
#                     0.0179439 -0.430013 0.783074 -0.794889 -18.3346 -3.14767
#         FixedParameters: -0.60936 21.1593 10.6148
#
#     Parameters
#     ----------
#     transform_file : string
#         name of ITK affine transform file
#
#     Returns
#     -------
#     transform : numpy array
#         4x4 affine transform matrix
#
#     Examples
#     --------
#     >>> import os
#     >>> from mindboggle.mio.vtks import read_itk_transform
#     >>> transform_file = os.path.join('mri',
#     ...                               't1weighted_brain.MNI152Affine.txt') # doctest: +SKIP
#     >>> read_itk_transform(transform_file) # doctest: +SKIP
#     array([[  9.07680e-01,   4.35290e-02,   1.28917e-02,   -8.16765e-01],
#            [ -4.54455e-02,   8.68937e-01,   4.06098e-01,   -2.31926e+01],
#            [  1.79439e-02,  -4.30013e-01,   7.83074e-01,   3.52899e+00],
#            [  0 0 0 1]])
#     """
#     import numpy as np
#     from io import open
#
#     # Read the transform:
#     transform = None
#     with open( transform_file, 'r' ) as f:
#       for line in f:
#
#         # Check for Parameters:
#         if line.startswith( 'Parameters:' ):
#           values = line.split( ': ' )[1].split( ' ' )
#
#           # Filter empty spaces and line breaks:
#           values = [float( e ) for e in values if ( e != '' and e != '\n' )]
#           # Create the upper left of the matrix:
#           transform_upper_left = np.reshape( values[0:9], ( 3, 3 ) )
#           # Grab the translation as well:
#           translation = values[9:]
#
#         # Check for FixedParameters:
#         if line.startswith( 'FixedParameters:' ):
#           values = line.split( ': ' )[1].split( ' ' )
#
#           # Filter empty spaces and line breaks:
#           values = [float( e ) for e in values if ( e != '' and e != '\n' )]
#           # Set up the center:
#           center = values
#
#     # Compute the offset:
#     offset = np.ones( 4 )
#     for i in range( 0, 3 ):
#       offset[i] = translation[i] + center[i];
#       for j in range( 0, 3 ):
#         offset[i] -= transform_upper_left[i][j] * center[i]
#
#     # add the [0, 0, 0] line:
#     transform = np.vstack( ( transform_upper_left, [0, 0, 0] ) )
#     # and the [offset, 1] column:
#     transform = np.hstack( ( transform, np.reshape( offset, ( 4, 1 ) ) ) )
#
#     return transform


def apply_affine_transforms(transform_files, inverse_booleans,
                            transform_format='itk', vtk_or_points=[],
                            vtk_file_stem='affine_'):
    """
    Transform coordinates using an affine matrix.

    For use with ANTs, x and y columns are multiplied by -1 before and after
    applying the inverse affine transform because ITK uses a different
    coordinate system than the NIfTI coordinate system.

    Parameters
    ----------
    transform files : list of strings
        names of affine transform files
    inverse_booleans : list of of zeros and ones
        for each transform, 1 to take the inverse, else 0
    transform_format : string
        format for transform file (currently 'itk');
        complications arise with other formats, such as
        'txt' for text, or 'mat' for Matlab format, since
        software-specific assignment of parameters such as
        the origin need to be taken into account
    vtk_or_points : string or list of lists of three integers
        name of VTK file containing point coordinate data, or the data
        (if vtk file, assumes scalars are a list of floats or integers)
    vtk_file_stem : string
        save transformed coordinates in a vtk file with this file prepend
        (empty string if vtk_or_points is points)

    Returns
    -------
    affine_points : list of lists of floats
        transformed coordinates
    output_file : string or None (if not vtk_file_stem or vtk_or_points is points)
        name of VTK file containing transformed point data

    Examples
    --------
    >>> import numpy as np
    >>> from mindboggle.mio.vtks import apply_affine_transforms
    >>> from mindboggle.mio.fetch_data import prep_tests
    >>> urls, fetch_data = prep_tests()
    >>> vtk_or_points = fetch_data(urls['left_pial'], '', '.vtk')
    >>> transform_files = [fetch_data(urls['ants_affine_subject2template'], '', '.txt')]
    >>> inverse_booleans = [1]
    >>> transform_format = 'itk'
    >>> vtk_file_stem = 'affine_'
    >>> affine_points, output_file = apply_affine_transforms(transform_files,
    ...     inverse_booleans, transform_format, vtk_or_points, vtk_file_stem) # doctest: +SKIP
    >>> print(np.array_str(np.array(affine_points[0:5]),
    ...       precision=5, suppress_small=True)) # doctest: +SKIP
    [[-123.02735 -228.19407 -101.14381]
     [-123.46156 -228.39812 -101.24258]
     [-124.22058 -228.39971 -101.15211]
     [-121.66154 -228.72653 -102.39572]
     [-122.55212 -228.56696 -101.82275]]

    View resulting vtk file (skip test):

    >>> from mindboggle.mio.plots import plot_surfaces
    >>> plot_surfaces(output_file, vtk_or_points) # doctest: +SKIP

    """
    import os
    import numpy as np
    #from scipy.io import loadmat

    from mindboggle.thirdparty.ants import antsApplyTransformsToPoints
    from mindboggle.mio.vtks import read_vtk, write_vtk
                                        #read_itk_transform
    transform_format = 'itk'

    ## Read affine transform file:
    # if transform_format == 'itk':
    #     transform = read_itk_transform(transform_file)
    # elif transform_format == 'txt':
    #     transform = np.loadtxt(transform_file)
    # elif transform_format == 'mat':
    #     transform = loadmat(transform_file)
    # else:
    #     import sys
    #     sys.exit('Transform file format not understood.')

    # Read VTK file:
    if isinstance(vtk_or_points, str):
        points, indices, lines, faces, scalars, scalar_names, npoints, \
            input_vtk = read_vtk(vtk_or_points)
        points = np.array(points)
    elif isinstance(vtk_or_points, list):
        points = np.array(vtk_or_points)
        vtk_file_stem = ''
    elif isinstance(vtk_or_points, np.ndarray):
        points = vtk_or_points.copy()
        vtk_file_stem = ''

    # Transform points:
    # For use with ANTs, x and y columns are multiplied by -1 before and after
    # applying the inverse affine transform because ITK uses a different
    # coordinate system than the NIfTI coordinate system.
    if transform_format == 'itk' and len(points):
        points[:, :2] = points[:, :2] * np.array((-1, -1))
        affine_points = antsApplyTransformsToPoints(points,
                            transform_files, inverse_booleans)
        affine_points = np.array(affine_points)
        affine_points[:, :2] = affine_points[:, :2] * np.array((-1, -1))
        ## fix alternative to ANTs: compose transforms and take inverse(s)
        # points = np.concatenate((points,
        #                          np.ones((1, np.shape(points)[1]))), axis=0)
        # affine_points = np.transpose(np.dot(transform, points))[:, 0:3]
    else:
        affine_points = []

    # Write transformed VTK file:
    if vtk_file_stem and isinstance(vtk_or_points, str):
        output_file = os.path.join(os.getcwd(), vtk_file_stem +
                                   os.path.basename(vtk_or_points))
        if np.size(scalars):
            if np.ndim(scalars) == 1:
                scalar_type = type(scalars[0]).__name__
            elif np.ndim(scalars) == 2:
                scalar_type = type(scalars[0][0]).__name__
            else:
                raise IOError("Undefined scalar type!")
        else:
            scalars = []
            scalar_type = 'int'

        write_vtk(output_file, affine_points,
                  indices, lines, faces, scalars, scalar_names, scalar_type)
    else:
        output_file = None

    return affine_points, output_file


def freesurfer_surface_to_vtk(surface_file, orig_file='', output_vtk=''):
    """
    Convert FreeSurfer surface file to VTK format.

    If a file named orig.mgz exists in '../mri', the surface coordinates
    are transformed into scanner RAS space during format conversion
    according to the vox2ras transform in that file.

    Parameters
    ----------
    surface_file : string
        name of FreeSurfer surface file
    orig_file : string
        name of FreeSurfer mri/orig.mgz file
    output_vtk : string
        name of output VTK file; if blank, appends
        ".vtk" to surface_file and saves to the
        current working directory.

    Returns
    -------
    output_vtk : string
        name of output VTK file

    Examples
    --------
    >>> import os
    >>> from mindboggle.mio.vtks import freesurfer_surface_to_vtk
    >>> from mindboggle.mio.fetch_data import prep_tests
    >>> urls, fetch_data = prep_tests()
    >>> surface_file = fetch_data(urls['left_freesurfer_pial'], '', '.pial')
    >>> urls, fetch_data = prep_tests()
    >>> orig_file = fetch_data(urls['freesurfer_orig_mgz'], '', '.mgz')
    >>> output_vtk = 'freesurfer_surface_to_vtk.vtk'
    >>> os.rename(surface_file, surface_file + '.pial')
    >>> os.rename(orig_file, orig_file + '.mgz')
    >>> surface_file = surface_file + '.pial'
    >>> orig_file = orig_file + '.mgz'
    >>> output_vtk = freesurfer_surface_to_vtk(surface_file, orig_file,
    ...                                        output_vtk)

    View output vtk file (skip test):

    >>> from mindboggle.mio.plots import plot_surfaces # doctest: +SKIP
    >>> plot_surfaces(output_vtk) # doctest: +SKIP

    """
    import os
    import nibabel as nb
    from io import open

    from mindboggle.mio.vtks import write_header, write_points, write_faces

    surf = nb.freesurfer.read_geometry(surface_file)
    points = surf[0]
    faces = surf[1]

    # Transform surface coordinates into normal scanner RAS.
    # See example 3 in "Transforms within a subject's anatomical space":
    # https://surfer.nmr.mgh.harvard.edu/fswiki/CoordinateSystems

    if not orig_file:
        orig_file = os.path.join(os.path.dirname(surface_file),
                                 "..", "mri", "orig.mgz")

    if os.path.exists(orig_file):
        import numpy as np
        Norig = nb.load(orig_file).get_affine()
        Torig = np.array([[-1, 0, 0, 128],
                          [0, 0, 1, -128],
                          [0, -1, 0, 128],
                          [0, 0, 0, 1]], dtype=float)
        xfm = np.dot(Norig, np.linalg.inv(Torig))
        points = np.transpose(np.dot(xfm, np.transpose(
            np.concatenate((points, np.ones((np.shape(points)[0],1))),
                           axis=1))))[:,0:3]
    else:
        raise IOError(orig_file + " does not exist in the FreeSurfer "
                      "subjects directory.")

    if not output_vtk:
        output_vtk = os.path.join(os.getcwd(),
                                  os.path.basename(surface_file + '.vtk'))
    Fp = open(output_vtk, 'w')
    write_header(Fp, Title='vtk output from ' + surface_file)
    write_points(Fp, points)
    write_faces(Fp, faces)
    Fp.close()

    if not os.path.exists(output_vtk):
        raise IOError("Output VTK file " + output_vtk + " not created.")

    return output_vtk


def freesurfer_curvature_to_vtk(surface_file, vtk_file, output_vtk='',
                                background_value=-1):
    """
    Convert FreeSurfer curvature, thickness, or convexity file to VTK format.

    Parameters
    ----------
    surface_file : string
        name of FreeSurfer surface file
    vtk_file : string
        name of VTK surface file
    output_vtk : string
        name of output VTK file
    background_value : integer or float
        background value

    Returns
    -------
    output_vtk : string
        name of output VTK file, where each vertex is assigned
        the corresponding shape value

    Examples
    --------
    >>> from mindboggle.mio.vtks import freesurfer_curvature_to_vtk
    >>> from mindboggle.mio.fetch_data import prep_tests
    >>> urls, fetch_data = prep_tests()
    >>> surface_file = fetch_data(urls['left_freesurfer_thickness'], '', '.vtk')
    >>> vtk_file = fetch_data(urls['left_pial'], '', '.vtk')
    >>> output_vtk = 'freesurfer_curvature_to_vtk.vtk'
    >>> background_value = -1
    >>> output_vtk = freesurfer_curvature_to_vtk(surface_file, vtk_file,
    ...                                          output_vtk, background_value)

    View output vtk file (skip test):

    >>> from mindboggle.mio.plots import plot_surfaces
    >>> plot_surfaces(output_vtk) # doctest: +SKIP

    """
    import os
    import nibabel as nb

    from mindboggle.mio.vtks import rewrite_scalars

    curvature_values = nb.freesurfer.read_morph_data(surface_file)
    scalar_names = os.path.basename(surface_file)

    if not output_vtk:
        output_vtk = os.path.join(os.getcwd(),
                                  os.path.basename(surface_file)+'.vtk')
    rewrite_scalars(vtk_file, output_vtk, curvature_values, scalar_names,
                    [], background_value)
    if not os.path.exists(output_vtk):
        raise IOError("Output VTK file " + output_vtk + " not created.")

    return output_vtk


def freesurfer_annot_to_vtk(annot_file, vtk_file, output_vtk='',
                            background_value=-1):
    """
    Load a FreeSurfer .annot file and save as a VTK format file.

    Parameters
    ----------
    annot_file : string
        name of FreeSurfer .annot file
    vtk_file : string
        name of VTK surface file
    output_vtk : string
        name of output VTK file, where each vertex is assigned
        the corresponding annot value
    background_value : integer or float
        background value

    Returns
    -------
    labels : list
        integers (one label per vertex)
    output_vtk : string
        name of output VTK file, where each vertex is assigned
        the corresponding shape value

    Examples
    --------
    >>> import numpy as np
    >>> from mindboggle.mio.vtks import freesurfer_annot_to_vtk
    >>> from mindboggle.mio.fetch_data import prep_tests
    >>> urls, fetch_data = prep_tests()
    >>> annot_file = fetch_data(urls['left_freesurfer_aparc_annot'], '', '.annot')
    >>> vtk_file = fetch_data(urls['left_pial'], '', '.vtk')
    >>> output_vtk = 'freesurfer_annot_to_vtk.vtk'
    >>> background_value = -1
    >>> labels, output_vtk = freesurfer_annot_to_vtk(annot_file,
    ...                          vtk_file, output_vtk, background_value)
    >>> nlabels = [len(np.where(labels == x)[0]) for x in np.unique(labels)]
    >>> nlabels[0:10]
    [8305, 1414, 1171, 4096, 2213, 633, 5002, 6524, 4852, 1823]

    View output vtk file (skip test):

    >>> from mindboggle.mio.plots import plot_surfaces
    >>> plot_surfaces(output_vtk) # doctest: +SKIP

    """
    import os
    import nibabel as nb
    import numpy as np

    from mindboggle.mio.vtks import rewrite_scalars

    labels, ctab, names = nb.freesurfer.read_annot(annot_file)

    # Note regarding 2013 version of pip install nibabel:
    # (https://github.com/nipy/nibabel/issues/205#issuecomment-25294009)
    #
    # The 'True' flag in nibabel.freesurfer.read_annot(annot_file, True)
    # gives the original FreeSurfer label values, not the FreeSurferColorLUT
    # labels, and when set to 'False' assigns all otherwise unlabeled
    # left cortical vertices to 3, which is also assigned to the caudal
    # middle frontal gyrus.  To correct this ambiguity, this program assigns
    # -1 to all vertices with label 0 in the original ('True') labels.
    #
    # Resolution:
    #labels_orig, ctab, names = nb.freesurfer.read_annot(annot_file, True)
    #labels[np.where(labels_orig == 0)[0]] = background_value
    #
    # Test removal of unlabeled cortex from label 3:
    #labels[np.where(labels==3)[0]]=1000

    if not output_vtk:
        output_vtk = os.path.join(os.getcwd(),
            os.path.basename(annot_file).split('.annot', 1)[0] + '.vtk')

    rewrite_scalars(vtk_file, output_vtk, labels, 'Labels', [],
                    background_value)

    if not os.path.exists(output_vtk):
        raise IOError("Output VTK file " + output_vtk + " not created.")

    return labels, output_vtk


# def transform_to_volume(vtk_file, points, volume_file, output_volume=''):
#     """
#     Transform vtk coordinates to voxel index coordinates in a target
#     volume by using the header transformation.
#
#     This function assumes that the nibabel-readable volume has LPI orientation.
#
#     Parameters
#     ----------
#     vtk_file : string
#         name of VTK file containing point coordinate data
#     points : list of lists of floats
#         each element is a list of 3-D coordinates of a surface mesh vertex
#     volume_file : string
#         name of target nibabel-readable image volume file
#     output_volume : string
#         name of output nibabel-readable image volume file
#
#     Returns
#     -------
#     output_volume : string
#         name of nifti file containing transformed point data
#
#     Examples
#     --------
#     >>> import os
#     >>> from mindboggle.mio.vtks import transform_to_volume
#     >>> from mindboggle.mio.vtks import read_points
#     >>> from mindboggle.mio.fetch_data import prep_tests
#     >>> urls, fetch_data = prep_tests()
#     >>> vtk_file = fetch_data(urls['left_pial'], '', '.vtk')
#     >>> volume_file = fetch_data(urls['T1_001'], '', '.nii.gz')
#     >>> points  = read_points(vtk_file)
#     >>> output_volume = ''
#     >>> output_volume = transform_to_volume(vtk_file, points, volume_file,
#     ...                                     output_volume) # doctest: +SKIP
#
#     View resulting vtk file (skip test):
#
#     >>> from mindboggle.mio.plots import plot_volumes
#     >>> plot_volumes([output_volume, volume_file]) # doctest: +SKIP
#
#     """
#     import os
#     import numpy as np
#     import nibabel as nb
#
#     from mindboggle.mio.vtks import read_vtk
#
#     # Read vtk file:
#     points, indices, lines, faces, scalars, scalar_names, npoints, \
#             input_vtk = read_vtk(vtk_file)
#
#     # Read target image volume header information:
#     img = nb.load(volume_file)
#     hdr = img.get_header()
#     dims = img.get_shape()
#     ndims = len(dims)
#     affine = img.get_affine()
#     inv_transform = np.linalg.inv(affine)
#
#     # Transform vtk coordinates:
#     points = np.array(points)
#     points = np.concatenate((points, np.ones((npoints,1))), axis=1)
#     voxels = np.transpose(np.dot(inv_transform, np.transpose(points)))[:,0:ndims]
#
#     voxels = np.reshape([int(np.round(x)) for lst in voxels for x in lst],
#                         (-1,ndims))
#     # Write vtk scalar values to voxels:
#     data = np.zeros(dims)
#     if scalars:
#         for ivoxel, ijk in enumerate(voxels):
#             data[ijk[0], ijk[1], ijk[2]] = scalars[ivoxel]
#
#     # Write output image volume:
#     if not output_volume:
#         output_volume = os.path.join(os.getcwd(),
#                                      os.path.basename(vtk_file) +
#                                      '_to_volume.nii.gz')
#
#     img = nb.Nifti1Image(data, affine, header=hdr)
#     img.to_filename(output_volume)
#
#     if not os.path.exists(output_volume):
#         raise IOError(output_volume + " not found")
#
#     return output_volume


# ============================================================================
# Doctests
# ============================================================================
if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)  # py.test --doctest-modules
