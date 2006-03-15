#!/usr/bin/python

"""<h1>Tutorial 2 A Complete Demo</h1> """

import array, cgi, fcntl, glob, os, pty, re, signal, select, sys, time

# Optional: Add the QWeb .egg or ../qweb in sys path
sys.path[0:0]=glob.glob('QWeb-*-py%d.%d.egg'%sys.version_info[:2])+glob.glob('../../src')

import qweb, qweb_static

class Terminal:
	def __init__(self,width=80,height=25):
		self.width=width
		self.height=height
		self.init()
	def peek(self,y1,x1,y2,x2):
		return self.scr[self.width*y1+x1:self.width*y2+x2]
	def poke(self,y,x,s):
		pos=self.width*y+x
		if isinstance(s,str):
			s=array.array('c',s)
		self.scr[pos:pos+len(s)]=s
	def zero(self,y,x,w):
		self.poke(y,x,' '*w)
	def lineup(self):
		s=self.scr
		w=self.width
		st=self.st
		sb=self.sb
		ss=(sb-st)*w
		l0=w*st
		l1=w*(st+1)
		ll=w*(sb)
		s[l0:l0+ss]=s[l1:l1+ss]
		s[ll:ll+w]=array.array('c'," "*w)
	def cdown(self):
		if self.cy>=self.st and self.cy<=self.sb:
			self.cl=0
			q,r=divmod(self.cy+1,self.sb+1)
			if q:
				self.lineup()
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
		self.escbuf=""
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
	def esc_dch(self,s,l):
		w,cx,cy=self.width,self.cx,self.cy
		if len(l)<1: l=[1]
		end=self.peek(cy,cx,cy,w)
		self.esc_el(s,[0])
		self.poke(cy,cx,end[l[0]:])
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
	def esc_color(self,*s):
		pass
	def esc_ignore(self,*s):
		print "term:ignore: %s"%repr(s)
	def escape(self):
		e=self.escbuf
#		print "ESC %r %r"%(e,(self.st,self.sb))
		if len(e)>32:
			print "error %r"%e
			self.escbuf=""
		elif e in self.esc_seq:
			f=self.esc_seq[e]
			if f:
				f(e)
			self.escbuf=""
		else:
			for r,f in self.esc_re:
				mo=re.match(r,e)
				if mo:
					if f:
						l=mo.group(1).split(';')
						l2=[]
						for i in l:
							try:
								val=int(i)
								l2.append(val)
							except ValueError:
								pass
						f(e,l2)
					self.escbuf=""
	def init(self):
		self.esc_reset()
		self.esc_seq={
			"\x05": None,
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
			"\x1b7": self.esc_save,
			"\x1b8": self.esc_restore,
			"\x1bD": None,
			"\x1bE": None,
			"\x1bH": None,
			"\x1bM": None,
			"\x1bN": None,
			"\x1bO": None,
			"\x1bZ": None,
			"\x1bc": self.esc_reset,
			"\x1bn": None,
			"\x1bo": None,
			"\x1b[s": self.esc_save,
			"\x1b[u": self.esc_restore,
		}
		for k,v in self.esc_seq.items():
			if v==None:
				self.esc_seq[k]=self.esc_ignore
		escre={
			r'\[([0-9]*)@' : self.esc_ich,
			r'\[([0-9]*)A' : self.esc_cuu,
			r'\[([0-9]*)C' : self.esc_cuf,
			r'\[([0-9]*)L' : self.esc_il,
			r'\[([0-9;]*)H' : self.esc_cup,
			r'\[([0-9]*)J' : self.esc_ed,
			r'\[([0-9]*)K' : self.esc_el,
			r'\[([0-9]*)P' : self.esc_dch,
#term:ignore: ('\x1b[?1049h', [1049])
#term:ignore: ('\x1b[4h', [4])
#term:ignore: ('\x1b[?1h', [1])
			r'\[([0-9;]*)l' : None,
			r'\[([0-9;]*)m' : self.esc_color,
			r'\[([0-9;]+)r' : self.esc_csr,
			r'\[([0-9;\>]+)c' : None,
			r'\[\?([0-9;]+)[chlrst]' : None,
			r'\]([^\x07]+)\x07' : None,
		}
		self.esc_re=[]
		for k,v in escre.items():
			if v==None:
				v=self.esc_ignore
			self.esc_re.append(('\x1b'+k,v))
		self.tr=""
		for i in range(256):
			if i<32:
				self.tr+=" "
			elif i<127:
				self.tr+=chr(i)
			else:
				self.tr+="+"
	def write(self,s):
		for i in s:
			if len(self.escbuf) or (i in self.esc_seq):
				self.escbuf+=i
				self.escape()
			elif i == '\x1b':
				self.escbuf+=i
			else:
				self.echo(i)
	def dump(self):
		return self.scr.tostring()
	def dumpascii(self):
		return self.dump().translate(self.tr)
	def dumphtml(self):
		h=self.height
		w=self.width
		s=self.dumpascii()
		r=""
		for i in range(h):
			line=s[w*i:w*(i+1)]
			if self.cy==i:
				pre=cgi.escape(line[:self.cx])
				pos=cgi.escape(line[self.cx+1:])
				r+=pre+'<span class="cursor">'+cgi.escape(line[self.cx])+'</span>'+pos+'<br/>'
			else:
				r+=cgi.escape(line)+"<br/>"
		return r
	def __repr__(self):
		d=self.dumpascii()
		r=""
		for i in range(self.height):
			r+="|%s|\n"%d[self.width*i:self.width*(i+1)]
		for i in range(self.height):
			r+="|%r|\n"%self.scr[self.width*i:self.width*(i+1)]
		return r

class Process:
	def __init__(self,cmd):
		signal.signal(signal.SIGCHLD, signal.SIG_IGN)
		pid,fd=pty.fork()
		if pid==0:
			os.environ["TERM"]="linux"
			os.execv(cmd[0],cmd)
		else:
			self.pid=pid
			self.fd=fd
			self.buf=""
#			fcntl.fcntl(fd, fcntl.F_SETFL, os.O_NONBLOCK)
	def read(self):
		r=""
		while 1:
			i,o,e=select.select( [self.fd], [], [], 0.001)
			if len(i):
				r+=os.read(self.fd,8192)
			else:
				break
#		print "proc:read:%r"%r
		return r
	def write(self,s):
		i,o,e=select.select( [], [self.fd], [], 0.001)
		if len(o):
#			print "proc:write:%r"%s
			os.write(self.fd,s)
		else:
			print "proc:BLOCK:%r"%s

class AjaxTerm:
	def __init__(self,cmd=['/bin/sh']):
		self.template = qweb.QWebHtml("ajaxterm.xml")
		self.proc = Process(cmd)
		self.term = Terminal()
		self.termp = ""

	def __call__(self, environ, start_response):
		req = qweb.QWebRequest(environ, start_response)
		req.response_gzencode=1
		if req.PATH_INFO.startswith('/test'):
			c=req.REQUEST["a"]
			self.proc.write(c)
			time.sleep(0.001)
			r=self.proc.read()
			self.term.write(r)
			s=self.term.dumphtml()
			if self.termp==s:
				print "nochange"
				req.write('')
			else:
#				print self.term
				req.write(s)
				self.termp=s
		else:
			v={}
			v['url']=qweb.QWebURL('/',req.PATH_INFO)
			req.write(self.template.render("at_main",v))
		return req
#		qweb.qweb_control(self,'main',[req,req.REQUEST,{}])

		pass

if __name__ == '__main__':
	at=AjaxTerm()
	qweb.qweb_wsgi_autorun(at,ip='')



