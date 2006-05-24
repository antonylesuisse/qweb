= [http://antony.lesuisse.org/qweb/trac/wiki/AjaxTerm Ajaxterm] =

Ajaxterm is a web based terminal. It was totally inspired and works almost
exactly like http://anyterm.org/ except it's much easier to install.

Ajaxterm written in python (and some AJAX javascript for client side) and depends only on python2.3 or better.[[BR]]
Ajaxterm is '''very simple to install''' on Linux, Unix, MacOS X and cygwin.[[BR]]
Ajaxterm was written by Antony Lesuisse (email: al AT udev.org), License Public Domain.

Use the [/qweb/forum/viewforum.php?id=2 Forum], if you have any question or remark.

== News ==

 * 2006-05-23: v0.6 Applied debian and gentoo patches, renamed to Ajaxterm, default port 8022
 * 2006-04-07: Added Paste from clipboard.

== Download and Install ==

 * Release: [/qweb/files/Ajaxterm-0.6.tar.gz Ajaxterm-0.6.tar.gz]
 * Browse src: [/qweb/trac/browser/trunk/examples/ajaxterm/ ajaxterm/]

To install Ajaxterm issue the following commands:
{{{
wget http://antony.lesuisse.org/qweb/files/Ajaxterm-0.6.tar.gz
tar zxvf Ajaxterm-0.6.tar.gz
cd Ajaxterm-0.6
./ajaxterm.py
}}}
Then point your browser to this URL : http://localhost:8022/

== Screenshot ==

{{{
#!html
<center><img src="/qweb/trac/attachment/wiki/AjaxTerm/scr.png?format=raw" alt="ajaxterm screenshot" style=""/></center>
}}}

== Documentation and Caveats ==

 * Ajaxterm only support latin1, if you use Ubuntu or any LANG==en_US.UTF-8 distribution don't forget to unset LANG.

 * If run as root ajaxterm will run /bin/login, otherwise it will run ssh
   localhost. To use an other command use the -c option.

 * By default Ajaxterm only listen at 127.0.0.1:8022. For remote access, it is
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
       ProxyPass /ajaxterm/ http://localhost:8022/
       ProxyPassReverse /ajaxterm/ http://localhost:8022/
    </VirtualHost>
}}}

 * Using GET HTTP request seems to speed up ajaxterm, just click on GET in the
   interface, but be warned that your keystrokes might be loggued (by apache or
   any proxy). I usually enable it after the login.

 * Ajaxterm commandline usage:

{{{
usage: ajaxterm.py [options]

options:
  -h, --help            show this help message and exit
  -pPORT, --port=PORT   Set the TCP port (default: 8022)
  -cCMD, --command=CMD  set the command (default: /bin/login or ssh localhost)
  -l, --log             log requests to stderr (default: quiet mode)
}}}

 * Ajaxterm was first written as a demo for qweb (my web framework), but actually doesn't use many features of qweb.

 * Ajaxterm files are released in the Public Domain, (except [http://sarissa.sourceforge.net/doc/ sarissa*] which are LGPL).

== TODO ==

 * insert mode ESC [ 4 h
 * multiplex change size x,y from gui
 * vt102 graphic codepage

