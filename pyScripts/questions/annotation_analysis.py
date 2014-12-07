from pprint import *
import cPickle as pickle
import numpy as np
import json

questions = pickle.load(open('annotated_questions_final.p', 'rb'))
analysis = []
for q in questions:

	if len(q['mc_entities']) > 0:
		avg_mc_entity_count = sum(map(len, q['mc_entities'])) / float(len(q['mc_entities']))
	else:
		avg_mc_entity_count = 0

	a = {
		'QID': q['QID'],

		# Ratio of represented mc answers
		'mc_representation': float(len(q['mc_entities'])) / len(q['mc']),

		# Number of question entities
		'q_entity_count': len(q['q_entities']),

		# Average number of mc answer entities
		'avg_mc_entity_count': avg_mc_entity_count
	}
	analysis.append(a)

pickle.dump(analysis, open('analysis.p', 'w'))
