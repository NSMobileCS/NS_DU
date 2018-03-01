"""
NRS Disk Usage Utility

Usage: You can open the program with python cmd-line or IDLE python.
If you want to check the size of a given directory you're browsing through
a file explorer, another option is to copy or move the nrs_du_x.x.py file into
the directory in question, then run it by your preferred method

"""
version="Alpha 0.3.1"


class Path:
    """
    Class for storing/managing directory paths on windows & unix based OSes.
    Recommend using absolute paths
    """
    def __init__(self, addr):
        import sys

        try:
            addr = addr.get()
        except (TypeError, AttributeError) as theError:
            pass

        self.list = []
        self.win = False

        winList, linList = addr.split("\\"), addr.split("/")
        if len(winList) < len(linList):
            self.list = linList
        else:
            self.list = winList

        if sys.platform[:3].lower() == 'win':
            self.win = True

        while self.list[0] == '' and len(self.list) > 1:
            self.list = self.list[1:]


    def __str__(self):
        return self.get()

    def __repr__(self):
        s = self.get()
        return s

    def get(self):
        if self.win:
            if len(self.list) < 2:
                return self.list[0] + "\\"
            return '\\'.join(self.list)
        return '/' + '/'.join(self.list)

    def lvl_up(self):
        """
        removes a file system hierarchy level
        if p = Path('/home/user/docs'), p.lvl_up() ==> '/home/user'
        """
        if self.win:
            if len(self.list) == 1:
                print("My program sees this as the top of the filesystem. If you need to select a different Windows drive letter, you'll probably have to manually restart my program there, or map the drive to a subfolder under whichever drive you're under now")
                return self.get()
            self.list = self.list[:-1]
            # print('self.list: ',)
            # print(self.list)
            return self.get()

        if len(self.list) < 1:
            return "/"
        self.list = self.list[:-1]
        return self.get()

    def add(self, subdir):
        """
        adds a file-system-hierarchy level. ie, a directory name
        as when descending into a subdirectory
        """
        if self.win:
            self.list.append(subdir.strip('\\'))
        if not self.win:
            self.list.append(subdir.strip('/'))


    def short(self):
        return self.list[-1]




