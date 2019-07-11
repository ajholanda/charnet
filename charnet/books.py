"""This module wraps the semantics of the cfg.Project.
    The books used are classified and some methods
    are implemented to allow data handling."""

import logging
from enum import Enum

import numpy as np

# LOCAL
from  .graphs import Graphs
from . import config as cfg

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

class SGB(cfg.Project):
    '''Handle specific configuration for books gathered by Stanford
       GraphBase project.'''
    def __init__(self):
        cfg.Project.__init__(self)
    @staticmethod
    def get_datadir():
        """Directory containing data from Stanford GraphBase."""
        return 'sgb-data/'

class Charnet(cfg.Project):
    '''Handle specific configuration for books gathered by Charnet project.'''
    def __init__(self):
        cfg.Project.__init__(self)
    @staticmethod
    def get_datadir():
        """Directory containing data."""
        return cfg.Project.get_data_dir()

class BookGenre(Enum):
    '''Books are classified in categories.'''
    BIOGRAPHY = 0
    LEGENDARY = 1 # e.g., Bible
    FICTION = 2

class Book():
    """Superclass with methods to handle all data needed to obtain
        the measures for the networks of characters obtained from the chosen
        books."""
    def __init__(self):
        self.graph = Graphs.create_graph() # Graph to be created from the book
        self.avg = {} # Dictionary to load average values associated with a centrality as key
        self.was_read = False # if the data file was already parsed, dont do it again
        # Dictionaries to store graph information
        # map vertex index and its label
        self.graph.vertex_properties["label"] = self.graph.new_vertex_property("string")
        # map vertex 'index' object and its frequency
        self.graph.vertex_properties["frequency"] = self.graph.new_vertex_property("int")
        # map edge index and its weight
        self.graph.edge_properties["weight"] = self.graph.new_edge_property("int")
        # map vertex index and its character name
        self.graph.vertex_properties["char_name"] = self.graph.new_vertex_property("string")
        # map vertex label and its vertex 'index' object
        self.vprop_l2v = {}
        # Store a boolean value indicating if vertex PropertyMap containing degree
        # values was already filled
        self.graph.graph_properties["was_vprop_degree_set"] = \
            self.graph.new_graph_property("boolean")
        self.graph.graph_properties["was_vprop_degree_set"] = False
        # Store degree non-normalized degree of vertices
        self.graph.vertex_properties["degree"] = self.graph.new_vertex_property("int")
    def __str__(self):
        '''Return the name of the book.'''
        return 'Book'
    def get_data_dir(self):
        """Directory containing data. Default value."""
        return cfg.Project.get_data_dir()
    def set_graph_name(self, name):
        """Set the graph name for the current object."""
        self.graph.graph_properties["name"] = self.graph.new_graph_property("string")
        self.graph.graph_properties["name"] = name
    def get_char_label(self, idx):
        """Return the chracter label for the index idx."""
        return self.graph.vertex_properties["label"][idx]
    def set_char_label(self, idx, label):
        """Set a label for character with index idx."""
        self.graph.vertex_properties["label"][idx] = label
        self.vprop_l2v[label] = idx
    def set_char_name(self, idx, char_name):
        """Set a name for the character with index idx."""
        self.graph.vertex_properties["char_name"][idx] = char_name
    def get_char_idx_from_label(self, label):
        """Return the character index mapped to label."""
        return self.vprop_l2v[label]
    def add_char(self, label, char_name):
        '''Add character labelled with character name in the graph. Map label
        and frequency with index; and character name with label.'''
        vert = self.graph.add_vertex()
        idx = int(vert)
        self.set_char_label(idx, label)
        self.set_char_name(idx, char_name)
        self.graph.vertex_properties["frequency"][idx] = 0
    def inc_freq(self, label):
        """"Increment the frequency of character represented by label."""
        idx = self.get_char_idx_from_label(label)
        self.graph.vertex_properties["frequency"][idx] += 1

    def exists(self, label):
        '''Verify the existence of the label in the dictionary associated with
        the graph. The existence means the label was already inserted in the
        graph G.'''
        if label in self.vprop_l2v:
            return True
        return False
    def degree(self, label):
        """Return the degree of the character represented by label."""
        idx = self.get_char_idx_from_label(label)
        return self.graph.vertex(idx).out_degree()
    def met(self, char_lbl_a, char_lbl_b):
        '''Return True if character label a (char_lbl_a) have met with character
        label b (char_lbl_b), False otherwise.
        '''
        a_vert = self.get_char_idx_from_label(char_lbl_a)
        b_vert = self.get_char_idx_from_label(char_lbl_b)
        if self.graph.edge(a_vert, b_vert) is None:
            return False
        return True
    def add_encounter(self, char_lbl_a, char_lbl_b):
        """Add edge a-b."""
        a_vert = self.get_char_idx_from_label(char_lbl_a)
        b_vert = self.get_char_idx_from_label(char_lbl_b)
        edge = self.graph.add_edge(a_vert, b_vert)
        self.graph.edge_properties["weight"][edge] = 1
    def inc_weight(self, char_lbl_a, char_lbl_b):
        """Increment the weight of edge a-b."""
        a_vert = self.get_char_idx_from_label(char_lbl_a)
        b_vert = self.get_char_idx_from_label(char_lbl_b)
        edge = self.graph.edge(a_vert, b_vert)
        self.graph.edge_properties["weight"][edge] += 1
    def get_weight(self, char_lbl_a, char_lbl_b):
        """Return the weight of edge a-b."""
        a_vert = self.get_char_idx_from_label(char_lbl_a)
        b_vert = self.get_char_idx_from_label(char_lbl_b)
        edge = self.graph.edge(a_vert, b_vert)
        return self.graph.edge_properties["weight"][edge]
    def get_genre(self):
        """Return the genre."""
        return None
    def get_comment_token(self):
        '''Asterisk is used as comment to reflect same convention of SGB (Stanford GraphBase).'''
        return '*'
    def get_file_ext(self):
        '''Return the default file extension.'''
        return '.dat'
    def get_file_name(self):
        '''Return the file name to be read.'''
        return self.get_data_dir() + self.__str__() + self.get_file_ext()
    def get_graph(self):
        """Return the graph for the current book."""
        return self.graph
    def get_label(self):
        """Format the label of the book to print in table or plot."""
        return '\\emph{' + self.get_raw_book_label() + '}'
    def get_name(self):
        """Return the book name."""
        return self.__str__()
    def get_number_characters(self):
        """Return the number of characters."""
        assert self.graph
        return len(self.graph.vs)
    def get_number_hapax_legomenas(self):
        """
        _Hapax_ _Legomena_ are words with occurrence frequency equals to one.
        """
        assert self.graph
        nr_hapaxes = 0
        for vert in self.graph.vertices():
            freq = self.graph.vertex_properties['frequency'][vert]
            if freq == 1:
                nr_hapaxes += 1
        return nr_hapaxes

    def get_number_dis_legomenas(self):
        """
        _Dis_ _Legomena_ are words with occurrence frequency equals to two.
        """
        assert self.graph
        nr_dis = 0
        for vert in self.graph.vertices():
            freq = self.graph.vertex_properties['frequency'][vert]
            if freq == 2:
                nr_dis += 1
        return nr_dis
    def get_raw_book_label(self):
        """Return the book label in uppercase."""
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
        a graph
        """
        are_edges = False
        book_name = self.get_name().title()
        # assert data file is not read several times
        if self.was_read is False:
            self.was_read = True
        else:
            return self.graph
        # set graph name
        self.set_graph_name(self.get_name())
        file_name = self.get_file_name()
        _file = open(file_name, "r")
        u_vert = 'AA' # store old vertex label and it is used to check it the order is right
        for line in _file:
            # ignore comments
            if line.startswith(self.get_comment_token()):
                continue
            # edges start after an empty line
            if line.startswith('\n') or line.startswith('\r'):
                are_edges = True
                continue
            # remove new line
            line = line.rstrip('\r\n')
            # boolean are_edges indicates if it is inside vertices region
            if are_edges is False:
                (v_vert, character_name) = line.split(' ', 1)
                # check the order
                if u_vert > v_vert:
                    LOGGER.error('* Labels %s and %s is \
                                 out of order in %s',
                                 u_vert, v_vert, book_name)
                    exit()
                #DEBUG
                LOGGER.debug("* G.add_vertice(%s, name=%s)", v_vert, character_name)
                #GUBED
                if not self.exists(v_vert):
                    self.add_char(v_vert, character_name)
                    u_vert = v_vert
                else:
                    LOGGER.error('* Label %s is repeated in book %s.', v_vert, book_name)
                    exit()
                continue
            # edges region from here
            # eg., split "1.2:ST,MR;ST,PH,MA;MA,DO" => ["1.2" , "ST,MR;ST,PH,MA;MA,DO"]
            (_, edges_list) = line.split(':', 1)
            # eg., split "ST,MR;ST,PH,MA;MA,DO" => ["ST,MR", "ST,PH,MA", "MA,DO"]
            edges = edges_list.split(';')
            if edges[0] == '': # eliminate chapters with no edges
                continue
            for edge in edges:
                # eg., split "ST,PH,MA" => ["ST", "PH", "MA"]
                verts = edge.split(',')  # vertices
                # add vertices to graph G if it does not exit
                # otherwise, increment frequency
                for v_vert in verts:
                    if not self.exists(v_vert):
                        LOGGER.error('* Label \"%s\" was not added \
                                     as node in the graph for book %s.',
                                     v_vert, book_name)
                        exit()
                    else:
                        self.inc_freq(v_vert)
                # add characters encounters (edges) to graph G
                for i in enumerate(verts):
                    u_vert = verts[i]
                    for j in range(i+1, len(verts)):
                        v_vert = verts[j]
                        # link u--v
                        if not self.met(u_vert, v_vert):
                            self.add_encounter(u_vert, v_vert)
                        else: # u--v already in G, increase weight
                            self.inc_weight(u_vert, v_vert)
                        #DEBUG
                        action = 'add'
                        w_vert = self.get_weight(u_vert, v_vert)
                        if w_vert > 1:
                            action = 'mod'
                        LOGGER.debug('* G.%s_edge(%s, %s, weight=%s)',
                                     action, u_vert, v_vert, w_vert)
                        #GUBED
        _file.close()
        LOGGER.info("* Read G from book \"%s\"", book_name)
        return self.graph

class Acts(Book, Charnet):
    """Data about Acts of Apostles gospel."""
    def __init__(self):
        Book.__init__(self)
        Charnet.__init__(self)
    def __str__(self):
        return 'acts'
    def get_genre(self):
        return BookGenre.LEGENDARY
    def get_vertex_color(self):
        """Return the color to fill the vertex."""
        return 'khaki'

class Apollonius(Book, Charnet):
    """Data about Applonius of Tyana book."""
    def __init__(self):
        Book.__init__(self)
        Charnet.__init__(self)
    def __str__(self):
        return 'apollonius'
    def get_genre(self):
        return BookGenre.LEGENDARY
    def get_vertex_color(self):
        """Return the color to fill the vertex."""
        return 'red'

class Arthur(Book, Charnet):
    """Data about king Arthur book."""
    def __init__(self):
        Book.__init__(self)
        Charnet.__init__(self)
    def __str__(self):
        return 'arthur'
    def get_genre(self):
        return BookGenre.FICTION
    def get_vertex_color(self):
        """Return the color to fill the vertex."""
        return 'cyan'

class David(Book, SGB):
    """Data about David Copperfield book."""
    def __init__(self):
        Book.__init__(self)
        SGB.__init__(self)
    def __str__(self):
        return 'david'
    def get_genre(self):
        return BookGenre.FICTION
    def get_vertex_color(self):
        """Return the color to fill the vertex."""
        return 'orange'

class Dick(Book, Charnet):
    """Data about Dick's biography."""
    def __init__(self):
        Book.__init__(self)
        Charnet.__init__(self)
    def __str__(self):
        return 'dick'
    def get_genre(self):
        return BookGenre.BIOGRAPHY
    def get_vertex_color(self):
        """Return the color to fill the vertex."""
        return 'orchid'

