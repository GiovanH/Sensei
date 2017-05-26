#python 3.6
#sensei_dataprocessing
from bs4 import BeautifulSoup
#import csv
import glob
import math
import pickle
import argparse
import os
import queue
import urllib3
import sys,traceback

def enums():
	final = dict();
	ues_label_enum = {
		0: 'The course objectives were clearly defined.',
		1: 'The course was well organized.',
		2: 'Overall, the course was excellent.',
		3: 'The instructor was well prepared in the subject area.',
		4: 'The instructor communicated information effectively.',
		5: 'The instructor seemed genuinely interested in teaching.',
		6: 'The instructor provided timely feedback.',
		7: 'The instructor was accessible outside of class.',
		8: 'The instructor evaluated students fairly.',
		9: 'Overall, this instructor was excellent.',
		10: 'I was free to ask questions and express my opinions and ideas.',
		11: 'My performance was evaluated fairly.',
		12: 'I discussed ideas from this course with others outside the classroom.',
		13: 'This course has been (or will be) of value to me.',
		14: 'This course inspired me to learn more.'
	}
	ues_label_enum.update({
		0: 'Course: Well Defined',
		1: 'Course: Organization',
		2: 'Course: Overall',
		3: 'Instructor: Preperation',
		4: 'Instructor: Communication',
		5: 'Instructor: Interest',
		6: 'Instructor: Responsive',
		7: 'Instructor: Accessibility',
		8: 'Instructor: Evalulation Objectivity',
		9: 'Instructor: Overall',
		10: 'Experience: Freedom to communicate',
		11: 'Experience: Evalulation Objectivity',
		12: 'Experience: Outside discussion',
		13: 'Experience: Course value',
		14: 'Experience: Inspiring'
	})
	final.update({'ues':ues_label_enum})
	rmp_label_enum = dict({
		'overall':'RMP: Overall',
		'wouldtakeagain':'RMP: Would take again',
		'difficulty':'RMP: Difficulty',
		'hottness':'RMP: Hot'
	})
	final.update({'rmp':rmp_label_enum})
	legacy_h_label_enum = dict({
		0:'Lab: Overall',
		1:'Lab: Overall content',
		2:'Lab: Instructor contribution to course',
		3:'Lab: Instructor teaching effectiveness',
		4:'Lab: Instructor explanations',
		5:'Lab: Instructor preparedness',
		6:'Lab: Quality of problems/questions',
		7:'Lab: Instructor enthusiasm',
		8:'Lab: Confidence in instructor knowledge',
		9:'Lab: Ab\'lty to solve unexpected problems',
		10:'Lab: Answers to student questions',
		11:'Lab: Interest level of lab sessions',
		12:'Lab: Communication of safety procedures',
		13:'Lab: Ability to deal with difficulties',
		14:'Lab: Availability of extra help',
		15:'Lab: Use of lab section time',
		16:'Lab: Interest in student learning',
		17:'Lab: Amount learned',
		18:'Lab: Relevance of content',
		19:'Lab: Relevance to lectures',
		20:'Lab: Reasonableness of assigned work',
		21:'Lab: Clarity of requirements',
		22:'Lab: Relative expected grade',
		23:'Lab: Relative intelectual challenge',
		24:'Lab: Relative effort invested',
		25:'Lab: Relative effort required',
		26:'Lab: Relative involvement (time?)' 
	})
	final.update({'legacy_H':legacy_h_label_enum})
	
	legacy_2_label_enum = dict({
		0:'L2: Course as a whole',
		1:'L2: Course content',
		2:'L2: Instructor contribution to course',
		3:'L2: Instructor effectiveness',
		4:'L2: Course organization',
		5:'L2: Opportunity to ask questions',
		6:'L2: Explanations by instructor',
		7:'L2: Contribution to personal ability',
		8:'L2: Instructor use of examples',
		9:'L2: Length and difficulty of homework',
		10:'L2: Usefulness of exams in understanding',
		11:'L2: Instructor enthusiasm',
		12:'L2: Textbook overall',
		13:'L2: Answers to questions from class',
		14:'L2: Lectures-text relationship',
		15:'L2: Availability of extra help',
		16:'L2: Instructor interest in learning',
		17:'L2: Amount you learned in course',
		18:'L2: Relevance of course content',
		19:'L2: Relevance of homework assignments',
		20:'L2: Reasonableness of assigned work',
		21:'L2: Relationship of exams to material',
		22:'L2: Relative expected grade',
		23:'L2: Relative intelectual challenge',
		24:'L2: Relative effort invested',
		25:'L2: Relative effort required',
		26:'L2: Relative involvement (time?)' 
	})
	final.update({'legacy_2':legacy_2_label_enum})
	
	legacy_1_label_enum = dict({
		0:'L1: Course as a whole',
		1:'L1: Course content',
		2:'L1: Instructor contribution to course',
		3:'L1: Instructor effectiveness',
		4:'L1: Course organization',
		5:'L1: Sequential concept presentation',
		6:'L1: Explanations by instructor',
		7:'L1: Contribution to personal ability',
		8:'L1: Instructor use of examples',
		9:'L1: Enhancement of interest',
		10:'L1: Confidence in instructor knowledge',
		11:'L1: Instructor enthusiasm',
		12:'L1: Clarity of objectives',
		13:'L1: Interest level of classes',
		14:'L1: Availibility of extra help',
		15:'L1: Use of class time',
		16:'L1: Instructor interest in learning',
		17:'L1: Amount you learned in course',
		18:'L1: Relevance of course content',
		19:'L1: Grading techniques',
		20:'L1: Reasonableness of assigned work',
		21:'L1: Clarity of student requirements',
		22:'L1: Relative expected grade',
		23:'L1: Relative intelectual challenge',
		24:'L1: Relative effort invested',
		25:'L1: Relative effort required',
		26:'L1: Relative involvement (time?)' 
	})
	final.update({'legacy_1':legacy_1_label_enum})
	return final


