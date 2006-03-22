#!/usr/bin/python

"""<h1>Ajaxterm</h1>


TODO
	insert
	erase char bug in mutt
	color
	multiplex change sizex= sizey=
	copy/paste

To use with apache in modssl:
-----------------------------

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
    ProxyPass / http://localhost:8080/
    ProxyPassReverse / http://localhost:8080/
</VirtualHost>

"""

import array,cgi,fcntl,glob,os,pty,random,re,signal,select,sys,threading,time,termios,struct


# Optional: Add the QWeb .egg or ../qweb in sys path
sys.path[0:0]=glob.glob('QWeb-*-py%d.%d.egg'%sys.version_info[:2])+glob.glob('../../src')

import qweb, qweb_static

class Terminal:
	def __init__(self,width=80,height=24):
		self.width=width
		self.height=height
		self.init()
		self.esc_reset()
	def init(self):
		self.esc_seq={
			"\x05": self.esc_da,
			"\x07": None,
			"\x08": self.esc_0x08,
			"\x09": self.esc_0x09,
			"\x0a": self.esc_0x0a,
			"\x0b": self.esc_0x0a,
			"\x0c": self.esc_0x0a,
			"\x0d": self.esc_0x0d,
			"\x0e": None,
			"\x0f": None,
			"\x1b#8": None,
			"\x1b=": None,
			"\x1b>": None,
			"\x1b(0": None,
			"\x1b(A": None,
			"\x1b(B": None,
			"\x1b[s": self.esc_save,
			"\x1b[u": self.esc_restore,
			"\x1b]R": None,
			"\x1b7": self.esc_save,
			"\x1b8": self.esc_restore,
			"\x1bD": None,
			"\x1bE": None,
			"\x1bH": None,
			"\x1bM": self.esc_ri,
			"\x1bN": None,
			"\x1bO": None,
			"\x1bZ": self.esc_da,
			"\x1ba": None,
			"\x1bc": self.esc_reset,
			"\x1bn": None,
			"\x1bo": None,
		}
		for k,v in self.esc_seq.items():
			if v==None:
				self.esc_seq[k]=self.esc_ignore
		d={
#term:ignore: ('\x1b[4h', [4])
#term:ignore: ('\x1b[4l', [4])
#error '\x1b[3M\x1b[1;24r\x1b[9;1H\x1b[37m\x1b[44m-   - '
#error '\x1b[15X\x1b[9;40HDNS offer netforce.co'

			r'\[([0-9]*)@' : self.esc_ich,
			r'\[([0-9]*)A' : self.esc_cuu,
			r'\[([0-9]*)C' : self.esc_cuf,
			r'\[([0-9]*)L' : self.esc_il,
			r'\[([0-9]*)G' : self.esc_hpa,
			r'\[([0-9;]*)H' : self.esc_cup,
			r'\[([0-9]*)J' : self.esc_ed,
			r'\[([0-9]*)K' : self.esc_el,
			r'\[([0-9]*)M' : self.esc_dl,
			r'\[([0-9]*)P' : self.esc_dch,
			r'\[([0-9]*)X' : self.esc_ech,
			r'\[([0-9]*)c' : self.esc_da,
			r'\[([0-9]*)d' : self.esc_vpa,
			r'\[([0-9]*)g' : None,
			r'\[([0-9;]*)h' : None,
			r'\[([0-9;]*)l' : None,
			r'\[([0-9;]*)m' : self.esc_color,
			r'\[([0-9;]+)r' : self.esc_csr,
			r'\[([0-9;\>]+)c' : None,
			r'\[\?([0-9;]+)[chlrst]' : None,
			r'\]([^\x07]+)\x07' : None,
		}
		self.esc_re=[]
		for k,v in d.items():
			if v==None:
				v=self.esc_ignore
			self.esc_re.append((re.compile('\x1b'+k),v))
		self.tr=""
		for i in range(256):
			if i<32:
				self.tr+=" "
			elif i<127 or i>160:
				self.tr+=chr(i)
			else:
				self.tr+="?"
	def peek(self,y1,x1,y2,x2):
		return self.scr[self.width*y1+x1:self.width*y2+x2]
	def poke(self,y,x,s):
		pos=self.width*y+x
		if isinstance(s,str):
			s=array.array('c',s)
		self.scr[pos:pos+len(s)]=s
	def zero(self,y,x,w):
		self.poke(y,x,' '*w)
	def scroll_up(self,y1,y2):
		self.poke(y1,0,self.peek(y1+1,0,y2,self.width))
		self.zero(y2,0,self.width)
	def scroll_down(self,y1,y2):
		self.poke(y1+1,0,self.peek(y1,0,y2-1,self.width))
		self.zero(y1,0,self.width)
	def cdown(self):
		if self.cy>=self.st and self.cy<=self.sb:
			self.cl=0
			q,r=divmod(self.cy+1,self.sb+1)
			if q:
				self.scroll_up(self.st,self.sb)
				self.cy=self.sb
			else:
				self.cy=r
	def cright(self):
		q,r=divmod(self.cx+1,self.width)
		if q:
			self.cl=1
		else:
			self.cx=r
	def echo(self,c):
		if self.cl:
			self.cdown()
			self.cx=0
		self.scr[(self.cy*self.width)+self.cx]=c
		self.cright()
	def esc_reset(self,s=""):
		self.scr=array.array('c'," "*(self.width*self.height))
		self.st=0
		self.sb=self.height-1
		self.cx_bak=self.cx=0
		self.cy_bak=self.cy=0
		self.cl=0
		self.buf=""
		self.outbuf=""
		self.last_html=""
	def esc_0x08(self,s):
		self.cx=max(0,self.cx-1)
	def esc_0x09(self,s):
		x=self.cx+8
		q,r=divmod(x,8)
		self.cx=(q*8)%self.width
	def esc_0x0a(self,s):
		self.cdown()
	def esc_0x0d(self,s):
		self.cl=0
		self.cx=0
	def esc_save(self,s):
		self.cx_bak=self.cx
		self.cy_bak=self.cy
	def esc_restore(self,s):
		self.cx=self.cx_bak
		self.cy=self.cy_bak
		self.cl=0
	def esc_ri(self,s):
		self.cy=min(self.st,self.cy-1)
		if self.cy==self.st:
			self.scroll_down(self.st,self.sb)
	# CSI sequences
	def esc_ich(self,s,l):
		if len(l)<1: l=[1]
		x,y=self.cx,self.cy
		for i in range(l[0]):
			self.echo(" ")
		self.cx,self.cy=x,y
	def esc_csr(self,s,l):
		if len(l)<2: l=(0,self.height)
		self.st=min(self.height-1,l[0]-1)
		self.sb=min(self.height-1,l[1]-1)
		self.sb=max(self.st,self.sb)
	def esc_cup(self,s,l):
		if len(l)<2: l=(1,1)
		self.cl=0
		self.cx=min(self.width,l[1])-1
		self.cy=min(self.height,l[0])-1
	def esc_cuu(self,s,l):
		if len(l)<1: l=[1]
		self.cy=max(self.st,self.cy-l[0])
	def esc_cuf(self,s,l):
		if len(l)<1: l=[1]
		for i in range(l[0]):
			self.cright()
	def esc_da(self,s,l=[]):
		self.outbuf="\x1b[?6c"
	def esc_dch(self,s,l):
		w,cx,cy=self.width,self.cx,self.cy
		if len(l)<1: l=[1]
		end=self.peek(cy,cx,cy,w)
		self.esc_el(s,[0])
		self.poke(cy,cx,end[l[0]:])
	def esc_dl(self,s,l):
		if len(l)<1: l=[1]
		if self.cy>=self.st and self.cy<=self.sb:
			for i in range(l[0]):
				self.scroll_up(self.cy,self.sb)
	def esc_ech(self,s,l):
		if len(l)<1: l=[1]
		cx,cy,cl=self.cx,self.cy,self.cl
		self.echo(" ")
		self.cx,self.cy,self.cl=cx,cy,cl
	def esc_ed(self,s,l):
		self.scr=array.array('c'," "*(self.width*self.height))
	def esc_el(self,s,l):
		if len(l)<1: l=[0]
		if l[0]==0:
			s=self.width*self.cy+self.cx
			e=self.width*(self.cy+1)
		elif l[0]==1:
			e=self.width*self.cy
			s=self.width*self.cy+self.cx
		elif l[0]==2:
			s=self.width*self.cy
			e=self.width*(self.cy+1)
		size=e-s
		self.scr[s:e]=array.array('c'," "*size)
	def esc_hpa(self,s,l):
		if len(l)<1: l=[1]
		self.cl=0
		self.cx=min(self.width,l[0])-1
	def esc_il(self,s,l):
		w=self.width
		cy=self.cy
		sb=self.sb
		if len(l)<1:
			l=[1]
		for i in range(l[0]):
			if cy<sb:
				l0=cy*w
				l1=(cy+1)*w
				ss=(sb-cy)*w
				self.scr[l1:l1+ss]=self.scr[l0:l0+ss]
			self.esc_el(s,[2])
	def esc_vpa(self,s,l):
		if len(l)<1: l=[1]
		self.cy=min(self.height,l[0])-1
	def esc_color(self,*s):
		pass
	def esc_ignore(self,*s):
		print "term:ignore: %s"%repr(s)
	def csiarg(self,s):
		l=[]
		try:
			l=[int(i) for i in s.split(';') if len(i)<4]
		except ValueError:
			pass
		return l
	def escape(self):
		e=self.buf
