<h1>Ajaxterm</h1>

<h2>Intro</h2>
<pre>
Ajaxterm is a web based terminal. It was totally inspired and works almost
exactly like http://anyterm.org/ except it's much easier to install (see
comparaison with anyterm below).

Ajaxterm written in python (and some AJAX javascript for client side) and
depends only on python2.3 or better.

Ajaxterm is '''very simple to install''' on Linux, MacOS X, FreeBSD, Solaris,
cygwin and any Unix that runs python2.3.

Ajaxterm was written by Antony Lesuisse (email: al AT udev.org), License Public
Domain.
</pre>

<!-- ====================================================== -->

<h2>News</h2>
<pre>
 - 2008-11-13: v0.11 switch to git, apply minor patches
 - 2006-10-29: v0.10 allow space in login, cgi launch fix, redhat init
 - 2006-07-12: v0.9 change uid, daemon fix (Daniel Fischer)
 - 2006-07-04: v0.8 add login support to ssh (Sven Geggus), change max width to 256
 - 2006-05-31: v0.7 minor fixes, daemon option
 - 2006-05-23: v0.6 Applied debian and gentoo patches, renamed to Ajaxterm, default port 8022
</pre>

<!-- ====================================================== -->

<h2>Download and Install</h2>
<pre>

 - Release: /ajaxterm/files/Ajaxterm-0.10.tar.gz

To install Ajaxterm issue the following commands:

    wget http://antony.lesuisse.org/ajaxterm/files/Ajaxterm-0.10.tar.gz
    tar zxvf Ajaxterm-0.10.tar.gz
    cd Ajaxterm-0.10
    ./ajaxterm.py

Then point your browser to this URL : http://localhost:8022/
</pre>

<!-- ====================================================== -->

<h2>Screenshot</h2>

<img src="scr.png" alt="ajaxterm screenshot"/>

<!-- ====================================================== -->

<h2>Documentation and Caveats</h2>
<pre>
 * Ajaxterm only support latin1, if you use Ubuntu or any LANG==en_US.UTF-8
   distribution don't forget to "unset LANG".

 * If run as root ajaxterm will run /bin/login, otherwise it will run ssh
   localhost. To use an other command use the -c option.

 * By default Ajaxterm only listen at 127.0.0.1:8022. For remote access, it is
   strongly recommended to use '''https SSL/TLS''', and that is simple to
   configure if you use the apache web server using mod_proxy.[[BR]][[BR]]
   Using ssl will also speed up ajaxterm (probably because of keepalive).[[BR]][[BR]]
   Here is an configuration example:

    Listen 443
    NameVirtualHost *:443

    &lt;VirtualHost *:443&gt;
       ServerName localhost
       SSLEngine On
       SSLCertificateKeyFile ssl/apache.pem
       SSLCertificateFile ssl/apache.pem

       ProxyRequests Off
       &lt;Proxy *&gt;
               Order deny,allow
               Allow from all
       &lt;/Proxy&gt;
       ProxyPass /ajaxterm/ http://localhost:8022/
       ProxyPassReverse /ajaxterm/ http://localhost:8022/
    &lt;/VirtualHost&gt;

 * Using GET HTTP request seems to speed up ajaxterm, just click on GET in the
   interface, but be warned that your keystrokes might be loggued (by apache or
   any proxy). I usually enable it after the login.

 * Ajaxterm commandline usage:

    usage: ajaxterm.py [options]

    options:
      -h, --help            show this help message and exit
      -pPORT, --port=PORT   Set the TCP port (default: 8022)
      -cCMD, --command=CMD  set the command (default: /bin/login or ssh localhost)
      -l, --log             log requests to stderr (default: quiet mode)
      -d, --daemon          run as daemon in the background
      -PPIDFILE, --pidfile=PIDFILE
                            set the pidfile (default: /var/run/ajaxterm.pid)
      -iINDEX_FILE, --index=INDEX_FILE
                            default index file (default: ajaxterm.html)
      -uUID, --uid=UID      Set the daemon's user id

 * Ajaxterm was first written as a demo for qweb (my web framework), but
   actually doesn't use many features of qweb.

 * Compared to anyterm:
   * There are no partial updates, ajaxterm updates either all the screen or
     nothing. That make the code simpler and I also think it's faster. HTTP
     replies are always gzencoded. When used in 80x25 mode, almost all of
     them are below the 1500 bytes (size of an ethernet frame) and we just
     replace the screen with the reply (no javascript string handling).
   * Ajaxterm polls the server for updates with an exponentially growing
     timeout when the screen hasn't changed. The timeout is also resetted as
     soon as a key is pressed. Anyterm blocks on a pending request and use a
     parallel connection for keypresses. The anyterm approch is better
     when there aren't any keypress.

 * Ajaxterm files are released in the Public Domain, (except
 [http://sarissa.sourceforge.net/doc/ sarissa*] which are LGPL).
</pre>

<!-- ====================================================== -->

<h2>TODO</h2>
<pre>
 * insert mode ESC [ 4 h
 * change size x,y from gui (sending signal)
 * vt102 graphic codepage
 * use innerHTML or prototype instead of sarissa
</pre>
