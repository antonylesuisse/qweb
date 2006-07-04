SRCDIR=QWeb-0.7
SRCTGZ=${SRCDIR}.tar.gz
ATDIR=Ajaxterm-0.8
ATTGZ=${ATDIR}.tar.gz

all: dist
	true

tgz:
	# Build
	rm README.txt || true
	python2.3 python/setup.py bdist_egg
	python2.4 python/setup.py bdist_egg
	# clean build
	find . -iname '*.pyc' -exec rm -v '{}' ';'
	rm -Rf build python/QWeb.egg-info || true
	# Source
	mkdir ${SRCDIR} || true
	cp -r Makefile README* contrib examples python ${SRCDIR}
	tar czf dist/${SRCTGZ} --owner=0 --group=0 --exclude=\*.pyc --exclude=.svn ${SRCDIR}

	# AjaxTerm
	mkdir ${ATDIR} || true
	cp python/qweb/qweb.py ${ATDIR}
	cp examples/ajaxterm/R*.txt examples/ajaxterm/[a-z]* ${ATDIR}
	tar czf dist/${ATTGZ} ${ATDIR}

dist: tgz
	# cleanup
	rm -Rf ${SRCDIR} ${DEMODIR} ${ATDIR}

pub: tgz
	# publish
ifeq ($(USER),wis)
	rsync -av dist/ wis@udev.org:sites/antony.lesuisse.org/public/qweb/files/
	rm -Rf ${SRCDIR} ${DEMODIR} ${ATDIR}
	contrib/trac/tracsave.py 'http://antony.lesuisse.org/qweb/trac/wiki/WikiStart' 'dist/QWeb-README-wiki.txt'
	contrib/trac/tracsave.py 'http://antony.lesuisse.org/qweb/trac/wiki/AjaxTerm' 'examples/ajaxterm/README.txt'
endif

