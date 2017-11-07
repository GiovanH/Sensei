#Python 3.6.0
#     exec(open("sensei.py").read(), globals())
#import csv
import argparse
import glob
import locale
import math
import os
import pickle
import queue
import shlex
import statistics
import sys

import urllib3
from bs4 import BeautifulSoup

import nestfn as nf
import sensei_data_build as sdat
import sensei_netcode as snc

#global DEBUG
DEBUG = False

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,epilog="""
List of Commands with arguments:

  --help
  scoreteacher [teacher]
     Report the full score of a specific teacher, by name. Use quotes.
  scoreteacherbyid [teacher netid]
     Report the full score of a specific teacher, by name. Use quotes.
  scoreclass [classcode]
     Compare the scores of all teachers of a class, by code (XX[XX]####)
  compare teacher teacher [teacher teacher teacher...]
     Compare the scores of a list of teachers, by name. Use quotes.

Utility Commands:

  0. setclasscodes [classcode, classcode...] (uppercase)
     Save a list of class codes (CS, ATEC, etc) for use
  1. downloaddirlists [year, year] (eg. 02 16)
     Download directory listings for a range of years.
  2. downloadevals (uses last class list from dirlists)
     Download individual evalulation reports for building datasets.
  3. rebuild [list of glob matches within /evals]
     Build datasets out of evalulation files for use in main program.

  Also availible as --classcodes, --yearrange, --redownload, and --glob, respectively.

Development Commands:
  dump
     Print a full list of saved variables to stdout
  prompt
     Drop down to interactive level
""")
parser.add_argument('--version', action='version', version='%(prog)s 0.1 beta')
#See end of doc for extension

parser.add_argument("cmd", help="Command to execute.")
parser.add_argument("args", nargs='*', help="Arguments for command.")
parser.add_argument('--admin')
parser.add_argument('--glob',dest='glob',nargs='+')
parser.add_argument('--yearrange',dest='yearrange',nargs='+')
parser.add_argument('--classcodes',dest='classcodes',nargs='+')
parser.add_argument('--redownload', action='store_true')
parser.add_argument('--quiet','-q', action='store_true')
parser.add_argument('--offline','-o', action='store_true')
args = parser.parse_args()
snc.args(args)
sdat.args(args)
#print(args)


global instructors
instructors = dict()
global classlist
classlist = dict()

def pickleLoad(filename):
    #Todo: Handle exceptions from pickle
    """
    Loads an object from the filesystem with pickle.

    Returns: Any data structure

    Parameters:
    str filename -- file to load from obj/filename.obj"""
    filehandler = open("obj/" + filename + ".obj", 'rb')
    object = pickle.load(filehandler)
    return object

def pickleSave(object, filename):
    #Todo: Handle exceptions from pickle
    """
    Saves an object to the filesystem with pickle.

    Returns: None

    Parameters:
    str filename -- filename to save at obj/filename.obj
    any object -- Serializable object to save"""
    filehandler = open("obj/" + filename + ".obj", 'wb')
    pickle.dump(object, filehandler)

def getInstructorByName(instructors, name):
    """
    Get instructor by name from database

    Returns: Instructor object

    Parameters:
    str name -- Name of instructor in the form "Firstname Lastname"

    Throws: _____exception if no instructor is found by that name
    """
    for ID in instructors:
        instructor = instructors.get(ID)
        if instructor['name'] == name:
            return instructor
    # TODO: this code should be replaced with an exception
    print("No instructor by name " + name + " on file!")
    return None

def getInstructorByNetID(instructors,netid):
    """
    Get instructor by net id from database

    Returns: Instructor object

    Parameters:
    str netid -- netid of instructor

    Throws: _____exception if no instructor is found by that name
    """
    for ID in instructors:
        instructor = instructors.get(ID)
        if instructor['id'] == netid:
            return instructor
    print("No instructor by id " + netid + " on file!")
    return None

def getInstructorsByNames(names):
    """
    Get a list of instructors by name from database

    Returns: List of instructors

    Parameters:
    names -- a list of name strings, each with the format "Firstname Lastname". May be the empty list.
    """
    # TODO: test to make sure this works
    instructors_ = []
    for name in names:
        teacher = getInstructorByName(instructors,name)
        if teacher == None and name != 'void':
            #print("No such teacher " + name)
            break
        instructors_.append(teacher)
    return instructors_


