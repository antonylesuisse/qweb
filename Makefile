VERSION=0.5
SRCDIR=QWeb-${VERSION}
SRCTGZ=${SRCDIR}.tar.gz
BLOGDIR=${SRCDIR}-blog
BLOGTGZ=${BLOGDIR}.tar.gz
ATDIR=${SRCDIR}-ajaxterm
ATTGZ=${ATDIR}.tar.gz

all: dist
	true

tgz:
	# Build
	rm README.txt || true
	python2.3 setup.py bdist_egg
	python2.4 setup.py bdist_egg
	# clean build
	find . -iname '*.pyc' -exec rm -v '{}' ';'
	rm -Rf build src/QWeb.egg-info || true
	# Source
	mkdir ${SRCDIR} || true
	cp -r Makefile README* contrib examples ez_setup.py setup.py src ${SRCDIR}
	tar czf dist/${SRCTGZ} --owner=0 --group=0 --exclude=\*.pyc --exclude=.svn ${SRCDIR}

	# Blog
	mkdir ${BLOGDIR} || true
	cp dist/QWeb-*.egg ${BLOGDIR}
	rsync -a examples/blog/ ${BLOGDIR}/
	tar czf dist/${BLOGTGZ} --exclude=.svn ${BLOGDIR}

	# AjaxTerm
	mkdir ${ATDIR} || true
	cp src/qweb/qweb.py ${ATDIR}
	cp examples/ajaxterm/R*.txt examples/ajaxterm/[a-z]* ${ATDIR}
	tar czf dist/${ATTGZ} ${ATDIR}

dist: tgz
	# cleanup
	rm -Rf ${SRCDIR} ${DEMODIR} ${BLOGDIR} ${ATDIR}

pub: tgz
	# publish
ifeq ($(USER),wis)
	rsync -av dist/ wis@udev.org:sites/antony.lesuisse.org/public/qweb/files/
	rm -Rf ${SRCDIR} ${DEMODIR} ${BLOGDIR} ${ATDIR}
	contrib/trac/tracsave.py 'http://antony.lesuisse.org/qweb/trac/wiki/WikiStart' 'dist/QWeb-README-wiki.txt'
	contrib/trac/tracsave.py 'http://antony.lesuisse.org/qweb/trac/wiki/AjaxTerm' 'examples/ajaxterm/README.txt'
endif

