#Python 3.6.0
#print("Processing core imports")
from bs4 import BeautifulSoup
import requests
import sys,traceback
import pickle
import os

#print("Defining user variables")
global classcodes

def ncpLoad(filename):
	try:
		filehandler = open("obj/" + filename + ".obj", 'rb')
		object = pickle.load(filehandler)
		return object
	except FileNotFoundError:
		print("No file to load for object " + filename)
		raise ValueError('FILENOTFOUND')

def ncpSave(object, filename):
	filehandler = open("obj/" + filename + ".obj", 'wb')
	pickle.dump(object, filehandler)

#allclasscodes = ['ACCT', 'ACN', 'ACTS', 'AERO', 'AHST', 'AIM','AMS','AP','ARAB','ARHM','ARTS','ATCM','ATEC','ATEM','AUD','BA','BCOM','BIOL','BIS','BLAW','BMEN','BPS','BUAN','CE','CGS','CHEM','CHIN','CJS','CLDP','COMD','COMM','COOP','CRIM','CRWT','CS','DANC','DMTH','DRAM','DRDG','DWTG','ECO','ECON','ECS','ECSC','ED','EE','EEBM','EECS','EECT','EEDG','EEGR','EEMF','EEOP','EEPE','EERF','EESC','EMAC','EMTH','ENGR','ENGY','ENTP','ENVR','EPPS','FILM','FIN','FREN','GEOG','GEOS','GERM','GISC','GOVT','GST','HCS','HDCD','HIST','HLTH','HMGT','Honors','College','HUAS','HUED','HUHI','HUMA','HUSL','IMS','IPEC','ISAE','ISAH','ISEC','ISGS','ISHD','ISIS','ISNS','ISSS','ITSS','JAPN','LANG','LATS','LIT','MAIS','MAS','MATH','MECH','MECO','MED','MILS','MIS','MKT','MSEN','MTHE','MUSI','NANO','NATS','NSC','OB','OBHR','OPRE','PA','PHIL','PHIN','PHYS','PLTL','POEC','PPOL','PPPE','PSCI','PSY','PSYC','REAL','RHET','RMIS','SCE','SCI','SE','SMED','SOC','SOCS','SPAN','SPAU','STAT','SYSE','SYSM','TE','THEA','Undergraduate','Studies','UNIV','UTD','UTSW','GREK','UTTC','VIET']

def setClassCodes(new):
	global classcodes
	if new == ['void']:
		print("You must specify class codes. ")
		print("Defaulting. ")
		classcodes = ['CS','HONS','GOVT','PHYS','UNIV']
	else:
		classcodes = new
	ncpSave(classcodes,'classcodes')
	print("Classcodes: ")
	print(classcodes)


#classcodes = allclasscodes

rmp_hotness_enum = {
	'/assets/chilis/cold-chili.png':"Yes",
	'/assets/chilis/new-hot-chili.png':"No",
	'?':"No"
}

#print("Defining core routines")
def download(term, classcode):
	url = "https://coursebook.utdallas.edu/search/searchresults/term_" + term + "/cp_" + classcode + "/hasevaluation_1"
	localfile = "directorylisting/" + term + "_" + classcode + ".html"
	save(localfile,url)

def downloadDirlists(args):
	global classcodes
	try:
		filename = 'classcodes'
		filehandler = open("obj/" + filename + ".obj", 'rb')
		classcodes = pickle.load(filehandler)
	except TypeError:
		print("No saved classcodes file, using defaults")
		classcodes = ['CS','HONS','GOVT','PHYS','UNIV']
	print(classcodes)
	terms = []
	#if args[0] == 'void': return
	try:
		print([int(args[0]),int(args[1])+1])
	except IndexError:
		print("You must specify a year range!")
		return
	for year in range(int(args[0]),int(args[1])+1):
		for term in ('s','u','f'):
			terms.append(str(year).zfill(2) + term)
	evalnames = []
	
	#Progress bar code
	p1 = 0
	p2 = 0
	for term in terms:
		for classcode in classcodes:
			p1 = p1 + 1
	pbar = 0
	print('[####################]\n[',end='')
	
	
	for term in terms:
		for classcode in classcodes:
			soup = None
			localfile = "./directorylisting/" + term + "_" + classcode + ".html"
			#print("Processing " + localfile)
			#Progress bar code
			p2 = p2 + 1
			if (int(p2/p1*20) > pbar):
				print("#",end='')
				sys.stdout.flush()
			pbar = int(p2/p1*20)
			
			if not os.path.isfile(localfile):
				print("Missing file " + localfile)
				download(term,classcode)
			try:
				soup = BeautifulSoup (open(localfile), 'html.parser')
			except:
				print("Cannot read file " + localfile + "! Critical error. Skipping.")
				continue

			if soup == None:
				print("Soup error")
				break
			i = 0
			header = ""
			for tr in soup.find_all("tr"):
				# if i == 0 or str(tr) == header:
					# header = str(tr)
					# continue

				i += 1
				if i == 295:
					print("WARNING: CLASS " + classcode + "HAS TOO MANY CLASSES")
				try:
					classnum = tr.find_all("td")[1].text.split('.')[0].split(' ')[1]
					classprefix = tr.find_all("td")[1].text.split('.')[0].split(' ')[0]
					#aclass = {'prefix':classprefix,'num':classnum}
					aclass = classprefix.lower() + classnum + "." + tr.find_all("td")[1].text.split('.')[1][:3] + "." + term
					#print(aclass)
					evalnames.append(aclass)
				except:
					#print("fail")
					#print("row is not a row:" + str(tr))
					#print("row is not a row")
					continue
					#traceback.print_exc(file=sys.stdout)
					#continue
			#print(i)
	#print(classes)
	ncpSave(evalnames, 'evalnames')
	print(']')