def getInstructorsByIDlist(aclass):
    """
    TODO: Docstring
    Description in english.

    Returns: Return type

    Parameters:
    parameter -- description
    """
    alist = list()
    #Todo: If we don't have the class, append the class prefix to classcodes and attempt redownload.
    #On second thought, that should never happen?
    if aclass == None: return alist
    for c in aclass:
        #print(c)
        #print(instructors[c]['name'])
        alist.append(instructors[c])
    return alist


def uesdatapoints(teacher):
    """
    Counts UES datapoints

    Returns: number of datapoints availible in survey

    Parameters:
    teacher -- teacher object to count
    """
    points = 0
    for criteria in range(0,15):
        for degree in range(1,6):
            #TODO: nonetype error here means we do not have data for the teacher
            points += teacher['data']['ues'][criteria]['degree' + str(degree)]
    return points

def legacydatapoints(teacher):
    """
    Counts legacy survey datapoints

    Returns: number of datapoints availible in survey

    Parameters:
    teacher -- teacher object to count
    """
    points = 0
    for surveytype in ['2','1','H']:
        for criteria in range(0,22):
            for degree in range(0,6):
                try:
                    points += teacher['data'][surveytype][criteria]['degree' + str(degree)]
                except:
                    pass
        for criteria in range(22,27):
            for degree in range(0,7):
                try:
                    points += teacher['data'][surveytype][criteria]['degree' + str(degree)]
                except:
                    pass
    return points

def statistify(criteria):
    """
    Prepares data for the python statistics module

    Returns: data reformatted for statistics module (???)

    Parameters:
    criteria -- object to process
    """
    final = []
    for degree in criteria.keys():
        if degree == 'total':
            continue
        for num in range(0,criteria[degree]):
            final.append(int(degree.split('degree')[1]))
    return final

def scoreTeacherues(teacher):
    """
    TODO: Docstring
    Description in english.

    Returns: Return type

    Parameters:
    parameter -- description
    """
    if teacher['data'].get('ues') == None:
        if not args.quiet: print("No UES data availible.")
        return
    print("## UES Survey data")
    print("Datapoints: " + str(uesdatapoints(teacher)))
    ues_label_enum = sdat.enums().get('ues')
    print("{0:<40}  {1:5}% {2:>5} [{3[0]:>3}, {3[1]:>3}, {3[2]:>3}, {3[3]:>3}, {3[4]:>3}]".format("Criteria","%","σ",["SD","D","N","A","SA"]))
    for criteria in range(0,15):
        total = teacher['data']['ues'][criteria]['total']
        score = {}
        for degree in range(0,5):
            score[degree] = teacher['data']['ues'][criteria]['degree' + str(degree+1)]
        percent = 0
        for degree in range(0,5):
            #print(str(percent) + " ", end='')
            percent += int(score[degree]*(degree))
        try:
            percent = percent/(total*4)
        except ZeroDivisionError:
            percent = 0
        percent = round(percent*100,2)
        try:
            stdev = round(statistics.stdev(statistify(teacher['data']['ues'][criteria])),2)
        except statistics.StatisticsError:
            stdev = '-'
        print("{0:<40}  {1:5}% {2:>5} [{3[0]:>3}, {3[1]:>3}, {3[2]:>3}, {3[3]:>3}, {3[4]:>3}]".format(ues_label_enum[criteria],percent,stdev,score))
#done

