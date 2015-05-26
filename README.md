# NS_DU
NS_DU Disk Usage Explorer App
Requires:

PySide - available on pip & ubuntu repo's

Qt 4.8 - http://download.qt.io/archive/qt/4.8/4.8.6/ is the site (assuming you want the Community license version)

Python 3.4 (any 3+ i'd imagine)

all 3 files should be in a directory together.

to invoke as gui program:

on linux

$ python3 nsdu.py #python nsdu.py will fail on a majority of linux & os x because it defaults to python 2.7 or older

on windows add python (python 3, and not python 2) to your system PATH & go

$ python nsdu.py

(if you need python 2 on your path, you can leave it & use "C:\Python34\python.exe nsdu.py" instead)

to invoke as command line (text only) program:

$ python3 -c "from nsduCore import txtuiLoop as ui; ui()" (windows omit the '3' but note same as above re: python 3 in your PATH)

if you don't want to install qt & pyside, i've made a windows executable version (made with cx_Freeze & IExpress) available on my Google Drive https://drive.google.com/file/d/0ByNYpfFU1GXccEkyVTlkd0FGbk0/view?usp=sharing

Questions/comments/etc: nrsmith012@gmail.com
