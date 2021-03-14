from itertools import dropwhile
import numpy

#For customization
iterhist_rc = {
                'ascii_width' : 40,
              }

errors_options = [None,'poisson','added','subtracted','scaled']

class IstosException(Exception):
    '''Generic module exception class.'''
    pass

class Bin:
    '''A bin has a lower and upper edge, and a notion of whether a value
    is within the (lower,upper) interval.'''
    def __init__(self,lo,hi):
        self.__dict__.update({k:v for k,v in locals().items() if k!='self'})
    def __contains__(self,v):
        return self.lo <= v < self.hi
    def __eq__(self,other):
        return self.lo == other.lo and self.hi == other.hi

class Axis:
    '''Axes have a list of Bin objects and an optional label.
    Axes can be regrouped, as long as the number of bins is divisible by regrouping size.
    This regrouping is used by the Histogram rebinned routine.'''
    def __init__(self,bins,label=''):
        if any(
                 [
                     b1.lo>=b1.hi or b1.hi>b2.lo \
                     for b1,b2 in zip(bins[:-1],bins[1:])
                 ]
                +[bins[-1].lo >= bins[-1].hi]
              ):
            raise IstosException('bins must be ordered, non-empty, and non-overlapping')
        self.__dict__.update({k:v for k,v in locals().items() if k!='self'})

    def __contains__(self,v):
        return self.bins[0].lo <= v < self.bins[-1].hi

    def __eq__(self,other):
        return all([s==o for s,o in zip(self.bins,other.bins)])

    @staticmethod
    def regular_bins(lo,hi,N,label=''):
        '''Returns an axis with N evenly spaced bins over the given range.'''
        width = (hi-lo)/float(N)
        return Axis([Bin(lo+j*width,lo+(j+1)*width) for j in range(N)],label=label)

    @staticmethod
    def regrouped(axis,grouping):
        '''Returns an axis with "grouping" number of bins combined. Used by Histogram.rebinned.'''
        if len(axis.bins)%grouping != 0:
            raise IstosException('Number of axis bins must be divisible by grouping')
        return Axis([Bin(b1.lo,b2.hi) \
               for b1,b2 in zip(axis.bins[::grouping],axis.bins[grouping-1::grouping])],
               label=axis.label)

class Histogram:
    '''A Histogram is a tuple of axes, and a numpy array with shape
    (B1,B2,...) where B1 is the number of bins in the first axis,
    B2 in the second axis, and so on.'''
    def __init__(self,axes,error_type=None):
        self.axes = tuple(axes)
        self.counts = numpy.zeros(tuple(len(axis.bins) for axis in self.axes))
        self.dimension = len(self.axes)
        if error_type not in errors_options:
            raise IstosException('Error type must be one of {}'.format(errors_options))
        self.error_type = error_type
        if error_type=='poisson':
            self.errors = numpy.zeros(tuple(len(axis.bins) for axis in self.axes))

    def set_counts(self,A):
        self.counts = A
        if self.error_type=='poisson':
            self.errors = numpy.sqrt(A)

    def set_errors(self,E):
        self.errors = E

    @staticmethod
    def histogramdd(A,axes,error_type=None,**kwargs):
        '''Instead of calling the Histogram object to fill the histogram,
        provide an array of all of the values to be inserted
        and use numpy.histogramdd to fill the bins.'''
        if A.shape[1] != len(axes):
            raise IstosException('number of axes must match input data dimension') 
        freq, edges = numpy.histogramdd(
                                        A,
                                        bins=tuple(len(axis.bins) for axis in axes),
                                        range=[(axis.bins[0].lo,axis.bins[-1].hi) for axis in axes],
                                        **kwargs
                                       )
        H = Histogram(axes,error_type=error_type)
        H.set_counts(freq)

        return H

    def __call__(self,val,weight=1.0):
        try:
            indices = tuple(
                          j for j,eb in \
                          [
                              next(dropwhile(lambda b : v_ not in b[1],enumerate(axis.bins))) \
                              for v_,axis in zip(val,self.axes)
                          ]
                      )
            self.counts[indices]+=weight 
        except (RuntimeError,StopIteration):
            pass

    def __repr__(self):
        print('{} lo\t{} hi\tcounts'.format(self.axes[0].label,self.axes[0].label))
        if self.dimension==1:
            return('\n'.join(['{:+.2f}\t{:+.2f}\t{:+.2f}'.format(b.lo,b.hi,c) \
                   for b,c in zip(self.axes[0].bins,self.counts)]))
        else:
            h1 = projected(self,(0,))
            return('\n'.join(['{:+.2f}\t{:+.2f}\t{:+.2f}'.format(b.lo,b.hi,c) \
                   for b,c in zip(h1.axes[0].bins,h1.counts)]))

    def __add__(self,other):
        if not all([a1==a2 for a1,a2 in zip(self.axes,other.axes)]):
            raise IstosException('cannot add histograms with unequal axes')
        h_new = Histogram(self.axes)
        h_new.counts = self.counts + other.counts
        if self.error_type!=None and other.error_type!=None:
            h_new.errors = numpy.sqrt(self.errors**2.0+other.errors**2.0)
            h_new.error_type = 'added'
        return h_new

    def __sub__(self,other):
        if not all([a1==a2 for a1,a2 in zip(self.axes,other.axes)]):
            raise IstosException('cannot add histograms with unequal axes')
        h_new = Histogram(self.axes)
        h_new.counts = self.counts - other.counts
        if self.error_type!=None and other.error_type!=None:
            h_new.errors = numpy.sqrt(self.errors**2.0+other.errors**2.0)
            h_new.error_type = 'subtracted'
        return h_new

    def __mul__(self,c):
        h_new = Histogram(self.axes)
        h_new.counts = self.counts*c
        if self.error_type!=None:
            h_new.errors = self.errors*c
            h_new.error_type = 'scaled'
        return h_new

    def __truediv__(self,c):
        h_new = Histogram(self.axes)
        h_new.counts = self.counts/c
        if self.error_type!=None:
            h_new.errors = self.errors/c
            h_new.error_type = 'scaled'
        return h_new

