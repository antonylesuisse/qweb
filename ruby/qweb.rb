#!/usr/bin/ruby
# vim:set noet fdm=syntax fdl=0 fdc=3 fdn=2:

require "rexml/document"
require "fileutils"

class QWebContext
	def initialize(context)
		@qweb_context={};
		context.each { |k, v|
			self[k]=v;
		}
	end
	def method_missing(name,*args)
		if m=@qweb_context[name.to_s]
			return m
		elsif t=@qweb_context["template"]
			return t.send(name, *args)
		end
	end

	def []=(k,v)
		@qweb_context[k]=v
		instance_variable_set("@#{k}", v) if k.kind_of?(String)
		return v
	end
	def [](k)
		return @qweb_context[k]
	end
	def clone
		return QWebContext.new(@qweb_context)
	end

	def qweb_eval_object(expr)
		if r=@qweb_context[expr]
			return r
		else
			begin
				r=instance_eval(expr)
			rescue SyntaxError, NameError => boom
				r="String doesn't compile: " +expr+ boom
			rescue StandardError => bang
				r="Error running script: " +expr+ bang
			end
			return r
		end
	end
	def qweb_eval_str(expr)
		if expr=="0":
			return @qweb_context[0]
		else
			return qweb_eval_object(expr).to_s
		end
	end
	def qweb_eval_bool(expr)
		if qweb_eval_object(expr)
			return true
		else
			return false
		end
	end
	def qweb_eval_format(expr)
		begin
			r=eval("<<QWEB_EXPR\n#{expr}\nQWEB_EXPR\n").chop!
		rescue SyntaxError, NameError => boom
			r="String doesn't compile: " +expr+ boom
		rescue StandardError => bang
			r="Error running script: " +expr+ bang
		end
		return r
	end
end

