#!/usr/bin/python
import os,cgi


s="""
<!-- EXAMPLE -->

"""
l=[i for i in os.listdir(".") if i.startswith("demo")]
l.sort()
for i in l:
	s+="""
	Example : %s<br>

	<pre style="padding: 10px 10px 10px 3em; background-color: #f0f0f0;border: 1px solid #dddddd;">%s</pre>
	<br>
	<br>
	"""%(i,cgi.escape(file(i).read()))

s+= """ </div> </div> """


ff=file("README.html").read()
v=ff.find("<!-- EXAMPLE")
tmp=ff[:v]
file("README.html","w").write( tmp+s)

