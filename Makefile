SRCDIR=QWeb-0.8
SRCTGZ=${SRCDIR}.tar.gz
ATDIR=Ajaxterm-0.10
ATTGZ=${ATDIR}.tar.gz

all: dist
	true

tgz:
	mkdir dist || true
	# Build
	rm README.txt || true
	cd python; python2.3 setup.py bdist_egg
	cd python; python2.4 setup.py bdist_egg
	# copy files
	cp python/dist/*.egg dist
	# clean build
	find . -iname '*.pyc' -exec rm -v '{}' ';'
	rm -Rf python/build python/dist python/QWeb.egg-info || true
	# Source
	mkdir ${SRCDIR} || true
	cp -r Makefile python ${SRCDIR}
	tar czf dist/${SRCTGZ} --owner=0 --group=0 --exclude=\*.pyc --exclude=.svn ${SRCDIR}
	rm -Rf ${SRCDIR}
	# AjaxTerm
	mkdir ${ATDIR} || true
	cp python/qweb/qweb.py ${ATDIR}
	cp ajaxterm/R*.txt ajaxterm/[a-z]* ${ATDIR}
	tar czf dist/${ATTGZ} ${ATDIR}

dist: tgz
	# cleanup
	rm -Rf ${SRCDIR} ${DEMODIR} ${ATDIR}

pub: tgz
	# publish
ifeq ($(USER),wis)
	rsync -av dist/ wis@udev.org:sites/antony.lesuisse.org/public/qweb/files/
	rm -Rf ${SRCDIR} ${DEMODIR} ${ATDIR}
	./tracsave.py 'http://antony.lesuisse.org/qweb/trac/wiki/WikiStart' 'README.txt'
	./tracsave.py 'http://antony.lesuisse.org/qweb/trac/wiki/QwebPython' 'python/README-wiki.txt'
	./tracsave.py 'http://antony.lesuisse.org/qweb/trac/wiki/AjaxTerm' 'ajaxterm/README.txt'
endif

