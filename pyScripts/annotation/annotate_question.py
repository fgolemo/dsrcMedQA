import requests
from pprint import *
import cPickle as pickle
import numpy as np
import json

def annotate_question(text, mc, confidence=0.2, support=20):
	"""
	Annotates question and mc text with DBPedia entities using dbpedia spotlight

	See also github.com/dbpedia-spotlight/
	"""
	uri = "http://spotlight.dbpedia.org/rest/annotate/"

	sep = ' aaaaaaaa '
	data = {
		'text': text + sep + sep.join(mc),
		'confidence': confidence,
		'support': support
	}
	headers = {'Accept': 'application/json'}

	r = requests.get(uri, params=data, headers=headers)
	annotation = r.json()

	# pickle.dump(annotation, open('annotation.p', 'w'))
	# annotation = pickle.load(open('annotation.p', 'rb'))

	# Check annotation
	if 'Resources' not in annotation:
		return [[] for i in range(len(mc)+1)]

	# List with position of each part (text, mc1, mc2, mc3,... )
	# in the joined string.
	part_pos = np.insert(map(len, mc), 0, len(text)) 
	part_pos = part_pos + (np.ones(len(part_pos)) * len(sep))
	part_pos = np.cumsum(part_pos)

	partition = {}
	i = 0
	for entity in annotation['Resources']:
		pos = int(entity['@offset'])

		if pos >= part_pos[i]:	
			# Not in part[i], increase i untill part_pos[i] <= pos < part_pos[i+1]
			i += 1 
			while pos >= part_pos[i]:
				i += 1 
				partition[i] = []

		if (i not in partition):# or (partition[i] == None) :
		 	partition[i] = []
		partition[i].append(entity)

	return [v for k,v in partition.iteritems()]


def uri_annotation(annotation):
	"""
	Replaces annotations by uri's
	"""

	output = []
	for part in annotation:
		if part != []: 
			output.append( map(lambda x: x['@URI'], part) )
	return output


def main():
	text = "President Obama called Wednesday on Congress to extend a tax break USA"
	mc = ['USA has New York as a city', 'Holland not', 'I like Riemann', 'Yeah', 'Avjacie', 'ackeianc', 'Why Cauchy did not invent the lambda calculus']

	r = annotate_question(text,mc,.15,50)
	print uri_annotation(r)



if __name__ == '__main__':
	"""
	Annotates the question in selected_question_objects.p
	"""


	raw_questions =  pickle.load(open('selected_question_objects.p', 'rb'))
	questions = raw_questions ## IMPORTANT!!! CHANGE '2'
	annotated_questions = [];

	i=0;
	for q in questions:

		try:
			annotation = uri_annotation( annotate_question(q['qtext'], q['mc']) )
			
			# pickle.dump(annotation, open('annotation.p', 'w'))
			# annotation = pickle.load(open('annotation.p', 'rb'))

			q['q_entities'] = annotation[0]
			q['mc_entities'] = annotation[1:]
			
			annotated_questions.append(q)

		except:
			continue

		if i % 20 == 0:
			pickle.dump(annotated_questions, open('annotated_questions_'+str(i)+'.p', 'w'))	


		i += 1

	pickle.dump(annotated_questions, open('annotated_questions_final.p', 'w'))	




