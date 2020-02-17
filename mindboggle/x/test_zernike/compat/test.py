import mindboggle.guts
import numpy
import os.path
import scipy.io
import glob
import functools

from . import CompatPipeline

def read_vtk(filename):
    points, indices, lines, faces, depths, scalar_names, npoints, \
        input_vtk = mindboggle.mio.vtks.read_vtk(filename)
    return numpy.array(points), numpy.array(faces)

head,tail = os.path.split(__file__)
DATA_DIR = os.path.join(head,'test_data')
ALLOWED_ERROR = 1e-8

FNS_AND_ARGS = [ #('D_CV_orig',              ('facet','num_vertices','N','X','K','tri_matrix',), ('C','Vol',) ),
                 #('trinomial',              ('i','j','k',),                                     ('t',) ),
                 #('trinomial_matrix',       ('N',),                                             ('tri_matrix',) ),
                 #('mon_comb',               ('tri_matrix','vertex','N',),                       ('c',) ),
                 #('D_SG_orig_part',         ('num_facets','i','j','k','C','D','S','Vol','F',),  ('S',) ),
                 #('D_SG_orig',              ('num_facets','i','N','C','D','Vol','F',),          ('G',) ),
                 ('Dabc_orig',              ('C','N',),                                         ('D',) ), #slow
                 #('factorial_precalc',      ('N',),                                             ('F',) ),
                 #('Yljm',                   ('l','j','m',),                                     ('y',) ),
                 #('Qklnu',                  ('k','l','nu',),                                    ('q',) ),
                 #('zernike',                ('G','N',),                                         ('Z',) ),
                 #('feature_extraction',     ('Z','N',),                                         ('Descriptors',) ),
                 #('geometric_moments_orig', ('X','K','N','num_facets','num_vertices',),         ('G',) ), #slow
                 #('demo',                   ('V','F','ZMvtk'),                                   ('Descriptors',) ),
                 #('reformat_zernike',      ('Z','N',),                                         ('ZM,') ),
                 ]

def test() :
    pl = CompatPipeline()
    for fnname, inargs, outargs in FNS_AND_ARGS :
        globname = '{}-*.mat'.format(fnname)
        fn = getattr(pl,fnname)
        files = sorted( glob.glob( os.path.join(DATA_DIR,globname) ) )
        if len(files) == 0 : raise Exception(globname)
        for filename in files :
            p = functools.partial(run, fn, filename, inargs, outargs)
            p.description = filename
            yield (p, )

def run(fn,filename,inarg_names,outarg_names) :
    matfile = scipy.io.loadmat( filename,squeeze_me=True )
    inargs = tuple([ matfile[a] for a in inarg_names ])
    outargs = tuple([ matfile[a] for a in outarg_names ])
    new_outargs = fn(*inargs)
    if not isinstance(new_outargs,tuple) : new_outargs = tuple([new_outargs])
    for n,a,aa in zip(outarg_names, outargs, new_outargs) :
        if isinstance(a,numpy.ndarray) and isinstance(aa,numpy.ndarray) : assert a.shape == aa.shape, 'Output {}: {} != {}'.format(n,a.shape,aa.shape)
        err_max = numpy.max( numpy.abs( a-aa ) )
        assert err_max < ALLOWED_ERROR, 'Output {}: Error ({}) > ALLOWED_ERROR ({})'.format(n,err_max, ALLOWED_ERROR)
        #assert a.dtype == aa.dtype, '{} != {}'.format(a.dtype,aa.dtype)



'''
def test__geometric_moments() :
    matfile = scipy.io.loadmat( os.path.join(DATA_DIR,'geometric_moments_orig-0.mat') )
    X,K,N,num_facets,num_vertices = matfile['X'], matfile['K'], matfile['N'], matfile['num_facets'], matfile['num_vertices']
    pl = CompatPipeline()
    X,K = pl.array(X), pl.array(K)
    GG = pl.geometric_moments_orig(X,K,N,num_facets,num_vertices)

def test__Dabc_orig() :
    for filename in glob.glob( os.path.join(DATA_DIR,'Dabc_orig-*.mat' ) ) : yield run__Dabc_orig, filename

def run__Dabc_orig(filename) :
    matfile = scipy.io.loadmat( filename )
    C,N,D = matfile['C'], matfile['N'], matfile['D']
    pl = CompatPipeline()
    DD = pl.Dabc_orig(C,N)
    assert DD.dtype == D.dtype, 'dtype'
    assert DD.shape == D.shape, 'shape'
    assert numpy.max( numpy.abs( D-DD ) ) < ALLOWED_ERROR, 

def test__mon_comb() :
    for filename in glob.glob( os.path.join(DATA_DIR,'mon_comb-*.mat' ) ) : yield run__mon_comb, filename
'''
