from itertools import dropwhile
from collections import OrderedDict

class _Bin:
    def __init__(self,lo,hi):
        self.__dict__.update({k:v for k,v in locals().items() if k!='self'})
    def __contains__(self,v):
        return self.lo <= v < self.hi

class IterHist:
    def __init__(self,bin_list):
        bins = [_Bin(l,h) for l,h in bin_list]
        for b0,b1 in zip(bins[:-1],bins[1:]):
            if b0.lo >= b0.hi \
            or b1.lo >= b1.hi \
            or b0.hi  > b1.lo:
                raise Exception('bins must be ordered,non-empty and non-overlapping')
        self.bin_dict = OrderedDict((bin,0.0) for bin in bins)

    def __call__(self,val,weight=1.0):
        try:
            bin = next(dropwhile(lambda b : val not in b,self.bin_dict.keys()))
            self.bin_dict[bin]+=weight 
        except StopIteration:
            pass

    def __repr__(self):
        return '\n'.join(['%f\t%f\t%f'%(b.lo,b.hi,c) for b,c in self.bin_dict.items()])

def mpl_bar_args(h):
    x = list(map(lambda b : 0.5*(b.lo+b.hi),h.bin_dict.keys()))
    y = list(h.bin_dict.values())
    w = list(map(lambda b : b.hi-b.lo,h.bin_dict.keys()))
    return x,y,w
