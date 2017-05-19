rm obj/*
set PYTHONIOENCODING=utf-8

python3 sensei.py --help
python3 sensei.py setclasscodes
python3 sensei.py setclasscodes CS UNIV
python3 sensei.py downloaddirlists
python3 sensei.py downloaddirlists 15 16
python3 sensei.py downloadevals
python3 sensei.py rebuild
rem python3 sensei.py rebuild "16f/cs1*"
python3 sensei.py rebuild "03f/cs1315.003.03f" "16u/cs1335.0U1.16u" "16u/cs1136.6U1.16u" "03f/cs1315.004.03f"
python3 sensei.py scoreteacher
python3 sensei.py scoreteacher "George Steinhorst"
python3 sensei.py scoreteacher "Seth Giovanetti"
python3 sensei.py compare
python3 sensei.py scoreteacher "Michael Christiansen"
python3 sensei.py scoreteacher "Gordon Arnold"
python3 sensei.py compare "Michael Christiansen" "Gordon Arnold"
python3 sensei.py compare "Michael Christiansen" "Gordon Arnold" "Seth Giovanetti"
python3 sensei.py scoreteacher "George Steinhorst"
python3 sensei.py scoreteacher "Martha Sanchez"
python3 sensei.py compare "George Steinhorst" "Martha Sanchez"
python3 sensei.py compare "George Steinhorst" "Martha Sanchez" "Seth Giovanetti"
python3 sensei.py scoreclass
python3 sensei.py scoreclass CS1315
python3 sensei.py scoreclass NOTACLASS

REM return
REM pause

REM python3 -m cProfile sensei.py --help > help.log
REM python3 -m cProfile sensei.py setclasscodes > set1.log
REM python3 -m cProfile sensei.py setclasscodes CS UNIV > set2.log
REM python3 -m cProfile sensei.py downloaddirlists > dl1.log
REM python3 -m cProfile sensei.py downloaddirlists 15 16 > dl2.log
REM python3 -m cProfile sensei.py downloadevals > dle.log
REM python3 -m cProfile sensei.py rebuild > rb1.log
REM python3 -m cProfile sensei.py rebuild "16f/cs1*" > rb2.log
REM python3 -m cProfile sensei.py rebuild "16f/*" > rb3.log
REM python3 -m cProfile sensei.py scoreteacher > score1.log
REM python3 -m cProfile sensei.py scoreteacher "Jason Smith" > score2.log
REM python3 -m cProfile sensei.py scoreteacher Timothy\ Farage > score3.log
REM python3 -m cProfile sensei.py scoreteacher Seth Giovanetti > score4.log
REM python3 -m cProfile sensei.py compare > comp1.log
REM python3 -m cProfile sensei.py compare "Jason Smith" "Timothy Farage" > comp2.log
REM python3 -m cProfile sensei.py compare "Jason Smith" "Timothy Farage" "Seth Giovanetti" > comp3.log
REM python3 -m cProfile sensei.py scoreclass > scorec1.log
REM python3 -m cProfile sensei.py scoreclass CS1337 > scorec2.log
REM python3 -m cProfile sensei.py scoreclass NOTACLASS > scorec3.log