class Hawking(Book, Charnet):
    """Data about Hawking's biography."""
    def __init__(self):
        Book.__init__(self)
        Charnet.__init__(self)
    def __str__(self):
        return 'hawking'
    def get_genre(self):
        return BookGenre.BIOGRAPHY
    def get_vertex_color(self):
        """Return the color to fill the vertex."""
        return 'silver'

class Hobbit(Book, Charnet):
    """Data about Hobbit book."""
    def __init__(self):
        Book.__init__(self)
        Charnet.__init__(self)
    def __str__(self):
        return 'hobbit'
    def get_genre(self):
        return BookGenre.FICTION
    def get_vertex_color(self):
        """Return the color to fill the vertex."""
        return 'gold'

class Huck(Book, SGB):
    """Data about Huckleberry Finn book."""
    def __init__(self):
        Book.__init__(self)
        SGB.__init__(self)
    def __str__(self):
        return 'huck'
    def get_genre(self):
        return BookGenre.FICTION
    def get_vertex_color(self):
        """Return the color to fill the vertex."""
        return 'salmon'

class Luke(Book, Charnet):
    """Data about Luke gospel."""
    def __init__(self):
        Book.__init__(self)
        Charnet.__init__(self)
    def __str__(self):
        return 'luke'
    def get_genre(self):
        return BookGenre.LEGENDARY
    def get_vertex_color(self):
        """Return the color to fill the vertex."""
        return 'wheat'

