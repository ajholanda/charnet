import tempfile
import numpy as np

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LOCAL
from graphs import *

class Project:
        # Where to store files generated by the scripts.
        outdir = tempfile.gettempdir()

        def __init__(self):
                pass
        
        '''Template for specific project configurations.'''
        @staticmethod
        def get_datadir():
                '''Return the directory containing data for the project.'''
                pass
        
        @staticmethod
        def get_outdir():
                return Project.outdir
        
        @staticmethod
        def set_outdir(directory):
                Project.outdir = directory
        
class SGB(Project):
        '''Handle specific configuration for books gathered by Stanford
           GraphBase project.'''

        def __init__(self):
                Project.__init__(self)
                
        @staticmethod
        def get_datadir():
                return 'sgb/'

class Charnet(Project):
        '''Handle specific configuration for books gathered by Charnet project.'''

        def __init__(self):
                Project.__init__(self)

        @staticmethod
        def get_datadir():
                return 'data/'
        
from enum import Enum
class BookCategory(Enum):
        '''Books are classified in categories.'''
        FICTION = 1
        BIOGRAPHY = 2
        LEGENDARY = 3 # e.g., Bible
        
class Book():
        def __init__(self):
                self.G = Graphs.create_graph() # Graph to be created from the book
                self.avg = {} # Dictionary to load average values associated with a centrality as key
                self.was_read = False # if the data file was already parsed, dont do it again
                
        def __str__(self):
                '''Return the name of the book.'''
                pass
                
        def get_category(self):
                pass
        
        def get_comment_token(self):
                '''Asterisk is used as comment to reflect same convention of SGB (Stanford GraphBase).'''
                return '*'
        
        def get_file_ext(self):
                '''Return the default file extension.'''
                return '.dat'

        def get_file_name(self):
                '''Return the file name to be read.'''
                return self.get_datadir() + self.__str__() + self.get_file_ext()

        def get_graph(self):
                return self.G

        def get_label(self):
                """Format the label of the book to print in table or plot."""
                return '\emph{' + self.get_raw_book_label() + '}'

        def get_name(self):
                return self.__str__()
        
        def get_number_characters(self):
                assert self.G
                return self.G.number_of_nodes()

        def get_number_hapax_legomenas(self):
                """
                _Hapax_ _Legomena_ are words with occurrence frequency equals to one.
                """
                assert self.G
                nr_hapaxes = 0
                freqs = nx.get_node_attributes(self.G, 'frequency')
                for freq in freqs:
                        if (freq == 1):
                                nr_hapaxes += 1

                return nr_hapaxes

        def get_number_dis_legomenas(self):
                """
                _Dis_ _Legomena_ are words with occurrence frequency equals to two.
                """
                nr_dis = 0
                freqs = nx.get_node_attributes(self.G, 'frequency')
                for freq in freqs:
                        if (freq == 2):
                                nr_dis += 1

                return nr_dis

        def get_raw_book_label(self):
                return self.__str__().title()

        def get_vertex_color(self):
                '''Return the color set to vertices in the plot of graph. Default: white.'''
                return 'white'
        
        def read(self):
                """
                Read the file containing characters encounters of a book 
                and return a graph.
                
                Returns
                -------
                networkx graph
                """
                are_edges = False
                book_name = self.get_name().title()

                # assert data file is not read several times
                if (self.was_read == False):
                        self.was_read = True
                else:
                        return self.G

                # name the Graph
                self.get_graph().graph['name'] = self.get_name()
                
                fn = self.get_file_name()
                f = open(fn, "r")
                u = 'AA' # store old vertex label and it is used to check it the order is right
                for ln in f:
                        # ignore comments
                        if (ln.startswith(self.get_comment_token())): 
                                continue

                        # edges start after an empty line
                        if (ln.startswith('\n') or ln.startswith('\r')):
                                are_edges = True
                                continue

                        # remove new line
                        ln = ln.rstrip("\n")
                        
                        # boolean are_edges indicates if it is inside nodes region
                        if (are_edges==False):
                                (v, character_name) = ln.split(' ', 1)

                                # check the order
                                if u > v:
                                        logger.error('* Labels {} and {} is out of order in {}'.format(u, v, book_name))
                                        exit()
                                
                                #DEBUG
                                logger.debug("* G.add_node({}, name={})".format(v, character_name))
                                #GUBED
                                if v not in self.G.node:
                                        self.G.add_node(v, frequency=1, name=character_name)
                                        u = v
                                else:
                                        logger.error('* Label {} is repeated in book {}.'.format(v, book_name))
                                        exit()
                                continue

                        # edges region from here
                        # eg., split "1.2:ST,MR;ST,PH,MA;MA,DO" => ["1.2" , "ST,MR;ST,PH,MA;MA,DO"]
                        (chapter, edges_list) = ln.split(':', 1)

                        # eg., split "ST,MR;ST,PH,MA;MA,DO" => ["ST,MR", "ST,PH,MA", "MA,DO"]
                        edges = edges_list.split(';')

                        if(edges[0] == ''): # eliminate chapters with no edges
                                continue
                        
                        for e in edges:
                                # eg., split "ST,PH,MA" => ["ST", "PH", "MA"]
                                vs = e.split(',')  # vertices

                                # add nodes to graph G if it does not exit
                                # otherwise, increment frequency
                                for v in vs:
                                        if (v not in self.G.node):
                                                logger.error('* Label <{}> was not added as node in the graph for book {}.'.format(v, book_name))
                                                exit()
                                        else:
                                                self.G.node[v]['frequency'] += 1

                                # add characters encounters (edges) to graph G
                                for i in range(len(vs)):
                                        u = vs[i]
                                        for j in range(i+1, len(vs)):
                                                v = vs[j]

                                                if (u,v) not in self.G.edges():
                                                        self.G.add_edge(u, v, weight=1)
                                                else:
                                                        self.G[u][v]['weight'] += 1

                                                #DEBUG
                                                action = 'add'
                                                w = self.G[u][v]['weight']
                                                if w > 1: action = 'mod'
                                                logger.debug('* G.{}_edge({}, {}, weight={})'.format(action, u, v, w))
                                                #GUBED
                f.close()
                logger.info("* Read G from book \"{}\"".format(book_name))
                return self.G
        
