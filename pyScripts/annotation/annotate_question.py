import requests
from pprint import *
import cPickle as pickle
import numpy as np
import json

class AnnotateQuestion():

	def annotate_question(self, text, mc, confidence=0.2, support=20):
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


	def uri_annotation(self, annotation):
		"""
		Replaces annotations by uri's
		"""

		output = []
		for part in annotation:
			if part != []: 
				output.append( map(lambda x: self.get_real_uri(x['@URI']), part) )
		return output


	def read_pickles(self):
		self.redirect_list =  pickle.load(open('redirects_transitive_en.nt.redirectList.p', 'rb'))
		self.redirect_dict =  pickle.load(open('redirects_transitive_en.nt.redirectDict.p', 'rb'))

	def get_real_uri(self, uri):
		if uri in self.redirect_list:
			return self.redirect_dict[uri]
		else:
			return uri


	def main(self):
		text = "President Obama called Wednesday on Congress to extend a tax break USA"
		mc = ['USA has New York as a city', 'Holland not', 'I like Riemann', 'Yeah', 'Avjacie', 'ackeianc', 'Why Cauchy did not invent the lambda calculus']

		r = self.annotate_question(text,mc,.15,50)
		print self.uri_annotation(r)



if __name__ == '__main__':
	"""
	Annotates the question in selected_question_objects.p
	"""

	a = AnnotateQuestion()

	raw_questions =  pickle.load(open('selected_question_objects.p', 'rb'))
	questions = raw_questions ## IMPORTANT!!! CHANGE '2'
	annotated_questions = [];

	i=0;
	for q in questions:

		try:
			annotation = a.uri_annotation( a.annotate_question(q['qtext'], q['mc']) )
			
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




