#!/usr/bin/python2
# -*- coding: utf-8 -*-

# Sample commands
# ./garchdeps.py -f qt -g /tmp/graph.dot  ; tred /tmp/graph.dot | dot -Tpng  -o /tmp/graph.png

# Import files
import os
import re
import sys
import pickle
import getopt

# Parameters
debug = 0
spkg = ""
slimit = 10000
counters = {}


def getCounter(name, inc=1):
    """Global counter"""
    global counters
    if name not in counters:
        counters[name] = 0

    counters[name] += inc

    return counters[name]


class Package:
    """ Object Package
    This object store the package informations
    """
    @property
    def pkgname(self):
        """ Package name"""
        return self.__pkgname

    @pkgname.setter
    def pkgname(self, value):
        self.__pkgname = value

    @property
    def realpkg(self):
        """ Real object package, from virtual package"""
        if self.virtual:
            p = self.providedby
        else:
            p = self
        return p

    @property
    def raw_deps(self):
        """ Packages deps during parsing pacman -Qi out"""
        return self.__raw_deps

    @property
    def alldeps(self):
        """ All dependencies object for this packages"""
        return self.__alldeps

    @property
    def nbtotaldeps(self):
        """ Total dependencies for this packages"""
        return len(self.__alldeps)

    @property
    def raw_provides(self):
        """ All provides packages during parsing pacman -Qi out"""
        return self.__raw_provides

    @property
    def deps(self):
        """ Dependencies objects"""
        return self.__deps

    @property
    def maxdepth(self):
        """ Max dept (level) dependencies"""
        return self.__maxdepth

    @maxdepth.setter
    def maxdepth(self, value):
        self.__maxdepth = value

    @property
    def usedby(self):
        """ Used objects who use this package"""
        return self.__usedby

    @property
    def nbused(self):
        """ Count nb packages who use this package"""
        return len(self.__usedby)

    @property
    def size(self):
        """Size of package"""
        return self.__size

    @size.setter
    def size(self, value):
        self.__size = value

    @property
    def totalsize(self):
        """Total size of dependencies packages"""
        return self.__totalsize

    @property
    def provides(self):
        """packages provided by this package"""
        return self.__provides

    @property
    def nbprovides(self):
        """nb packages provided by this package"""
        return len(self.__provides)

    @property
    def version(self):
        """ Version of this package"""
        return self.__version

    @version.setter
    def version(self, value):
        self.__version = value

    @property
    def virtual(self):
        return self.__virtual

    @virtual.setter
    def virtual(self, value):
        self.__virtual = value

    @property
    def providedby(self):
        return self.__providedby

    @providedby.setter
    def providedby(self, value):
        self.__providedby = value

    @property
    def manualinstalled(self):
        """this package is installed manually"""
        return self.__manualinstalled

    @manualinstalled.setter
    def manualinstall(self, value):
        self.__manualinstalled = value

    @property
    def idxcolor(self):
        """ store the idx color, used for generate a graph"""
        return self.__idxcolor

    @idxcolor.setter
    def idxcolor(self, value):
        self.__idxcolor = value

    def __init__(self, pkgname=""):
        """ Initialisation variable"""
        self.__pkgname = pkgname
        self.__size = 0
        self.__totalsize = 0
        self.__virtual = False
        self.__provides = Packages()
        self.__raw_provides = []
        self.__deps = Packages()
        self.__raw_deps = []
        self.__alldeps = []
        self.__maxdepth = 0
        self.__usedby = Packages()
        self.__manualinstalled = False
        self.__providedby = None
        self.__version = 0
        self.__idxcolor = -1

    def __repr__(self):
        return self.pkgname

    def convertSize(self, s):
        if s > (1000 * 1000):
            r = "%s %s" % (int(s / 1024 / 1024), "GB")
        else:
            if s > 1000:
                r = "%s %s" % (int(s / 1024), "MB")
            else:
                r = "%s KB" % s

        return r

    # Package
    def calcGraphviz(self,
                        packages,
                        blocklist,
                        endlevel=99,
                        level=0,
                        idxcolor=1,
                        duplicate=None):

        if not duplicate:
            duplicate = []

        s = ""

        size = len(packages)

        mini = packages[20].nbused
        mini1 = packages[40].nbused

        # If a virtual package, get a provided package
        p = self.realpkg

        # Check if allready exist
        exists = True
        if p not in duplicate:
            exists = False
            duplicate.append(p)

        subgraph = False
        if p in blocklist:
            subgraph = True
            s += 'subgraph cluster_%s { style="rounded,filled"; colorscheme=pastel28;\
 fillcolor=%s; color="#00000000"; fontsize=128;\
label = "%s (%s - %s)";\n' %\
                (getCounter('cluster'),
                 (getCounter('idxcolor') % 8) + 1,
                 p.pkgname,
                 self.convertSize(p.size),
                 self.convertSize(p.totalsize)
                 )

        fillcolor = ""
        if level == 0:
            fillcolor = ', fillcolor="red2", color="red2"'

        if not exists:
            nbused = p.nbused

            if nbused > mini1:
                opts = 'fontsize=30'
                if fillcolor == "":
                    opts += ', fillcolor="deepskyblue", color="deepskyblue"'

                if nbused > mini:
                    opts = 'fontsize=45'
                    if fillcolor == "":
                        opts += ', fillcolor="deeppink", color="deeppink"'

            else:
                opts = 'fontsize=10'

            if fillcolor != "":
                opts += fillcolor

            if self.virtual:
                s += '"%s" [label="%s(by %s)\\n%s\\n%s" %s];\n' %\
                    (self.pkgname,
                     self.pkgname,
                     p.pkgname,
                     self.convertSize(p.size),
                     self.convertSize(p.totalsize),
                     opts
                     )
            else:
                s += '"%s" [label="%s\\n%s\\n%s" %s];\n' %\
                    (p.pkgname,
                     self.pkgname,
                     self.convertSize(p.size),
                     self.convertSize(p.totalsize),
                     opts
                     )

        level += 1
        for o in p.deps:
            d = o.realpkg

            exists = True
            if d not in duplicate:
                exists = False

            if not exists:
                nbused = d.nbused
                if nbused > mini1:
                    opts = 'fontsize=30, fillcolor="deepskyblue", color="deepskyblue"'
                    if nbused > mini:
                        opts = 'fontsize=45, fillcolor="deeppink", color="deeppink"'
                else:
                    opts = 'fontsize=10'

                if o.virtual:
                    s += '"%s" [label="%s(by %s)\\n%s\\n%s" %s];\n' %\
                        (d.pkgname, o.pkgname, d.pkgname, self.convertSize(d.size), self.convertSize(d.totalsize), opts)
                else:
                    s += '"%s" [label="%s\\n%s\\n%s" %s];\n' % (o.pkgname, o.pkgname, self.convertSize(d.size), self.convertSize(d.totalsize), opts)

            s += '"%s" -> "%s";\n' % (p.pkgname, d.pkgname)

            if not exists:
                duplicate.append(d)
                s += d.calcGraphviz(packages,
                                       blocklist,
                                       endlevel,
                                       level,
                                       idxcolor,
                                       duplicate)

        if subgraph:
            s += "}/* bruno */\n"

        return s

    def showGraphviz(self, blocklist=None,
                     endlevel=99, level=0, idxcolor=1, duplicate=None):

        if not blocklist:
            blocklist = []

        if not duplicate:
            duplicate = []

        s = ""

        # If a virtual package, get a provided package
        p = self.realpkg

        # Check if allready exist
        exists = True
        if p not in duplicate:
            exists = False
            p.idxcolor = idxcolor
            duplicate.append(p)

        subgraph = False
        if p in blocklist:
            subgraph = True
            s += "subgraph cluster_%s { colorscheme=set312;style=filled;\
fillcolor=%s;fontsize=128;label = \"%s\";\n" %\
                (getCounter('cluster'),
                 (getCounter('idxcolor') % 12) + 1,
                 p.pkgname)

        # Check if manual installation for calc color
        ccolor = (p.idxcolor % 8) + 2
        if p.manualinstalled:
            if len(p.deps) == 0:
                ccolor = 1
            else:
                found = False
                for t in p.deps:
                    if t.idxcolor != -1:
                        found = True
                if found:
                    ccolor = 1

        if not exists:
            opts = ""
            if p.manualinstalled:
                opts = "shape=house"

            if self.virtual:
                opts = "shape=diamond"

            if self.virtual:
                s += '"%s"[label="L:%s %s(by %s){%s}\n%s\n%s" %s  fillcolor=%s];\n' %\
                    (self.pkgname,
                     level,
                     self.pkgname,
                     p.pkgname,
                     p.idxcolor,
                     p.convertSize(p.size),
                     p.convertSize(p.totalsize),
                     opts,
                     ccolor)
            else:
                s += '"%s"[label="L:%s %s/{%s}\n%s\n%s" %s fillcolor=%s];\n' %\
                    (p.pkgname,
                     level,
                     self.pkgname,
                     p.idxcolor,
                     p.convertSize(p.size),
                     p.convertSize(p.totalsize),
                     opts,
                     ccolor)

        level += 1
        for o in p.deps:
            d = o.realpkg
            if d.idxcolor == -1:
                d.idxcolor = idxcolor

            exists = True
            if d not in duplicate:
                exists = False

            ccolor = (p.idxcolor % 8) + 2
            if not exists:
                if o.virtual:
                    s += '"%s" [label="%s(by %s)/{%s}\n%s\n%s" shape=diamond fillcolor=%s];\n' %\
                        (d.pkgname, o.pkgname, d.pkgname, d.idxcolor, d.convertSize(d.size), d.convertSize(d.totalsize), ccolor)
                else:
                    s += '"%s" [label="%s/{%s}\n%s\n%s" fillcolor=%s];\n' % (o.pkgname, o.pkgname, idxcolor, d.convertSize(d.size), d.convertSize(d.totalsize), ccolor)

            s += '"%s" -> "%s";\n' % (p.pkgname, d.pkgname)

            if not exists:
                duplicate.append(d)
                s += d.showGraphviz(blocklist,endlevel, level, idxcolor, duplicate)

        if subgraph:
            s += "}/* bruno */\n"

        return s

    def showDeps(self, level=0, pkglist=None):
        s = ""

        if not pkglist:
            pkglist = []

        if self.virtual:
            p = self.providedby
        else:
            p = self

        if level == 0:
            if self.virtual:
                s = "%s──%s(by %s)\n" % (level * " ", self.pkgname, p.pkgname)
            else:
                s = "%s──%s \n" % (level * " ", p.pkgname)

        if p.pkgname not in pkglist:
            pkglist.append(p.pkgname)

        level += 1
        nbdeps = len(p.deps)
        cdeps = 0
        for o in p.deps:
            cdeps += 1
            if o.virtual:
                p = o.providedby
            else:
                p = o

            # Calc a separator
            space = level * "   "
            if cdeps == nbdeps:
                line = '└'
            else:
                line = '├'

            if o.virtual:
                s += "%s%s─%s(by %s) \n" % (space, line, o.pkgname, p.pkgname)
            else:
                s += "%s%s─%s \n" % (space, line, p.pkgname)

            if p.pkgname not in pkglist:
                pkglist.append(p.pkgname)
                s += p.showDeps(level, pkglist)

        return s

    def searchMaxDepth(self, current=0, maxlevel=0, result=None ):

        if not result:
            result = []
        rp = self.realpkg

        if len(rp.deps) > 0:
            maxlevel = current + 1
            tmpmax = maxlevel
            for d in rp.deps:
                p = d.realpkg

                if p not in result:
                    result.append(p)
                    tmpmax = p.searchMaxDepth(current + 1, maxlevel, result)
                    maxlevel = max(tmpmax, maxlevel)

                if maxlevel > 50 or current > 50:
                    raise Exception("!!! Ca boucle trop pour %s" % self)

        return maxlevel

    def calcAllDeps(self, uniq=None, current=0):
        if not uniq:
            uniq = []

        for d in self.__deps:
            p = d.realpkg
            if p not in uniq:
                uniq.append(p)
                p.calcAllDeps(uniq, current + 1)

        if current == 0:
            self.__alldeps = uniq

    def calcNbTotalSize(self):
        totalsize = 0
        for d in self.__alldeps:
            totalsize += d.size

        self.totalsize = totalsize

    def addDeps(self, obj):
        if obj not in self.__deps:
            self.__deps.append(obj)

    def addUsedBy(self, obj):
        if obj not in self.__usedby:
            self.__usedby.append(obj)

    def getidxcolor4Useby(self):
        idxcolor = -1

        for o in self.__usedby:
            p = o.realpkg
            if p.idxcolor != -1 and idxcolor == -1:
                idxcolor = p.idxcolor

        return idxcolor


