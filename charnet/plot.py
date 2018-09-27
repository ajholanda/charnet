import os.path
import functools

import matplotlib.pyplot as plt
import matplotlib.pylab as pylab

import scipy.stats as ss
import scipy.special as sz
from numpy import argmax

from scipy.stats import pearsonr
import sys

# LOCAL
sys.path.append('./plfit/')
import plfit

from books import *
from graphs import *

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

params = {'axes.labelsize': 'small',
          'axes.titlesize':'large',
          'xtick.labelsize':'x-small',
          'ytick.labelsize':'x-small',
          'legend.fontsize':'x-small'}
pylab.rcParams.update(params)

marker_style = dict(marker='.', linestyle='', markersize=3)

def get_empty_xy_arrays():
        return ([], [])

class MultiPlots():
        def __init__(self, nrows=1, ncols=1, hspace=.1, wspace=.1):
                self.fig, self.axes = plt.subplots(nrows=nrows, ncols=ncols)
                self.fig.subplots_adjust(hspace, wspace)
                self.nrows = nrows
                self.ncols = ncols
                self.hspace = hspace
                self.wspace = wspace

        def get_xy_coords(self, c):
                return (c % self.nrows, c % self.ncols)

        def set_axislog(self, i, j, which):
                ok = False
                if which == 'x' or which == 'xy':
                        self.axes[i, j].set_xscale('log')
                        ok = True
                if which == 'y' or which == 'xy':
                        self.axes[i, j].set_yscale('log')
                        ok = True

                if not ok:
                        logger.error('Wrong label for axes: \"{}\"'.format(which))
                        exit()
                
        def set_lims(self, i, j, which_axe, inf=0.0, sup=1.0):
                '''
                Set the inferior and superior limits for plot according 
                to axe.
                '''
                if which_axe == 'x':
                        self.axes[i, j].set_xlim(inf, sup)
                elif which_axe == 'y':
                        self.axes[i, j].set_ylim(inf, sup)
                else:
                        logger.error('Unknown axe {}' % which_axe)
                        exit()

        def print_legend(self, i, j, fontsize=4, location='upper right'):
                self.axes[i, j].legend(fontsize=5, loc=location)

        def print_axis(self, i, j, label, which, fontsize=6):
                if which is 'x':
                        if i == self.nrows-1:
                                self.axes[i, j].set_xlabel(label, fontsize=fontsize)
                elif which is 'y':
                        if j == 0:
                                self.axes[i, j].set_ylabel(label, fontsize=fontsize)
                else:
                        logger.error('* Axes {} is not defined' % which)
                        exit()

        def fill(self, i, j, subtitle, xs, ys, xlabel, ylabel, color='black', loglog=True):
                self.axes[i, j].set_title(subtitle, fontsize=8)
                if loglog:
                        self.is_loglog=True
                        self.set_axislog(i, j, 'xy')

                self.axes[i, j].plot(xs, ys,
                                     c = color,
			             alpha=.6,
                                     **marker_style)
                self.axes[i, j].grid(True)
                self.axes[i, j].text(0.5, 1.1, '' ,
                                     style='italic',
                                     horizontalalignment='center',
                                     verticalalignment='center',
                                     color='gray',
                                     transform=self.axes[i, j].transAxes)

                #self.set_lims(i, j, 'y')
                self.print_axis(i, j, xlabel, 'x')
                self.print_axis(i, j, 'Lobby', 'y')

        def plot_CDF(self, i, j, datax, book, **kwargs):
                pl = plfit.plfit(np.array(datax), usefortran=False, verbose=True, quiet=False)
                a = pl._alpha
                a_str = '{0:.2f}'.format(round(a,2))
                xmin = pl._xmin

                # Empirical data, inverse CDF
                vals, base = np.histogram(datax, bins=len(np.unique(datax)))
                vals = vals/float(len(datax)) # nomalize frequncy in hist.

                csum = np.cumsum(vals) # accumulate the probability
                ys = np.insert(csum, 0, 0.0) # add 0.0 at front
                
                xs = np.unique(datax)
                ys = 1 - ys[:len(ys)-1] # invert the distribution

                # Theoretical line
                cf = np.power(xs[xs>=xmin], -a)/(sz.zeta(a) - np.power(np.sum(np.arange(1,xmin)), -a))
                cf = np.cumsum(cf)
                cf = np.insert(cf, 0, 0.0)
                cf = 1 - cf[:len(cf)-1] # invert the probs
                print(xmin, '\t\t', cf)
                ci, = np.where(xs == xmin)
                ci = ci[0]
                cf = cf * ys[ci] # normalize

                print('\n\nys=', ys,'\n\n')
                print(book.get_name(), '\n\ny=',  ys[ci],' cf=', cf, 'xs[xmin-1:]', xs[ci:], '\n\n')
                
                self.axes[i, j].plot(xs, ys, '.', label=book.get_name(), color=Plot.get_color(book), **marker_style, **kwargs)
                self.axes[i, j].plot(xs[ci:], cf, '--', color='gray', label=r'$x^{1-\alpha}, \alpha=' + a_str + '$')
                
                self.print_legend(i, j)
                self.set_axislog(i, j, 'xy')
                
                self.print_axis(i, j, 'k', 'x')
                self.print_axis(i, j, 'CDF', 'y')

                # Write CDF data to a file to debug
                lns = []
                fn = book.get_name() + '-CDF.csv'
                fn = os.path.join(Project.get_outdir(), fn)
                f = open(fn, 'w')
                for k in range(len(xs)):
                        lns.append(str(xs[k]) + ',')
                        lns.append('{0:.5f}'.format(ys[k]) + '\n')
                f.writelines(lns)
                f.close()
                logger.info('* Wrote {}'.format(fn))
                
        def finalize(self, fn=os.path.join(Project.get_outdir(), 'plot.pdf')):
                self.fig.subplots_adjust(hspace=0)
                plt.tight_layout()
                plt.savefig(fn)
                plt.close()
                logger.info('* Wrote plot %s', fn)

