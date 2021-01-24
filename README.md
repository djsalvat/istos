# IterHist

IterHist provides a histogram object with some of the
functionality of `ROOT`'s `TH*` objects. An IterHist instance
is a callable object, providing effectively the behavior of
ROOT histogram's `->Fill()` method.

IterHists can be of arbitrary dimension `N`. Counts are stored
in an `N`-dimensional numpy array. IterHist provides basic
arithmetic operator overloading, utilities to generate
axes, and projection and rebinning utilities similar to `ROOT`.
Further, it provides utilities to generate arguments needed
by matplotlib's `bar()` and `contour()` functions for plotting.

An IterHist object consists of an immutable set of `N` `Axis`
objects. Each `Axis` consists of a collection of `Bin` objects
and optional axis `label`. Each `Bin` has a lower and upper edge.
Bins can be arbitrarily defined, as long as they are in ascending
order, non-empty, and non-overlapping.

As an example, we can define a one-dimensional histogram
with four arbitrary bins:
```python
import IterHist as IH
from itertools import repeat
lo_edges = [0.0,1.5,3.5,10.0]
hi_edges = [1.5,3.5,10.0,30.0]

ih = IH.IterHist((Axis([Bin(l,h) for l,h in zip(lo_edges,hi_edges)],\
     label='example axis'),))
```

In this example, the bins are adjacent (a bin's high edge corresponds
to the next's low edge), but this not need be the case.
We can generate evenly-spaced bins via
```python
ih_even = IH.IterHist((Axis.regular_bins(0.0,10.0,5,label='five evenly-spaced bins'),))
```

If we define a multi-dimensional histogram, we can project axes to generate
lower dimensional histograms
```python
my_axes = repeat(Axis.regular_bins(-1.0,1.0,10),3)
ih3 = IH.IterHist(my_axes)
#project to 1-D histogram about the second axis (viz. axis 1)
ih_proj = projected(ih3,(1,))
```
