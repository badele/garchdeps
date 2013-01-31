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
import unittest

# Parameters
debug = 0
spkg = ""
slimit = 10000
counters = {}


def getCounter(name, inc=1):
    """Global counter, used for generate idx color"""
    global counters
    if name not in counters:
        counters[name] = 0

    counters[name] += inc

    return counters[name]


def convertSize(s):
    """ Convert size to human readable"""
    if s > (1000 * 1000):
        r = "%s %s" % (int(s / 1024 / 1024), "GB")
    else:
        if s > 1000:
            r = "%s %s" % (int(s / 1024), "MB")
        else:
            r = "%s KB" % s

    return r



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
        """ Is virtual"""
        return self.__virtual

    @virtual.setter
    def virtual(self, value):
        self.__virtual = value

    @property
    def providedby(self):
        """Provided by"""
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


    def calcGraphviz(self,
                        packages,
                        blocklist,
                        endlevel=99,
                        level=0,
                        idxcolor=1,
                        duplicate=None):
        """Generate dot for a package"""
        if not duplicate:
            duplicate = []

        s = ""

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
                 convertSize(p.size),
                 convertSize(p.totalsize)
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
                     convertSize(p.size),
                     convertSize(p.totalsize),
                     opts
                     )
            else:
                s += '"%s" [label="%s\\n%s\\n%s" %s];\n' %\
                    (p.pkgname,
                     self.pkgname,
                     convertSize(p.size),
                     convertSize(p.totalsize),
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
                        (d.pkgname, o.pkgname, d.pkgname, convertSize(d.size), convertSize(d.totalsize), opts)
                else:
                    s += '"%s" [label="%s\\n%s\\n%s" %s];\n' % (o.pkgname, o.pkgname, convertSize(d.size), convertSize(d.totalsize), opts)

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

    def showTreeDeps(self, level=0, pkglist=None):
        """Show the tree deps for a package"""
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
                s += p.showTreeDeps(level, pkglist)

        return s

    def searchMaxDepth(self, current=0, maxlevel=0, result=None ):
        """Search the max depth for a package"""
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
        """Calc all deps for a package"""
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
        """Calc a total size for a package"""
        totalsize = 0
        for d in self.__alldeps:
            totalsize += d.size

        self.totalsize = totalsize

    def addDeps(self, obj):
        """Add package object in deps object"""
        if obj not in self.__deps:
            self.__deps.append(obj)

    def addUsedBy(self, obj):
        """Add package object in used object"""
        if obj not in self.__usedby:
            self.__usedby.append(obj)

class Packages:
    """ Packages object"""
    @property
    def mini(self):
        return self.__mini

    @property
    def maxi(self):
        return self.__maxi

    @property
    def fullsize(self):
        return self.__fullsize

    def __init__(self, initvalue=()):
        self.mylist = []
        self.__mini = {}
        self.__maxi = {}
        self.__fullsize = 0
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
        """Private method for searching min/max value"""
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
        """Return package object by pkgname"""
        for o in self.mylist:
            if o.pkgname == pkgname:
                return o
        return None

    def __contains__(self, obj):
        """search pkg object"""
        for o in self.mylist:
            if o == obj:
                return o
        return None

    def beforeGraph(self):
        """Generate top dot file"""
        s = 'digraph G0 {\n'
        s += "forcelabels=true;\n"
        s += "rankdir=TB;\n"
        s += 'node [shape=egg, fontname=Deja, style="filled",\
 truecolor=true, fontsize=10, \
 fillcolor="gray70", color="gray70", fontcolor="white"];\n'

        return s

    def afterGraph(self):
        """Generate end dot file"""
        s = ("}")

        return s

    def calcGraphviz(self, tograph=None, blocklist=None, endlevel=99):
        """Generate dot for packages"""
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

    def filterManualInstall(self, search=True):
        """Filter packages by manual install"""
        result = Packages()
        for o in self.mylist:
            if o.manualinstalled == search:
                result.append(o)

        return result

    def filterNbDeps(self, minsearch, maxsearch=9999, maxlevel=99):
        """Filter packages by nbdeps (range)"""
        result = Packages()
        for o in self.mylist:
            if o.filterNbDeps(minsearch, maxsearch, maxlevel):
                result.append(o)

        return result

    def filterByNbProvides(self, minsearch, maxsearch):
        """Filter packages by nbprovides (range)"""
        result = Packages()
        for o in self.mylist:
            if o.nbprovides >= minsearch and o.nbprovides <= maxsearch:
                result.append(o)

        return result

    def filterByNbUsed(self, minsearch, maxsearch=9999):
        """Filter packages by nbused (range)"""
        result = Packages()
        for o in self.mylist:
            if o.nbused >= minsearch and o.nbused <= maxsearch:
                result.append(o)

        return result

    def analyzeDependencies(self):
        """Analyze and populate datas"""
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

    def calcFullSize(self):
        """ Get size of all installed packages"""
        size = 0
        for p in self.mylist:
            size += p.size

        self.__fullsize = size

    def calcStats(self):
        """Calc and Seach Min/Max"""
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

    def searchMaxDepth(self):
        """Calc maxdep for all packages"""
        for p in self.mylist:
            p.maxdepth = p.searchMaxDepth(0, 0)


    def showItem(self, title, field):
        """ Show Item field"""
        if field in ('size', 'totalsize'):
            minvalue = convertSize(
                getattr(self.__mini[field], field))
            maxvalue = convertSize(
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
        """Show summary infos"""
        print ("Packages installed: %s" % len(self.mylist))
        self.showItem("Size", 'size')
        self.showItem("Total Size", 'totalsize')
        self.showItem('Used by', 'nbused')
        self.showItem('Total deps', 'nbtotaldeps')
        self.showItem('Max depths', 'maxdepth')
        print ("All packages size: %s" % convertSize(self.fullsize))


    def showColumn(self):
        """Show list packages in column"""
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
                    convertSize(p.size),
                    convertSize(p.totalsize),
                    "#" * int((p.totalsize / float(maxtsize)) * 10)))

    def sortBy(self, sortby):
        """Sort by package property"""
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


