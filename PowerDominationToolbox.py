#!/usr/bin/env python
# coding: utf-8
# 
# 
# The Power Domination Toolbox
# Authors: Johnathan Koch (Youngstown State University), Beth Bjorkman (Air Force Research Laboratory)
# 
# The first 4 function definitions comprise example networks used demonstratively.
# The next function, "ZeroForce" is a functional rewrite of the zeros game as available in the Minimum Rank Sage Library cited in "Program for calculating bounds on the minimum rank of a graph using Sage."
# The next two functions, "Dominate" and "PowerDominate", comprise the power domination algorithm described in "Domination in graphs applied to electric power networks."
# The remaining 27 functions perform the parallel search of a minimum power dominating set by performing the following 4 pre-processing steps on the network.
# 

import itertools as it
import networkx as nx
import numpy as np
import math
import multiprocessing
import copy
import pickle
import os
import time
import logging

def NewEnglandGraph():
    return nx.parse_adjlist(['1 2 39', '2 3 25 30', '39 9', '3 4 18', '25 26 37', '4 5 14', '18 17', '5 6 8', '14 13 15', '6 7 11 31', '8 7 9', '11 10 12', '10 13 32', '13 12', '15 16', '16 17 19 21 24', '17 27', '19 20 33', '21 22', '24 23', '27 26', '20 34', '22 23 35', '23 36', '26 28 29', '28 29', '29 38'])

def IEEE118():
    return nx.parse_adjlist(['1 2 3', '2 12', '3 5 12', '4 5 11', '5 6 11 8', '6 7', '7 12', '8 9 30', '9 10', '11 12 13', '12 14 16 117', '13 15', '14 15', '15 17 19 33', '16 17', '17 18 31 113 30', '18 19', '19 20 34', '20 21', '21 22', '22 23', '23 24 25 32', '24 70 72', '25 27 26', '26 30', '27 28 32 115', '28 29', '29 31', '30 38', '31 32', '32 113 114', '33 37', '34 36 37 43', '35 36 37', '37 39 40 38', '38 65', '39 40', '40 41 42', '41 42', '42 49', '43 44', '44 45', '45 46 49', '46 47 48', '47 49 69', '48 49', '49 50 51 54 66 69', '50 57', '51 52 58', '52 53', '53 54', '54 55 56 59', '55 56 59', '56 57 58 59', '59 60 61 63', '60 61 62', '61 62 64', '62 66 67', '63 64', '64 65', '65 66 68', '66 67', '68 69 81 116', '69 70 75 77', '70 71 74 75', '71 72 73', '74 75', '75 77 118', '76 77 118', '77 78 80 82', '78 79', '79 80', '80 96 97 98 99 81', '82 83 96', '83 84 85', '84 85', '85 86 88 89', '86 87', '88 89', '89 90 92', '90 91', '91 92', '92 93 94 100 102', '93 94', '94 95 96 100', '95 96', '96 97', '98 100', '99 100', '100 101 103 104 106', '101 102', '103 104 105 110', '104 105', '105 106 107 108', '106 107', '108 109', '109 110', '110 111 112', '114 115'])

def ZimGraph():
    return nx.parse_adjlist(['1 2 5', '2 3 6', '3 7', '4 5', '5 6 9', '6 7 9', '7 8 9', '9 10 11', '10 11'])

def MutatedZimGraph():
    return nx.parse_adjlist(['1 2 5', '2 6 3', '5 4 6 9', '6 7 9', '3 7', '7 8 9', '15 14', '14 13', '13 4', '9 10 11', '8 12', '10 16', '11 19', '16 17', '19 18', '17 18'])

def BarbellGraph():
    return nx.parse_adjlist(['0 1 2 3', '1 2 3', '2 3', '3 4', '4 5', '5 6', '6 7', '7 8', '8 9 10 11', '9 10 11', '10 11'])