class QWeb
	# t-att t-raw t-esc t-if t-foreach t-set t-call t-trim
	def initialize(xml=nil)
		@t={}
		@tag={}
		@att={}
		methods.each { |m|
			@tag[m[11..-1]]=method(m) if m =~ /^render_tag_/
			@att[m[11..-1]]=method(m) if m =~ /^render_att_/
		}
		add_template(xml) if xml
	end
	def add_template(s)
		if s.respond_to? "root"
			doc=s
		elsif s =~ /\<\?xml/
			doc=REXML::Document.new(s)
		else
			doc=REXML::Document.new(File.new(s))
		end
		doc.root.elements.each("t") { |e|
			@t[e.attributes["t-name"]]=e
		}
	end
	def get_template(name)
		return @t[name]
	end
	# Evaluation
	def eval_object(e,v)
		return v.qweb_eval_object(e)
	end
	def eval_format(e,v)
		return v.qweb_eval_format(e)
	end
	def eval_str(e,v)
		return v.qweb_eval_str(e)
	end
	def eval_bool(e,v)
		return v.qweb_eval_bool(e)
	end
	# Escaping
	def escape_text(string)
		string.gsub(/&/n, '&amp;').gsub(/>/n, '&gt;').gsub(/</n, '&lt;')
	end
	def escape_att(string)
		string.gsub(/&/n, '&amp;').gsub(/\"/n, '&quot;').gsub(/>/n, '&gt;').gsub(/</n, '&lt;')
	end
	# Rendering
	def render(tname,v={})
		return render_context(tname,QWebContext.new(v))
	end
	def render_context(tname,v)
		if n=@t[tname]
			return render_node(n,v)
		else
			return "qweb: template '#{tname}' not found"
		end
	end
	def render_node(e,v)
		r=""
		if e.node_type==:text
			r=e.value
		elsif e.node_type==:element
			pre=""
			g_att=""
			t_render=nil
			t_att={}
			e.attributes.each { |an,av|
				if an =~ /^t-/
					n=an[2..-1]
					found=false
					# Attributes
					for i,m in @att;
						if n[0...i.size] == i
							g_att << m.call(e,an,av,v)
							found=true
							break
						end
					end
					if not found
						if @tag[n]
							t_render=n
						end
						t_att[n]=av
					end
				else
					g_att << sprintf(' %s="%s"',an,escape_att(av))
				end
			}
			if t_render:
				r=@tag[t_render].call(e,t_att,g_att,v)
			else
				r=render_element(e,g_att,v,pre,t_att["trim"])
			end
		end
		return r
	end
	def render_element(e,g_att,v,pre="",trim=0)
		l_inner=[]
		e.each { |n|
			l_inner << render_node(n,v)
		}
		inner=l_inner.join()
		if trim=='left'
			inner.lstrip!
		elsif trim=='right'
			inner.rstrip!
		elsif trim=='both'
			inner.strip!
		end
		if e.name=="t"
			return inner
		elsif inner.length==0
			return sprintf("<%s%s/>",e.name,g_att)
		else
			return sprintf("<%s%s>%s%s</%s>",e.name,g_att,pre,inner,e.name)
		end
	end
	# Attributes
	def render_att_att(e,an,av,v)
		if an =~ /^t-attf-/
			att=an[7..-1]
			val=eval_format(av,v)
		elsif an =~ /^t-att-/
			att=an[6..-1]
			val=eval_str(av,v)
		else
			o=eval_object(av,v)
			att=o[0]
			val=o[1]
		end
		return sprintf(' %s="%s"',att,escape_att(val))
	end
	# Tags
	def render_tag_raw(e,t_att,g_att,v)
		return eval_str(t_att["raw"],v)
	end
	def render_tag_rawf(e,t_att,g_att,v)
		return eval_format(t_att["rawf"],v)
	end
	def render_tag_esc(e,t_att,g_att,v)
		return escape_text(eval_str(t_att["esc"],v))
	end
	def render_tag_escf(e,t_att,g_att,v)
		return escape_text(eval_format(t_att["escf"],v))
	end
	def render_tag_foreach(e,t_att,g_att,v)
		expr=t_att["foreach"]
		enum=eval_object(expr,v)
		if enum
			var=t_att['as']
			if not var
				var=expr.gsub(/[^a-zA-Z0-9]/,'_')
			end
			d=v.clone
			size=-1
			size=enum.length if enum.respond_to? "length"
			d["%s_size"%var]=size
			d["%s_all"%var]=enum
			index=0
			ru=[]
			for i in enum
				d["%s_value"%var]=i
				d["%s_index"%var]=index
				d["%s_first"%var]=index==0
				d["%s_even"%var]=index%2
				d["%s_odd"%var]=(index+1)%2
				d["%s_last"%var]=index+1==size
				d["%s_parity"%var]=(index%2==1 ? 'odd' : 'even')
				if i.kind_of?(Hash)
					d.merge(i)
				else
					d[var]=i
				end
				ru << render_element(e,g_att,d)
				index+=1
			end
			return ru.join()
		else
			return "qweb: t-foreach %s not found."%expr
		end
	end
	def render_tag_if(e,t_att,g_att,v)
		if eval_bool(t_att["if"],v)
			return render_element(e,g_att,v)
		else
			return ""
		end
	end
	def render_tag_call(e,t_att,g_att,v)
		if t_att["import"]
			d=v
		else
			d=v.clone
		end
		d[0]=render_element(e,g_att,d)
		return render_context(t_att["call"],d)
	end
	def render_tag_set(e,t_att,g_att,v)
		if t_att["eval"]
			v[t_att["set"]]=eval_object(t_att["eval"],v)
		else
			v[t_att["set"]]=render_element(e,g_att,v)
		end
		return ""
	end
end

class QWebRHTML < QWeb
	def render_rhtml(root)
		@root=root
		@t.each do |k,v|
			@arg=0;
			name=File.join(root,k)
			FileUtils.mkdir_p(File.dirname(name))
			fname="#{name}.rhtml"
			if File.exists?(fname)
				unless File.new(fname,"r").read =~ /qweb_vars/
					puts "skip #{fname}"
					next
				end
			end
			f=File.new(fname,"w")
			head=<<EOS.chomp!
<%
qweb_vars||={};
qweb_vars['qweb_vars']=qweb_vars;
%>
EOS
			f.write(head+render_node(v,k))
			f.close
#			p "wrote #{fname}"
		end
	end
	def render_att_att(e,an,av,v)
		if an =~ /^t-attf-/
			return " #{an[7..-1]}=\"<%=h \"#{av}\" %>\""
		elsif an =~ /^t-att-/
			return " #{an[6..-1]}=\"<%=h (#{av}).to_s %>\""
		else
			return " <%(#{av})[0]%>=\"<%=h (#{av})[1] %>\""
		end
	end
	# Tags
	def render_tag_raw(e,t_att,g_att,v)
		if t_att["raw"]=="0"
			return "<%= qweb_0 %>" 
		else
			return "<%= #{t_att["raw"]} %>" 
		end
	end
	def render_tag_rawf(e,t_att,g_att,v)
		return "<%= \"#{t_att["rawf"]}\" %>" 
	end
	def render_tag_esc(e,t_att,g_att,v)
		if t_att["esc"]=="0"
			return "<%=h qweb_0 %>" 
		else
			# TODO not escape &quot;
			return "<%=h #{t_att["esc"]} %>" 
		end
	end
	def render_tag_escf(e,t_att,g_att,v)
		# TODO not escape &quot;
		return "<%=h \"#{t_att["escf"]}\" %>" 
	end
	def render_tag_if(e,t_att,g_att,v)
		return "<% if(#{t_att["if"]}) then %>#{render_element(e,g_att,v)}<% end %>"
	end
	def render_tag_foreach(e,t_att,g_att,v)
		expr=t_att["foreach"]
		n=t_att['as']
		if not n
			n=expr.gsub(/[^a-zA-Z0-9]/,'_')
		end
		inner=render_element(e,g_att,v)
		pre="#{n}_all=#{expr};#{n}_size=-1;#{n}_size=#{n}_all.length if #{n}_all.respond_to? 'length';#{n}_index=0;"
		inner0="qweb_vars['#{n}']=#{n}_value=#{n}; #{n}_first=#{n}_index==0; #{n}_even=#{n}_index%2; #{n}_odd=(#{n}_index+1)%2;"
		inner1="#{n}_last=#{n}_index+1==#{n}_size; #{n}_parity=(#{n}_index%2==1 ? 'odd' : 'even');%>#{inner}<%#{n}_index+=1;"
		code="<% \n#{pre}\n #{n}_all.each do |#{n}|\n #{inner0} \n #{inner1}\n end %>"
		return code
	end
	def render_tag_call(e,t_att,g_att,v)
		name=t_att["call"]
		s=render_element(e,g_att,v)
		if (s =~ /\<\%/) or (s =~ /\"/) or (s =~ /\\/) or (s =~ /\#/)
			@arg+=1
			arg="#{v}__#{@arg}"
			f=File.new(File.join(@root,"#{arg}.rhtml"),"w")
			f.write(s)
			f.close
			s="qweb_vars.merge('qweb_0' => render_file('#{arg}.rhtml',true,qweb_vars))"
		else
			s="qweb_vars.merge('qweb_0' => \"#{s}\")"
		end
		return "<%= render_file('#{name}.rhtml', true, #{s}) %>"
	end
	def render_tag_set(e,t_att,g_att,v)
		name=t_att["set"]
		if t_att["eval"]
			return "<% #{name}=qweb_vars[\"#{name}\"]=#{t_att["eval"]} %>"
		else
			s=render_element(e,g_att,v)
			if (s =~ /\<\%/) or (s =~ /\"/) or (s =~ /\\/) or (s =~ /\#/)
				@arg+=1
				arg="#{v}__#{@arg}"
				f=File.new(File.join(@root,"#{arg}.rhtml"),"w")
				f.write(s)
				f.close
				s="render_file('#{arg}.rhtml',true,qweb_vars)"
				return "<% #{name}=qweb_vars[\"#{name}\"]=#{s} %>"
			else
				return "<% #{name}=qweb_vars[\"#{name}\"]=\"#{s}\" %>"
			end
		end
	end
end

if __FILE__ == $0
	q=QWebRHTML.new("qweb_template.xml").render_rhtml("../views")
end



#class QWebField:
#    def __init__(self,name=None,default="",check=None):
#        self.name=name
#        self.default=default
#        self.check=check
#        # optional attributes
#        self.type=None
#        self.trim=1
#        self.required=1
#        self.cssvalid="form_valid"
#        self.cssinvalid="form_invalid"
#        # set by addfield
#        self.form=None
#        # set by processing
#        self.input=None
#        self.css=None
#        self.value=None
#        self.valid=None
#        self.invalid=None
#        self.validate(1)
#    def validate(self,val=1,update=1):
#        if val:
#            self.valid=1
#            self.invalid=0
#            self.css=self.cssvalid
#        else:
#            self.valid=0
#            self.invalid=1
#            self.css=self.cssinvalid
#        if update and self.form:
#            self.form.update()
#    def invalidate(self,update=1):
#        self.validate(0,update)
#class QWebForm:
#    class QWebFormF:
#        pass
#    def __init__(self,e=None,arg=None,default=None):
#        self.fields={}
#        # all fields have been submitted
#        self.submitted=False
#        self.missing=[]
#        # at least one field is invalid or missing
#        self.invalid=False
#        self.error=[]
#        # all fields have been submitted and are valid
#        self.valid=False
#        # fields under self.f for convenience
#        self.f=self.QWebFormF()
#        if e:
#            self.add_template(e)
#        # assume that the fields are done with the template
#        if default:
#            self.set_default(default,e==None)
#        if arg!=None:
#            self.process_input(arg)
#    def __getitem__(self,k):
#        return self.fields[k]
#    def set_default(self,default,add_missing=1):
#        for k,v in default.items():
#            if self.fields.has_key(k):
#                self.fields[k].default=str(v)
#            elif add_missing:
#                self.add_field(QWebField(k,v))
#    def add_field(self,f):
#        self.fields[f.name]=f
#        f.form=self
#        setattr(self.f,f.name,f)
#    def add_template(self,e):
#        att={}
#        for (an,av) in e.attributes.items():
#            an=str(an)
#            if an.startswith("t-"):
#                att[an[2:]]=av.encode("utf8")
#        for i in ["form-text", "form-password", "form-radio", "form-checkbox", "form-select","form-textarea"]:
#            if att.has_key(i):
#                name=att[i].split(".")[-1]
#                default=att.get("default","")
#                check=att.get("check",None)
#                f=QWebField(name,default,check)
#                if i=="form-textarea":
#                    f.type="textarea"
#                    f.trim=0
#                if i=="form-checkbox":
#                    f.type="checkbox"
#                    f.required=0
#                self.add_field(f)
#        for n in e.childNodes:
#            if n.nodeType==n.ELEMENT_NODE:
#                self.add_template(n)
#    def process_input(self,arg):
#        for f in self.fields.values():
#            if arg.has_key(f.name):
#                f.input=arg[f.name]
#                f.value=f.input
#                if f.trim:
#                    f.input=f.input.strip()
#                f.validate(1,False)
#                if f.check==None:
#                    continue
#                elif callable(f.check):
#                    pass
#                elif isinstance(f.check,str):
#                    v=f.check
#                    if f.check=="email":
#                        v=r"/^[^@#!& ]+@[A-Za-z0-9-][.A-Za-z0-9-]{0,64}\.[A-Za-z]{2,5}$/"
#                    if f.check=="date":
#                        v=r"/^(19|20)\d\d-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])$/"
#                    if not re.match(v[1:-1],f.input):
#                        f.validate(0,False)
#            else:
#                f.value=f.default
#        self.update()
#    def validate_all(self,val=1):
#        for f in self.fields.values():
#            f.validate(val,0)
#        self.update()
#    def invalidate_all(self):
#        self.validate_all(0)
#    def update(self):
#        self.submitted=True
#        self.valid=True
#        self.errors=[]
#        for f in self.fields.values():
#            if f.required and f.input==None:
#                self.submitted=False
#                self.valid=False
#                self.missing.append(f.name)
#            if f.invalid:
#                self.valid=False
#                self.error.append(f.name)
#        # invalid have been submitted and 
#        self.invalid=self.submitted and self.valid==False
#    def collect(self):
#        d={}
#        for f in self.fields.values():
#            d[f.name]=f.value
#        return d
#class QWebHtml(QWebXml):
#    # QWebForm from a template
#    def form(self,tname,arg=None,default=None):
#        form=QWebForm(self._t[tname],arg,default)
#        return form
#
#    # HTML Att
#    def render_att_checked(self,e,an,av,v):
#        if self.eval_bool(av,v):
#            return ' %s="%s"'%(an[2:],an[2:])
#        else:
#            return ''
#    def render_att_selected(self,e,an,av,v):
#        return self.render_att_checked(e,an,av,v)
#
#    # HTML Tags forms
#    def render_tag_form_text(self,e,t_att,g_att,v):
#        f=self.eval_object(t_att["form-text"],v)
#        g_att+=' type="text" name="%s" value="%s" class="%s"'%(f.name,cgi.escape(f.value,1),f.css)
#        return self.render_element(e,g_att,v)
#    def render_tag_form_password(self,e,t_att,g_att,v):
#        f=self.eval_object(t_att["form-password"],v)
#        g_att+=' type="password" name="%s" value="%s" class="%s"'%(f.name,cgi.escape(f.value,1),f.css)
#        return self.render_element(e,g_att,v)
#    def render_tag_form_textarea(self,e,t_att,g_att,v):
#        type="textarea"
#        f=self.eval_object(t_att["form-textarea"],v)
#        g_att+=' name="%s" class="%s"'%(f.name,f.css)
#        r="<%s%s>%s</%s>"%(type,g_att,cgi.escape(f.value,1),type)
#        return r
#    def render_tag_form_radio(self,e,t_att,g_att,v):
#        f=self.eval_object(t_att["form-radio"],v)
#        val=t_att["value"]
#        g_att+=' type="radio" name="%s" value="%s"'%(f.name,val)
#        if f.value==val:
#            g_att+=' checked="checked"'
#        return self.render_element(e,g_att,v)
#    def render_tag_form_checkbox(self,e,t_att,g_att,v):
#        f=self.eval_object(t_att["form-checkbox"],v)
#        val=t_att["value"]
#        g_att+=' type="checkbox" name="%s" value="%s"'%(f.name,val)
#        if f.value==val:
#            g_att+=' checked="checked"'
#        return self.render_element(e,g_att,v)
#    def render_tag_form_select(self,e,t_att,g_att,v):
#        f=self.eval_object(t_att["form-select"],v)
#        g_att+=' name="%s" class="%s"'%(f.name,f.css)
#        return self.render_element(e,g_att,v)
#    def render_tag_option(self,e,t_att,g_att,v):
#        f=self.eval_object(e.parentNode.getAttribute("t-form-select"),v)
#        val=t_att["option"]
#        g_att+=' value="%s"'%(val)
#        if f.value==val:
#            g_att+=' selected="selected"'
#        return self.render_element(e,g_att,v)