def processFile(filename,classlist,instructors):
	#print("Processing evalulation " + filename)
	soup = BeautifulSoup (open(filename), 'html.parser')
	surveytype = ""
	try:
		surveytype = soup.find_all('b')[-3:][0].text
		#print("INFO: File " + filename + " has type " + surveytype)
		if surveytype == '1': print("INFO: File " + filename + " has type " + surveytype)
	except IndexError:
		print("Error with file " + filename + ". Is it even a survey?")
		os.remove(filename)
		raise ValueError('CANNOT PARSE SURVEYTYPE')

	if surveytype == 'ues':
		return processSurveyTypeUES(soup,classlist,instructors)
	else:
		try:
			processLegacySurvey(surveytype,soup,classlist,instructors)
		except:
			print("Unsupported survey type " + surveytype + " in file " + filename +". Too old?")
			#traceback.print_exc(file=sys.stdout)
			raise ValueError('CANNOT PARSE LEGACY SURVEY')
	return;
	
def processLegacySurvey(surveytype,soup,classlist,instructors):
	rows = soup.find_all("tr","statement-row")
	
	instructorID = soup.find_all("a")[1].attrs['href'].split('eval/')[1]
	classID = soup.find_all('a')[0].text.split('.')[0]

	if classlist.get(classID) == None:
		classlist.update({classID:[instructorID]})
	else:
		#print(classlist.get(classID))
		if instructorID not in classlist.get(classID):
			classlist[classID].append(instructorID)
		else:
			pass

	if instructors.get(instructorID) == None:
		instructors.update({instructorID:{
			'name':soup.find_all("a")[1].text,
			'id':instructorID,
			'classes':[],
			'data':{}
		}})

	if not (classID in instructors[instructorID]['classes']):
		instructors[instructorID]['classes'].append(classID)
	instructors[instructorID]['data'].update({surveytype:{}})
	data = instructors[instructorID]['data'][surveytype]

	#For each row
	for section in [{'critrange':range(0,22),'degrange':range(2,8)},{'critrange':range(22,27),'degrange':range(2,9)}]:
		for crit in section['critrange']:
			row = rows[crit]
				
				
			#Create row in data file if DNE
			if data.get(crit) == None:
				data.update({crit	:dict()})	

			#Create key value if DNE
			if data[crit].get('total') == None:
				data[crit].update({'total':0})
			
			
			data[crit]['total'] = 0
			
			try:
				responses = int(row.find_all('td')[9].text)
			except ValueError:
				responses = 0
			
			maxval = (section['degrange'].stop - section['degrange'].start - 1)
			for degree in section['degrange']:
				stat = degree - 2
				
				degreelabel = 'degree' + str(maxval-stat)
				data[crit].update({degreelabel:0})
				percent = row.find_all('td')[degree]
				points = int(int(percent.text[:-1])/100 * responses)
				data[crit]['total'] += points
				data[crit].update({degreelabel:points})
	return

