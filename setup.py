#!/usr/bin/python

import ez_setup, os, setuptools, sys
ez_setup.use_setuptools()

sys.path[0:0]=['src']
import qweb

if not os.path.isfile("README.txt"):
	file("README.txt","w").write(qweb.qweb_doc())

setuptools.setup(
	name = 'QWeb',
	version = '0.5',
	url = 'http://antony.lesuisse.org/',
	download_url = 'http://antony.lesuisse.org/',
	license = 'BSD',
	author = 'Antony Lesuisse',
	author_email = 'qweb@udev.org',
	description = 'A high-level Python Web framework, a xml-based templating system, a controler and a request handler.',
	keywords = 'web application server wsgi template xml',
	package_dir = {'': 'src'},
	packages = [i for i in os.listdir('src') if i.startswith("qweb")],
	# How to exclude files from QWeb.egg-info/SOURCES.txt
	# exclude_package_data = { '': ['Makefile'] }
)