#		print "ESC %r %r"%(e,(self.st,self.sb))
		if len(e)>32:
			print "error %r"%e
			self.buf=""
		elif e in self.esc_seq:
			self.esc_seq[e](e)
			self.buf=""
		else:
			for r,f in self.esc_re:
				mo=r.match(e)
				if mo:
					f(e,self.csiarg(mo.group(1)))
					self.buf=""
					break
	def write(self,s):
		for i in s:
			if len(self.buf) or (i in self.esc_seq):
				self.buf+=i
				self.escape()
			elif i == '\x1b':
				self.buf+=i
			else:
#				print "ECHO %r"%i
				self.echo(i)
	def read(self):
		b=self.outbuf
		self.outbuf=""
		return b
	def dump(self):
		return self.scr.tostring()
	def dumplatin1(self):
		return self.dump().translate(self.tr)
	def dumphtml(self):
		h=self.height
		w=self.width
		s=self.dumplatin1()
		r=""
		for i in range(h):
			line=s[w*i:w*(i+1)]
			if self.cy==i:
				pre=cgi.escape(line[:self.cx])
				pos=cgi.escape(line[self.cx+1:])
				r+=pre+'<span>'+cgi.escape(line[self.cx])+'</span>'+pos+'\n'
			else:
				r+=cgi.escape(line)+"\n"
		# replace nbsp
