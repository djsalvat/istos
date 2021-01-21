from iterhist import IterHist,mpl_bar_args,mpl_contour_args,regular_bins,project
from numpy import diag,sqrt
from numpy.random import multivariate_normal
from matplotlib.pylab import figure,bar,contourf,grid,xlabel,ylabel,show
from matplotlib import use
use('WebAgg')

mu = [0.0,0.1]

sigma = [[1.0*1.0,1.0*0.1],\
         [1.0*0.1,0.1*0.1]]

bins = (15,20)

if __name__=='__main__':
    #Make some toy data
    data = multivariate_normal(mu,sigma,1500)

    ih = IterHist(
                  tuple(
                    regular_bins(m-sqrt(s)*3.0,m+sqrt(s)*3.0,b) \
                    for (m,s,b) in zip(mu,diag(sigma),bins) \
                  )     
                 )


    for d in data:
        ih(d) 

    figure(1)
    bar(*mpl_bar_args(ih))
    grid()

    figure(2)
    contourf(*mpl_contour_args(ih))
    grid()
    show()
