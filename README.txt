QWeb Framework

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

QWeb applications are runnable:

  * in standalone mode (run it from commandline)
  * in FastCGI mode (via a FastCGI compatible webserver)
  * in Regular CGI mode (via a CGI compatible webserver)
  * by any python WSGI compliant server
  * from php using support/php/pyphp wrapper
  * from asp.net using support/aspnet wrapper

QWeb doesn't provide any database access but it intergrates nicely with ORMs
such as SQLObject, SQLAlchemy or plain DB-API.

== Quick Start (for Linux, MacOS X and cygwin) ==

Make sure you have at least python 2.3 installed and run the following commands:

{{{
$ wget http://antony.lesuisse.org/qweb/files/QWeb-0.5-DemoApp.tar.gz
$ tar zxvf QWeb-0.5-DemoApp.tar.gz
$ cd QWeb-0.5-DemoApp
$ ./demoapp.fcgi
}}}

And point your browser to http://localhost:8080/

You may also try the [http://antony.lesuisse.org/qweb/demo/ online demo]

WARNING:

Despite his naming in .fcgi, the demo is RUNNABLE FROM COMMANDLINE.  When
runned from command line it will start its own webserver on port 8080.  The demo
also may be run as FastCGI or regular CGI by any FastCGI or CGI compatible web
server.


QWeb Components:
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


TODO
----
    Announce QWeb to python-announce-list@python.org web-sig@python.org
    qweb_core
        rename request methods into
            request_save_files
            response_404
            response_redirect
            response_download

        request urldispatcher ?
        request callback_generator, callback_function ?
        wsgi callback_server_local
        xml tags explicitly call render_attributes(t_att)?
        priority form-checkbox over t-value (for t-option)



QWebXml
-------

QWeb Xml templating engine
    
    The templating engine use a very simple syntax, "magic" xml attributes, to
    produce any kind of texutal output (even non-xml).
    
    QWebXml:
        the template engine core implements the basic magic attributes:
    
        t-att t-raw t-esc t-if t-foreach t-set t-call t-trim
    
    

QWebHtml
--------

QWebHtml
    QWebURL:
    QWebField:
    QWebForm:
    QWebHtml:
        an extended template engine, with a few utility class to easily produce
        HTML, handle URLs and process forms, it adds the following magic attributes:
    
        t-href t-action t-form-text t-form-password t-form-textarea t-form-radio
        t-form-checkbox t-form-select t-option t-selected t-checked t-pager
    
    # explication URL:
    # v['tableurl']=QWebUrl({p=afdmin,saar=,orderby=,des=,mlink;meta_active=})
    # t-href="tableurl?desc=1"
    #
    # explication FORM: t-if="form.valid()"
    # Foreach i
    #   email: <input type="text" t-esc-name="i" t-esc-value="form[i].value" t-esc-class="form[i].css"/>
    #   <input type="radio" name="spamtype" t-esc-value="i" t-selected="i==form.f.spamtype.value"/>
    #   <option t-esc-value="cc" t-selected="cc==form.f.country.value"><t t-esc="cname"></option>
    # Simple forms:
    #   <input t-form-text="form.email" t-check="email"/>
    #   <input t-form-password="form.email" t-check="email"/>
    #   <input t-form-radio="form.email" />
    #   <input t-form-checkbox="form.email" />
    #   <textarea t-form-textarea="form.email" t-check="email"/>
    #   <select t-form-select="form.email"/>
    #       <option t-value="1">
    #   <input t-form-radio="form.spamtype" t-value="1"/> Cars
    #   <input t-form-radio="form.spamtype" t-value="2"/> Sprt
    

QWebForm
--------

None

QWebURL
-------

 URL helper
    assert req.PATH_INFO== "/site/admin/page_edit"
    u = QWebURL(root_path="/site/",req_path=req.PATH_INFO)
    s=u.url2_href("user/login",{'a':'1'})
    assert s=="../user/login?a=1"
    
    

qweb_control
------------

 qweb_control(self,jump='main',p=[]):
    A simple function to handle the controler part of your application. It
    dispatch the control to the jump argument, while ensuring that prefix
    function have been called.

    qweb_control replace '/' to '_' and strip '_' from the jump argument.

    name1
    name1_name2
    name1_name2_name3

    

QWebRequest
-----------

QWebRequest a WSGI request handler.

    QWebRequest is a WSGI request handler that feature GET, POST and POST
    multipart methods, handles cookies and headers and provide a dict-like
    SESSION Object (either on the filesystem or in memory).

    It is constructed with the environ and start_response WSGI arguments:
    
      req=qweb.QWebRequest(environ, start_response)
    
    req has the folowing attributes :
    
      req.environ standard WSGI dict (CGI and wsgi ones)
    
    Some CGI vars as attributes from environ for convenience: 
    
      req.SCRIPT_NAME
      req.PATH_INFO
      req.REQUEST_URI
    
    Some computed value (also for convenience)
    
      req.FULL_URL full URL recontructed (http://host/query)
      req.FULL_PATH (URL path before ?querystring)
    
    Dict constructed from querystring and POST datas, PHP-like.
    
      req.GET contains GET vars
      req.POST contains POST vars
      req.REQUEST contains merge of GET and POST
      req.FILES contains uploaded files
      req.GET_LIST req.POST_LIST req.REQUEST_LIST req.FILES_LIST multiple arguments versions
      req.debug() returns an HTML dump of those vars
    
    A dict-like session object.
    
      req.SESSION the session start when the dict is not empty.
    
    Attribute for handling the response
    
      req.response_headers dict-like to set headers
      req.response_cookies a SimpleCookie to set cookies
      req.response_status a string to set the status like '200 OK'
    
      req.write() to write to the buffer
    
    req itselfs is an iterable object with the buffer, it will also also call
    start_response automatically before returning anything via the iterator.
    
    To make it short, it means that you may use
    
      return req
    
    at the end of your request handling to return the reponse to any WSGI
    application server.
    

QWebSession
-----------

None

QWebWSGIServer
--------------

 QWebWSGIServer
        qweb_wsgi_autorun(wsgiapp,ip='127.0.0.1',port=8080,threaded=1)
        A WSGI HTTP server threaded or not and a function to automatically run your
        app according to the environement (either standalone, CGI or FastCGI).

        This feature is called QWeb autorun. If you want to  To use it on your
        application use the following lines at the end of the main application
        python file:

        if __name__ == '__main__':
            qweb.qweb_wsgi_autorun(your_wsgi_app)

        this function will select the approriate running mode according to the
        calling environement (http-server, FastCGI or CGI).
    

qweb_wsgi_autorun
-----------------

None