def ZeroForce(Graph, SeedSet=[]):
    #INPUT
    #
    #Graph - a networkx graph object
    #   This is used as the graph to play the zero forcing game on
    #SeedSet - a list object containing networkx vertex objects (defaults to an empty list)
    #   This is used as the initially colored vertices
    #
    #OUTPUT
    #
    #Blues - a set object containing networkx vertex objects
    #   This is the result after propagating the seed set until no more propagating steps can be taken

    #To implement zero forcing the algorithm needs to keep track of active, inactive, and neighbors of blue vertices
    NewBlues = set(SeedSet)
    Blues = set()
    BlueNeighbors = {}
    ActiveBlues = set()
    InactiveBlues = set()
    
    #To be sure we try to zero force at least once, we set the flag for coloring to true
    HaveColored = True
    
    while HaveColored:
        
        #Now we continue zero forcing until we don't color any vertices
        HaveColored = False
        
        #Now we update the set of blues with the vertices colored in the last iteration of the loop
        Blues.update(NewBlues)
        ActiveBlues.update(NewBlues)
        ActiveBlues.difference_update(InactiveBlues)
        
        #Now we update the list of neighbors to blue vertices and clear the NewBlues and InactiveBlues for this iteration
        BlueNeighbors.update([[Vertex, set(Graph.neighbors(Vertex)).difference(Blues)] for Vertex in NewBlues])
        NewBlues.clear()
        InactiveBlues.clear()
        
        #Now we check if any of the active blue vertices can zero force
        for Vertex in ActiveBlues:
            BlueNeighbors[Vertex].difference_update(Blues)
            
            #If the vertex has exactly one uncolored neighbor, then we flag it for coloring and set the flag that we have colored in this iteration of the loop
            if len(BlueNeighbors[Vertex]) == 1:
                NewBlues.add(BlueNeighbors[Vertex].pop())
                InactiveBlues.add(Vertex)
                HaveColored = True
                
    return Blues

def Dominate(Graph, SeedSet):
    #INPUT
    #
    #Graph - a networkx graph object
    #   This is used as the graph to power dominate on
    #SeedSet - a set object containing networkx vertex objects
    #   This is used as the initially colored vertices (before the domination step)
    #
    #OUTPUT
    #
    #DominatedBlues - a list object containing networkx vertex objects
    #   This is the result after propagating the seed set

    Blues = set(SeedSet)
    DominatedBlues = set(SeedSet)
    
    [DominatedBlues.add(Neighbor) for Vertex in Blues for Neighbor in nx.neighbors(Graph,Vertex)]
    
    return list(DominatedBlues)

def PowerDominate(Graph, SeedSet):
    #INPUT
    #
    #Graph - a networkx graph object
    #   This is used as the graph to power dominate on
    #SeedSet - a set object containing networkx vertex objects
    #   This is used as the initially colored vertices (before the domination step)
    #
    #OUTPUT
    #
    #a set of vertices that are the result of power domination on the input graph with the input seed set

    #First, color the initial set of vertices to start with
    Blues = list(SeedSet)
    
    #Second, color the neighbors of the initial set of vertices (domination step)
    DominatedBlues = Dominate(Graph, Blues)
        
    #Third, we play the zero forcing game
    Blues = ZeroForce(Graph, DominatedBlues)
    
    return Blues

def isPDS(Graph, SeedSet):
    #INPUT
    #
    #Graph - a networkx graph object
    #   This is used as the graph to power dominate on
    #SeedSet - a set object containing networkx vertex objects
    #   This is used as the initially colored vertices (before the domination step)
    #
    #OUTPUT
    #
    #True or False, depending on whether the supplied set of vertices is a power dominating set (PDS for short) for the given graph

    #First, color the initial set of vertices to start with
    Blues = list(SeedSet)
    
    #Second, color the neighbors of the initial set of vertices (domination step)
    DominatedBlues = Dominate(Graph, Blues)
        
    #Third, we play the zero forcing game
    Blues = ZeroForce(Graph, DominatedBlues)

    #Now if the entire graph is blue, then we found a power dominating set!
    if len(Blues) == Graph.number_of_nodes():
        return True
    else:
        return False

def _DeletedConnectedComponents(Graph, Vertex):
    #INPUT
    #
    #Graph - a networkx graph object
    #   This is used as the graph under inspection
    #Vertex - a networkx vertex object
    #   This is used to be the vertex that is removed
    #
    #OUTPUT
    #
    #a list object that contains networkx graph objects
    
    #First, we copy the graph just in case, so we never alter the original graph
    VertexDeleted = Graph.copy()
    
    #Second, we remove the indicated veretex
    VertexDeleted.remove_node(Vertex)
    
    #This is copied directly from the documentation on how to make a list of the connected components of a graph
    return [VertexDeleted.subgraph(component).copy() for component in nx.connected_components(VertexDeleted)]

