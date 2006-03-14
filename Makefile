VERSION=0.5
SRCDIR=QWeb-${VERSION}
SRCTGZ=${SRCDIR}.tar.gz
DEMODIR=${SRCDIR}-demo
DEMOTGZ=${DEMODIR}.tar.gz
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
	# DemoApp
	mkdir ${DEMODIR} || true
	cp dist/QWeb-*.egg ${DEMODIR}
	cp examples/demo/[A-Za-z]* ${DEMODIR}
	tar czf dist/${DEMOTGZ} ${DEMODIR}
	# DemoApp
	mkdir ${ATDIR} || true
	cp dist/QWeb-*.egg ${ATDIR}
	cp examples/ajaxterm/[A-Za-z]* ${ATDIR}
	tar czf dist/${ATTGZ} ${ATDIR}

dist: tgz
	# cleanup
	rm -Rf ${SRCDIR}
	rm -Rf ${DEMODIR}
	rm -Rf ${ATDIR}

pub: tgz
	# publish
ifeq ($(USER),wis)
	rsync -av dist/ wis@udev.org:sites/antony.lesuisse.org/public/qweb/files/
	rsync -av --delete ${DEMODIR}/ wis@udev.org:sites/antony.lesuisse.org/public/qweb/demo/
endif
	rm -Rf ${SRCDIR}
	rm -Rf ${DEMODIR}
	rm -Rf ${ATDIR}