#Done

def save(output, input):
	#print("Saving " + input + " as " + output)
	with open(output, 'wb') as handle:
		response = requests.get(input, stream=True)
		if not response.ok:
			print("oh no! network pipe failed!")
		for block in response.iter_content(1024):
			handle.write(block)
#Done

def downloadEvals():
	try:
		evalnames = ncpLoad('evalnames')
	except: 
		print("You need to run downloadDirlists first!")
		return
	#print(evalnames)
	#Todo: Sort classes into folders by either year or code. Leaning towards year.
	j = 0
	#Progress bar code
	i = 0
	pbar = 0
	print('[####################]\n[',end='')
	for c in evalnames:
		#Progress bar code
		i = i + 1
		if (int(i/len(evalnames)*20) > pbar):
			print("#",end='')
			sys.stdout.flush()
		pbar = int(i/len(evalnames)*20)
		
		year = c.split('.')[2]
		if not os.path.exists("evals/" + year):
			os.makedirs("evals/" + year)
		if not os.path.isfile("evals/" + year + "/" + c):
			j = j + 1
			save("evals/" + year + "/" + c,"https://coursebook.utdallas.edu/ues-report/" + c)
	print(']') #Progress bar code
	print("Downloaded " + str(j) + " new evalulation files.")

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

	
def rateThisProfessor(instructor,instructors):
	filepath = "part/rmp/" + instructor['id'] + ".rpt"
	global rmp_hotness_enum;
	grades = []
	try:
		prof = ncpLoad(filepath)
	except:
		prof = {'name':instructor['name'],'id':instructor['id']}
		
		try:
			save('temporary/rmp.html',"http://www.ratemyprofessors.com/search.jsp?queryoption=HEADER&queryBy=teacherName&schoolName=University+of+Texas+at+Dallas&schoolID=1273&query=" + prof['name'])
			soup = BeautifulSoup (open("temporary/rmp.html"), 'html.parser')
			subpage = soup.find_all('li','listing')[0].find_all('a')[0].attrs['href']

			save('temporary/rmp2.html',"http://www.ratemyprofessors.com" + subpage)
			soup = BeautifulSoup (open("temporary/rmp2.html"), 'html.parser')
			grades = soup.find_all('div','grade')
		except:
			prof.update({'rmpdata':{
				'nodata':True
			}})
			print("No data on RMP website for " + prof['name'])
			ncpSave(prof,filepath)
			dict_merge(instructor,prof)
			return
		try:
			overall = grades[0].text[:3] + "/5"
		except:
			overall =  "??"

		try:
			wouldtakeagain = grades[1].text.split('\n')[1][-3:-1] + "%"
		except:
			wouldtakeagain =  "??"

		try:
			difficulty = grades[2].text.split('\n')[1][-3:] + "/5"
		except:
			difficulty = "??"
		try:
			hottness = rmp_hotness_enum[soup.find_all('figure')[0].find_all('img')[0].attrs['src']]
		except IndexError:
			hottness = '?'
		prof.update({'rmpdata':{
			'overall':overall,
			'wouldtakeagain':wouldtakeagain,
			'difficulty':difficulty,
			'hottness':hottness
		}})
	#print(prof['rmpdata'])
	ncpSave(prof,filepath)
	dict_merge(instructor,prof)
	#ncpSave(instructors,'instructors')

def rateTheseProfessors(alist):
	for professors in alist:
		 rateThisProfessor(professors)


#print("Processing")
#downloadDirlists()
#downloadEvals()
#print(classes)