def isPath(Graph):
    #INPUT
    #
    #Graph - a networkx graph object
    #   This is used as the graph under inspection
    #
    #OUTPUT
    #
    #True or False, depending on whether the graph is a cycle or not
    
    #First, paths must be connected
    if not nx.is_connected(Graph):
        return False
    
    #Then we check to see if there are only vertices of degree 1 and 2 (or in the edge cases of P_2 only degree 1 and the trivial graph only degree 0)
    VertexDegrees = set(Degree for (Vertex, Degree) in Graph.degree())
    if VertexDegrees == {1, 2} or VertexDegrees == {1} or VertexDegrees == {0}:
        return True
    else:
        return False

def _NumTerminalPaths(Graph, Vertex):
    #INPUT
    #
    #Graph - a networkx graph object
    #   This is used as the graph under inspection
    #Vertex - a networkx vertex object
    #   This is used to be the vertex that is removed
    #
    #OUTPUT
    #
    #an integer
    #   This represents the number of terminal paths that emanate from the supplied vertex
        
    return sum([isPath(nx.subgraph(Graph,set(Component.nodes()).union(set((Vertex,))))) for Component in _DeletedConnectedComponents(Graph,Vertex)])

def isCycle(Graph):
    #INPUT
    #
    #Graph - a networkx graph object
    #   This is used as the graph under inspection
    #
    #OUTPUT
    #
    #True or False, depending on whether the graph is a cycle or not
    
    #First, cycles must be connected
    if not nx.is_connected(Graph):
        return False
    
    #Then we check to see if there are only vertices of degree 2
    VertexDegrees = set(Degree for (Vertex, Degree) in Graph.degree())
    if VertexDegrees == {2}:
        return True
    else:
        return False

def _NumTerminalCycles(Graph, Vertex):
    #INPUT
    #
    #Graph - a networkx graph object
    #   This is used as the graph under inspection
    #Vertex - a networkx vertex object
    #   This is used as the vertex under inspection
    #
    #OUTPUT
    #
    #an integer
    #   This represents the number of terminal cycles that emanate from the supplied vertex
    
    return sum([isCycle(nx.subgraph(Graph,set(Component.nodes()).union(set((Vertex,))))) for Component in _DeletedConnectedComponents(Graph,Vertex)])

def _FindPreferredVertices(Graph):
    #INPUT
    #
    #Graph - a networkx graph object
    #   This is used as the graph under inspection - _ShrinkGraph() has already been applied to this graph, performing all valid contractions
    #
    #OUTPUT
    #
    #a list of vertices that have more than one terminal paths, and/or have a fort they power dominate (but aren't inactive while considering all previous preferred vertices)
    #
    #NOTE: this leverages that _ShrinkGraph() has already been called on the graph - so all terminal paths are just terminal leaves. If this function is called on a graph without first contracting the graph all terminal paths that are not leaves will be considered forts that make the associated cut vertex a f-preferred vertex
        
    Pref = set()
    
    # We iterate over all cut vertices
    for vertex in nx.articulation_points(Graph):
        num_leaves = 0
        vertex_deleted_subgraph = nx.induced_subgraph(Graph, set(Graph.nodes())-set((vertex,)))
        # we then iterate over the connected components of the vertex-deleted subgraph, checking for forts and leaves
        for connected_component_vertices in nx.connected_components(vertex_deleted_subgraph):
            # a leaf is a degree 1 vertex, which would leave the connected component being a single vertex
            if len(connected_component_vertices) == 1:
                num_leaves += 1
                # if this isn't the first leaf that's associated with this cut vertex, then the vertex is a b-preferred vertex
                if num_leaves == 2:
                    Pref.add(vertex)
                    break
            # assuming that the connected component isn't a leaf but the connected component is observed by the cut vertex, then the cut vertex is a f-preferred vertex
            elif connected_component_vertices.issubset(PowerDominate(Graph, set((vertex,)))):
                Pref.add(vertex)
        
    return _FPreferredFilter(Graph, Pref)