class Dir:



    def __init__(self, path, rcr_dep=0, rcr_dep_max=16, dialog_active=False, isThread=False, verbose=False):
        import os

        shortout = False
        self.path = Path(path)
        self.rcr_dep = rcr_dep
        self.rcr_dep_max = rcr_dep_max
        self.verbose = verbose
        self.l_dir = [] #updates to list of contents of current path
        self.sdrs = []  #all files; gets updated to (size, path) tuples
        self.filz = []  #all dirs; gets updated to (size, path) tuples
        self.top_f = [] #top usage files
        self.top_d = [] #top usage dirs
        self.totalSize = 0
        self.isThread = isThread








        try:
            os.chdir(self.path.get())
        except OSError:
            if self.verbose:
                print("\n"*3 + "!"*5 + "__OSError__" + "!" * 5 + "\n" * 2)
                print(self)
            shortout = True

        if not shortout:
            self.popl_dir()
            self.pop_sf()
            self.totalSize = self.sumOwnSize()
            self.top_f = self.filz[:6]
            self.top_d = self.sdrs[:6]

        if self.isThread:
            self.mkGlobScoreSizeFactor()
            self.applySizeScoreFactors()

        if dialog_active == True:
            self.dialog()

    def mkGlobScoreSizeFactor(self):
        sz = self.totalSize
        self.glbSzFct = 2
        for i in range(3):
            sz /= 1024
            if sz < 1024:
                break
            self.glbSzFct += 2

    def sizeScoreBot(self, rawSize):
        indvScore = 2
        for n in range(3):
            rawSize /= 1024
            if rawSize < 1024:
                break
            indvScore += 2
        return indvScore

    def applySizeScoreFactors(self):
        l=[]
        for rawSize, path in self.top_d:
            # print('rawSize', end='\t')
            # print(rawSize, end='\t')
            # print(type(rawSize), end='\n\n')
            # print('path', end='\t')
            # print(path, end='\t')
            # print(path, end='\t')
            # print(type(path))
            txtSize = self.prettySize(rawSize)
            dispSize = self.sizeScoreBot(rawSize)
            p = Path(path)
            l.append((txtSize, dispSize*self.glbSzFct, p.short(), p.get()))


        self.sdrsTuple = tuple(l)
        # print(self.sdrsTuple)

        m = []
        for rawSize, path in self.top_f:
            txtSize = self.prettySize(rawSize)
            dispSize = self.sizeScoreBot(rawSize)
            p = Path(path)
            m.append((txtSize, dispSize*self.glbSzFct, p.short()))

        self.filzTuple = tuple(m)








    def __str__(self):
        s = "Dir instance. path = " + str(self.path.get()) + "\n" + "rcr_dep, rcr_dep_max = " + str(self.rcr_dep) + " , " + str(self.rcr_dep_max) + "\n\n" + "l_dir: \n\n" # + str(self.totalSize)
        stopper = 0
        for i in self.l_dir:
            stopper += 1
            if stopper > 20:
                return str(s)
            s += str(i)
            s += "\n"
        return str(s)

    def prettySize(self, n):
        i = 0
        while i < 3 and n / 1024 > 1:
            n = n / 1024
            i += 1
        sl = ['bytes', 'KiB', 'MiB', 'GiB']
        return str(n) + " " + sl[i]


    def popl_dir(self):
        """
        populates self.l_dir w/ modified output of os.listdir()
        """
        import os
        try:
            curpath = self.path.get()

            for i in os.listdir(curpath):
                if i[0] != ".":
                    temPath = Path(curpath)
                    temPath.add(i)
                    self.l_dir.append(temPath)
        except Exception as ex:
            if self.verbose:
                print("!*!"*3+"EXCEPTION IN SELF.popl_dir: "+"!*!"*3)
                print(ex)
            else:
                pass


    def pop_sf(self):
        """
        populates self.sdrs & self.filz using self.l_dir

        """
        from operator import itemgetter
        import os
        for fi in self.l_dir:
            fi = fi.get()

            try:
                if os.path.isfile(fi):
                    self.filz.append(Path(fi))
                else:
                    self.sdrs.append(Path(fi))
            except Exception as ex:
                if self.verbose:
                    print("!*! EXCEPTION IN SELF.pop_sf() !*!")
                    print(ex)
                else:
                    pass


        for i in range(len(self.filz)):
            try:
                a = os.path.getsize(self.filz[i].get())
                b = self.filz[i]

                self.filz[i] = (a, b)
            except Exception as ex:
                if self.verbose:
                    print("!*! EXCEPTION IN SELF.pop_sf() !*!")
                    print(ex)
                else:
                    pass
        for i in range(len(self.sdrs)):
            sd = self.sdrs[i].get()
            sz = self.getdirsize(sd)
            self.sdrs[i] = (sz, sd)


        self.filz = sorted(self.filz, key=self.displayscore, reverse=True)
        self.sdrs = sorted(self.sdrs, key=self.displayscore, reverse=True)



    def getdirsize(self, d):
        if self.rcr_dep > self.rcr_dep_max:
            return 0
        spawn = Dir(d, self.rcr_dep + 1, self.rcr_dep_max, isThread=self.isThread, verbose=self.verbose)
        return spawn.totalSize


    def sumOwnSize(self):
        total = 0
        for f in self.filz:
            total += f[0]
        for d in self.sdrs:
            total += d[0]
        return total


    def displayscore(self, term):
        return term[0] * 16


    def dialog(self):
        import os
        import sys
        print("\nCURRENT DIRECTORY: " + self.path.get() + " \t\t TOTAL SIZE: " + self.prettySize(self.totalSize) + "\n\n")
        
        sdcount, sfcount = 0, 0

        print("Files with Highest Disk Usage: \n")

        for siz, pth in self.top_f:
            sfcount += 1
            print(str(sfcount) + '.' + '\t' + '[[' + self.prettySize(siz) +']] ' + pth.short())

        print(" - - - - - - - - - - - - - - - - \n\n")

        print("Sub-Directories with Highest Disk Usage: \n")

        print("\nCURRENT DIRECTORY: " + self.path.get() + " \t\t TOTAL SIZE: " + self.prettySize(self.totalSize) + "\n\n")

        for siz, pth in self.top_d:
            sdcount += 1
            print("{} . {} [[ {} ]]   {}".format(sdcount, '\t', self.prettySize(siz), pth))
        print("\n")
        print("---> You can explore any of the subdirectories (sub-folders) listed here - just enter the number next to it & have a look inside")
        print("'..'  -  Go up one level. \n'd'  -  view current directory in Dolphin explorer (Kubuntu)...\n'e'  -  windows explorer...\n'o'  -  OS X (finder)...\n...or enter 'q' to quit to Python interpreter\n")

        dlg = input("Your choice: ")
        if dlg == '..' or dlg == '\'..\'':
            return Dir(self.path.lvl_up(), rcr_dep=self.rcr_dep, rcr_dep_max=self.rcr_dep_max, dialog_active=True, verbose=self.verbose)
        if dlg == 'd' or dlg == 'D':
            return os.system("dolphin %s" % str(self.path))
        if dlg == 'o' or dlg == 'O':
            return os.system("open %s" % str(self.path))
        if dlg == 'e' or dlg == 'E':
            return os.system("explorer %s" % str(self.path))
        if dlg == 'q' or dlg == 'Q':            
            return
        else:
            try:
                dlg = int(dlg)
                return Dir(path=self.sdrs[dlg-1][-1], rcr_dep=self.rcr_dep, rcr_dep_max=self.rcr_dep_max, dialog_active=True, verbose=self.verbose)
            except Exception:
                return self.dialog()
        