class Newton(Book, Charnet):
    """Data about Newton's biography."""
    def __init__(self):
        Book.__init__(self)
        Charnet.__init__(self)
    def __str__(self):
        return 'newton'
    def get_genre(self):
        return BookGenre.BIOGRAPHY
    def get_vertex_color(self):
        """Return the color to fill the vertex."""
        return 'tan'

class Pythagoras(Book, Charnet):
    """Data about Pythagoras' biography"""
    def __init__(self):
        Book.__init__(self)
        Charnet.__init__(self)
    def __str__(self):
        return 'pythagoras'
    def get_genre(self):
        return BookGenre.LEGENDARY
    def get_vertex_color(self):
        """Return the color to fill the vertex."""
        return 'tomato'

class Tolkien(Book, Charnet):
    """Data about Tolkien's biography."""
    def __init__(self):
        Book.__init__(self)
        Charnet.__init__(self)
    def __str__(self):
        return 'tolkien'
    def get_genre(self):
        return BookGenre.BIOGRAPHY
    def get_vertex_color(self):
        """Return the color to fill the vertex."""
        return 'yellowgreen'

class Books(Book):
    """Books class joins in place books data."""
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
    genre_names = ['Biography', 'Legendary', 'Fiction']

    @staticmethod
    def get_genre_label(book):
        """Given a genre ID, return its letter label."""
        lab = None
        gen = book.get_genre()
        if gen == BookGenre.BIOGRAPHY:
            lab = 'B'
        elif gen == BookGenre.LEGENDARY:
            lab = 'L'
        elif gen == BookGenre.FICTION:
            lab = 'F'
        else:
            LOGGER.error('* Unknown book: \"%s\"', book.get_name())
            exit()
        return lab

    @staticmethod
    def get_genre_name(idx):
        """Given a genre ID, return its name."""
        return Books.genre_names[idx]

    @staticmethod
    def get_genre_enums():
        """Get the genres IDs"""
        return np.arange(0, len(Books.genre_names))

    @staticmethod
    def get_books():
        """Return the books data."""
        if Books.was_already_read is False:
            Books.was_already_read = True
            LOGGER.info("\n\t#### PRE-PROCESSING ####")
            for book in Books.books:
                book.read()
        return Books.books
