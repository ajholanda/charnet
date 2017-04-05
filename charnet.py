import math
import networkx as nx
import matplotlib.pyplot as plt
import pygraphviz as pgv
from book import *

#The `write_hapax_legomena_table()` function write the _Hapax_
#frequency to be included in the paper using LaTeX syntax for tables.

def write_hapax_legomena_table(books):
	fn = 'hapax.tex'

	f = open(fn, "w")
	f.write("\\begin{tabular}{l|c}\n")
	f.write("\\bf Book & number of {\\it Hapax Legomena} characters/number of characters \\\\\n")
	
	# count the lapaxes for each book
	for book in books:
		nr_hapaxes = book.get_number_hapax_legomenas()
		nr_chars = book.get_number_characters()

                ln = book.name + " & "
                ln += '{0:02d}'.format(nr_hapaxes) + "/"
                ln += '{0:02d}'.format(nr_chars) + " = "
                ln += '{0:.3f}'.format(float(nr_hapaxes)/nr_chars) + " \\\\\n"
                
		f.write(ln)

	f.write("\end{tabular}\n")
	f.close()

# Writing global measures

# Global measures for each character network are written as a table and
# included in a LaTeX file named `global.tex` to be included in the
# manuscript.

# Clustering coefficient is calculated using _NetworkX_ library
# [transitivity](https://networkx.github.io/documentation/networkx-1.10/reference/generated/networkx.algorithms.cluster.transitivity.html#networkx.algorithms.cluster.transitivity)
# routine.  We also calculate
# [density](https://networkx.github.io/documentation/networkx-1.9/reference/generated/networkx.classes.function.density.html)
# and
# [diameter](https://networkx.github.io/documentation/networkx-1.10/reference/generated/networkx.algorithms.distance_measures.diameter.html)
# of the graph.

def write_global_measures(books):
	fn = 'global.tex'

	f = open(fn, "w")

	f.write("\\begin{tabular}{l|c|c|c}\\hline\n")
	f.write("\\bf\\hfil book\\hfil "
                + " & \\bf\\hfil clustering coefficient\hfil"
		+ " & \\bf\\hfil density\\hfil "
               # + " & \\bf\\hfil diameter\\hfil
                +"\\\\ \\hline\n"
        )
	for book in books:
	        book.G.graph['clustering'] = nx.transitivity(book.G)
	        book.G.graph['density'] = nx.density(book.G)
	        #book.G.graph['diameter'] = nx.diameter(book.G)

                ln = book.name + " & "
                ln += '{0:.3f}'.format(book.G.graph['clustering']) + " & "
		ln += '{0:.3f}'.format(book.G.graph['density'])
                        #+ " & " + str(book.G.graph['diameter'])
                ln += "\\\\ \n"
                        
		f.write(ln)
                
	f.write("\\hline\\end{tabular}\n")
	f.close()

# Plotting

## Ranking frequency

# Character appearance frequency is ranked in the y axis. The scale for
# y axis is logarithmic.

def plot_rank_frequency(books, normalize=True):
	fns = ['figure1a.png', 'figure1b.png']
	normalizes = [False, True]

	for k in range(len(fns)):
		fig, ax = plt.subplots()

		for book in books:
			name = book.name
			color = book.color
			marker = book.marker
	    		freqs = {}		
			xs = []
			ys = []
			ys_normalized = []
			max_freq = 0.0

			x = 1
			for character, freq in book.name_freqs.items():
			    	y = int(freq)
			    	xs.append(x)
				ys.append(y)
				x += 1

				if (y > max_freq): 
					max_freq = y 

			ys = sorted(ys, key=int, reverse=True)

			if (normalizes[k]==True):
				# normalize y (frequency)
				for i in range(len(ys)):
					ys[i] = float(ys[i]) / float(max_freq)

			marker_style = dict(linestyle=':', color=color, markersize=6)
			ax.plot(xs, ys, c=color,
			        marker=marker,
			        label=name,
               		        alpha=0.3, 
			        **marker_style)

		plt.xscale('log')
		ax.set_xlabel('rank')
		plt.yscale('log')
		ax.set_ylabel('F(r)') # frequency

		plt.rc('legend',fontsize=10)
		ax.legend()
		ax.grid(True)

		plt.savefig(fns[k])
		print("INFO: Wrote plot in " + fns[k])

## Centralities

# [Betweenness](http://igraph.org/python/doc/igraph.GraphBase-class.html#betweenness),
# [closeness](http://igraph.org/python/doc/igraph.GraphBase-class.html#closeness)
# and
# [eigenvector](http://igraph.org/python/doc/igraph.GraphBase-class.html#eigenvector_centrality)
# centralities are calculated using `igraph`. The normalization of
# betweeness is obtained by dividing the value by $(N-1)(N-2)/2$, where $N$ is
# the number of vertices.