def _FPreferredFilter(Graph, FPreferredVertices):
    #INPUT
    #
    #Graph - a networkx graph object
    #   This is used as the graph under inspection
    #
    #FPreferredVertices - a list of vertices that have a terminal fort that they alone power dominate
    #   This is used as the preferred vertices that we will filter out redundancies from
    #
    #OUTPUT
    #
    #This filters out any f=preferred vertices that are within the fort of other f=preferred vertices
    
    
    InactiveBlues = set()
    PreferredVertices = []

    # for each vertex in our list
    for vertex in FPreferredVertices:

        # and the vertex has non-blue neighbors
        if vertex not in InactiveBlues:

            # We add the vertex to our output list and recalculate the blue vertices
            PreferredVertices.append(vertex)
            InactiveBlues = set(inactive_blue for inactive_blue in set(Graph.nodes()).intersection(PowerDominate(Graph, PreferredVertices)) if Graph.degree(inactive_blue) == Graph.subgraph(PowerDominate(Graph, PreferredVertices)).degree(inactive_blue))
    return PreferredVertices


def _DegreeDistanceRating(Graph, Vertex, PreferredVertices = None):
    #INPUT
    #
    #Graph - a networkx graph object
    #   This is used as the graph under inspection
    #Vertex - a networkx vertex object
    #   This is used as the vertex under inspection
    #PreferredVertices - a set object containing networkx vertex objects (defaults to an empty set)
    #   This is the set of vertices that are guaranteed to be in some minimum power dominating set, so we may as well force all of our potential power dominating sets to include these. If the default value is input, then the first thing that happens is we find call the FindPreferredVertices
    #
    #OUTPUT
    #
    #Value - a floating point number
    #   This value encodes the degree (as the integer component) and the distance from a preferred vertex (the fractional component)
    
    #If PreferredVertices is empty, we will make sure they should be empty by calling FindPreferredVertices
    if (PreferredVertices) is None:
        PreferredVertices = _FindPreferredVertices(Graph)
    
    #We first encode the degree of the vertex into the integer portion of the return value
    Value = Graph.degree(Vertex)
    if len(PreferredVertices) == 0:

        #If there aren't any preferred vertices, then we simply return the vertex's degree
        return Value
    else:

        #Otherwise, we append the minimum distance to a preferred vertex as the fractional component
        MinDistanceToPreferred = min([len(nx.shortest_path(Graph, source = Vertex, target = PreferredVertex)) for PreferredVertex in PreferredVertices])
        Value += 1 - (1/MinDistanceToPreferred)
        return Value

def _TrimAndSortVertexSet(Graph, PreferredVertices=None):
    #INPUT
    #
    #Graph - a networkx graph object
    #   This is used as the graph under inspection
    #PreferredVertices - a set object containing networkx vertex objects (defaults to an empty set)
    #   This is the set of vertices that are guaranteed to be in some minimum power dominating set, so we may as well force all of our potential power dominating sets to include these. If the default value is input, then the first thing that happens is we find call the FindPreferredVertices
    #
    #OUTPUT
    #
    #a list of networkx node components
    #   This has the highest degree vertices at the front of the list and only contains vertices of degree 3 or higher
    
    #First we sort the list of vertices by degree with high degree vertices first
    if PreferredVertices==None:
        PreferredVertices = _FindPreferredVertices(Graph)
    
    return [Vertex for Vertex in sorted(nx.nodes(Graph), key=lambda Vertex : _DegreeDistanceRating(Graph, Vertex, PreferredVertices), reverse=True) if Graph.degree(Vertex) >= 3]

def _FindInactiveBlues(Graph, PreferredVertices = None):
    #INPUT
    #
    #Graph - a networkx graph object
    #   This is used as the graph under inspection
    #PreferredVertices - a set object containing networkx vertex objects (defaults to an empty set)
    #   This is the set of vertices that are guaranteed to be in some minimum power dominating set, so we may as well force all of our potential power dominating sets to include these. If the default value is input, then the first thing that happens is we find call the FindPreferredVertices
    #
    #OUTPUT
    #
    #a list of networkx vertex objects
    #   These vertices may be omitted from consideration of minimum power dominating sets
    
    #If PreferredVertices is empty, we will make sure they should be empty by calling FindPreferredVertices
    if (PreferredVertices) is None:
        PreferredVertices = _FindPreferredVertices(Graph)
    
    #We initially perform the domination step from the preferred vertices
    DominatedBlues = Dominate(Graph, PreferredVertices)
    
    #We then zero force from this initial set
    FinalBlues = ZeroForce(Graph, DominatedBlues)
                
    #The vertices that have no uncolored neighbors are then the resulting list that we are interested in
    return [Vertex for Vertex in FinalBlues if Graph.degree(Vertex) == Graph.subgraph(FinalBlues).degree(Vertex)]