def projected(ih,axes):
    '''Sum over the tuple of axes provided, reducing the dimension of the histogram.'''
    ih_new = Histogram(a for j,a in enumerate(ih.axes) if j in axes)
    sum_axes = tuple(set(range(ih.dimension)) - set(axes))
    ih_new.counts += numpy.sum(ih.counts,axis=sum_axes)
    if ih.error_type!=None:
        ih_new.errors = numpy.sqrt(numpy.sum(ih.errors**2.0,axis=sum_axes))
    return ih_new

def rebinned(ih,grouping,axis=0):
    '''Rebin histogram by combining "grouping" number of bins along the given axis.'''
    new_axes = list(ih.axes)
    new_axes[axis] = Axis.regrouped(ih.axes[axis],grouping)
    ih_new = Histogram(new_axes)
    for k in range(len(new_axes[axis].bins)):
        c_slice = ih.counts[
                            tuple(
                             slice(None) if j!=axis else slice(k*grouping,(k+1)*grouping) \
                             for j in range(ih.dimension)
                            )
                           ]
        ih_new.counts[tuple(k if j==axis else slice(None) for j in range(ih.dimension))] = c_slice.sum(axis=axis)
    return ih_new

def mpl_bar_args(h):
    '''Return abcissa and ordinate values, along with bin widths,
    required by matplotlib's bar() plotting function.'''
    if h.dimension!=1:
        h = projected(h,(0,))
    x = [0.5*(b.lo+b.hi) for b in h.axes[0].bins]
    y = h.counts
    w = [b.hi-b.lo for b in h.axes[0].bins]
    return x,y,w

def mpl_errorbar_args(h):
    '''Return abcissa and ordinate values,
    along with bin widths and errors,
    required by matplotlib's errorbar() plotting function.'''
    if h.dimension!=1:
        h = projected(h,(0,))
    x = [0.5*(b.lo+b.hi) for b in h.axes[0].bins]
    y = h.counts
    w = [(b.hi-b.lo)*0.5 for b in h.axes[0].bins]
    s = h.errors
    return x,y,s,w

def mpl_contour_args(h):
    '''Return abcissa, ordinate, and number of counts
    required by matplotlib's contour() and contourf() plotting functions.'''
    if h.dimension<2:
        raise IstosException('Histogram must be at least two-dimensional')
    elif h.dimension>2:
        h = projected(h,(0,1))
    x = [0.5*(b.lo+b.hi) for b in h.axes[0].bins]
    y = [0.5*(b.lo+b.hi) for b in h.axes[1].bins]
    z = h.counts.transpose()
    return x,y,z

def to_ascii(h):
    '''Print a bar chart in ascii.'''
    if h.dimension!=1:
        h = projected(h,(0,))
    max_val = max(h.counts)
    return('\n'.join(['\t{:+.2f}\t{:+.2f}\t{}'.format(b.lo,b.hi,'#'*(int(c*iterhist_rc['ascii_width']/max_val))) \
            for b,c in zip(h.axes[0].bins,h.counts)]))

if __name__=='__main__':
    import argparse
    import sys
    mainparser = argparse.ArgumentParser(prog='iterhist',description='A pythonic histogram object.')
    mainparser.add_argument('--version', action='version', version='The current version is 0.1.')
    mainparser.add_argument('lo',type=float,nargs=1,help='lower histogram boundary')
    mainparser.add_argument('hi',type=float,nargs=1,help='upper histogram boundary')
    mainparser.add_argument('N',type=int,nargs=1,help='number of bins')
    mainparser.add_argument('infile',type=argparse.FileType('r'),nargs='?',default=sys.stdin,help='number of bins')
    args = mainparser.parse_args()
    LO = args.lo[0]
    HI = args.hi[0]
    N = args.N[0]

    ih = Histogram((Axis.regular_bins(LO,HI,N),))
    for l in args.infile.readlines():
        ih((float(l.strip()),))
    print(to_ascii(ih))
