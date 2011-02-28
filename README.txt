What is QWeb ?
--------------
QWeb is web framework (mainly an XML templating system) implemented in various laguages.

The core component of qweb is its cool XML templating engine. Some versions
only implements that. While others (python/php) provide additional components.

QWeb was cool around 2006 when it was developped. Now we have many web frameworks.

But i'm still conviced that the xml template engine is better than enything
else on the market in 2011.


What is Ajaxterm ?
------------------
Ajaxterm is an ajax terminal it was made as a showcase for the python version
of QWeb. It only uses the QWeb request handler, not thei xml template engine.

I plan to separate it from qweb and update it to use WebOb instead of qweb.Request.


What is pyphp ? 
---------------
pyphp is a bridge that allow to use python on a php host, and call phpfunction
from python. I wanted to use QWeb python on a php host.


Versions of QWeb
----------------
And the components implemented:

 * qweb_javascript: XML templating
 * qweb_python: XML templating, HTML forms, Controller, WSGI/cgi/fastcgi/builtin-web-server Request handler, Sessions
 * qweb_ruby: XML templating, HTML forms
 * qweb_csharp: XML templating, Controller
 * qweb_java: XML templating, Controller
 * qweb_php: XML templating, HTML forms, Controller, Misc
 
Feedback
--------
Antony Lesuisse: lesuisse AT gmail.com

