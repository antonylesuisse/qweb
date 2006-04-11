#!/usr/bin/ruby
# vim:set noet fdm=syntax fdl=0 fdc=3 fdn=2:

require "rexml/document"
require "pp"

class QWebEval
	def initialize(context)
		@context = context
	end
	def method_missing(m)
		@context[m.to_s]
	end
	def eval_object(expr)
		return instance_eval(expr)
	end
	def eval_str(expr)
		if expr=="0":
			return @context[0]
		else
			return eval_object(expr).to_s
		end
	end
	def eval_bool(expr)
		if eval_object(expr)
			return true
		else
			return false
		end
	end
	def eval_format(expr)
		return ""
#        try:
#            return str(expr%self)
#        except:
#            return "qweb: format error '%s' "%expr
#    def __getitem__(self,expr):
#        if self.data.has_key(expr):
#            return self.data[expr]
#        r=None
#        try:
#            r=eval(expr,self.data)
#        except NameError,e:
#            pass
#        except AttributeError,e:
#            pass
#        except Exception,e:
#            print "qweb: expression error '%s' "%expr,e
#        if self.data.has_key("__builtins__"):
#            del self.data["__builtins__"]
#        return r
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
		return QWebEval.new(v).eval_object(e)
	end
	def eval_format(e,v)
		return QWebEval.new(v).eval_format(e)
	end
	def eval_str(e,v)
		return QWebEval.new(v).eval_str(e)
	end
	def eval_bool(e,v)
		return QWebEval.new(v).eval_bool(e)
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
				if enum.kind_of?(Hash)
					d.merge(i)
				else
					puts var
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
		return render(t_att["call"],d)
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

q=QWeb.new("demo.xml")
print q.render("demo",{'varname'=>"This is a tag <tag>"})

