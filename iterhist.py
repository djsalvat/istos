from itertools import dropwhile
import numpy

class _Bin:
    def __init__(self,lo,hi):
        self.__dict__.update({k:v for k,v in locals().items() if k!='self'})
    def __contains__(self,v):
        return self.lo <= v < self.hi

class IterHist:
    def __init__(self,bin_lists):
        for bin_list in bin_lists:
            #check adjacent bin edges
            if any(
                     [
                         lo1>=hi1 or hi1>lo2 \
                         for (lo1,hi1),(lo2,hi2) in zip(bin_list[:-1],bin_list[1:])
                     ]
                    +[bin_list[-1][0] >= bin_list[-1][1]]
                  ):
                raise Exception('bins must be ordered, non-empty, and non-overlapping')
        self.bin_lists = tuple([_Bin(l,h) for l,h in bin_list] for bin_list in bin_lists)
        self.counts = numpy.zeros(tuple(len(bin_list) for bin_list in self.bin_lists))

    def __call__(self,val,weight=1.0):
        try:
            indices = tuple(
                          j for j,eb in \
                          [
                              next(dropwhile(lambda b : v_ not in b[1],enumerate(bin_list))) \
                              for v_,bin_list in zip(val,self.bin_lists)
                          ]
                      )
            self.counts[indices]+=weight 
        except (RuntimeError,StopIteration):
            pass

    def __repr__(self):
        if len(self.bin_lists)==1:
            return('\n'.join(['{}\t{}\t{}'.format(b.lo,b.hi,c) for b,c in zip(self.bin_lists[0],self.counts)]))
        else:
            h1 = project(self,(0,))
            return('\n'.join(['{}\t{}\t{}'.format(b.lo,b.hi,c) for b,c in zip(h1.bin_lists[0],h1.counts)]))

def project(ih,axes):
    ih_new = IterHist(
                      tuple(
                        [(b.lo,b.hi) for b in bl] \
                        for j,bl in enumerate(ih.bin_lists) \
                        if j in axes
                      )
                     )
    sum_axes = tuple(set(range(len(ih.bin_lists))) - set(axes))
    ih_new.counts += numpy.sum(ih.counts,axis=sum_axes)
    return ih_new

def regular_bins(lo,hi,N):
    width = (hi-lo)/float(N)
    return [(lo+j*width,lo+(j+1)*width) for j in range(N)]

def mpl_bar_args(h):
    if len(h.bin_lists)!=1:
        h = project(h,(0,))
    x = [0.5*(b.lo+b.hi) for b in h.bin_lists[0]]
    y = h.counts
    w = [b.hi-b.lo for b in h.bin_lists[0]]
    return x,y,w

def mpl_contour_args(h):
    if len(h.bin_lists)<2:
        raise Exception('Histogram must be at least two-dimensional')
    if len(h.bin_lists)>2:
        h = project(h,(0,1))
    x = [0.5*(b.lo+b.hi) for b in h.bin_lists[0]]
    y = [0.5*(b.lo+b.hi) for b in h.bin_lists[1]]
    z = h.counts.transpose()
    return x,y,z