class Packages:

    @property
    def mini(self):
        return self.__mini

    @property
    def maxi(self):
        return self.__maxi

    def __init__(self, initvalue=()):
        self.mylist = []
        self.__mini = {}
        self.__maxi = {}
        for x in initvalue:
            self.append(x)

    def __len__(self):
        return len(self.mylist)

    def __getitem__(self, index):
        if isinstance(index, slice):
            tp = Packages(self.mylist[index.start:index.stop])
            tp.maxi = self.maxi
            return tp
        else:
            return self.mylist[index]

    def append(self, obj):
        if obj not in self.mylist:
            self.mylist.append(obj)

    def __repr__(self):
        return self.mylist.__repr__()

    def __compareField(self, field, obj):
        # Mini
        if not obj.virtual:
            if field not in self.__mini:
                self.__mini[field] = obj
            else:
                if getattr(obj, field) <= getattr(self.__mini[field], field):
                    self.__mini[field] = obj

        # Maxi
        if not obj.virtual:
            if field not in self.__maxi:
                self.__maxi[field] = obj
            else:
                if getattr(obj, field) >= getattr(self.__maxi[field], field):
                    self.__maxi[field] = obj

    def getPkgByName(self, pkgname):
        for o in self.mylist:
            if o.pkgname == pkgname:
                return o
        return None

    def __contains__(self, obj):
        for o in self.mylist:
            if o == obj:
                return o
        return None

    def beforeGraph(self):

        s = 'digraph G0 {\n'
        s += "forcelabels=true;\n"
        s += "rankdir=TB;\n"
        s += 'node [shape=egg, fontname=Deja, style="filled",\
 truecolor=true, fontsize=10, \
 fillcolor="gray70", color="gray70", fontcolor="white"];\n'

        return s

    def afterGraph(self):
        s = ("}")

        return s

    # Packages
    def calcGraphviz(self, tograph=None, blocklist=None, endlevel=99):
        if not tograph:
            tograph = []

        if not blocklist:
            blocklist = []

        r = ""
        idxcolor = 0
        duplicate = [None]
        for o in tograph:
            idxcolor += 1
            r += o.calcGraphviz(self,
                                   blocklist,
                                   endlevel,
                                   0,
                                   idxcolor,
                                   duplicate)

        return r

    def showGraphviz(self, pkglist=None, blocklist=None, endlevel=99):
        if not pkglist:
            pkglist = []

        if not blocklist:
            blocklist = []

        # reset idxcolor
        for o in pkglist:
            o.idxcolor = -1

        r = ""
        idxcolor = 0
        duplicate = [None]
        for o in pkglist:
            idxcolor += 1
            r += o.showGraphviz(blocklist, endlevel, 0, idxcolor, duplicate)

        return r

    def filterManualInstall(self, search=True):
        result = Packages()
        for o in self.mylist:
            if o.manualinstalled == search:
                result.append(o)

        return result

    def filterNbDeps(self, minsearch, maxsearch=9999, maxlevel=99):
        result = Packages()
        for o in self.mylist:
            if o.filterNbDeps(minsearch, maxsearch, maxlevel):
                result.append(o)

        return result

    def filterByNbProvides(self, minsearch, maxsearch):
        result = Packages()
        for o in self.mylist:
            if o.nbprovides >= minsearch and o.nbprovides <= maxsearch:
                result.append(o)

        return result

    def filterByNbUsed(self, minsearch, maxsearch=9999):
        result = Packages()
        for o in self.mylist:
            if o.nbused >= minsearch and o.nbused <= maxsearch:
                result.append(o)

        return result

    def analyseDependencies(self):

        # Calc provide package
        for p in self.mylist:
            for d in p.raw_provides:
                r = self.getPkgByName(d)
                if not r:
                    t = Package(d)
                    t.virtual = True
                    t.providedby = p
                    p.provides.append(d)
                    self.mylist.append(t)

        # Calc a dependencies
        for p in self.mylist:
            for d in p.raw_deps:
                r = self.getPkgByName(d)
                if r:
                    p.deps.append(r)
                    r.usedby.append(p)
                else:
                    print ("Paquet de dependance non trouve %s" % d)

        # Calc depth
        self.searchMaxDepth()

    def calcStats(self):
        for p in self.mylist:
            # Calc dependencies
            p.calcAllDeps()
            p.calcNbTotalSize()

            # Calc mini/maxi
            self.__compareField('size', p)
            self.__compareField('totalsize', p)
            self.__compareField('nbused', p)
            self.__compareField('nbtotaldeps', p)
            self.__compareField('maxdepth', p)

    def showItem(self, title, field):
        if field in ('size', 'totalsize'):
            minvalue = self.__mini[field].convertSize(
                getattr(self.__mini[field], field))
            maxvalue = self.__maxi[field].convertSize(
                getattr(self.__maxi[field], field))
        else:
            minvalue = getattr(self.__mini[field], field)
            maxvalue = getattr(self.__maxi[field], field)

        print ("   %-20s (min/max) : %-30s     %s(%s)" %
               (title,
                "%s(%s)" % (self.__mini[field].pkgname, minvalue),
                self.__maxi[field].pkgname,
                maxvalue
                ))

    def showInfo(self):
        print ("Packages installed: %s" % len(self.mylist))
        self.showItem("Size", 'size')
        self.showItem("Total Size", 'totalsize')
        self.showItem('Used by', 'nbused')
        self.showItem('Total deps', 'nbtotaldeps')
        self.showItem('Max depths', 'maxdepth')

    def showColumn(self):
        maxtsize = 0
        for p in self.mylist:
            maxtsize = max(maxtsize, p.totalsize)

        print ('-----------------------------------------+---------+\
----------+----------+----------+-----------+------------+' )

        print ('%-40s | %-7s | %-8s | %-8s | %-8s | %-9s | %10s |' %
               ("Package",
                "T. Deps",
                "N. depth",
                "N usedby",
                " Size",
                "T. Size",
                "% T. Size"))

        print ('-----------------------------------------+---------+\
----------+----------+----------+-----------+------------+' )

        for p in self.mylist:
            print ('%-40s | %7d | %8d | %8d | %8s | %9s | %-10s |' %
                   (p.pkgname,
                    p.nbtotaldeps,
                    p.maxdepth,
                    p.nbused,
                    p.convertSize(p.size),
                    p.convertSize(p.totalsize),
                    "#" * int((p.totalsize / float(maxtsize)) * 10)))

    def searchMaxDepth(self):
        for p in self.mylist:
            p.maxdepth = p.searchMaxDepth(0, 0)

    def sortBy(self, sortby):
        if sortby != "":
            if sortby == "name":
                self.sortByName()
            if sortby == "nusedby":
                self.sortByNbUsed()
            if sortby == "tsize":
                self.sortByTotalSize()
            if sortby == "size":
                self.sortBySize()
            if sortby == "tdeps":
                self.sortByTotalDeps()

    def sortByName(self):
        self.mylist.sort(key=lambda p: p.pkgname, reverse=False)

    def sortByMaxDepth(self):
        self.mylist.sort(key=lambda p: p.maxdepth, reverse=True)

    def sortByNbUsed(self):
        self.mylist.sort(key=lambda p: p.nbused, reverse=True)

    def sortByTotalDeps(self):
        self.mylist.sort(key=lambda p: p.nbtotaldeps, reverse=True)

    def sortBySize(self):
        self.mylist.sort(key=lambda p: p.size, reverse=True)

    def sortByTotalSize(self):
        self.mylist.sort(key=lambda p: p.totalsize, reverse=True)




