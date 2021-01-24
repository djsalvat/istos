from iterhist import * 
from numpy import diag,sqrt
from numpy.random import multivariate_normal
from itertools import count
from matplotlib.pylab import figure,bar,contourf,grid,xlabel,ylabel,show,title
from matplotlib import use
use('TkAgg')

if __name__=='__main__':
    #set of means, covariances,
    #and associated axis information
    #for generating pseudodata and histograms
    mu = [0.0,0.1]
    sigma = [[    1.0*1.0,0.5*1.0*0.1],\
             [0.5*1.0*0.1,    0.1*0.1]]
    bins = (24,20)
    labels = ('X','Y')

    #Make some toy data
    data = multivariate_normal(mu,sigma,10000)

    #make a histogram to bin the data
    ih = IterHist(
                    Axis.regular_bins(m-sqrt(s)*3.0,m+sqrt(s)*3.0,b,label=l) \
                    for (m,s,b,l) in zip(mu,diag(sigma),bins,labels) \
                 )
    #make another histogram to demonstrate histogram arithmetic operations
    ih_other = IterHist(
                         Axis.regular_bins(m-sqrt(s)*3.0,m+sqrt(s)*3.0,b,label=l) \
                         for (m,s,b,l) in zip(mu,diag(sigma),bins,labels) \
                       )

    #fill the histogram
    for d in data:
        ih(d) 
    #set the bin content of the other histogram
    ih_other.counts += ih.counts
    #IterHist's __repr__() in action
    print(ih)
    #ascii bar chart representation
    print(to_ascii(ih))

    #Show how axes can be regrouped
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

    #counter to keep track of figures
    fig_count = count()

    #series of plots demonstrating
    #projection, rebinning, arithmetic,
    #and matplotlib argument generation
    figure(next(fig_count))
    bar(*mpl_bar_args(ih))
    xlabel(ih.axes[0].label,fontsize='x-large')
    ylabel('counts',fontsize='x-large')
    title('example 1-D histogram',fontsize='x-large')
    grid()

    figure(next(fig_count))
    bar(*mpl_bar_args(rebinned(ih,3)))
    xlabel(ih.axes[0].label,fontsize='x-large')
    ylabel('counts',fontsize='x-large')
    title('rebinned histogram',fontsize='x-large')
    grid()

    figure(next(fig_count))
    bar(*mpl_bar_args(ih-ih_other))
    xlabel(ih.axes[0].label,fontsize='x-large')
    ylabel('counts',fontsize='x-large')
    title('zero histogram',fontsize='x-large')
    grid()

    figure(next(fig_count))
    bar(*mpl_bar_args((ih*0.01)/5.0))
    xlabel(ih.axes[0].label,fontsize='x-large')
    ylabel('counts',fontsize='x-large')
    title('scaled histogram',fontsize='x-large')
    grid()

    figure(next(fig_count))
    contourf(*mpl_contour_args(ih))
    xlabel(ih.axes[0].label,fontsize='x-large')
    ylabel(ih.axes[1].label,fontsize='x-large')
    title('2-D histogram',fontsize='x-large')
    grid()

    figure(next(fig_count))
    contourf(*mpl_contour_args(rebinned(ih,5,axis=1)))
    xlabel(ih.axes[0].label,fontsize='x-large')
    ylabel(ih.axes[1].label,fontsize='x-large')
    title('rebinned 2-D histogram',fontsize='x-large')
    grid()
    show()