def scoreTeacherlegacy(teacher):
    """
    TODO: Docstring
    Description in english.

    Returns: Return type

    Parameters:
    parameter -- description
    """
    if (legacydatapoints(teacher) > 1): print("Datapoints: " + str(legacydatapoints(teacher)))
    for surveytype in ['1','2','H','C']:
        if teacher['data'].get(surveytype) == None:
            if not args.quiet: print("No v" + surveytype + " data availible.")
            continue
        else:
            print("## Survey v" + surveytype + " data")

        label_enum = sdat.enums().get("legacy_" + surveytype)
        if label_enum == None:
            print("CODING ERROR: Missing friendly enumeration labels for survey type " + surveytype)
            continue

        sections = []
        sections.append({'critrange':range(0,22),'degrange':range(0,6),'scorefmtstr':"{1:<40} {2:5}%  {3[0]:<5} [{0[0]:>3}, {0[1]:>3}, {0[2]:>3}, {0[3]:>3}, {0[4]:>3}, {0[5]:>3}]",'labels':["VP","PR","FR","GD","VG","EX"]})
        sections.append({'critrange':range(22,27),'degrange':range(0,7),'scorefmtstr':"{1:<40} {2:5}%  {3[0]:<5} [{0[0]:>3}, {0[1]:>3}, {0[2]:>3}, {0[3]:>3}, {0[4]:>3}, {0[5]:>3}, {0[6]:>3}]",'labels':["MH","","","AVG","ML","","ML"]})
        for section in sections:
            print(section['scorefmtstr'].format(section['labels'],"Criteria","%",["σ"]))
            for criteria in section['critrange']:
                total = teacher['data'][surveytype][criteria]['total']
                score = {}
                for degree in section['degrange']:
                    score[degree] = teacher['data'][surveytype][criteria]['degree' + str(degree)]

                percent = 0
                for degree in section['degrange']:
                    percent += int(score[degree]*(degree))
                try:
                    percent = percent/(total*(len(section['labels']))-1)
                except ZeroDivisionError:
                    percent = 0
                try:
                    stdev = round(statistics.stdev(statistify(teacher['data'][surveytype][criteria])),2)
                except statistics.StatisticsError:
                    stdev = '-'
                print(section['scorefmtstr'].format(score,label_enum[criteria],str(round(percent*100,2)),[stdev]))
#done

def scoreTeacherrmp(teacher):
    """
    TODO: Docstring
    Description in english.

    Returns: Return type

    Parameters:
    parameter -- description
    """
    rmp_label_enum = sdat.enums().get('rmp')
    #print(sdat.enums())
    global DEBUG
    if teacher.get('rmpdata') == None:
        try:
            if DEBUG: print("Downloading missing RMP data for " + teacher['name'])
            snc.rateThisProfessor(teacher,instructors)
        except:
            print("Can't rate professor, and no data!")
    if teacher.get('rmpdata').get('nodata') == True:
        print("No RMP data availible.")
        return
    for criteria in ('overall','wouldtakeagain','difficulty','hottness'):
        print("{1:<42} {0:>5}".format(teacher['rmpdata'][criteria],rmp_label_enum[criteria]))
        #print(str(score[degree]) + " ", end='')

def deepscore(teacher):
    """
    Scores a teacher with legacy, ues, and rmp

    Returns: None

    Parameters:
    teacher -- Teacher to score
    """
    if teacher == None:
        print("Not a valid teacher")
        return
    if teacher.get('rmpdata') == None: snc.rateThisProfessor(teacher,instructors)
    print("# " + teacher['name'])
    scoreTeacherlegacy(teacher)
    scoreTeacherues(teacher)
    scoreTeacherrmp(teacher)

def deepcompare(teachers):
    """
    TODO: Docstring
    Description in english.

    Returns: Return type

    Parameters:
    parameter -- description
    """
    if teachers == [None] or teachers == None:
        print("No valid teachers to compare [DC]")
        return
    for teacher in teachers:
        if teacher == None:# and name != 'void':
            print("One or more teachers were invalid.")
            break
    print("                                         <--Highest           Lowest-->")
    multicomparelegacy(teachers)
    multicompare(teachers)
    multicomparermp(teachers)

