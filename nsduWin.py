#!/usr/bin/python3

"""
Main classes for nsdu graphical edition.

NSDU - disk usage explorer for you

Copyright  2015 Nathan R Smith.
		[Contact: nrsmith012@gmail.com]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

"""

from PySide import QtCore, QtGui
import sys
from time import sleep as zzz
import os
import nsduCoreWin as nsduCore
from nsduCore import Path
import lineBoxesWin as lineBoxes
from lineBoxes import LBDir, LBFile



class SignalMaker(QtCore.QObject):
    tupSig = QtCore.Signal(tuple)
    strSig = QtCore.Signal(str)
    pathObjSig = QtCore.Signal(type(nsduCore.Path("/home/example")))

class NWorker(QtCore.QThread):

    fromWorker = QtCore.Signal(tuple)

    def __init__(self, parent=None):
        super(NWorker, self).__init__(parent)
        self.toGuiSig = SignalMaker()

    def run(self):
        print("Debugging Info Start.\n")
        print("Multithreading: NWorker thread initialized")

    @QtCore.Slot(str)
    def runCycle(self, path):
        self.du = nsduCore.Dir(path, dialog_active=False, isThread=True)
        fz = self.du.filzTuple
        sd = self.du.sdrsTuple
        size = self.du.prettySize(self.du.totalSize)
        allTuples = (sd, fz, size)
        print('nworker tuples')
        print(allTuples)
        self.fromWorker.emit(allTuples)
        print("cycle done")