class Acts(Book, Charnet):
        def __init__(self):
                Book.__init__(self)
                Charnet.__init__(self)
                
        def __str__(self):
                return 'acts'

        def get_category(self):
                return BookCategory.LEGENDARY
        
        def get_vertex_color(self):
                return 'khaki'

class Apollonius(Book, Charnet):
        def __init__(self):
                Book.__init__(self)
                Charnet.__init__(self)
                
        def __str__(self):
                return 'apollonius'

        def get_category(self):
                return BookCategory.LEGENDARY
        
        def get_vertex_color(self):
                return 'red'

class Arthur(Book, Charnet):
        def __init__(self):
                Book.__init__(self)
                Charnet.__init__(self)
                
        def __str__(self):
                return 'arthur'

        def get_category(self):
                return BookCategory.FICTION
        
        def get_vertex_color(self):
                return 'cyan'

class David(Book, SGB):
        def __init__(self):
                Book.__init__(self)
                SGB.__init__(self)
                
        def __str__(self):
                return 'david'

        def get_category(self):
                return BookCategory.FICTION
        
        def get_vertex_color(self):
                return 'orange'

class Dick(Book, Charnet):
        def __init__(self):
                Book.__init__(self)
                Charnet.__init__(self)
                
        def __str__(self):
                return 'dick'

        def get_category(self):
                return BookCategory.BIOGRAPHY
        
        def get_vertex_color(self):
                return 'orchid'

class Hawking(Book, Charnet):
        def __init__(self):
                Book.__init__(self)
                Charnet.__init__(self)
                
        def __str__(self):
                return 'hawking'

        def get_category(self):
                return BookCategory.BIOGRAPHY
        
        def get_vertex_color(self):
                return 'silver'

class Hobbit(Book, Charnet):
        def __init__(self):
                Book.__init__(self)
                Charnet.__init__(self)
                
        def __str__(self):
                return 'hobbit'

        def get_category(self):
                return BookCategory.FICTION
        
        def get_vertex_color(self):
                return 'gold'

class Huck(Book, SGB):
        def __init__(self):
                Book.__init__(self)
                SGB.__init__(self)
                
        def __str__(self):
                return 'huck'

        def get_category(self):
                return BookCategory.FICTION
        
        def get_vertex_color(self):
                return 'salmon'

class Luke(Book, Charnet):
        def __init__(self):
                Book.__init__(self)
                Charnet.__init__(self)
                
        def __str__(self):
                return 'luke'

        def get_category(self):
                return BookCategory.LEGENDARY
        
        def get_vertex_color(self):
                return 'wheat'

class Newton(Book, Charnet):
        def __init__(self):
                Book.__init__(self)
                Charnet.__init__(self)
                
        def __str__(self):
                return 'newton'

        def get_category(self):
                return BookCategory.BIOGRAPHY
        
        def get_vertex_color(self):
                return 'tan'

class Pythagoras(Book, Charnet):
        def __init__(self):
                Book.__init__(self)
                Charnet.__init__(self)
                 
        def __str__(self):
                return 'pythagoras'

        def get_category(self):
                return BookCategory.LEGENDARY
        
        def get_vertex_color(self):
                return 'tomato'

class Tolkien(Book, Charnet):
        def __init__(self):
                Book.__init__(self)
                Charnet.__init__(self)
                                
        def __str__(self):
                return 'tolkien'
                
        def get_category(self):
                return BookCategory.BIOGRAPHY
        
        def get_vertex_color(self):
                return 'yellowgreen'

class Books(Book):
        was_already_read = False
        books = [             # row, col
                Dick(),       #  0,  0
                Apollonius(), #  1,  1
                Hobbit(),     #  2,  2
                Tolkien(),    #  3,  0
                Acts(),       #  0,  1
                David(),      #  1,  2
                Newton(),     #  2,  0
                Pythagoras(), #  3,  1
                Arthur(),     #  0,  2
                Hawking(),    #  1,  0
                Luke(),       #  2,  1
                Huck(),       #  3,  2
        ]

        @staticmethod
        def get_books():
                if Books.was_already_read == False:
                        Books.was_already_read = True
                        logger.info("\n\t#### PRE-PROCESSING ####")
                        for book in Books.books:
                                book.read()
                return Books.books
