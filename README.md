# IterHist

## Introduction

IterHist provides a histogram object with some of the
functionality of `ROOT`'s `TH*` objects. An IterHist instance
is a callable object, providing effectively the behavior of
the `TH*->Fill()` method.

IterHists can be of arbitrary dimension `N`. Counts are stored
in an `N`-dimensional numpy array. IterHist provides basic
arithmetic operator overloading, utilities to generate
axes, and projection and rebinning utilities similar to `ROOT`.
Further, it provides utilities to generate arguments needed
by matplotlib's `bar()`, `errorbar()`, and `contour()` functions for plotting.

An IterHist object consists of an immutable set of `N` `Axis`
objects. Each `Axis` consists of a collection of `Bin` objects
and optional axis `label`. Each `Bin` has a lower and upper edge.
Bins can be arbitrarily defined, as long as they are in ascending
order, non-empty, and non-overlapping.

As an example, we can define a one-dimensional histogram
with four arbitrary bins:
```python
import iterhist as IH
from itertools import repeat
lo_edges = [0.0,1.5,3.5,10.0]
hi_edges = [1.5,3.5,10.0,30.0]

ih = IH.IterHist((IH.Axis([IH.Bin(l,h) for l,h in zip(lo_edges,hi_edges)],\
     label='example axis'),))
```

In this example, the bins are adjacent (a bin's high edge corresponds
to the next's low edge), but this not need be the case.
We can generate evenly-spaced bins via
```python
ih_even = IH.IterHist((IH.Axis.regular_bins(0.0,10.0,5,label='five evenly-spaced bins'),))
```

If we define a multi-dimensional histogram, we can project axes to generate
lower dimensional histograms
```python
my_axes = repeat(IH.Axis.regular_bins(-1.0,1.0,10),3)
ih3 = IH.IterHist(my_axes)
#project to 1-D histogram about the second axis (viz. axis 1)
ih_proj = IH.projected(ih3,(1,))
```

## Plotting

The module provides a few functions which return the data from an `iterhist` object
in the proper format for some of `matplotlib.pyplot`'s functions.
For example, we can plot a 2-D histogram using `contour()` or `pcolor()`:
```python
from matplotlib.pyplot import figure,pcolor,show
figure()
pcolor(*IH.mpl_contour_args(h2))
show()
```
There are similar functions for use with `bar()` and `errorbar()`.

## Errors

An `IterHist` object contains an optional `errors` data member,
which is a bin-by-bin uncertainty also stored as a `numpy` array.
These uncertainties are scaled and propagated appropriately
when an `IterHist` object's overloaded arithmetic operators are employed.
The functionality is limited, and for now only handles root-N
Poisson-like statistical uncertainties for each bin.
This behavior can be overridden by accessing an `IterHist` object's
`counts` and `errors` members directly.
