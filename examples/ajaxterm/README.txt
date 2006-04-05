About Ajaxterm
--------------

Ajaxterm is a web based terminal. It was totally inspired and works almost
exactly like http://anyterm.org/ except it's much more easy to install.

Written by Antony Lesuisse (email: al AT udev.org)

Homepage: http://antony.lesuisse.org/qweb/trac/wiki/AjaxTerm

Usage:
------

usage: ajaxterm.py [options]

options:
  -h, --help            show this help message and exit
  -pPORT, --port=PORT   Set the TCP port (default: 8080)
  -sSIZE, --size=SIZE   set the terminal size (default: 80x25)
  -cCMD, --command=CMD  set the command (default: /bin/login or ssh localhost)
  -l, --log             log requests to stderr (default: quiet mode)


To use with apache with mod_ssl and mod_proxy:
----------------------------------------------

	Listen 443
	NameVirtualHost *:443

	<VirtualHost *:443>
		ServerName localhost
		SSLEngine On
		SSLCertificateKeyFile ssl/apache.pem
		SSLCertificateFile ssl/apache.pem

		ProxyRequests Off
		<Proxy *>
			Order deny,allow
			Allow from all
		</Proxy>
		ProxyPass /ajaxterm/ http://localhost:8080/
		ProxyPassReverse /ajaxterm/ http://localhost:8080/

	</VirtualHost>

License
-------

(C) 2006 by Antony Lesuisse, the files are released in the public domain.

Includes the LGPL sarissa from http://sarissa.sourceforge.net/doc/.

TODO
----
	insert mode ESC [ 4 h
	multiplex change sizex= sizey=
	paste from browser
	vt102 graphic codepage

