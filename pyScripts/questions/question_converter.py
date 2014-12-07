import cPickle as pickle
import csv

class QuestionConverter():

	def load_csv(self,filename='data/question_collection.csv'):
		csvfile = open(filename, 'rb')
		dreader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
		questions = [a for a in dreader]

		for q in questions:
		    # Replace letter of correct mc by index (a-->0, b-->1, ...)
		    q['correct'] = 'abcdefghijklmnopqrstuvwxyz'.index(q['correct'])

		self.questions = questions
		return questions

	def load_valid_ids(self, filename='data/valid_question_ids.csv'):
		csvfile = open(filename, 'rb')
		reader = csv.reader(csvfile, delimiter=';', quotechar='"')
		ids = [id for id in reader]
		self.valid_ids = map(list, zip(*[id for id in reader]))[0]
		return self.valid_ids

	def get_valid_questions(self):
		# To do: check if variables exist already
		valid_ids = self.load_valid_ids()
		questions = self.load_csv()

		return [q for q in questions if q['QID'] in valid_ids]

