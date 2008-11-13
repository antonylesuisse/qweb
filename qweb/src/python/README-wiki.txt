= QWeb Framework =

== What is QWeb ? ==

QWeb is a python based [http://www.python.org/doc/peps/pep-0333/ WSGI]
compatible web framework, it provides an infratructure to quickly build web
applications consisting of:

 * A lightweight request handler (QWebRequest)
 * An xml templating engine (QWebXml and QWebHtml)
 * A simple name based controler (qweb_control)
 * A standalone WSGI Server (QWebWSGIServer)
 * A cgi and fastcgi WSGI wrapper (taken from flup)
 * A startup function that starts cgi, factgi or standalone according to the
   evironement (qweb_autorun).

QWeb applications are runnable in standalone mode (from commandline), via
FastCGI, Regular CGI or by any python WSGI compliant server.

QWeb doesn't provide any database access but it integrates nicely with ORMs
such as SQLObject, SQLAlchemy or plain DB-API.

Written by Antony Lesuisse (email al AT udev.org)

Homepage: http://antony.lesuisse.org/qweb/trac/

Forum: [http://antony.lesuisse.org/qweb/forum/viewforum.php?id=1 Forum]

== Quick Start (for Linux, MacOS X and cygwin) ==

Make sure you have at least python 2.3 installed and run the following commands:

{{{
$ wget http://antony.lesuisse.org/qweb/files/QWeb-0.7.tar.gz
$ tar zxvf QWeb-0.7.tar.gz
$ cd QWeb-0.7/examples/blog
$ ./blog.py
}}}

And point your browser to http://localhost:8080/

You may also try AjaxTerm which uses qweb request handler.

== Download ==

 * Version 0.7:
   * Source [/qweb/files/QWeb-0.7.tar.gz QWeb-0.7.tar.gz]
   * Python 2.3 Egg [/qweb/files/QWeb-0.7-py2.3.egg QWeb-0.7-py2.3.egg]
   * Python 2.4 Egg [/qweb/files/QWeb-0.7-py2.4.egg QWeb-0.7-py2.4.egg]

 * [/qweb/trac/browser Browse the source repository]

== Documentation ==

 * [/qweb/trac/browser/trunk/README.txt?format=raw Read the included documentation] 
 * QwebTemplating

== Mailin-list ==

 * Forum: [http://antony.lesuisse.org/qweb/forum/viewforum.php?id=1 Forum]
 * No mailing-list exists yet, discussion should happen on: [http://mail.python.org/mailman/listinfo/web-sig web-sig] [http://mail.python.org/pipermail/web-sig/ archives]