def _SortValidNonPreferredVertices(Graph, PreferredVertices=None):
    #INPUT
    #
    #Graph - a networkx graph object
    #   This is used as the graph under inspection
    #PreferredVertices - a set object containing networkx vertex objects (defaults to an empty set)
    #   This is the set of vertices that are guaranteed to be in some minimum power dominating set, so we may as well force all of our potential power dominating sets to include these. If the default value is input, then the first thing that happens is we find call the FindPreferredVertices
    #
    #OUTPUT
    #
    #ValidNonPreferredVertices - a list object of networkx vertex objects
    #   This is a list of all the non-preferred vertices, that aren't totally colored with no uncolored neighbors
    
    #First we need to gather the list of preferred vertices
    if PreferredVertices==None:
        PreferredVertices = _FindPreferredVertices(Graph)

    #Second we need to gather the list of inactive blue vertices
    InactiveBlues = _FindInactiveBlues(Graph, PreferredVertices)
    
    #Now we gather the list of vertices of degree 3 or higher (this by default also sorts the list)
    SortedVertices = _TrimAndSortVertexSet(Graph)
    ValidNonPreferredVertices = []
    
    #Now we iterate through the list of our sorted vertices, and if it is not a preferred vertex, then we append this to the list that we will end up returning
    [ValidNonPreferredVertices.append(Vertex) for Vertex in SortedVertices if (Vertex not in PreferredVertices and Vertex not in InactiveBlues)]
            
    #As a fail safe, if there aren't any vertices, we'll just return all but the preferred vertices
    if len(ValidNonPreferredVertices) == 0:
        
        #We will alert to the command line that there are no valid non-preferred vertices
        assert RuntimeWarning("There happened to be no valid, non-preferred vertices")
        [ValidNonPreferredVertices.append(Vertex) for Vertex in nx.nodes(Graph)]

    #Finally, since we've iterated through all of the vertices, we can return the list we've constructed
    return ValidNonPreferredVertices

def _GetLowDegVerts(Graph):
    #INPUT
    #Graph - a networkx graph object
    #   This is used as the graph under inspection
    #
    #OUTPUT
    #a list of networkx node objects
    #   This is a list of all of the vertices that have degree 1 or 2 on the input graph
    
    return [Vertex for Vertex,Degree in Graph.degree() if Degree<3]

def _ShortenPath(Graph, Path):
    #INPUT
    #
    #Graph - a networkx graph object
    #   This is used as the graph under inspection
    #Path - a netwrokx graph object
    #   This is  the path to be shortened in the input graph
    #
    #OUTPUT
    #
    #GraphCopy - a networkx graph object
    #   This is the input graph, but with Path shortened to at most a P_2
    
    #First we have to check to see if the input path is actually a path
    if not isPath(Path):
        
        #If not then we cannot proceed
        raise nx.NetworkXNoPath('The input is not a path')
    else:
        #Remove all the degree 2 nodes
        Graph.remove_nodes_from([Vertex for Vertex in Path.nodes() if Path.degree(Vertex)==2])
                
        #Add an edge between the 2 remaining nodes
        RemainingNodes = [Vertex for Vertex in Path.nodes() if Path.degree(Vertex)==1]
        Graph.add_edge(RemainingNodes[0],RemainingNodes[1])
        return Graph

def _ShortenAllPaths(Graph):
    #INPUT
    #
    #Graph - a networkx graph object
    #   This is used as the graph under inspection
    #
    #OUTPUT
    #
    #Graph - a networkx graph object
    #   This is the input graph, but with all of the sub-paths shortened to at most a P_2
    
    #First we start by creating a copy of the input graph, so we don't alter it in any way
    GraphCopy = copy.deepcopy(Graph)
    
    #We will inspect only the vertices in the input graph of degree 1 and 2, since paths have no vertices of degree 3 or higher
    LowDegVerts = _GetLowDegVerts(Graph)
    
    #We will iterate through the connected components of the subgraph induced by these low degree vertices
    Paths = copy.deepcopy(Graph.subgraph(LowDegVerts))
    
    #And we shorten all of the valid paths
    [_ShortenPath(Graph, Paths.subgraph(Component)) for Component in nx.connected_components(Paths) if (len(Component)>2 and isPath(Paths.subgraph(Component)))]
            
    #Once we've gone through each of the connected components, we return the graph
    return Graph