def multicomparelegacy(teacherlist):
    """
    TODO: Docstring
    Description in english.

    Returns: Return type

    Parameters:
    parameter -- description
    """
    global args
    for surveytype in ['1','2','H']:
        label_enum = sdat.enums().get("legacy_" + surveytype)
        if label_enum == None:
            print("CODING ERROR: Missing friendly enumeration labels for survey type " + surveytype)
            continue
        tempdict = dict()
        percentages = dict()
        teachers = list(teacherlist)
        bad = []
        if teachers == [None]:
            if not args.quiet: print("No valid teachers to compare [MCL1]")
            continue
        for teacher in teachers:
            if teacher['data'].get(surveytype) == None:
                if not args.quiet: print("No v" + surveytype + " data availible for " + teacher['name'])
                bad.append(teacher)
            if teacher == None:
                bad.append(teacher)
            percentages.update({teacher['name']:0})
            tempdict.update({teacher['id']:{'total':0,'percent':0,'percentstr':""}})
        for error in bad:
            teachers.remove(error)
        if teachers == []:
            #if not args.quiet: print("No valid teachers to compare [MCL2]")
            continue
        sections = []
        sections.append({'critrange':range(0,22),'degrange':range(0,6),'scorefmtstr':"{1:<40} {2:5}% [{0[0]:>3}, {0[1]:>3}, {0[2]:>3}, {0[3]:>3}, {0[4]:>3}, {0[5]:>3}] ",'labels':["EX","VG","GD","FR","PR","VP"]})
        sections.append({'critrange':range(22,27),'degrange':range(0,7),'scorefmtstr':"{1:<40} {2:5}% [{0[0]:>3}, {0[1]:>3}, {0[2]:>3}, {0[3]:>3}, {0[4]:>3}, {0[5]:>3}, {0[6]:>3}] ",'labels':["MH","","","AVG","ML","","ML"]})
        for section in sections:
            for criteria in section['critrange']:
                for teacher in teachers:
                    percent = 0
                    for degree in section['degrange']:
                        percent += teacher['data'][surveytype][criteria]['degree' + str(degree)] * (degree-1)
                    tempdict[teacher['id']]['total'] = teacher['data'][surveytype][criteria]['total']
                    try:
                        percent = percent/(tempdict[teacher['id']]['total']*4)
                    except ZeroDivisionError:
                        percent = 0
                    tempdict[teacher['id']]['percent'] = percent
                    tempdict[teacher['id']]['percentstr'] = str(round(percent*100,2)) + "% "
                    percentages.update({teacher['name']:percent})
                sortedd = sorted(percentages, key=percentages.get, reverse=True)[:5]
                print("{0:<40} ".format(label_enum[criteria]), end='')
                for teacher in sortedd:
                    print("{0:<20} ".format(teacher), end='')
                print("")

def multicompare(teachers):
    """
    TODO: Docstring
    Description in english.

    Returns: Return type

    Parameters:
    parameter -- description
    """
    ues_label_enum = sdat.enums().get('ues')
    tempdict = dict()
    percentages = dict()
    bad = []
    if teachers == [None]:
        print("No valid teachers to compare [MCUES]")
        return
    for teacher in teachers:
        if teacher['data'].get('ues') == None:
            if not args.quiet: print("No UES data availible for " + teacher['name'])
            bad.append(teacher)
        if teacher == None:
            bad.append(teacher)
        percentages.update({teacher['name']:0})
        tempdict.update({teacher['id']:{'total':0,'percent':0,'percentstr':""}})
    for error in bad:
        teachers.remove(error)
    if teachers == []:
        print("No valid teachers to compare after removals.")
        return
    for criteria in range(0,15):
        for teacher in teachers:
            percent = 0
            #print(teacher['name'])
            for degree in range(0,5):
                percent += teacher['data']['ues'][criteria]['degree' + str(degree+1)] * (degree)
            tempdict[teacher['id']]['total'] = teacher['data']['ues'][criteria]['total']
            try:
                percent = percent/(tempdict[teacher['id']]['total']*4)
            except ZeroDivisionError:
                percent = 0
            tempdict[teacher['id']]['percent'] = percent
            tempdict[teacher['id']]['percentstr'] = str(round(percent*100,2)) + "% "
            percentages.update({teacher['name']:percent})
        sortedd = sorted(percentages, key=percentages.get, reverse=True)[:5]
        print("{0:<40} ".format(ues_label_enum[criteria]), end='')
        for teacher in sortedd:
            print("{0:<20} ".format(teacher), end='')
        print("")