def cmp_pkgused(p1, p2):
    if p1.count == p2.count: return 0
    if p1.count > p2.count: return 1
    return -1

installed = []
depends = {}


def sysexec(cmdLine):
    cmd = os.popen(cmdLine)
    return cmd.read()


def getPkgListNew(filter=""):
    global spkg
    global slimit
    packages = Packages()
    current_pkg = None
    begin_tag_count = 0
    end_tag_count = 1

    output = sysexec("LC_ALL=C pacman -Qi %s 2>>/dev/null" % (filter))
    lines = output.split('\n')

    for line in lines:
        # Search name package
        m = re.match(r'^Name +: +(.+)', line)
        if m:
            begin_tag_count += 1

            if begin_tag_count != end_tag_count:
                raise Exception('no found end tag')

            if m.group(1):
                begin_tag = 1
                pkgname = m.group(1)

                if pkgname not in packages:
                    current_pkg = Package(pkgname)
                    packages.append(current_pkg)

        # Search package version
        m = re.match(r'^Version +: +(.+)', line)
        if m and m.group(1) != "None":
            p = m.group(1)
            current_pkg.version = p

        # Search manual installation
        m = re.match(r'^Install Reason +: +(.+)', line)
        if m:
            current_pkg.manualinstalled = (m.group(1) == "Explicitly installed")

        # Search provide package
        m = re.match(r'^Provides +: +(.+)', line)
        if m and m.group(1) != "None":
            for p in m.group(1).split(' '):
                if p != '':
                    m = re.match(r'([^\=\>\<]+).*', p)

                # Leve le numero de version
                if m:
                    p = m.group(1)
                    if p not in current_pkg.raw_provides:
                        current_pkg.raw_provides.append(p)

        # Search dependancy
        m = re.match(r'^Depends On +: +(.+)', line)
        if m and m.group(1) != "None":
            for p in m.group(1).split(' '):
                if p != '':
                    m = re.match(r'([^\=\>\<]+).*', p)

                    # Leve le numero de version
                    if m:
                        pkgname = m.group(1)
                        if pkgname not in current_pkg.raw_deps:
                            current_pkg.raw_deps.append(pkgname)

                    else:
                        raise Exception('ERROR', 'DEPEND SEARCH for %s' % p)

        m = re.match(r'^Installed Size +: +(.+) KiB', line)
        if m:
            p = m.group(1)
            current_pkg.size = float(p)

        # Search end of package
        m = re.match(r'^Description +: +(.+)', line)
        if m:
            end_tag_count += 1

    return packages