def processSurveyTypeUES(soup,classlist,instructors):

	rows = soup.find_all("tr","statement-row")

	instructorID = soup.find_all("a")[1].attrs['href'].split('eval/')[1]
	classID = soup.find_all('a')[0].text.split('.')[0]

	if classlist.get(classID) == None:
		classlist.update({classID:[instructorID]})
	else:
		classlist[classID].append(instructorID)

	if instructors.get(instructorID) == None:
		instructors.update({instructorID:{
			'name':soup.find_all("a")[1].text,
			'id':instructorID,
			'classes':[],
			'data':{}
		}})

	if not (classID in instructors[instructorID]['classes']):
		instructors[instructorID]['classes'].append(classID)
	instructors[instructorID]['data'].update({'ues':{}})
	data = instructors[instructorID]['data']['ues']

	#For each row
	for rownumber in range(0,15):
		row = rows[rownumber]
		rowdata = row.find_all("tr")[1]

		#Create row in data file if DNE
		if data.get(rownumber) == None:
			data.update({rownumber:dict()})

		#Create key value if DNE
		if data[rownumber].get('total') == None:
			data[rownumber].update({'total':0})

		total = rowdata.find_all("td")[6].getText()
		#Replace - with 0 in table values
		if total == '-' or total == '':
			total = '0'
		data[rownumber]['total'] += int(total)

		for degree in range(1,6):
			score = rowdata.find_all("td")[degree].getText()
			if score == '-' or score == '':
				score = '0'
			degreelabel = 'degree' + str(degree)

			#Create key value if DNE
			if data[rownumber].get(degreelabel) == None:
				data[rownumber].update({degreelabel:0})
			data[rownumber][degreelabel] += int(score)

def pickleLoad(filename):
	filehandler = open("obj/" + filename + ".obj", 'rb')
	object = pickle.load(filehandler)
	return object

def pickleSave(object, filename):
	filehandler = open("obj/" + filename + ".obj", 'wb')
	pickle.dump(object, filehandler)

def dict_merge(dct, merge_dct):
	import collections
	""" Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
	updating only top-level keys, dict_merge recurses down into dicts nested
	to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
	``dct``.
	:param dct: dict onto which the merge is executed
	:param merge_dct: dct merged into dct
	:return: None
	"""
	#By angstwad on github
	for k, v in merge_dct.items():
		if (k in dct and isinstance(dct[k], dict)
				and isinstance(merge_dct[k], collections.Mapping)):
			dict_merge(dct[k], merge_dct[k])
		else:
			dct[k] = merge_dct[k]	
	
def rebuild(matches,classlist,instructors,quiet):
	# global instructors
	# global classlist
	# instructors = dict();
	# classlist = dict();
	#Example usage:  rebuild(["cs*","*.15f"])
	i = 0
	for match in matches:
		i = i + 1
	if not quiet: print("Loaded " + str(i) + " individual globs. Processing...")
	
	for match in matches:
		imatch = "part/" + match.translate({ord('*'):'_',ord('/'):'.'}) + ".ipt"
		cmatch = "part/" + match.translate({ord('*'):'_',ord('/'):'.'}) + ".cpt"
		try:
			ipart = pickleLoad(imatch)
			cpart = pickleLoad(cmatch)
			if not quiet: print(imatch)
		except:
			print('No cached data, building.')
			ipart = dict()
			cpart = dict()
		#process
			i = 0
			j = 0
			pbar = 0
			files = glob.glob("evals/" + match)
			print('[########################################]\n[',end='')
			for filename in files:
				try:
					i = i + 1
					if (int(i/len(files)*40) > pbar):
						print("#",end='')
						sys.stdout.flush()
					pbar = int(i/len(files)*40)
					processFile(filename,cpart,ipart)
					#print(int(i/len(files)*20))
				except KeyboardInterrupt:
					return
				except ValueError:
					#traceback.print_exc(file=sys.stdout)
					j = j + 1
					#pass
				except:
					print("Unknown error with file " + filename)
					traceback.print_exc(file=sys.stdout)
					j = j + 1
			pickleSave(ipart,imatch)
			pickleSave(cpart,cmatch)
			print(']')
		dict_merge(instructors,ipart)
		dict_merge(classlist,cpart)

	#print("Successfully processed " + str(i) + " evals. Skipped " + str(j))
	#print(instructors)
#Rebuild
