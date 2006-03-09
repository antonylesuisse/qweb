VERSION=0.5
SRCDIR=QWeb-${VERSION}
SRCTGZ=${SRCDIR}.tar.gz
DEMODIR=${SRCDIR}-DemoApp
DEMOTGZ=${DEMODIR}.tar.gz

all: tgz
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
	cp -r Makefile README* contrib demo ez_setup.py setup.py src tut* ${SRCDIR}
	tar czvf dist/${SRCTGZ} --owner=0 --group=0 --exclude=\*.pyc --exclude=.svn ${SRCDIR}
	# DemoApp
	mkdir ${DEMODIR} || true
	cp dist/QWeb-*.egg ${DEMODIR}
	cp demo/[A-Za-z]* ${DEMODIR}
	tar czvf dist/${DEMOTGZ} ${DEMODIR}
	# publish
ifeq ($(USER),wis)
#	rsync -av dist/ wis@udev.org:sites/antony.lesuisse.org/public/qweb/files/
#	rsync -av --delete ${DEMODIR}/ wis@udev.org:sites/antony.lesuisse.org/public/qweb/demo/
endif
	# cleanup
	rm -Rf ${SRCDIR}
	rm -Rf ${DEMODIR}
