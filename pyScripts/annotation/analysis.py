from pprint import *
import cPickle as pickle
import numpy as np
import json

questions = pickle.load(open('annotated_questions_final.p', 'rb'))
pprint(questions[1])
print 'boe'