def _TrimAllTerminalPaths(Graph):
    #INPUT
    #
    #Graph - a networkx graph object
    #   This is used as the graph under inspection
    #
    #OUTPUT
    #
    #Graph - a networkx graph object
    #   This is the input graph, but with terminal paths shortened by one
    
    Graph.remove_nodes_from([
        Vertex for Vertex,Degree in Graph.degree() if Degree==1 and max([
            Degree for Vertex,Degree in Graph.degree(Graph.neighbors(Vertex))
        ])==2
    ])
    return Graph

def _ShrinkGraph(Graph):
    #INPUT
    #
    #Graph - a networkx graph object
    #   This is used as the graph under inspection
    #
    #OUTPUT
    #
    #GraphCopy - a networkx graph object
    #   This is a deep copy of the input graph, sub-paths shortened to at most P_4s and terminal paths reduced to leaves
    
    #First we start by creating a copy of the input graph, so we don't alter the original in any way
    GraphCopy = copy.deepcopy(Graph)
    
    #Then we condense all sub-paths to at most P_2s
    GraphCopy = _ShortenAllPaths(GraphCopy)
    
    #Then we remove the degree 1 vertices of terminal paths of length at least 3
    #Since we shortened, and then trimmed, this has the effect of reducing all terminal paths to be P_2s as well as all sub paths
    GraphCopy = _TrimAllTerminalPaths(GraphCopy)
    
    #Once all of this is done, we may return the altered graph
    return GraphCopy

def _PDSIterator(NumWorkers,PDVertices,VertexList,nAdditionalVertices,WorkerID):
    #INPUT
    #
    #NumWorkers - an integer
    #   This is going to be the number of processes to split into
    #PDVertices - a list of vertex labels
    #   This is the list of vertices to be appended to a potential power dominating set
    #VertexList - a list of vertex labels
    #   This is the vertices contained in Graph sorted by the likelihood function
    #nAdditionalVertices - an integer
    #   This is used as the number of vertices to add to PD vertices
    #WorkerID - an integer
    #   This is used as the number of jobs to skip because other processes will process that particular subset
    #
    #OUTPUT
    #
    #One by one a set of vertices are returned

    for counter,subset in enumerate(it.combinations(VertexList,nAdditionalVertices)):
        if counter%NumWorkers == WorkerID:
            yield list(PDVertices)+list(subset)
        else:
            continue

def _PDSHelper(Graph,NumWorkers,PDVertices,VertexList,nAdditionalVertices,WorkerID):
    #INPUT
    #
    #Graph - a networkx graph object
    #   This is used as the graph under inspection
    #NumWorkers - an integer
    #   This is going to be the number of processes to split into
    #PDVertices - a list of vertex labels
    #   This is the list of vertices to be appended to a potential power dominating set
    #VertexList - a list of vertex labels
    #   This is the vertices contained in Graph sorted by the likelihood function
    #nAdditionalVertices - an integer
    #   This is used as the number of vertices to add to PD vertices
    #WorkerID - an integer
    #   This is used as the number of jobs to skip because other processes will process that particular subset
    #
    #OUTPUT
    #
    #There is no output. If a power dominating set is found a file will be created that contains it, or a file will be created indicating no power dominating set was found.

    for subset in _PDSIterator(NumWorkers,PDVertices,VertexList,nAdditionalVertices,WorkerID):
        if isPDS(Graph,subset):

            # If a pds is found, use pickle to dump it to a file that can be seen by the main process
            with open(f"ValidPDS.worker-{WorkerID}.nAV-{nAdditionalVertices}.pickle", "wb") as OutputFile:
                pickle.dump(subset,OutputFile)
                return
        else:
            # Otherwise keep looping through the assigned work
            continue

    # If no pds is found in the assigned work, dump a file that can be seen by the main process
    with open(f"NOPDS.worker-{WorkerID}.nAV-{nAdditionalVertices}.txt", "w") as OutputFile:
        OutputFile.write("")
    return