class NSDUGui(QtGui.QDialog):

    toWorker = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(NSDUGui, self).__init__()

        self.nWorker = NWorker()
        self.nWorker.start()
        self.nWorker.fromWorker.connect(self.recDUTuple)


        self.toWorker.connect(self.nWorker.runCycle)

        #the following code starts a listener thread for 'open in explorer' functionality
        self.opener = OpenInExplorer()
        self.openPathSig = SignalMaker()
        self.openPathSig.strSig.connect(self.opener.openUrl)
        self.opener.start()
        self.opener.setPriority(QtCore.QThread.LowPriority)

        self.path = Path(os.getcwd())

        self.initUI()





    def initUI(self):

        self.setMinimumWidth(1600)
        self.setMinimumHeight(800)
        self.createMenu()
        self.createPathDlg()

        self.initSubDirGroupBox()
        self.initFilzGroupBox()

        self.mkUpButtonCtrls()



        self.regFont = QtGui.QFont()
        self.regFont.setFamily("Meiryo UI")
        self.regFont.setPointSize(12)
        self.bigFont = QtGui.QFont()
        self.bigFont.setFamily("Meiryo UI")
        self.bigFont.setPointSize(12)
        self.setFont(self.regFont)


        self.mainLayout = QtGui.QGridLayout()


        self.mainLayout.setMenuBar(self.menuBar)

        self.mainLayout.setColumnMinimumWidth(0, 512)
        self.mainLayout.setColumnMinimumWidth(1, 648)
        self.mainLayout.setRowMinimumHeight(0, 648)

        self.mainLayout.addWidget(self.filzGroupBox, 0, 0)
        self.mainLayout.addWidget(self.subDirGroupBox, 0, 1)
        self.mainLayout.addWidget(self.topGroupBox, 2, 0)
        self.mainLayout.addWidget(self.navBox, 2, 1)
        self.setLayout(self.mainLayout)

        self.setWindowTitle("NS_DU - The disk-usage explorer for you")

    def createMenu(self):
        self.menuBar = QtGui.QMenuBar()

        self.fileMenu = QtGui.QMenu("&File", self)
        self.exitAction = self.fileMenu.addAction("E&xit")
        self.exitAction.triggered.connect(self.appQuit)
        self.menuBar.addMenu(self.fileMenu)



    def appQuit(self):

        try:
            self.nWorker.exit()
            if self.nWorker.isRunning():
                self.nWorker.terminate()
        except Exception as e:
            print(e)
            self.nWorker.terminate()

        try:
            self.opener.exit()
            if self.opener.isRunning():
                self.opener.terminate()
        except Exception as xception:
            print(xception)
            self.opener.terminate()

        QtGui.QApplication.closeAllWindows()

        self.close()

    @QtCore.Slot(tuple)
    def recDUTuple(self, tup):
        print('recDUTuple\ntuple:', end="\t")
        print(tup)
        self.subDirTuples = tup[0]
        self.filzTuples = tup[1]
        self.totalSizeLineEdit.setText("[[ %s ]]" % tup[2])
        self.updateSubDirGroupBox(self.subDirTuples)
        self.updateFilzGroupbox(self.filzTuples)


    def createPathDlg(self):
        self.topGroupBox = QtGui.QGroupBox("    *** Start Here ***    ")

        layout = QtGui.QGridLayout()
        frameStyle = QtGui.QFrame.Sunken | QtGui.QFrame.Panel
        self.directoryButton = QtGui.QPushButton("Pick Directory Location (Folder) to Scan")
        self.directoryButton.clicked.connect(self.setDirectoryDialog)

        self.directoryLabel = QtGui.QLabel()
        self.directoryLabel.setFrameStyle(frameStyle)

        stButton = QtGui.QPushButton("Start")
        stButton.clicked.connect(self.btnCallNSDU)

        layout.setColumnStretch(1,1)
        layout.setColumnMinimumWidth(1,260)

        layout.addWidget(self.directoryButton, 0, 0)
        layout.addWidget(self.directoryLabel, 0, 1)
        layout.addWidget(stButton, 1, 1)



        pthTxt = self.path.get().split('\\')
        pthTxt = '/'.join(pthTxt)



        self.directoryLabel.setText(pthTxt)
        self.topGroupBox.setLayout(layout)


    def setDirectoryDialog(self):
        options = QtGui.QFileDialog.DontResolveSymlinks | QtGui.QFileDialog.ShowDirsOnly
        directory = QtGui.QFileDialog.getExistingDirectory(self,
                "QFileDialog.getExistingDirectory()",
                self.directoryLabel.text(), options)
        if directory:
            self.path = Path(directory)

    @QtCore.Slot()
    def btnCallNSDU(self):
        self.callNSDU(self.path.get())

    @QtCore.Slot(str)
    def callNSDU(self, strPath):
        dirTxt = '/'.join(strPath.split('\\'))
        self.directoryLabel.setText(dirTxt)
        self.toWorker.emit(strPath)


    def initSubDirGroupBox(self):

        self.subDirLayout = QtGui.QVBoxLayout()
        self.subDirLineWidgetsList = []

        self.subDirGroupBox = QtGui.QGroupBox("Highest Disk Usage -- Directories")
        self.subDirGroupBox.setLayout(self.subDirLayout)



    def updateSubDirGroupBox(self, dirTuplesTuple):

        self.subDirTuples = dirTuplesTuple

        santityCheckCount = 0
        while len(self.subDirLineWidgetsList) > 0:
            santityCheckCount += 1
            if santityCheckCount > 36:
                break
            for oldWidget in self.subDirLineWidgetsList:
                try:
                    self.subDirLayout.removeWidget(oldWidget)
                except Exception as xception:
                    print('removeWidget didnt work')
                    print(xception)
                try:
                    oldWidget.deleteLater()
                except Exception as xception:
                    print('deleteLater didnt work')
                    print(xception)

        del self.subDirLineWidgetsList
        self.subDirLineWidgetsList = []


        for tup in (self.subDirTuples):
            lbd = LBDir(tup)
            lbd.setDirSig.connect(self.callNSDU)

            self.subDirLineWidgetsList.append(lbd)
            self.subDirLayout.addWidget(lbd)


    def initFilzGroupBox(self):

        self.filzGroupBox = QtGui.QGroupBox("Highest Disk Usage -- Files")

        self.filzLineWidgetsList = []
        self.filzLayout = QtGui.QVBoxLayout()

        self.filzGroupBox.setLayout(self.filzLayout)



    def updateFilzGroupbox(self, tup):
        sanityCheckCount = 0
        while len(self.filzLineWidgetsList) > 0:
            sanityCheckCount += 1
            if sanityCheckCount > 100:
                break
            for oldWidget in self.filzLineWidgetsList:
                try:
                    oldWidget.deleteLater()
                    self.filzLayout.removeWidget(oldWidget)
                    del oldWidget
                except Exception as xception:
                    print("self.filzLayout.removeWidget(oldWidget) failed")
                    print("Exception: %s" % xception)
                    print("self.filzLayout: %s\n\noldWidget: %s" % (str(self.filzLayout.__repr__())), str(oldWidget.__repr__()))


        del self.filzLineWidgetsList
        self.filzLineWidgetsList = []

        for num, tup in enumerate(self.filzTuples):
            if num > 4:
                break
            widget = LBFile()
            self.filzLineWidgetsList.append(widget)
            sig = SignalMaker()
            sig.tupSig.connect(widget.set)
            sig.tupSig.emit(tup)

            self.filzLayout.addWidget(widget)



    def mkUpButtonCtrls(self):
        self.navBox = QtGui.QGroupBox("Navigation: ")
        # = QtGui.QFormLayout()
        gridLay = QtGui.QGridLayout()


        upButton=QtGui.QPushButton("^\nUp Dir Level")
        upButton.clicked.connect(self.goUpLvl)

        upLabel = QtGui.QLabel("To enclosing folder ")

        openCurDirLabel = QtGui.QLabel("Open in default System")
        self.openCurDirBtn = QtGui.QPushButton("File Explorer")
        self.openCurDirBtn.clicked.connect(self.openFolderinExplorer)
        sizeLabel = QtGui.QLabel("Total Size: ")
        self.totalSizeLineEdit = QtGui.QLineEdit('[[ 0 bytes ]]')
        self.totalSizeLineEdit.setMinimumWidth(260)
        gridLay.addWidget(openCurDirLabel, 3, 2)
        gridLay.addWidget(self.openCurDirBtn, 3, 3)
        gridLay.addWidget(upLabel, 0, 2)
        gridLay.addWidget(upButton, 0, 3)

        gridLay.addWidget(sizeLabel, 5, 0)
        gridLay.addWidget(self.totalSizeLineEdit, 5, 1)


        self.navBox.setLayout(gridLay)


    @QtCore.Slot()
    def openFolderinExplorer(self):
        path = self.path.get()
        self.openPathSig.strSig.emit(path)



    def goUpLvl(self):
        ptxt = self.path.lvl_up()
        print(str(ptxt)+'  '+'=='+'  '+str(self.path))

        self.directoryLabel.setText(ptxt)
        self.callNSDU(self.path.get())