#		or=unicode(r,'latin1').encode('utf8')
		r=r.replace(' ','\xa0')
		r='<?xml version="1.0" encoding="ISO-8859-1"?><pre class="term">%s</pre>'%r
		if self.last_html==r:
#			print "nochange"
			return '<?xml version="1.0"?><idem></idem>'
		else:
			self.last_html=r
#			print self
			return r
	def __repr__(self):
		d=self.dumplatin1()
		r=""
		for i in range(self.height):
			r+="|%s|\n"%d[self.width*i:self.width*(i+1)]
		return r

class SynchronizedMethod:
	def __init__(self,lock,orig):
		self.lock=lock
		self.orig=orig
	def __call__(self,*l):
		self.lock.acquire()
		r=self.orig(*l)
		self.lock.release()
		return r

class Multiplex:
	def __init__(self,*l):
		signal.signal(signal.SIGCHLD, signal.SIG_IGN)
		self.proc={}
		self.lock=threading.RLock()
		self.thread=threading.Thread(target=self.loop)
		self.alive=1
		# synchronize methods
		for name in ['create','fds','proc_read','proc_write','dump','die','run']:
			orig=getattr(self,name)
			setattr(self,name,SynchronizedMethod(self.lock,orig))
		self.thread.start()
	def create(self,cmd=[]):
		cmd=['/bin/bash','-l']
		if os.getuid()==0:
			cmd=['/bin/login']
		else:
			cmd=['/usr/bin/ssh','-F/dev/null','-oPreferredAuthentications=password','-oNoHostAuthenticationForLocalhost=yes','localhost']
		w,h=100,30
		w,h=80,25
		pid,fd=pty.fork()
		if pid==0:
			try:
				fdl=[int(i) for i in os.listdir('/proc/self/fd')]
			except OSError:
				fdl=range(256)
			for i in [i for i in fdl if i>2]:
				try:
					os.close(i)
				except OSError:
					pass
			env={}
			env["COLUMNS"]=str(w)
			env["LINES"]=str(h)
			env["TERM"]="linux"
			os.execve(cmd[0],cmd,env)
		else:
			fcntl.fcntl(fd, fcntl.F_SETFL, os.O_NONBLOCK)
			fcntl.ioctl(fd, termios.TIOCSWINSZ , struct.pack("HHHH",h,w,0,0))
			self.proc[fd]={'pid':pid,'term':Terminal(w,h),'buf':'','time':time.time()}
			return fd
	def die(self):
		self.alive=0
	def run(self):
		return self.alive
	def fds(self):
		return self.proc.keys()
	def proc_kill(self,fd):
		if fd in self.proc:
			self.proc[fd]['time']=0
		t=time.time()
		for i in self.proc.keys():
			t0=self.proc[i]['time']
			if (t-t0)>3600:
				try:
					os.close(i)
					os.kill(self.proc[i]['pid'],signal.SIGTERM)
				except (IOError,OSError):
					pass
				del self.proc[i]
	def proc_read(self,fd):
		try:
			t=self.proc[fd]['term']
			t.write(os.read(fd,65536))
			reply=t.read()
			if reply:
				os.write(fd,reply)
			self.proc[fd]['time']=time.time()
		except (KeyError,IOError,OSError):
			self.proc_kill(fd)
	def proc_write(self,fd,s):
		try:
			os.write(fd,s)
		except (IOError,OSError):
			self.proc_kill(fd)
	def dump(self,fd):
		try:
			return self.proc[fd]['term'].dumphtml()
		except KeyError:
			return False

	def loop(self):
		while self.run():
			fds=self.fds()
			i,o,e=select.select(fds, [], [], 1.0)
			for fd in i:
				self.proc_read(fd)
			if len(i):
				time.sleep(0.002)
		for i in self.proc.keys():
			try:
				os.close(i)
				os.kill(self.proc[i]['pid'],signal.SIGTERM)
			except (IOError,OSError):
				pass


