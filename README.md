# Degrees of Wikipedia

## Dependencies

* bs4
* matplotlib
* networkx
* graphviz
* tkinter

You can run the setup.sh to install `bs4`, and `networkx` all at once. Also
it will create `graph_bank` and `graph_img` directories at where the result graphs will
be stored.

## File included

* main_gui.py
* main_on_server.py
* main_on_server_common.py
* log.py
* crawler.py
* fileio.py
* searcher.py
* searcher_common.py
* send_email.py
* settings.py
* setup.sh
* graph.png
* test_dot.dot
* README.md

## How to run
This program consists of two parts: finding path and finding common ancestors.
Then you can run either `main_gui.py`, `main_on_searver.py` or
`main_on_server_common.py` by `python3 <filename>`.

## Introduction

### finding path

Finding a shortest path from the given starting point and ending point.
This can help you build up a basic relation between two things.
To start, simply entering the starting point and ending point you want an
an optional max limit that will prevent the program from parsing wikipedia
too deep.

### finding common ancestors

Finding the common ancestors that can both be reached from two given starting points.
To start, simply entering two starting points and the optional max limit. The order
of two starting points does not matter since the program will parse starting from two
points simultaneously.

### run from cloud

We also allow users to run this program on the cloud, where GUI is nod needed but some additional
features such as sending results via email to users once the program is completed.

## How it works

The core algorithm in this program is a complicated version of breadth first search (BFS).
Unlike the BFS shown in class where the whole graph is loaded into memory all at once, we are
generating the graph on the go by sending new requests for every node to wikipedia server.
To optimize the speed, multi-threading techniques and threading-safe queues are used. One of the difficulties
is to make the searcher class thread-safe, where every operation needs to be taken into account. Others
may include desigining a proper interface between the `Searcher` class and the `Crawler` class,
and that between `Searcher` class and the `WikiApp` main GUI class.

### finding path

Apply the complicated version of BFS at starting node until the ending node is discovered. Also,
the partial graph is stored in a `networkx`'s `DiGraph` object in order to render the graph at the
end.

### finding common ancestors

Half number of total threads are assigned to each starting point, two separate queues are used for
each half.