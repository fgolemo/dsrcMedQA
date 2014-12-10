import cPickle as pickle
import numpy as np


class AnnotationAnalysis():

	def __init__(self, filename):
		self.questions = pickle.load(open(filename, 'rb'))


	def analyze(self):
		"""
		Calculates some statistics about the annotation
		"""
		analysis = []
		for q in self.questions:

			if len(q['mc_entities']) > 0:
				avg_mc_entity_count = sum(map(len, q['mc_entities'])) / float(len(q['mc_entities']))
			else:
				avg_mc_entity_count = 0

			a = {
				'QID': q['QID'],

				# Percentage of annotated mc answers
				'mc_annotation_rate': float(len(q['mc_entities'])) / len(q['mc_text']),

				# Number of question entities
				'q_entity_count': len(q['q_entities']),

				# Average number of mc answer entities
				'avg_mc_entity_count': avg_mc_entity_count
			}
			analysis.append(a)

		self.analysis = analysis
		return self.analysis


	def get_fully_annotated(self):
		"""
		Returns a list of QIDs of questions that are fully annotated,
		that is, have at least one entitiy in every question part. 
		"""
		return [a['QID'] for a in self.analysis if a['mc_annotation_rate']==1 and a['q_entity_count']>0]


	def get_under_annotated(self,threshold=1):
		"""
		Returns a list of QIDs of questions that are not fully annotated
		"""
		return [a['QID'] for a in self.analysis if a['mc_annotation_rate']<threshold]


	def get_somewhat_annotated(self, threshold=.5):
		"""
		Returns a list of QIDs of questions with mc_annotation_rate > threshold
		"""
		return [a['QID'] for a in self.analysis if a['mc_annotation_rate']>threshold]


	def percentage_fully_represented(self):
		"""
		Calculates the percentage of the questions that is fully annotated 
		"""
		num_fully_repr = len([a['mc_annotation_rate'] for a in self.analysis if a['mc_annotation_rate']==1])
		return float(num_fully_repr) / float(len(self.analysis)) * 100

	

