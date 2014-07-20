import numpy as np
import igraph as ig
from SPARQLWrapper import SPARQLWrapper, JSON
import copy
import pprint

class QAException(Exception):
    pass


def find_vertex_index(graph, uri_str):
	"""Finds the index of a vertex based on the uri attribute
	"""
	try:
		return graph.vs.find(uri=uri_str).index
	except:
		return None


def average_qa_distance(distances):
	"""Calculates the q-a distance based on distance matix

	The input must be a n x m matrix if there are n entities in the answer
	and m entities in the question. Cell (n,m) then contains the distance 
	between the n-th answer entity and the m-th question entity.

	For every question entity q, we first take the median of all the distances
	d(q,a) for a an answer entity. Then we average {d(q,a): q in question}.

	Entities that cannot be represented are removed and if no entities remain
	in the answer, it is assigned distance infinity.

	Args:
		distances: q-a distance matrix

	Returns:
		dist: the distance between the question and answer
	"""
	return np.average(np.median(distances,axis=0))


def rank_qa(graph, question1, answers1, method='deg_weight', qa_dist_fn = average_qa_distance):
	"""Ranks MC answers given as a list of uri's

	Args:
		graph: iGraph representation of the network
		question: a list of uri's
		answers: a list of lists; each list containing uri's of the entities
		in the corresponding multiple choice answer
		method: the weights to use: deg_weight (default), rel_weight or None
		qa_dist_fn: the function that gives the distance from a q-a distance
		matrix. Default to average_qa_distance

	Returns:
		best_guess:	index of the top ranked answer
		dist: vector of all distances
	"""
	question = copy.deepcopy(question1)
	answers = copy.deepcopy(answers1)
	
	if qa_dist_fn == None:
		qa_dist_fn = average_qa_distance

	# Replace uri's by indices and remove unrepresented & duplicate entities
	question = [find_vertex_index(graph,q) for q in question]
	question = list(set([q for q in question if q is not None]))
    
	if not question:
		raise QAException("None of the entities in the question can be found in the graph.")

	for i,ans in enumerate(answers):
		ans = [find_vertex_index(graph,entity) for entity in ans]
		ans = [entity for entity in ans if entity is not None]
		answers[i]=ans
    
	# Merge answers in one list for faster shortest path finding
	answer_lengths = map(len, answers)
	answers = [entity for ans in answers for entity in ans]
    
	# Calculate distances
	pairwise_dist = np.array(graph.shortest_paths(answers, question, weights=method))

	# Divide pairwise_dist in answers and calculate the distance for each answer
	qa_dist = np.array([])
	for k, v in enumerate(answer_lengths):
		start = sum(answer_lengths[:k])
		stop  = sum(answer_lengths[:k+1])
		ans_dist = pairwise_dist[start:stop,:]

		if len(ans_dist) == 0:
			 qa_dist = np.append(qa_dist, np.Inf)
		else:
			qa_dist = np.append(qa_dist, qa_dist_fn(ans_dist))
    
	return np.argmin(qa_dist), qa_dist


def search_entities(search, limit=10):
	"""Queries drugbank for entities with literals containing the search query
	"""

	if limit == 0:
		return []
	elif limit == None:
		lim  = ''
	else:
		lim = 'limit '+str(limit)

	csv_search = ("'"+search+"'").replace(" ", "','");

	query = (
	"select ?s1 as ?c1, ( bif:search_excerpt ( bif:vector ("+csv_search+") , ?o1 ) ) as ?c2, ?sc, ?rank, ?g where "
	+"""
	  { 
		{ 
		  { 
			select ?s1, ( ?sc * 3e-1 ) as ?sc, ?o1, ( sql:rnk_scale ( <LONG::IRI_RANK> ( ?s1 ) ) ) as ?rank, ?g where 
			{ 
			  quad map virtrdf:DefaultQuadMap 
			  { 
				graph ?g 
				{ 
				  ?s1 ?s1textp ?o1 .
	"""+"?o1 bif:contains ' ("+ search.replace(' ', ' AND ') +") ' option ( score ?sc ) ."+"""
				}
			  }
			}
			order by desc ( ?sc * 3e-1 + sql:rnk_scale ( <LONG::IRI_RANK> ( ?s1 ) ) )  """+lim+""" 
		  }
		}
	  }
	""")

	sparql = SPARQLWrapper("http://drugbank.bio2rdf.org/sparql")
	sparql.setQuery( query )
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()

	entities=[];
	for result in results["results"]["bindings"]:
	 	entities.append('<'+str(result["c1"]["value"])+'>')

	if limit == 1:
		if entities != []:
			return entities[0]
	else:
	 	return entities


def find_drugbank_entity(name, db_type="Drug", limit=1):
	"""Finds drugbank entity of a certain type (default: Drug) based on name

	Args:
		name: name of the entity to look for
		db_type: optional, type of the entity. Should be in the drugbank
		vocabulary, i.e. http://bio2rdf.org/drugbank_vocabulary:db_type.
		Default to 'Drug'
		limit: maximum number of entities to return (default 1)

	Returns:
		entity: uri of the entity
	"""
	query = (
		  "SELECT * WHERE { \n"
		+ "?s a <http://bio2rdf.org/drugbank_vocabulary:"+db_type+">.\n"
		+ "?s <http://www.w3.org/2000/01/rdf-schema#label> ?o.\n"
		+ "?o bif:contains '( "+name.replace(' ', ' AND ')+")'\n"
		+ "} LIMIT "+str(limit)
		)
    
	sparql = SPARQLWrapper("http://drugbank.bio2rdf.org/sparql")
	sparql.setQuery( query )
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()

	entities=[]
	for result in results["results"]["bindings"]:
		entities.append('<'+str(result["s"]["value"])+'>')

	if limit == 1:
		if entities != []:
			return entities[0]
	else:
		return entities


def represent_in_drugbank(question):
	"""Represents a question dictionary in DrugBank

	The question dictionary has the following structure
		- question_search: list of full text queries
		- question_entities: list of entities that must match in their label and
			be of a certain type, set in the following:
		- question_entity_type: the type, default 'Drug'
		- answers: a list of lists, each lists containing names of entities that
			must be machted in their label and be of the type Drug.
		- correct: index of the correct answer

	Args:
		question: the question dict (see above)

	Returns:
		question: the question dict with every query replaced by a drugbank uri
	"""
	q = copy.deepcopy(question)
    
    # Full text search for question entities
	entities = []
	for name in q['question_search']:
		if name[0] != '<':
			entities.append( search_entities(name,1) )
		else:
			entities.append(name)
	q['question_search'] = entities
    
	# Find entities of specific type
	entities=[]
	for name in q['question_entities']:
		if name[0] != '<':
			entities.append(find_drugbank_entity(name,q['question_entity_type']))
		else:
			entities.append(name)
	q['question_entities'] = entities

	# Search for answer entities
	for key, answer in enumerate(q['answers']): 
		entities=[]
		for name in answer:
			if name[0] != '<':
				entity = find_drugbank_entity(name)
				if entity:
					entities.append(entity)
				else:
					entities.append(search_entities(name,1))
			else:
				entities.append(name)
		q['answers'][key] = entities

	return q
