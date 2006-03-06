QWeb Framework

QuickStart
----------

$ wget http://antony.lesuisse.org/qweb/QWeb-0.5.tgz
$ tar zxvf QWeb-0.5.tgz
$ cd QWeb-0.5/tutorial2
$ ./demoapp.fcgi

point your browser to http://localhost:8080/

The examples are tutorial*/

WARNING: Despite their naming in .fcgi, the example are ALSO RUNNABLE FROM
COMMANDLINE.

When runned from command line where they start their own webserver on port
8080.  They also may be run as FastCGI or regular CGI by any FastCGI or CGI
compatible web server.

Qweb Core Features
------------------

QWeb has the following features, each feature may be used independently of all
the others:

	- An xml templating engine

	- An simple controller

	- A WSGI HTPP request handler

	- A WSGI server

QWeb applications are runnable:

	- in standalone mode (run it from commandline)
	- in FastCGI mode (throught a FastCGI compatible webserver)
	- in Regular CGI mode (throught a CGI compatible webserver)
	- by any python WSGI compliant server
	- from php using support/php/pyphp wrapper
	- from asp.net using support/aspnet wrapper

QWeb doesn't provide any database access but it intergrates nicely with ORMs
such as SQLObject, SQLAlchemy or the plain DB-API API.


Qweb Components:
----------------

QWeb also feature a simple components api, that enables developers to easily
produces reusable components.

Default qweb components:

	- qweb_static:
		A qweb component to serve static content from the filesystem or from
		zipfiles.


License
-------
qweb/fcgi.py wich is BSD-like from saddi.com.
Everything else is put in the public domain.