def loadPkgInfo(forceupdate):
    if not forceupdate and os.path.exists('/tmp/packages'):
        packages = pickle.load(open('/tmp/packages', 'rb'))
    else:
        # Parse all installed packages
        print ("Caching the package list, please wait ...")
        packages = getPkgListNew()
        packages.analyseDependencies()
        packages.calcStats()

        # Serialize the packages object
        oldlimit = sys.getrecursionlimit()
        sys.setrecursionlimit(10000)
        pickle.dump(packages, open('/tmp/packages', 'wb'))
        sys.setrecursionlimit(oldlimit)

    return packages


def generateGraph(packages, findpkg, filename):
    subgraph = []
    subgraph.append(packages.getPkgByName('kdebase-runtime'))
    subgraph.append(packages.getPkgByName('kdebase-workspace'))
    subgraph.append(packages.getPkgByName('qt'))
    subgraph.append(packages.getPkgByName('gtk3'))
    subgraph.append(packages.getPkgByName('wxgtk'))

    if not findpkg:
        findpkg = packages.filterManualInstall()[:100]
        findpkg.sortBy('tsize')

    r = packages.beforeGraph()
    r += packages.calcGraphviz(findpkg, subgraph, 99)
    r += packages.afterGraph()

    f = open(filename, 'wb')
    f.write(r)
    f.close()