def plot_centralities(books):
	offset_fig_nr = 1 # figure number starts after 1
	centrs = ["degree", "betweenness", "closeness"]
        
        # PRE-processing
	for book in books:
                book.calc_normalized_centralities()
		## Already do the assignment of lobby value to each vertex
		book.calc_graph_vertex_lobby()
        
        for book in books:
                G = book.G
                fn = book.name + '-centralities.csv'
                f = open(fn, "w")

                f.write("character;betweenness,closeness;lobby\n");
                for i in range(G.number_of_nodes()):
                        ln = G.node[i]['name'] + ";"
                        ln += '{0:.3f}'.format(G.node[i]['betweenness']) + ";"
		        ln += '{0:.3f}'.format(G.node[i]['closeness']) + ";"
                        ln += '{0:.3f}'.format(G.node[i]['lobby']) + "\n"
                        f.write(ln)
                f.close()
                
                        
	for c in centrs:
		fn = c + ".png"

		fig, ((ax0, ax1, ax2), (ax3, ax4, ax5), (ax6, ax7, ax8)) = plt.subplots(nrows=3, ncols=3, sharex=True, sharey=True)
                axes = [ax0, ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8]

		for i in range(len(books)):
                        G = books[i].G
			name = books[i].name
			color = books[i].color
			marker = books[i].marker
			xs = []
			ys = []
                        left = bottom = 100000.0
                        right = top = 0.0
                        
			# load the centrality measures
			for j in range(G.number_of_nodes()):
				x = G.node[j][c]
                                y = G.node[j]['lobby']

                                xs.append(x)
                                ys.append(y)

                                if (x < left): left = x
                                if (x > right): right = x
                                if (y < bottom): bottom = y
                                if (y > top): top = y
                                
			marker_style = dict(linestyle='', color=color, markersize=6)
			axes[i].plot(xs, ys, c=color,
				    marker=marker,
				    label=name,
               			    alpha=0.3, 
				    **marker_style)
		        axes[i].grid(True)
		        axes[i].set_xlabel(c)
		        axes[i].set_ylabel('lobby')

                        axes[i].text(.3, .85, name,
                        horizontalalignment='center',
                        verticalalignment='center',
                        fontsize=11, color='gray',
                        transform=axes[i].transAxes)

                        
		plt.xscale('log')   			       			       
		plt.yscale('log')
		#plt.legend()
                fig.subplots_adjust(hspace=0)
		plt.tight_layout()
		plt.savefig(fn)

# TODO DRAW GRAPH
def draw_graphs(books):
        for book in books:
                G = book.G
                fn = book.name + ".png"

                labels = {}
                for i in range(G.number_of_nodes()):
                        labels[i] = G.node[i]['name']
                
                fig = plt.figure(figsize=(12,12))
                ax = plt.subplot(111)
                ax.set_title('Graph - ' + book.name, fontsize=10)
                pos = nx.spring_layout(G)
                nx.draw(G, pos, node_size=1500, node_color=book.color, font_size=8, font_weight='bold')
                nx.draw_networkx_labels(G, pos, labels, font_size=16)
                plt.tight_layout()
                plt.savefig(fn, format="PNG")

# The main subroutine declares some attributes associated with the
# books. Those attributes are used to label the books and to
# standardize the pictorial elements properties like color and point
# marker in the plot.

if __name__ == "__main__":
        books = []
	color = {'bible': 'red', 'fiction': 'blue', 'biography': 'darkgreen'}

	acts = {'name': 'acts', 'source':'data', 'color': color['bible'], 'marker': 's'}
	arthur = {'name': 'arthur', 'source':'data', 'color': 'magenta', 'marker': '>'}
	david = {'name': 'david', 'source':'sgb', 'color': color['fiction'], 'marker': '8'}
	hobbit = {'name': 'hobbit', 'source':'data', 'color': color['fiction'], 'marker': 'p'}
	huck = {'name': 'huck', 'source':'sgb', 'color': color['fiction'], 'marker': 'H'}
	luke = {'name': 'luke', 'source':'data', 'color': color['bible'], 'marker': '8'}
	newton = {'name': 'newton', 'source':'data', 'color': color['biography'], 'marker': 'o'}
	pythagoras = {'name': 'pythagoras', 'source':'data', 'color': color['biography'], 'marker': '^'}
	tolkien = {'name': 'tolkien', 'source':'data', 'color': color['biography'], 'marker': 'd'}
	
	attrs = [acts, arthur, david, hobbit,
	      	      huck, luke, newton,
		      pythagoras, tolkien]

#	attrs = [david]

	for i in range(len(attrs)):
	    cn = Book(attrs[i]['name'], attrs[i]['source'], attrs[i]['color'], attrs[i]['marker'])
	    books.append(cn)

        write_global_measures(books)
	write_hapax_legomena_table(books)
	plot_rank_frequency(books)
	plot_centralities(books)
	draw_graphs(books)

