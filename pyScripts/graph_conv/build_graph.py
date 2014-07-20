import cPickle as pickle
import numpy as np
import igraph as ig


def build_graph(connList, vertexNames, outfile=None):
	"""Turn connectivity list and vertex names into iGraph object

	The connectivity list must be a pickle containing an array with three cols,
	each containing the source, target and edge weight respectively. The edge
	weight is supposed to be the numer of relations between source and target.
	This weight is referred to as the rel_weight (as opposed to the deg_weight)

	The vertexNames is also a pickle with a dictionary where every uri is a key
	whose value is the corresponding vertex id (just an integer). Note that the
	vertex id's are NOT preserved during conversion: iGraph creates new ids on
	the fly (numbering vertices in the order they appear in the edgelist).

	Args:
		- connList: filename of the pickle file containing a matrix, each row 
		containing source, target, weight
		- vertexNames: filename of a pickle containing a dictionary with uri's
		 as keys and vertex ids as values
		- outfile: filename where a GraphML version of the graph will be stored
		If outfile=None, then the graph object is only returned

	Returns
		- the iGraph graph object
		- stores an GraphML file if outfile is set.
	"""
	
	print('(1/6) Starting conversion, could take a while...')

	connList = pickle.load(open(connList,'rb'))
	connArr = np.array(connList, dtype='int')
	del connList
	vertexNames = pickle.load(open(vertexNames,'rb'))
	print('(2/6) Loading of pickle files completed.')

	edges = [{'source':s,'target':t,'rel_weight':w} for s,t,w in connArr]
	vertices = [{'orig_id':int(id),'uri':uri} for uri,id in vertexNames.iteritems()]
	print ('(3/6) Cleaning edges and vertices completed')

	graph = ig.Graph.DictList(vertices,edges, vertex_name_attr='orig_id')
	del graph.es['source']
	del graph.es['target']	
	print ('(4/7) iGraph object created')

	degrees=graph.degree()
	for e in graph.es:
		e['deg_weight'] = np.log(degrees[e.source]) + np.log(degrees[e.target])
	print ('(5/6) Finished calculating degree based weights')

	print('Summary of the graph:')
	ig.summary(graph)

	if outfile:
		graph.write_graphml(outfile)
		print('(6/6) GraphML file "'+outfile+'" saved; finished!')
	else:
	 	print('(6/6) Finished!')

	return graph