def multicomparermp(teachers):
    """
    TODO: Docstring
    Description in english.

    Returns: Return type

    Parameters:
    parameter -- description
    """
    rmp_label_enum = sdat.enums().get('rmp')
    percentages = dict()
    bad = []
    for teacher in teachers:
        percentages.update({teacher['name']:'0.0'})
        if teacher.get('rmpdata') == None:
            try:
                if not args.quiet: print("Downloading missing RMP data for " + teacher['name'])
                if not args.offline:
                    snc.rateThisProfessor(teacher,instructors)
                else:
                    raise ValueError('OFFLINE')
            except:
                print("Can't rate professor, and no data!")
                bad.append(teacher)
    for error in bad:
        teachers.remove(error)
    bad = []
    for teacher in teachers:
        if teacher.get('rmpdata').get('nodata') == True:
            #print("Removing teacher with missing data " + teacher['name'])
            bad.append(teacher)
    for error in bad:
        teachers.remove(error)
    if teachers == []:
        if not args.quiet: print("No valid teachers to compare [MCR]")
        return
    for criteria in ('overall','wouldtakeagain','difficulty','hottness'):
        for teacher in teachers:
            percent = teacher['rmpdata'][criteria]
            percentages.update({teacher['name']:percent})
        #print(percentages)
        sortedd = sorted(percentages, key=percentages.get, reverse=(criteria != 'difficulty'))[:5]
        print("{0:<40} ".format(rmp_label_enum[criteria]), end='')
        for teacher in sortedd:
            print("{0:<20} ".format(teacher), end='')
        print()

#exec(open("sensei.py").read(), globals())


def load():
    """
    TODO: Docstring
    Description in english.

    Returns: Return type

    Parameters:
    parameter -- description
    """
    global instructors
    global classlist
    instructors = pickleLoad('instructors')
    classlist = pickleLoad('classlist')
    #print(instructors)

def help():
    """
    TODO: Docstring
    Description in english.

    Returns: Return type

    Parameters:
    parameter -- description
    """
    commands = [
        'scoreTeacher(teacher)',
        'scoreTeacherrmp(teacher)',
        'getInstructorByName(string)',
        'datapoints(teacher)',
        'deepcompare([teachers])',
        'deepscore(teacher)',
        'help()',
        'instructorsOf(class)',
        'multicompare([teachers])',
        'multicomparermp([teachers])',
        'processAll([list of files])',
        'processFile(filename)',
        'rebuild([list of glob patterns])',
        ''
    ]
    for command in commands:
        print("  " + command)

def isAdmin():
    """
    TODO: Docstring
    Description in english.

    Returns: Return type

    Parameters:
    parameter -- description
    """
    global args
    import hashlib
    if args.admin == None:
        return False
    h = hashlib.sha256(args.admin.encode('utf-8'))
    h.update("Nobody better goddamn rainbow this".encode('utf-8'))
    if h.hexdigest() == '7c0db0fbfabcc9e94a86cf5e58002323e669066b4a2325ce60052b0aa07ced6d':
        return True
    else:
        return False

def compareAll():
    """
    TODO: Docstring
    Description in english.

    Returns: Return type

    Parameters:
    parameter -- description
    """
    if not isAdmin():
        print("Administrative permissions required.")
        return
    global classlist
    q = args.quiet
    for c in classlist:
        with open('bulk/classes/' + c + '.txt','w') as f:
            args.quiet = True
            sys.stdout = f
            #print("==============" + c)
            nf.fn(deepcompare,nf.fn(getInstructorsByIDlist,classlist.get(c))).exe()
        sys.stdout = sys.__stdout__
        args.quiet = q
        print("==============" + c)
        nf.fn(deepcompare,nf.fn(getInstructorsByIDlist,classlist.get(c))).exe()

def scoreAll():
    """
    TODO: Docstring
    Description in english.

    Returns: Return type

    Parameters:
    parameter -- description
    """
    if not isAdmin():
        print("Administrative permissions required.")
        return
    print("Authorized.")
    #global instructors
    #print(instructors)
    q = args.quiet
    for i in instructors.keys():
        with open('bulk/instructors/' + i + '.txt','w', encoding='utf8') as f:
            args.quiet = True
            sys.stdout = f
            #print("==============" + instructors.get(i)['name'])
            nf.fn(deepscore,instructors.get(i)).exe()
        sys.stdout = sys.__stdout__
        args.quiet = q
        print("==============" + instructors.get(i)['name'])
        nf.fn(deepscore,instructors.get(i)).exe()

