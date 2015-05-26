from PySide import QtCore, QtGui
import time

demoDirTuple = ('200.546875 KiB', 4, 'log', '/home/nrs/PycharmProjects/untitled/du/log')

demoFilzTuple = ('13.6005859375 KiB', 4, 'nsduCore.py')
demoPolyDirTuple = (('16.946187019348145 MiB', 16, 'git_demos', '/home/nrs/PycharmProjects/git_demos'), ('268.1923828125 KiB', 64, 'untitled', '/home/nrs/PycharmProjects/untitled'), ('20.14453125 KiB', 8, 'stk-ovr-flo-etc', '/home/nrs/PycharmProjects/stk-ovr-flo-etc'), ('12.2900390625 KiB', 8, 'untitled1', '/home/nrs/PycharmProjects/untitled1'))
demoPolyFilzTuple = (('3.591033935546875 MiB', 24, 'pyside_1.2.2.orig.tar.bz2'), ('1.1618928909301758 MiB', 24, 'MATH17-Review 2.4-2.6 and Ch 3 Spr13.pdf'), ('729.1259765625 KiB', 12, 'nsmobilelogo1.png'), ('705.2353515625 KiB', 12, 'fb2.png'), ('681.9697265625 KiB', 12, 'fb1.png'), ('628.4921875 KiB', 12, 'nsmobilelogo.png'))

demodtuple0=(('169.9404594898224 GiB', 36, 'Desktop', '/home/nrs/Desktop'), ('27.235816372558475 GiB', 36, 'Downloads', '/home/nrs/Downloads'), ('12.85695321764797 GiB', 36, 'VirtualBox VMs', '/home/nrs/VirtualBox VMs'), ('2.0525816520676017 GiB', 36, 'Android', '/home/nrs/Android'), ('1.7536027813330293 GiB', 36, 'Videos', '/home/nrs/Videos'), ('1.5728708812966943 GiB', 36, 'Pictures', '/home/nrs/Pictures'))

demodtuple1=(('200.546875 KiB', 4, 'log', '/home/nrs/PycharmProjects/untitled/du/log'), ('30.458984375 KiB', 4, '__pycache__', '/home/nrs/PycharmProjects/untitled/du/__pycache__'))
demodtuple2=(('14.924051284790039 MiB', 16, 'c++', '/usr/include/c++'), ('10.043505668640137 MiB', 16, 'qt4', '/usr/include/qt4'), ('2.530668258666992 MiB', 16, 'linux', '/usr/include/linux'), ('1.7461042404174805 MiB', 16, 'X11', '/usr/include/X11'), ('1.633737564086914 MiB', 16, 'xcb', '/usr/include/xcb'), ('1.4242286682128906 MiB', 16, 'GL', '/usr/include/GL'))

tresTupleList=[(('169.9404594898224 GiB', 36, 'Desktop', '/home/nrs/Desktop'), ('27.235816372558475 GiB', 36, 'Downloads', '/home/nrs/Downloads'), ('12.85695321764797 GiB', 36, 'VirtualBox VMs', '/home/nrs/VirtualBox VMs'), ('2.0525816520676017 GiB', 36, 'Android', '/home/nrs/Android'), ('1.7536027813330293 GiB', 36, 'Videos', '/home/nrs/Videos'), ('1.5728708812966943 GiB', 36, 'Pictures', '/home/nrs/Pictures')), (('200.546875 KiB', 4, 'log', '/home/nrs/PycharmProjects/untitled/du/log'), ('30.458984375 KiB', 4, '__pycache__', '/home/nrs/PycharmProjects/untitled/du/__pycache__')), (('14.924051284790039 MiB', 16, 'c++', '/usr/include/c++'), ('10.043505668640137 MiB', 16, 'qt4', '/usr/include/qt4'), ('2.530668258666992 MiB', 16, 'linux', '/usr/include/linux'), ('1.7461042404174805 MiB', 16, 'X11', '/usr/include/X11'), ('1.633737564086914 MiB', 16, 'xcb', '/usr/include/xcb'), ('1.4242286682128906 MiB', 16, 'GL', '/usr/include/GL'))]

import sys

class SignalMaker(QtCore.QObject):
    strSig = QtCore.Signal(str)


class LBDir(QtGui.QWidget):
    setDirSig = QtCore.Signal(str)

    def __init__(self, dirTup, parent=None):
        print("LBDir started")
        super(LBDir, self).__init__(parent)
        self.txtSize = "[  -  ]"
        self.dIndex = 0
        self.name = '  -  '
        self.pathCall = None
        self.parent = parent
        self.setMinimumWidth(620)
        print("dirTup", end='   ')
        print(dirTup)


        self.dIndex = dirTup[1]
        self.name = dirTup[3]

        nameLbl = QtGui.QLabel(dirTup[2])  #dirTup[0] is name, 1 sizeindex, 2 pathname
        sizeLbl = QtGui.QLabel("[Size: " + dirTup[0] + "]")
        sizeBarsLbl = QtGui.QLabel(round(dirTup[1]/3.5)*"||")
        self.btn = QtGui.QCommandLinkButton("Enter %s" % dirTup[2])
        self.btn.setMaximumHeight(36)
        self.btn.setMinimumWidth(90)
        self.btn.setMaximumWidth(140)
        self.btn.clicked.connect(self.sendSignal)

        lay = QtGui.QHBoxLayout()
        lay.addWidget(nameLbl)

        lay.addWidget(sizeLbl)
        lay.addWidget(sizeBarsLbl)
        lay.addWidget(self.btn)
        self.setLayout(lay)


    @QtCore.Slot()
    def sendSignal(self):
        print('signal initiated')
        self.setDirSig.emit(self.name)
        print('signal sent')




class LBFile(QtGui.QWidget):
    def __init__(self, parent=None):

        super(LBFile, self).__init__(parent)
        self.dIndex = 0
        self.parent = parent
        self.setMinimumWidth(620)

    @QtCore.Slot(tuple)
    def set(self, tup):
        self.txtSize = "[Size: " + tup[0] + "]"
        self.dIndex = tup[1]
        self.name = tup[2]
        self.go()

    def go(self):

        nameLbl = QtGui.QLabel(self.name)
        sizeLbl = QtGui.QLabel(self.txtSize)
        sizeBarsLbl = QtGui.QLabel(round(self.dIndex/3.5)*"||")

        lay = QtGui.QHBoxLayout()
        lay.addWidget(nameLbl)

        lay.addWidget(sizeLbl)
        lay.addWidget(sizeBarsLbl)
        groupBox = QtGui.QGroupBox(self.parent)
        groupBox.setLayout(lay)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(groupBox)
        self.setLayout(layout)