def _PDSWaiter(NumWorkers,PDVertices,VertexList,nAdditionalVertices):
    #INPUT
    #
    #NumWorkers - an integer
    #   This is going to be the number of processes to split into
    #PDVertices - a list of vertex labels
    #   This is the list of vertices to be appended to a potential power dominating set
    #VertexList - a list of vertex labels
    #   This is the vertices contained in Graph sorted by the likelihood function
    #nAdditionalVertices - an integer
    #   This is used as the number of vertices to add to PD vertices
    #
    #OUTPUT
    #
    #There is no output. This process checks the status of the _PDSHelper() processes periodically. The input parameters are used to wait a dynamic amount of time, if the processes are given more work then this will wait longer

    first_pass = True
    while True:

        # simulate the first process doing work
        dummy_counter = 0
        starting_time = time.time()
        for subset in _PDSIterator(NumWorkers,PDVertices,VertexList,nAdditionalVertices,0):
            
            # This allows a short-circuit that the causes a check after at most 2 seconds after the start of the search - because a PDS may be found rather quickly based on sorting the vertex set
            if first_pass:
                if time.time()-starting_time > 2:
                    first_pass = False
                    break

        # Look at the working directory for files that the different processes will make, categorized on whether a PDS was found or not
        valid_pds_files = []
        done_processes = []
        [valid_pds_files.append(file) for file in os.listdir() if "ValidPDS.worker-" in file and os.stat(file).st_size>0]
        [done_processes.append(file) for file in os.listdir() if "NOPDS.worker-" in file]

        # If at least on PDS was found, then stop all currently working child processes and return
        if len(valid_pds_files) > 0:
            # print("The process should end because something has been found")
            for child in multiprocessing.active_children():
                child.terminate()
            for child in multiprocessing.active_children():
                child.join()
            return
        elif len(done_processes)==NumWorkers:
            # print("The process should end because all the workers have returned)
            for child in multiprocessing.active_children():
                child.terminate()
            for child in multiprocessing.active_children():
                child.join()
            return

def _CheckForPDSOfSize(Graph,NumWorkers,PDVertices,VertexList,nAdditionalVertices):
    #INPUT
    #
    #Graph - a networkx graph object
    #   This is used as the graph under inspection
    #NumWorkers - an integer
    #   This is going to be the number of processes to split into
    #PDVertices - a list of vertex labels
    #   This is the list of vertices to be appended to a potential power dominating set
    #VertexList - a list of vertex labels
    #   This is the vertices contained in Graph sorted by the likelihood function
    #nAdditionalVertices - an integer
    #   This is used as the number of vertices to add to PD vertices
    #
    #OUTPUT
    #
    #PDS - a list of vertex labels that form a power dominating set or None if no power dominating set is found with the input number of vertices

    PDS = None
    Workers = []
    
    # This is where the separate processes are forked, each trying to find a power dominating set
    for WorkerID in range(NumWorkers):
        Worker = multiprocessing.Process(target=_PDSHelper, args=(Graph,NumWorkers,PDVertices,VertexList,nAdditionalVertices,WorkerID))
        Workers.append(Worker)
        Worker.start()
    _PDSWaiter(NumWorkers,PDVertices,VertexList,nAdditionalVertices)
    
    # Once all the workers have finished, check for any valid power dominating sets with the 
    found = False
    PDS_files = []

    # Gather all the files that the subprocesses created
    [PDS_files.append(f) for f in os.listdir('.') if os.path.isfile(f) and 'ValidPDS.worker-' in f]
    
    # Iterate through these files based off of their size, this fixes a bug where a process hasn't completed writing the pds to the file before being terminated
    for file in sorted(PDS_files, key=lambda file: os.stat(file).st_size, reverse=True):
        if not found:

            # Only record the first valid power dominating set that is found in the directory
            found = True
            with open(file, "rb") as input_file:
                PDS = pickle.load(input_file)

        # Remove the file
        os.remove(file)

    # Remove all the files for workers that did not find a pds
    [os.remove(file) for file in os.listdir() if os.path.isfile(file) and "NOPDS.worker-" in file]
    return PDS

def minpds(Graph, NumWorkers = None):
    #INPUT
    #
    #Graph - a networkx graph object
    #   This is used as the graph under inspection
    #NumWorkers - an integer (defaults to None)
    #   This is going to be the number of processes to split into
    #
    #OUTPUT
    #
    #PDS - an list of vertex labels
    #   This is a minimum power dominating set

    #If the number of workers isn't passed into the funciton, automatically determine it
    if NumWorkers == None:
        NumWorkers = max(1,multiprocessing.cpu_count()-1)

    Graph = _ShrinkGraph(Graph)

    PDVertices = _FindPreferredVertices(Graph)

    VertexList = _SortValidNonPreferredVertices(Graph,PDVertices)

    # Starting with the set of preferred vertices (0 additional), check for a pds by successively adding an additional vertex
    for nAdditionalVertices in range(Graph.number_of_nodes()):
        PDS = _CheckForPDSOfSize(Graph,NumWorkers,PDVertices,VertexList,nAdditionalVertices)
        if PDS == None:
            continue
        else:
            return PDS

    return

