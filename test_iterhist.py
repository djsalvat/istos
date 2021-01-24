from iterhist import * 
from numpy import diag,sqrt
from numpy.random import multivariate_normal
from matplotlib.pylab import figure,bar,contourf,grid,xlabel,ylabel,show
from matplotlib import use
use('TkAgg')

mu = [0.0,0.1]

sigma = [[    1.0*1.0,0.5*1.0*0.1],\
         [0.5*1.0*0.1,    0.1*0.1]]

bins = (24,20)

labels = ('X','Y')

if __name__=='__main__':
    #Make some toy data
    data = multivariate_normal(mu,sigma,10000)

    ih = IterHist(
                    Axis.regular_bins(m-sqrt(s)*3.0,m+sqrt(s)*3.0,b,label=l) \
                    for (m,s,b,l) in zip(mu,diag(sigma),bins,labels) \
                 )


    for d in data:
        ih(d) 

    print(ih)

    print(to_ascii(ih))

    a = Axis.regular_bins(0.0,30.0,24,label='to be rebinned')
    for b in a.bins:
        print('{},{}'.format(b.lo,b.hi))
    print(a.label)
    a_ = Axis.regrouped(a,6)
    for b in a_.bins:
        print('{},{}'.format(b.lo,b.hi))
    print(a_.label)
    try:
        a_ = Axis.regrouped(a,5)
    except IterHistException as e:
        print(e)

    figure(1)
    bar(*mpl_bar_args(ih))
    grid()

    figure(2)
    bar(*mpl_bar_args(rebinned(ih,3)))
    grid()

    figure(3)
    contourf(*mpl_contour_args(ih))
    grid()

    figure(4)
    contourf(*mpl_contour_args(rebinned(ih,5,axis=1)))
    grid()
    show()