# Test here due error pickle if i use test in test.py file
class TestPackages(unittest.TestCase):
    def setUp(self):
        """Before unittest"""
        pwd = os.path.dirname(__file__)
        filename = "%s/%s" % (pwd, "packages")
        self.__allpackages = loadPkgInfo(filename, False)

    def test_nbpackages(self):
        self.assertEqual(len(self.__allpackages), 1568)

    def test_fullsize(self):
        self.assertEqual(self.__allpackages.fullsize, 10671164)

    def test_maxiobject(self):
        self.assertEqual(self.__allpackages.maxi['size'].pkgname,
                         'microchip-mplabx-bin')
        self.assertEqual(self.__allpackages.maxi['totalsize'].pkgname,
                         'kdevelop')
        self.assertEqual(self.__allpackages.maxi['nbused'].pkgname,
                         'glibc')
        self.assertEqual(self.__allpackages.maxi['nbtotaldeps'].pkgname,
                         'kipi-plugins')
        self.assertEqual(self.__allpackages.maxi['maxdepth'].pkgname,
                         'kdevelop')

    def test_minobject(self):
        self.assertEqual(self.__allpackages.mini['size'].pkgname,
                         'xclm-dirs')
        self.assertEqual(self.__allpackages.mini['totalsize'].pkgname,
                         'yelp-xsl')
        self.assertEqual(self.__allpackages.mini['nbused'].pkgname,
                         'zsh')
        self.assertEqual(self.__allpackages.mini['nbtotaldeps'].pkgname,
                         'yelp-xsl')
        self.assertEqual(self.__allpackages.mini['maxdepth'].pkgname,
                         'yelp-xsl')

    def test_maxivalue(self):
        self.assertEqual(self.__allpackages.maxi['size'].size,
                         566304.0)
        self.assertEqual(self.__allpackages.maxi['totalsize'].totalsize,
                         1502348.0)
        self.assertEqual(self.__allpackages.maxi['nbused'].nbused,
                         177)
        self.assertEqual(self.__allpackages.maxi['nbtotaldeps'].nbtotaldeps,
                         296)
        self.assertEqual(self.__allpackages.maxi['maxdepth'].maxdepth,
                         16)

    def test_minivalue(self):
        self.assertEqual(self.__allpackages.mini['size'].size,
                         0)
        self.assertEqual(self.__allpackages.mini['totalsize'].totalsize,
                         0.0)
        self.assertEqual(self.__allpackages.mini['nbused'].nbused,
                         0)
        self.assertEqual(self.__allpackages.mini['nbtotaldeps'].nbtotaldeps,
                         0)
        self.assertEqual(self.__allpackages.mini['maxdepth'].maxdepth,
                         0)


def cmp_pkgused(p1, p2):
    if p1.count == p2.count: return 0
    if p1.count > p2.count: return 1
    return -1

installed = []
depends = {}


def sysexec(cmdLine):
    cmd = os.popen(cmdLine)
    return cmd.read()


def getPkgList(sfilter=""):
    """Load package list from pacman -Qi command"""
    packages = Packages()
    current_pkg = None
    begin_tag_count = 0
    end_tag_count = 1

    output = sysexec("LC_ALL=C pacman -Qi %s 2>>/dev/null" % (sfilter))
    lines = output.split('\n')

    for line in lines:
        # Search name package
        m = re.match(r'^Name +: +(.+)', line)
        if m:
            begin_tag_count += 1

            if begin_tag_count != end_tag_count:
                raise Exception('no found end tag')

            if m.group(1):
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
            current_pkg.manualinstalled = (
                m.group(1) == "Explicitly installed")

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


def loadPkgInfo(filename, forceupdate):
    """Load and cache a packages list"""
    if not forceupdate and os.path.exists(filename):
        packages = pickle.load(open(filename, 'rb'))
    else:
        # Parse all installed packages
        print ("Caching the package list, please wait ...")
        packages = getPkgList()
        packages.analyzeDependencies()
        packages.calcStats()
        packages.calcFullSize()

        # Serialize the packages object
        oldlimit = sys.getrecursionlimit()
        sys.setrecursionlimit(10000)
        pickle.dump(packages, open(filename, 'wb'))
        sys.setrecursionlimit(oldlimit)

    return packages


def generateGraph(packages, findpkg, filename):
    """ Generate a dot graphviz"""
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
    """Search package by pkgname"""
    findpkg = []
    pkglist = pkgnames.split(",")
    for p in pkglist:
        f = packages.getPkgByName(p)
        if f:
            findpkg.append(f)

    return findpkg


def showTreeDeps(p):
    """Show tree dependencies"""
    if p:
        print(p.showTreeDeps())


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
             "nblines=", "find=", "sortby=", "test"])
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

        if opt in ("--test"):
            action = "test"
            sys.argv = [ sys.argv[0] ]
            unittest.main(verbosity=2)

        if opt in ("-h", "--help"):
            usage()
            sys.exit()

    allpackages = loadPkgInfo("/tmp/packages", actionforceupdate)

    if actionfind:
        findpkg = searchPackage(allpackages, pkgnames)

    if action == "tree":
        if findpkg:
            showTreeDeps(findpkg[0])
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