def txtuiLoop():
    import os
    import time
    now = Path(os.getcwd())
    print("\t", end='')
    for i in range(20):
        print('|||', end='')
        time.sleep(.01)
    print('\n', end='')
        
    print("\tWelcome to NS_DU: NS Mobile Computing Sol's Disk Usage Investigator")
    print("\n\tVersion: %s\tTime: %s" % (version, time.asctime()))
    print("\tCURRENT DIRECTORY: %s" % str(now))
    print("\t", end='')
    for i in range(60):
        print('|', end='')
        time.sleep(.01)
    print('\n')

    print("Start in %s ?" % str(now))
    chpath = input("\nPress Enter to start, or enter \'C\' to change directory: ")
    if chpath.lower() == 'c' or chpath.lower() == "'c'":
        new = input("Enter directory path to change to: ")
        try:
            os.chdir(new)
            now = Path(os.getcwd())
            d = Dir(now.get(), dialog_active=True)

        except Exception:
            print("Error. Couldn't change directory to: %s. Please double check for typos &/or contact me to submit a bug report (ns.mobile.comp.slns@gmail.com)" % new.get(), end='')
            for i in range(5):
                print(".", end="")
                time.sleep(.6)
            print(" \n")
            return mainLoop()
    else:
        d = Dir(now.get(), dialog_active=True)
        
    
if __name__ == '__main__':
#    q=input("Make Selection:\n  1\tText Mode\n  2\tTuple Mode\n  3\tNeither\n\n\t\tSelection: ")
    q = '2'
    if q == '1':
        txtuiLoop()
    elif q == '2':
        d = Dir("/home/nrs/Python", isThread=True)
        # print("self.sdrsTuple,")
        # print(str(d.sdrsTuple),end="\n\n")
        # print("self.filzTuple,")
        # print(str(d.filzTuple))
    elif q == '3':
        d = Dir('/home/nrs/Python')