def searchPackage(packages, pkgnames):
    findpkg = []
    pkglist = pkgnames.split(",")
    for p in pkglist:
        f = packages.getPkgByName(p)
        if f:
            findpkg.append(f)

    return findpkg


def showDeps(p):
    if p:
        print(p.showDeps())


def usage():
    print ("Usage: %s [OPTIONS]" % (sys.argv[0]))
    print ("A package dependencies graph tools")
    print ("  -f, --find <pkgname>                 find package")
    print ("  -t, --tree                           show tree dependencies")
    print ("  -n, --num <Num>                      number lines displayed")
    print ("  -g, --graph <filename>               write a graphviz file")
    print ("  -s, --sortby <nusedby, tsize, tdeps> sort list by")
    print ("  -u, --updatep                        force update load pkgfile")
    print ("  -h, --help                           shows this help screen")


def main():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hiug:tn:f:s:",
            ["help", "info", "update", "graph=", "tree",
             "nblines=", "find=", "sortby="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    n = 20  # number line showed
    actionfind = False
    actionforceupdate = False
    findpkg = None
    action = ""
    pkgnames = ""
    filename = ""
    sortby = "nusedby"

    for opt, arg in opts:
        if opt in ("-n", "--nblines"):
            try:
                n = int(arg)
            except ValueError:
                usage()
                sys.exit(2)

        if opt in ("-f", "--find"):
            actionfind = True
            pkgnames = arg

        if opt in ("-u", "--update"):
            actionforceupdate = True

        if opt in ("-g", "--graph"):
            action = "graph"
            filename = arg

        if opt in ("-t", "--tree"):
            action = "tree"

        if opt in ("-s", "--sortby"):
            sortby = arg

        if opt in ("-i", "--info"):
            action = "info"

        if opt in ("-h", "--help"):
            usage()
            sys.exit()

    allpackages = loadPkgInfo(actionforceupdate)

    if actionfind:
        findpkg = searchPackage(allpackages, pkgnames)

    if action == "tree":
        if findpkg:
            showDeps(findpkg[0])
        else:
            print ("Package not found")

    if sortby != "":
        allpackages.sortBy(sortby)

    if action == "graph":
        generateGraph(allpackages, findpkg, filename)

    if action == "info":
        allpackages.showInfo()

    if action == "":
        allpackages[:n].showColumn()


if __name__ == "__main__":
    main()