class OpenInExplorer(QtCore.QThread):
    """
    this class implements "open in (default) file explorer" functionality

    it runs in its own thread & listens for the openPathSig signal

    testing so far, it works
    """
    def __init__(self, parent=None):
        super(OpenInExplorer, self).__init__(parent)
        self.path = None
        self.openedList = []
        self.hasEverHadPath_debug = 'no'

    @QtCore.Slot(str)
    def openUrl(self, path):
        self.path = path
        print("opening %s in default file explorer" % path)

    def run(self):
        while True:
            try:
                if len(self.path) > 1:
                    if sys.platform != 'win32': #if we're not on windows, try the linux (& os x) opener
                        self.linuxOpener(self.path)
                    else:
                        path = "\"file:\\\\\\\\"+path+"\""
                        QtGui.QDesktopServices.openUrl(path)
                    self.openedList.append(self.path)
                    self.path = None
                    self.hasEverHadPath_debug = 'yes'
                else:
                    pass
            except (ValueError, TypeError):
                pass
            zzz(.1)


    def linuxOpener(self, path):
        from subprocess import call
        openers = ['dolphin', 'finder', 'nautilus', 'pcmanfm', 'rox-filer']
        for opener in openers:
            args = [opener]
            args.append(path)
            try:
                print("call(%s)"%str(args))
                call(args)
                break
            except (OSError, FileNotFoundError):
                pass


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    duWin = NSDUGui()

    sys.exit(duWin.exec_())