def rebuild(rargs):
    """
    TODO: Docstring
    Description in english.

    Returns: Return type

    Parameters:
    parameter -- description
    """
    global classlist
    global instructors
    # instructors = dict()
    # classlist = dict()
    sdat.rebuild(rargs,classlist,instructors)
    pickleSave(instructors,'instructors')
    pickleSave(classlist,'classlist')

def dump():
    """
    TODO: Docstring
    Description in english.

    Returns: Return type

    Parameters:
    parameter -- description
    """
    if not isAdmin():
        print("Administrative permissions are required.")
        return
    global classlist
    global instructors

    import json
    #global classcodes
    objs = []
    objs.append([classlist,'classlist'])
    objs.append([instructors,'instructors'])
    for obj in objs :
        f = open('obj/' + obj[1] + '.dmp', 'w')
        f.write(json.dumps(obj[0]))
        f.close()

def prompt():
    """
    TODO: Docstring
    Description in english.

    Returns: Return type

    Parameters:
    parameter -- description
    """
    global arglist
    while True:
        try:
            i = input(">>> ")
            arglist = shlex.split(i)[1:]
            print([i,arglist])
            makeargs()
            argswitch[i.split(' ')[0]].exe()
        except KeyError:
            print("Invalid command.")
            print(argswitch.keys())
            continue
#Begin program execution

#Ensure all base paths exist
for path in ['obj', 'obj/part', 'obj/part/rmp', 'evals', 'directorylisting','temporary']:
    if not os.path.exists(path):
        os.makedirs(path)

#See if we can load any saved databases

try:
    load()
except:
    print("No data saved! Please download dirlists and download evals, then rebuild!")

#Pull report downloading modules
#exec(open("getreports.py").read(), globals())

if args.args == []: args.args = ['void']
arglist = list(args.args)
#print(args.args)

def makeargs():
    """
    TODO: Docstring
    Description in english.

    Returns: Return type

    Parameters:
    parameter -- description
    """
    global argswitch
    argswitch = {
        'rebuild':    nf.fn(rebuild,arglist),
        'downloadevals':    nf.fn(snc.downloadEvals,args),
        'downloaddirlists':     nf.fn(snc.downloadDirlists,arglist),
        'setclasscodes':    nf.fn(snc.setClassCodes,arglist),
        'scoreteacher':    nf.fn(deepscore,nf.fn(getInstructorByName,arglist[0])), #TODO: this is broken
        'scoreteacherbyid':    nf.fn(deepscore,nf.fn(getInstructorByNetID,arglist[0])), #TODO: this is broken
        'scoreclass':    nf.fn(deepcompare,nf.fn(getInstructorsByIDlist,nf.fn(classlist.get,arglist[0]))),
        'compare':    nf.fn(deepcompare,nf.fn(getInstructorsByNames,arglist)),
        'compareall':    nf.fn(compareAll,None),
        'scoreall':    nf.fn(scoreAll,None),
        'dump':    nf.fn(dump,None),
        'prompt':    nf.fn(prompt,None)
    }
makeargs()

args.cmd = args.cmd.lower()

# if argswitch[args.cmd]['args'] != 'NONE':
#     argswitch[args.cmd]['fn'](argswitch[args.cmd]['args'])
# else:
#     argswitch[args.cmd]['fn']()

try:
    cmd = argswitch[args.cmd]
except KeyError:
    print("Invalid command. Try with --help for a list.")


if args.classcodes is not None:
    if not args.quiet: print('Setting codes')
    snc.setClassCodes(args.classcodes)
if args.yearrange is not None:
    if not args.quiet: print('Getting dirlists')
    snc.downloadDirlists(args.yearrange)
if args.redownload:
    if not args.quiet: print('Getting evals')
    snc.downloadEvals(args)
if args.glob is not None:
    if not args.quiet: print('Rebuilding database')
    rebuild(args.glob)
#print(arglist)
cmd.exe()
