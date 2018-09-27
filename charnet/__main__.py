#!/usr/bin/python3
import os.path
import sys
sys.path.append('/usr/local/lib/python2.7/dist-packages/')

import logging

# LOCAL
from books import *
from draw import *
from formatting import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_all_tasks():
        i = 1
        while True:
                print(hdrs[i])
                tasks[i]()

                i += 1
                if i == len(tasks)-1: # BUG: without this, in this way, dont stop
                        exit()

# header to tasks dictionary
tasks = [ None, # sys.argv[0] name of the program, no flag associated
          Plot.do, # -c
          Draw.do_graphs, # -g
          Formatting.write_global_measures, # -m
          Formatting.write_hapax_legomena_table, # -l
          Formatting.write_stat_centralities, # -s
          Formatting.write_vertices_degree, # -d
          Formatting.write_vertices_frequency, # -f
          Formatting.write_edges_weight, # -e
          Formatting.write_biconnected_comps, # -b
          run_all_tasks] # -a
        
# headers
hdrs = ["__main__", 
        "\n\t#### TASK 1 - Plot graphics ####",
        "\n\t#### TASK 2 - Draw graph ####", 
        "\n\t#### TASK 3 - Write global measures ####", 
        "\n\t#### TASK 4 - Write the frequency of _hapax_ _legomena_ ####", 
        "\n\t#### TASK 5 - Write statistics of centralities ####",
        "\n\t#### TASK 6 - Write the vertices' degree ####",
        "\n\t#### TASK 7 - Write the characters' frequency ####",
        "\n\t#### TASK 8 - Write the edges' weight ####",
        "\n\t#### TASK 9 - Write the graph bicomponents ####", 
        "\n\t#### RUNNING ALL TASKS ####"] 

def usage():
        print('* Usage: python3 ' + sys.argv[0] + ''' [options]
        OPTIONS
        -p, --plot
        \tPlot the lobby and other centralities comparisons, assortativity mixing and degree distribution with fitting.
        -g, --draw-graph
        \tDraw the graph of characters encounters for visualization generating PNG files.
        -m, --global-measures
        \tWrite global measures in a table in a LaTeX file.
        -l, --legomena
        \tWrite the frequency of hapax legomena, characters that appear only once in a table in a LaTeX file.
        -s, --stat-centralities
        \tGenerate statistics from centralities.
        -d, --degree
        \tWrite the vertices' degree in a file named \"{dir}/<book_name>-vertex-degree.csv\".
        -f, --frequency
        \tWrite the frequency of characters' appearance in a file named \"{dir}/<book_name>-vertex-frequency.csv\".
        -e, --weight
        \tWrite the weight of edges in a file named \"{dir}/<book_name>-edge-weight.csv\".
        -b, --bicomps
        \tWrite the graph bicomponents in a file named \"{dir}/<book_name>-bicomponents.txt\".
        -a, --all
        \tExecute all options.
        -o <directory>, --output-dir <directory>
        \tSet the <directory> to write the generated files. Default directory: \"{dir}\"
        -h, --help
        \t Print this help message.

        One of the flags listed above must be selected, with exception of the \"-o\" or 
        \"--output-dir\" that changes the program behavior and it is optional.
        '''.format(dir=Project.get_outdir())
        )
        exit()

def print_out_banner(directory):
        spc = '\n\n'
        ln = '\t\t################################################'
        print(spc)
        print(ln)
        print('\t\t  Writing output to \"{}\"  '.format(directory))
        print(ln)
        print(spc)

if __name__ == "__main__":
        """The main subroutine declares some attributes associated with the
        books. Those attributes are used to label the books and to
        standardize the pictorial elements properties like color and point
        marker in the plot."""

        # Boolean array to store state of the flags 
        opts = [False] * len(tasks)

        # numer og arguments
        n = len(sys.argv)

        # retrieve the flags set by the user
        if n > 1:
                i=1
                while i<n:
                        opt = sys.argv[i]

                        # OPTIONAL
                        if opt == "-o" or opt == "--output-dir":
                                i += 1
                                if i == n:
                                        usage()
                                _dir = sys.argv[i]
                                _dir = _dir.rstrip('\n')
                                if os.path.exists(_dir):
                                        Project.set_outdir(_dir)
                                else:
                                        logger.error(' Directory \"{}\" does not exists!'.format(_dir))
                                        exit()
                        elif opt == "-p" or opt == "--plot":
                                opts[1] = True
                        elif opt == "-g" or opt == "--draw-graph":
                                opts[2] = True
                        elif opt == "-m" or opt == "--global-measures":
                                opts[3] = True
                        elif opt == "-l" or opt == "--legomena":
                                opts[4] = True
                        elif opt == "-s" or opt == "--stat-centralities":
                                opts[5] = True
                        elif opt == "-d" or opt == "--degree":
                                opts[6] = True
                        elif opt == "-f" or opt == "--frequency":
                                opts[7] = True
                        elif opt == "-e" or opt == "--weight":
                                opts[8] = True
                        elif opt == "-b" or opt == "--bicomps":
                                opts[9] = True
                        elif opt == "-a" or opt == "--all-tasks":
                                opts[10] = True
                                for i in range(1, n-1): # to not repeat tasks
                                        opts[i] = False
                        elif opt == "-h" or opt == "--help": # help make exit
                                usage()
                        else:
                                logger.error('* Unknown OPTION:', opt)
                                usage()
                        i += 1
        else:
                usage()

        print_out_banner(Project.get_outdir())
        for i in range(1, len(opts)):
                if opts[i] == True:
                        logger.info(hdrs[i])
                        tasks[i]()