def pdn(Graph, NumWorkers = None):
    #INPUT
    #
    #Graph - a networkx graph object
    #   This is used as the graph under inspection
    #NumWorkers - an integer (defaults to None)
    #   This is going to be the number of processes to split into
    #
    #OUTPUT
    #
    #PDN - an integer
    #   This is the count of all the vertices in the given power dominating set for each of the connected components


    if NumWorkers == None:
        NumWorkers = max(1,multiprocessing.cpu_count()-1)

    #Semantically, the power dominating number is the length of a minimum power dominating set, so we have to find a minimum power dominating set
    PDN = len(minpds(Graph, NumWorkers))

    #Now we can return this number
    return PDN

def _work_generator(Generator, WorkerID, nWorkers):
    #INPUT
    #
    #Generator - any iterable object
    #   this is used as the thing that will be split up
    #WorkerID - an integer
    #   This is used as the number of jobs to skip because other processes will process that particular subset
    #nWorkers - an integer
    #   This is the number of pieces the Generator will be split into
    #
    #OUTPUT
    #
    #One by one the pieces to the given part of the generator

    for JobID,Job in enumerate(Generator):
        if (JobID % nWorkers) == WorkerID:
            #This worker is tasked with this job
            yield Job
        else:
            #Another worker is tasked with this job
            continue
            
def _ParallelFindAllMinPDSPart(Graph, PDN, ID, nWorkers):
    #INPUT
    #
    #Graph - a networkx graph object
    #   this is used as the graph to inspect
    #PDN - an integer
    #   This is the power domination number of the given graph
    #ID - an integer
    #   This is used as the worker ID for use in _work_generator()
    #nWorkers - an integer
    #   This is the number of workers available to inspect the graph
    #
    #OUTPUT
    #
    #There is no return persay, but a pickle file will be created with the following:
    #PDSs - a list of list of vertex labels
    #   This is some of the minimum power dominating sets of the given graph

    PDSs = []
    for vertices in _work_generator(it.combinations(Graph.nodes(),PDN), ID, nWorkers):
        if isPDS(Graph,vertices):
            PDSs.append(vertices)
    with open(f'all.pds.part.{ID}.pickle', 'wb') as OutputFile:
        pickle.dump(PDSs, OutputFile)
    return

def _ParallelFindMinAllPDSFinish():
    #INPUT
    #
    #Nothing
    #   This function will search the active directory for pickel files that contain minimum power dominating sets
    #
    #OUTPUT
    #
    #PDSs - a list of list of vertex labels
    #   This is the list of all minimum power dominating sets located

    PDSs = []
    for file in [f for f in os.listdir('.') if os.path.isfile(f) and 'all.pds.part.' in f]:
        Temp = []
        with open(file, 'rb') as InputFile:
            Temp = pickle.load(InputFile)
        for PDS in Temp:
            PDSs.append(PDS)
        os.remove(file)
    return PDSs
            
def allminpds(Graph, PDN = None, NumWorkers = None):
    #INPUT
    #
    #Graph - a networkx graph object
    #   This is used as the graph to be inspected
    #PDN- an integer (defaults to None)
    #   This is the power domination number of the input graph, if none is given it is determined
    #NumWorkers - an integer (defaults to None)
    #   This is the number of workers that can be allocated to determining all minimum power dominating sets, if none is given, it is determined
    #
    #OUTPUT
    #
    #PDSs - a list of list of vertex labels
    #   This is the list of all minimum power dominating sets located

    if PDN == None:
        PDN = pdn(Graph, NumWorkers)

    if NumWorkers == None:
        NumWorkers = min(1,multiprocessing.cpu_count()-1)
        
    Workers = []
    for ID in range(NumWorkers):
        Worker = multiprocessing.Process(target=_ParallelFindAllMinPDSPart, args=(Graph, PDN, ID, NumWorkers))
        Worker.start()
        Workers.append(Worker)
    for Worker in Workers:
        Worker.join()
    return _ParallelFindMinAllPDSFinish()