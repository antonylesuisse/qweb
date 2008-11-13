#!/usr/bin/python
"""PyPHP, python - PHP bridge

Type Mapping

Python <=> PHP
str <=> string
unicode => string
int <=> integer
long <=> integer
float <=> double
list <=> array
tuple => array
dict <=> array
object => array
PHPObject <=> object

"""

__version__ = "$Id$"
__license__ = "Public Domain"
__author__ = "Antony Lesuisse"

import StringIO,os,re,signal,socket,struct,sys,types,urllib
#----------------------------------------------------------
# Serialization
#----------------------------------------------------------

class PHPObject:
	def __init__(self,name,attr={}):
		self.__doc__=name
		for i in attr:
			self.__dict__[i]=attr[i]

def serialize(v):
	t = type(v)
	if t == types.IntType or t == types.LongType:
		return 'i:%d;'%v
	elif t == types.FloatType:
		return 'd:'+str(v)+';'
	elif t is types.BooleanType:
		if v:
			return 'b:1;'
		else:
			return 'b:0;'
	elif t == types.NoneType:
		return 'N;'
	elif t == types.StringType:
		return 's:%d:"%s";'%(len(v),v)
	elif t == types.UnicodeType:
		v=v.encode("utf8")
		return 's:%d:"%s";'%(len(v),v)
	elif t == types.TupleType or t == types.ListType:
		i=0
		s=''
		for item in v:
			s+='i:%d;%s'%(i,serialize(item))
			i+=1
		return 'a:%d:{%s}'%(len(v),s)
	elif t == types.DictType:
		s=''
		for k in v:
			s+=serialize(k)+serialize(v[k])
		return 'a:%d:{%s}'%(len(v),s)
	elif isinstance(v,PHPObject):
		name=v.__doc__
		s='O:%d:"%s":%d:{'%(len(name),name,len(v.__dict__)-1)
		for k in v.__dict__:
			if k!='__doc__':
				s+=serialize(k)+serialize(v.__dict__[k])
		return s+'}'
	elif t == types.InstanceType:
		return serialize(v.__dict__)
	else:
		return 'N;'

def unserialize(l):
	if isinstance(l,str):
		l=re.split(';',l)
	a=l.pop(0)
	if a[0]=="i":
		return int(a[2:])
	elif a[0]=="d":
		return float(a[2:])
	elif a[0]=="b":
		return bool(int(a[2:]))
	elif a[0]=="N":
		return None
	elif a[0]=="s":
		h=a.split(":",2)
		size=int(h[1])
		val=h[2][1:]
		while len(val)<=size:
			val+=";"+l.pop(0)
		return val[0:-1]
	elif a[0]=="a":
		h=a.split(":",2)
		size=int(h[1])
		val=h[2][1:]
		l.insert(0,val)
		r={}
#		pure=1
		k_prev=-1
		for i in xrange(size):
			k=unserialize(l)
			v=unserialize(l)
			r[k]=v
#			pure=pure and isinstance(k,int) and k==k_prev+1
			k_prev=k
		l[0]=l[0][1:]
#		if pure:
#			return [r[i] for i in range(len(r))]
		return r
	elif a[0]=="O":
		h=a.split(":",3)
		name=h[2][1:-1]
		l.insert(0,"a:"+h[3])
		return PHPObject(name,unserialize(l))

#----------------------------------------------------------
# Python bindings
#----------------------------------------------------------

class PHPStdout:
	def __init__(self,proxy):
		self.proxy=proxy
	def write(self,data):
		self.proxy.pyphp_write(data)

class PHPFunction:
	def __init__(self,proxy,name):
		self.proxy=proxy
		self.name=name
	def __call__(self, *param):
		return self.proxy.pyphp_call(self.name,param)

class PHPSession:
	def __init__(self,proxy,dic={}):
		self.proxy=proxy
		if isinstance(dic,dict):
			self.dic=dic
		else:
			self.dic={}
	def __getitem__(self,key):
		return self.dic[key]
	def __setitem__(self,key,val):
		self.dic[key]=val
		self.proxy.pyphp_call('pyphp_session_add',(key,val))
	def __contains__(self,item):
		return item in self.dic
	def __len__(self):
		return len(self.dic)
	def __iter__(self):
		return self.dic.__iter__()

class PHPDict(dict):
	def __init__(self,*p):
		dict.__init__(self,*p)
	def __getitem__(self,key):
		return self.get(key,"")
	def int(self,key):
		try:
			return int(self.get(key,"0"))
		except ValueError:
			return 0