class Plot:
        markers = ['+', '^', 'v', 'o', 'p', 's', '.', '*', 'd']
        
        @staticmethod
        def get_color(book):
                if (book.get_category() == BookCategory.FICTION):
                        return 'red'
                elif (book.get_category() == BookCategory.BIOGRAPHY):
                        return 'blue'
                elif (book.get_category() == BookCategory.LEGENDARY):
                        return 'green'
                else:
                        logger.error('* Non categorized book ', book.get_name())
                        exit()

        @staticmethod
        def do_density_versus_clustering_coefficient():
                fn = os.path.join(Project.get_outdir(), 'Figure-Density_versus_CC.pdf')
                
                nms = 0 # counter for markers
                books = Books.get_books()
                for k in range(len(books)):
                        G = books[k].get_graph()

                        x = nx.density(G)
                        y = nx.average_clustering(G)

                        marker_style = dict(linestyle='', color=Plot.get_color(books[k]), markersize=6)
                        plt.plot(x, y, marker=Plot.markers[nms % len(Plot.markers)],
                                 label=books[k].get_raw_book_label(),
                                 **marker_style)

                        nms += 1 # increment no. of markers counter

                plt.ylim(0.0,1,0)
                plt.xlabel('Density')
                plt.ylabel('Clustering coefficient')
                plt.title('')
                plt.legend(fontsize=7, loc='center right')
                plt.savefig(fn)

                logger.info('* Wrote %s', fn)

        @staticmethod
        def do_degree_distrib():
                '''Plot degree distribution for books with curve fitting made by
                plfit.
                '''
                fn = os.path.join(Project.get_outdir(), 'Figure-Degree_Distrib.pdf')
                mplots = MultiPlots(4, 3)

                books = Books.get_books()
                for k in range(len(books)):
                        (i ,j) = mplots.get_xy_coords(k)
                        G = books[k].get_graph()
                        degs = []
                        
                        # get the degrees
                        for n in G.nodes():
                                deg = G.degree(n)
                                if deg > 0: degs.append(deg)

                        mplots.plot_CDF(i, j, degs, books[k])

                mplots.finalize(fn)
                        
        @staticmethod
        def do_centralities():
                """
                Centralities Lobby index centrality is calculated using function
                defined in lobby.py.  Degree, betweenness and closeness centralities
                are calculated using NetworkX. All measures are normalized.
                """
                offset_fig_nr = 1 # figure number starts after 1
                
                for centr_name in Graphs.get_centrality_names():
                        fn = 'Figure-' + centr_name + '.pdf'
                        fn = os.path.join(Project.get_outdir(), fn)
                        
                        mplots = MultiPlots(4, 3)
                        
                        books = Books.get_books()
                        for k in range(len(books)):
                                (i, j) = mplots.get_xy_coords(k)
                                (xs, ys) = get_empty_xy_arrays()
                                centrs = []
                                
                                G = books[k].get_graph()
                                centrs = Graphs.get_centrality_values(G, centr_name)
                                Graphs.get_centrality_values(G, 'Lobby')
                                for u in G.nodes():
                                        xs.append(centrs[u])
                                        ys.append(G.node[u]['Lobby'])

                                # Calculate Pearson correlation and concatenate to graphic title
                                (r_row, p_value) = pearsonr(xs, ys)
                                title = books[k].get_name() + ' ($r=$'+'${0:.2f}'.format(r_row) +'$)'

                                mplots.fill(i, j, title, xs, ys, centr_name, 'Lobby', Plot.get_color(books[k]))

                        mplots.finalize(fn)
                                
        @staticmethod
        def do_assortativity():
                """Assortativity mixing is calculated and plotted versus average degree.
                """
                fn = os.path.join(Project.get_outdir(), 'Figure-Assortativity.pdf')
                xticklabels = np.arange(0, 1.1, 0.1)
                yticklabels = xticklabels

                mplots = MultiPlots(4, 3)
                axes = mplots.axes
                
                books = Books.get_books()
                for k in range(len(books)):
                        (i, j) = mplots.get_xy_coords(k)
                        G = books[k].get_graph()
                        # xs (vertices), ys (degree of neighbors of xs), xs, ys_avg (avg degree of neighbors of xs)
                        (xs, ys, xxs, yavgs) = Graphs.get_degree_avg_neighbors(G)

                        axes[i, j].plot(xxs, yavgs, '--', label='avg', color='gray', linewidth=1)
                        axes[i, j].plot(xs, ys, '.', color=Plot.get_color(books[k]), label=books[k].get_name(), **marker_style)
                        axes[i, j].set_xlim(xticklabels[0], xticklabels[len(xticklabels)-1])
                        axes[i, j].set_ylim(yticklabels[0], yticklabels[len(yticklabels)-1])
                        
                        mplots.print_axis(i, j, '$k/k_{max}$', 'x')
                        mplots.print_axis(i, j, '$knn/knn_{max}$', 'y')
                        mplots.print_legend(i, j)
                        
                mplots.finalize(fn)

        @staticmethod
        def do():
                Plot.do_degree_distrib()
                Plot.do_density_versus_clustering_coefficient()
                Plot.do_centralities()
                Plot.do_assortativity()
