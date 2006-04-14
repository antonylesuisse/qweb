= [http://antony.lesuisse.org/qweb/trac/wiki/AjaxTerm Ajaxterm] =

Ajaxterm is a web based terminal. It was totally inspired and works almost
exactly like http://anyterm.org/ except it's much easier to install.

Ajaxterm written in python (and some AJAX javascript for client side) and depends only on python2.3 or better.[[BR]]
Ajaxterm is '''very simple to install''' on Linux, Unix, MacOS X and cygwin.[[BR]]
Ajaxterm was written by Antony Lesuisse (email: al AT udev.org), License Public Domain.

Use the [/qweb/forum/viewforum.php?id=2 Forum], if you have any question or remark.

== News ==

 * 2006-04-07: Added Paste from clipboard.
 * 2006-04-05: Removed the qweb egg, size is now 26kb
 * 2006-04-05: Getting popular on [http://programming.reddit.com/info/3xsl/comments reddit.com],
   [http://del.icio.us/url/93b77e52e1ae45c67b95a0a2d5bdc758 del.icio.us],
   [http://digg.com/programming/Ajaxterm_-_a_web_based_terminal digg.com]

== Download and Install ==

 * Release: [/qweb/files/QWeb-0.5-ajaxterm.tar.gz QWeb-0.5-ajaxterm.tar.gz]
 * Browse src: [/qweb/trac/browser/trunk/examples/ajaxterm/ ajaxterm/]

To install Ajaxterm issue the following commands:
{{{
wget http://antony.lesuisse.org/qweb/files/QWeb-0.5-ajaxterm.tar.gz
tar zxvf QWeb-0.5-ajaxterm.tar.gz
cd QWeb-0.5-ajaxterm
./ajaxterm.py
}}}
Then point your browser to this URL : http://localhost:8080/

== Screenshot ==

{{{
#!html
<center><img src="/qweb/trac/attachment/wiki/AjaxTerm/scr.png?format=raw" alt="ajaxterm screenshot" style=""/></center>
}}}

== Documentation and Caveats ==

 * Ajaxterm only support latin1, if you use Ubuntu or any LANG==en_US.UTF-8 distribution don't forget to unset LANG.

 * If run as root ajaxterm will run /bin/login, otherwise it will run ssh
   localhost. To use an other command use the -c option.

 * Ajaxterm was first written as a demo for qweb (my web framework), but actually doesn't use many features of qweb.

 * By default Ajaxterm only listen at 127.0.0.1:8080. For remote access, it is
   strongly recommended to use '''https SSL/TLS''', and that is simple to
   configure if you use the apache web server using mod_proxy. Here is an
   configuration example:

{{{
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
}}}

 * Using GET HTTP request seems to speed up ajaxterm, just click on GET in the
   interface, but be warned that your keystrokes might be loggued (by apache or
   any proxy). I usually enable it after the login process.

 * ./ajaxterm.py --help ouput:

{{{
usage: ajaxterm.py [options]

options:
  -h, --help            show this help message and exit
  -pPORT, --port=PORT   Set the TCP port (default: 8080)
  -sSIZE, --size=SIZE   set the terminal size (default: 80x25)
  -cCMD, --command=CMD  set the command (default: /bin/login or ssh localhost)
  -l, --log             log requests to stderr (default: quiet mode)
}}}


 * Ajaxterm files are released in the Public Domain, (except [http://sarissa.sourceforge.net/doc/ sarissa*] which are LGPL).

{{{
#!html
<!--
TODO
----
	insert mode ESC [ 4 h
	multiplex change sizex= sizey=
	paste from browser
	vt102 graphic codepage
-->
}}}
