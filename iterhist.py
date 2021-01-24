from itertools import dropwhile
from collections.abc import Iterable
import numpy

iterhist_rc = {
                'ascii_width' : 40,
              }

class IterHistException(Exception):
    pass

class Bin:
    def __init__(self,lo,hi):
        self.__dict__.update({k:v for k,v in locals().items() if k!='self'})
    def __contains__(self,v):
        return self.lo <= v < self.hi
    def __eq__(self,other):
        return self.lo == other.lo and self.hi == other.hi

class Axis:
    def __init__(self,bins,label=''):
        if any(
                 [
                     b1.lo>=b1.hi or b1.hi>b2.lo \
                     for b1,b2 in zip(bins[:-1],bins[1:])
                 ]
                +[bins[-1].lo >= bins[-1].hi]
              ):
            raise IterHistException('bins must be ordered, non-empty, and non-overlapping')
        self.__dict__.update({k:v for k,v in locals().items() if k!='self'})

    def __contains__(self,v):
        return self.bins[0].lo <= v < self.bins[-1].hi

    def __eq__(self,other):
        return all([s==o for s,o in zip(self.bins,other.bins)])

    @staticmethod
    def regular_bins(lo,hi,N,label=''):
        width = (hi-lo)/float(N)
        return Axis([Bin(lo+j*width,lo+(j+1)*width) for j in range(N)],label=label)

    @staticmethod
    def regrouped(axis,grouping):
        if len(axis.bins)%grouping != 0:
            raise IterHistException('Number of axis bins must be divisible by grouping')
        return Axis([Bin(b1.lo,b2.hi) \
               for b1,b2 in zip(axis.bins[::grouping],axis.bins[grouping-1::grouping])],
               label=axis.label)

class IterHist:
    def __init__(self,axes):
        self.axes = tuple(axes)
        self.counts = numpy.zeros(tuple(len(axis.bins) for axis in self.axes))
        self.dimension = len(self.axes)

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

def projected(ih,axes):
    ih_new = IterHist(a for j,a in enumerate(ih.axes) if j in axes)
    sum_axes = tuple(set(range(ih.dimension)) - set(axes))
    ih_new.counts += numpy.sum(ih.counts,axis=sum_axes)
    return ih_new

def rebinned(ih,grouping,axis=0):
    new_axes = list(ih.axes)
    new_axes[axis] = Axis.regrouped(ih.axes[axis],grouping)
    ih_new = IterHist(new_axes)
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
    if h.dimension!=1:
        h = projected(h,(0,))
    x = [0.5*(b.lo+b.hi) for b in h.axes[0].bins]
    y = h.counts
    w = [b.hi-b.lo for b in h.axes[0].bins]
    return x,y,w

def mpl_contour_args(h):
    if h.dimension<2:
        raise IterHistException('Histogram must be at least two-dimensional')
    elif h.dimension>2:
        h = projected(h,(0,1))
    x = [0.5*(b.lo+b.hi) for b in h.axes[0].bins]
    y = [0.5*(b.lo+b.hi) for b in h.axes[1].bins]
    z = h.counts.transpose()
    return x,y,z

def to_ascii(h):
    if h.dimension!=1:
        h = projected(h,(0,))
    max_val = max(h.counts)
    return('\n'.join(['\t{:+.2f}\t{:+.2f}\t{}'.format(b.lo,b.hi,'#'*(int(c*iterhist_rc['ascii_width']/max_val))) \
            for b,c in zip(h.axes[0].bins,h.counts)]))