class AjaxTerm:
	def __init__(self):
		self.template = file("ajaxterm.html").read()
		self.sarissa = file("sarissa.js").read()
		self.sarissa += file("sarissa_dhtml.js").read()
		self.multi = Multiplex()
		self.session = {}
	def __call__(self, environ, start_response):
		req = qweb.QWebRequest(environ, start_response,session=None)
		if req.PATH_INFO.endswith('/u'):
			s=req.REQUEST["s"]
			k=req.REQUEST["k"]
			if s in self.session:
				term=self.session[s]
			else:
				term=self.session[s]=self.multi.create()
			if k:
				self.multi.proc_write(term,k)
			time.sleep(0.002)
			dump=self.multi.dump(term)
			req.response_headers['Content-Type']='text/xml'
			if isinstance(dump,str):
				req.write(dump)
				req.response_gzencode=1
			else:
				del self.session[s]
				req.write('<?xml version="1.0"?><idem></idem>')
#			print "sessions %r"%self.session
		elif req.PATH_INFO.endswith('/sarissa.js'):
			req.response_headers['Content-Type']='application/x-javascript'
			req.write(self.sarissa)
#		elif not req.REQUEST['sid']:
#			req.http_redirect('terminal?sid=%s'%('%012x'%random.randint(1,2**48)))
		else:
			req.response_headers['Content-Type']='text/html; charset=UTF-8'
			req.write(self.template)
		return req


if __name__ == '__main__':
	at=AjaxTerm()
	f=lambda:os.system('firefox http://localhost:8080/&')
	qweb.qweb_wsgi_autorun(at,ip='localhost',port=8080,threaded=0,callback_ready=None)
	at.multi.die()




