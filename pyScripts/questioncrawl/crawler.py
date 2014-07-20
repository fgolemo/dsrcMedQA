#####
# Imports
#
from bs4 import BeautifulSoup
import requests
import re
import json
import time
import os
import pprint
import string
import nltk


#####
# Extracts all questions and multiple choice answers from 
# pharmacology2000.com
# @param 	string		html page
# @param 	string 		optional url saved in every question
# @return	list 		list of questions (each a dictionary)
#
def extractQuestions(data,url=''):
	
	# Soup!
	soup = BeautifulSoup(data)

	# Loop through all questions and save data
	q_count = len(soup.find_all('li', class_='QuizQuestion'))
	questions = []

	# Test if really are MC questions (not selection)
	try:
		if soup.find(id='Q_0').contents[1].get('class')[0] != 'MCAnswers':
			return
	except:
		return 

	for q_id in range(0, q_count):
		try:
			# HTML question li (q) and question dictionary (question)
			q = soup.find(id='Q_'+str(q_id))
			question = {'mc':[],'q_id':q_id,'url':url}

			# Question text
			question['text'] = q.contents[0].text
			
			# Looup through multiple choice answers
			mc_num=0;
			# print q.contents[1].get('class')[0] == 'MCAnswers'
			for mc in q.contents[1].children:
				# Each question has multiple choice answers, which are saved
				# in a javascript variable I, from which we extract all data

				# I[q_num][3][mc_num] = new Array('mc answer','comment', true/false, ...
				regex 	= 'I\['+str(q_id)+'\]\[3\]\['+str(mc_num)+'\]=new Array\(\'.*\',[01]{1}'
				mc_data = re.search(regex, soup.text).group()[21:]
				
				# Save the text of this mc answer
				question['mc'].append(
				 	re.search("\'.*?\'",mc_data).group()[1:-1]
				)

				# Check if this is the right answer
				if mc_data[-1] == '1':
					question['answer'] = mc_num

				mc_num +=1

			questions.append(question);
		except:
			pass

	return questions




#####
# Crawls all pharmacology2000.com question pages. 
# Questions are stored in a text file (json or optinally csv)
# @param 	int		Maximal number pages to crawl, default 0 (no limit)
# @param 	bool	Also output CSV file, default to true.
# @output 	file 	text file with json or csv data
#
def crawl(MAX = 0, CSV = True):

	data = requests.get('http://www.pharmacology2000.com/learning2.htm').text
	soup = BeautifulSoup(data)

	# Loop through all of the links to question sets
	i=0; questionsets=[];
	for page in soup.find_all('a', href=re.compile('\/questions*[0-9]\/')):
		if (i < MAX) | (MAX == 0):
			questionsets.append(
				extractQuestions(
					requests.get(page.get('href')).text,
					page.get('href')
				)
			)
		i+=1


	# Export data to file
	file_name = 'data-'+str(int(time.time()))+'.txt'
	outfile =  open(file_name, 'w')
	json.dump(questionsets, outfile)
	outfile.close();

	if CSV:
		import analyse
		analyse.json2csv(file_name)



#####
# Converts the json file with question data to a csv file
# with some additional statistics.
# @param 	string		filename of the json txt file to convert
# @param 	string 		Seperator to use in CSV file. Default to ';'
# @output	file 		CSV file
#
def json2csv(filename, sep=';', minmc = 2):

	data =  json.loads(open(filename).read())
	outfile = open(filename[0:-4]+'.csv','w')
	outfile.write(
		  '"QID"'+sep
		 +'"Q set"'+sep+'"Q number"'+sep+'"URL"'+sep
		 +'"Question"'+sep+'"MC Answers"'+sep+'"Answer"'+sep
		 +'"Q word count"'+sep+'"MC total word count"'+sep+'"MC count"'
		 +'\n')

	qset=0;alpha='abcdefghijklmnopqrstuvwxyz';
	for questionset in data:
	 	if (questionset != None):
	 		
	 		q = 0;
			for question in questionset:
				if len(question['mc']) > minmc:

					output = (
						 'Q'+str(qset)+'#'+str(q)+sep
						+ str(qset) + sep
						+ str(q) + sep
						+ '"' + question['url'].encode('utf-8') + '"' + sep
						+ '"' + question['text'].encode('utf-8') + '"' + sep
						+ '"')
					
					i=0;
					for mc in question['mc']:
						output = (output 
							+ alpha[i]+') '
							+ question['mc'][i].encode('utf-8').replace('"','').replace(';',',')
							+ ';  ')
						i+=1

					if question['answer'] != '':
						output = output+ '"'+sep+alpha[int(question['answer'])]+sep
					else:
						output = output+ '"'+sep+' '+sep

					# Statistics
					qWordCount = len(nltk.tokenize.word_tokenize(question['text']))
					mcWordCount = len(nltk.tokenize.word_tokenize(string.join(question['mc'])))
					mcCount = len(question['mc'])

					output = (output 
							+ str(qWordCount) + sep
							+  str(mcWordCount) + sep
							+  str(mcCount))
					
					outfile.write(output + '\n')

	 			q+=1
		qset+=1


	outfile.close();




#####
# Demo 
#
def demo():
	data = open('demopage.html').read()	
	outfile =  open('demodata.txt', 'w')
	json.dump([extractQuestions(data)], outfile)
	outfile.close();




################################################################
################################################################



# For a demo on demopage.html
# demo()

# To export to csv
# json2csv('demodata.txt')


# To crawl some pages
# crawl(3)

# To crawl all pages
# crawl()


