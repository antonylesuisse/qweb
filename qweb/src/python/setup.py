#!/usr/bin/python

import ez_setup, os, setuptools, sys
ez_setup.use_setuptools()

sys.path[0:0]=['.']
import qweb

setuptools.setup(
	name = 'QWeb',
	version = '0.8',
	url = 'http://antony.lesuisse.org/',
	download_url = 'http://antony.lesuisse.org/',
	license = 'BSD',
	author = 'Antony Lesuisse',
	author_email = 'qweb@udev.org',
	description = 'A high-level Python Web framework, a xml-based templating system, a controler and a request handler.',
	keywords = 'web application server wsgi template xml',
	package_dir = {'': '.'},
	packages = [i for i in os.listdir('.') if i.startswith("qweb")],
	package_data = {
		'qweb_dbadmin': ['*.xml','*.txt'],
	}
)

s=qweb.qweb_doc()
pub=s.split('QWeb Components:\n')[0]
file("README.txt","w").write(s)
file("README-wiki.txt","w").write(pub)

