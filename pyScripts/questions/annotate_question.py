import requests
from pprint import *
import cPickle as pickle
import numpy as np
import json
from repo.pyScripts.progress import ProgressBar

class AnnotateQuestion():

	# Class variables
	redirect_list_file = 'redirects_transitive_en.nt.redirectList.p'
	redirect_dict_file = 'redirects_transitive_en.nt.redirectDict.p'
	spotlight_uri = 'http://dbps.florian.ops.few.vu.nl/rest/annotate'
	question_part_separator = ' aaaaaaaa '

	def annotate_text(self, text, confidence=0.4, support=10):
		"""
		Annotates text using DBPedia Spotlight
		"""
		data = {
			'text': text,
			'confidence': confidence,
			'support': support
		}
		headers = {'Accept': 'application/json'}

		r = requests.get(self.spotlight_uri, params=data, headers=headers)
		return r.json()


	def annotate_question(self, text, mc, confidence=0.4, support=10):
		"""
		Annotates question and mc's at once using DPpedia Spotlight

		The question text and all mc's are combined in one string
		which is annotated. The recognized entities are returned
		afterwards splitting them in their respective parts.
		"""

		sep = self.question_part_separator
		annotation =  self.annotate_text( text+sep+sep.join(mc), confidence, support)

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


	def extract_uris(self, annotation, redirect=True):
		"""
		Replaces annotations by uri's and removes duplicates

		When redirect=True, the uri's are moreover replaced by
		possible redirects. Otherwise, the uri's from the 
		annotation are returned.
		"""

		output = []
		for part in annotation:
			if part != []: 
				part_uris = ['<'+x['@URI']+'>' for x in part]
				if redirect:
					part_uris = map(self.follow_uri_redirect, part_uris)
				output.append(list(set(part_uris)))
		return output


	def load_redirects(self):
		"""
		Loads the redirection lists & dictionaries
		"""
		self.redirect_list =  pickle.load(open(self.redirect_list_file, 'rb'))
		self.redirect_dict =  pickle.load(open(self.redirect_dict_file, 'rb'))


	def follow_uri_redirect(self, uri):
		"""
		Returns the 'real' uri, following possible redirects. 
		"""
		if uri in self.redirect_list:
			return self.redirect_dict[uri]
		else:
			return uri

	def ad_hoc_score(self, manual_ann, spotlight_ann):
		"""
		Own ad hoc measure
		"""
		if len(manual_ann) == 0 or len(spotlight_ann) == 0:
			return 'empty annotation'

		# Note: we also remove duplicates!
		MA = set(manual_ann) 
		A = set(spotlight_ann)

		return (len(A ^ MA) + 0.0) / len(A)
		

	def precision_recall(self, manual_ann, spotlight_ann):
		"""
		Calculates the precision of the annotation
		"""
		if len(manual_ann) == 0 or len(spotlight_ann) == 0:
			return 'empty annotation'

		# Note: we also remove duplicates!
		MA = set(manual_ann) 
		A = set(spotlight_ann)

		tp = len( A & MA ) + .0 # True  positives
		fp = len( A - MA ) + .0 # False positives
		fn = len( MA - A ) + .0 # False negatives

		# Always defined when A and MA nonempty
		precision = tp / (tp + fp)
		recall = tp / (tp + fn)

		return [precision, recall]


	def F1_measure(self, manual_ann, spotlight_ann):
		"""
		Calculates F1 measure for an annotation with respect
		to a certain manual annotation
		"""
		
		if len(manual_ann) == 0 or len(spotlight_ann) == 0:
			return 'empty annotation'

		precision_recall = self.precision_recall(manual_ann, spotlight_ann)
		precision = precision_recall[0]
		recall = precision_recall[1]

		if precision+recall == 0:
			return 'NaN'
		else:
			return (2.0 * precision * recall) / (precision + recall)


	def optimize_parameters(self, man_ann_questions, confValues=[.2], suppValues=[20], progress=False):
		"""
		Determines good parameters for the spotlight annotation
		"""
		if progress:
			p = ProgressBar(len(man_ann_questions)*len(confValues)*len(suppValues))
			i = 0

		results = []
		for confidence in confValues:
			for support in suppValues:
				for q in man_ann_questions:
					
					spotlight_ann = self.annotate_question(q['qtext'], q['mc'], confidence, support)
					spotlight_ann = self.extract_uris(spotlight_ann)
					spotlight_ann = self.flatten(spotlight_ann)
					manual_ann = q['q_entities'] + self.flatten(q['mc_entities'])

					F1 = self.F1_measure(manual_ann, spotlight_ann)
					results.append({
						'confidence': confidence,
						'support': support,
						'F1': F1,
						'QID': q['QID'],
						'spotlight_ann': spotlight_ann
					})

					if progress:
						p.animate(i)
						i += 1
		return results

	def flatten(self, myList):
		"""
		Flattens a two dimensional list.
		"""
		return [item for subList in myList for item in subList ]


	def annotate_question_collection(self, collection, confidence=.4, support=10, progress=True):
		if progress:
			p = ProgressBar(len(collection))
			i = 0

		for q in collection:
			ann = self.annotate_question(q['q_text'], q['mc_text'], confidence=confidence, support=support)
			ann = self.extract_uris(ann)
			q['q_entities'] = ann[0]
			q['mc_entities'] = ann[1:]
			
			if progress:
				p.animate(i)
				i += 1

		return collection




	# Old functions
	get_real_uri = follow_uri_redirect
	uri_annotation = extract_uris
	read_pickles = load_redirects



if __name__ == '__main__':

	"""
	Annotates the question in selected_question_objects.p
	"""

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
	"""