class PHPProxy:
	def __init__(self,sock):
		self._sock=sock
		self.pyphp_init()

	def __str__(self):
		return "PHPProxy"

	def __getattr__(self, name):
		return PHPFunction(self,name)

	def __repr__(self):
		return "<PHPProxy instance>"

	def __nonzero__(self):
		return 1

	def pyphp_msg_dec(self):
		msg=self._sock.recv(5)
		if msg[0]!="S":
			raise "py: protocol error"
		size=struct.unpack("i",msg[1:5])[0]
		serial=self._sock.recv(size)
		return unserialize(serial)

	def pyphp_send(self, msg):
		size=len(msg)
		sent=self._sock.send(msg)
		while sent<size:
			sent+=self._sock.send(msg[sent:])

	def pyphp_call(self,func,param):
		data="%s\x00%s"%(func,serialize(param))
		msg="C%s%s"%(struct.pack("i",len(data)),data)
		self.pyphp_send(msg)
		return self.pyphp_msg_dec();

	def pyphp_init(self):
		tmp=self.pyphp_call('pyphp_request',())
		stdout=PHPStdout(self)
		sys.stdout=stdout
		sys.stderr=stdout
		self._OUT=stdout
		self._SERVER=tmp["_SERVER"]
		self._ENV=tmp["_ENV"]
		self._GET=tmp["_GET"]
		self._POST=tmp["_POST"]
		self._ARG=PHPDict(self._GET)
		self._ARG.update(self._POST)
		self._COOKIE=tmp["_COOKIE"]
		self._REQUEST=tmp["_REQUEST"]
		self._FILES=tmp["_FILES"]
		self._SESSION=PHPSession(self,tmp["_SESSION"])
		self._SCRIPT_FILENAME=self._SERVER["SCRIPT_FILENAME"]

	def pyphp_write(self, data):
		msg="W%s%s"%(struct.pack("i",len(data)),data)
		self.pyphp_send(msg)

	def pyphp_echo(self, *param):
		data=""
		for i in param:
			data+=str(i)
		self.pyphp_write(data)

	def pyphp_wsgi_start_response(self,code,headlist):
#		if not code.startswith("200"):
		self.header("HTTP/1.1 %s"%code)
		for (n,v) in headlist:
			self.header("%s: %s"%(n,v))

	def echo(self, *param):
		self.pyphp_echo(*param)
	def eval(self, data):
		return self.pyphp_call('pyphp_eval',(data))
	def exit(self):
		self.pyphp_send("E\x00\x00\x00\x00")

def skipphp(f):
	while 1:
		li=f.readline()
		if li.find("?>")!=-1 or len(li)==0:
			break

def wsgicall(php,wsgiobj):
	environ=php._SERVER.copy()
	post=urllib.urlencode(php._POST.items())
	input=StringIO.StringIO(post)
	scheme="http"
	if environ.has_key("HTTPS"):
		scheme="https"
	environ.update({
		"wsgi.version":(1,0),
		"wsgi.url_scheme":scheme,
		"wsgi.input":input,
		"wsgi.errors":StringIO.StringIO(),
		"wsgi.multithread":0,
		"wsgi.multiprocess":1,
		"wsgi.run_once":1,
		"php":php,
	})
	for i in wsgiobj(environ,php.pyphp_wsgi_start_response):
		php.pyphp_write(i)

def log(s):
	pass
#	sys.stdout.write("pyphp:%d: %s"%(os.getpid(),s))
#	sys.stdout.flush()

def main():
	try:
		fd=[int(i) for i in os.listdir('/proc/self/fd')]
	except OSError:
		fd=range(256)
	for i in fd:
		try:
			os.close(i)
		except OSError:
			pass
	sys.stdout=sys.stderr=file("/dev/null","a")
#	sys.stdout=sys.stderr=file("/tmp/pyphp.log","a")
	os.chdir(os.path.normpath(os.path.dirname(__file__)))
	sname=sys.argv[1]
	log("NEW server socket %s \n"%sname)
	sl=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
	try:
		os.unlink(sname)
	except OSError,e:
		log("unlink: "+str(e)+"\n")
	sl.bind(sname)
	sl.listen(10)
	signal.signal(signal.SIGCHLD,signal.SIG_IGN)
	if os.fork():
		sys.exit()
	else:
		os.setsid()
		#----------------------------------------------------------
		# WSGI Mode get the wsgiapp object
		#----------------------------------------------------------
		wsgi_file=sys.argv[2]
		wsgi_app=sys.argv[3]
		wsgi_obj=None
		if len(wsgi_file):
			log("WSGI init, running '%s' to get the wsgi application '%s' \n"%(wsgi_file,wsgi_app))
			f=file(wsgi_file)
			skipphp(f)
			d={}
			exec f in d
			if d.has_key(wsgi_app):
				wsgi_obj=d[wsgi_app]
				log("WSGI wsgi application '%s' ready.\n"%wsgi_app)
		#----------------------------------------------------------
		num=0
		while 1:
			log("accept request %d\n"%num)
			sl.settimeout(30.0)
			try:
				(s,addr)=sl.accept()
			except socket.timeout,e:
				log("suicide after 30sec idle.\n")
				sys.exit()
			log("serving request %d\n"%num)
			if os.fork():
				num+=1
				s.close()
				continue
			else:
				sl.close()
				signal.signal(signal.SIGALRM,lambda x,y: sys.exit())
				signal.alarm(30)
				php=PHPProxy(s)
				scope={'php':php}
				#
				#
				if wsgi_obj:
					wsgicall(php,wsgi_obj)
				else:
					f=file(php._SCRIPT_FILENAME)
					skipphp(f)
					try:
						exec f in scope
					except:
						print "<xmp>"
						sys.excepthook(*sys.exc_info())
				#
				#
				php.exit()
				sys.exit()

if __name__ == '__main__':
	main()
