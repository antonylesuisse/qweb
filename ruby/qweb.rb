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
		@prefix = "t"
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
		prefix = doc.root.attributes["prefix"]
		if prefix and @t.length == 0
			if prefix =~ /[^a-zA-Z]/
				raise ArgumentError, "The prefix should only contains letters"
			elsif
				@prefix = prefix
			end
		end
		doc.root.elements.each(@prefix) { |e|
			@t[e.attributes["#{@prefix}-name"]]=e
		}
	end
	def get_template(name)
		return @t[name]
	end
	def template_exists?(name)
		return @t.has_key?(name)
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
		v["__template__"] = tname
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
			g_att = {}
			t_render=nil
			t_att={}
			e.attributes.each { |an,av|
				if an =~ Regexp.new("^#{@prefix}-")
					n=an[@prefix.length.next..-1]
					found=false
					# Attributes
					for i,m in @att;
						if n[0...i.size] == i
							#g_att << m.call(e,an,av,v)
							g_att.update m.call(e, an, av, v)
							found=true
							break
						end
					end
					if not found
						if n =~ Regexp.new("^eval-")
							n = n[5..-1]
							av = eval_str(av, v)
						end
						if @tag[n]
							t_render=n
						end
						t_att[n]=av
					end
				else
					#g_att << sprintf(' %s="%s"',an,escape_att(av))
					g_att.update an => av
				end
			}
			if t_render:
				r = @tag[t_render].call(e, t_att, g_att, v)
			else
				r = render_element(e, g_att, v, t_att["trim"])
			end
		end
		return r
	end
	def render_element(e, g_att, v, trim = 0)
		l_inner=[]
		e.each { |n|
			l_inner << render_node(n,v)
		}
		inner=l_inner.join()
		render_trim!(inner, trim)
		if e.name==@prefix
			return inner
		elsif inner.length==0
			return sprintf("<%s%s/>", e.name, render_atts(g_att))
		else
			return sprintf("<%s%s>%s</%s>", e.name, render_atts(g_att), inner, e.name)
		end
	end
	def render_atts(atts)
		if atts.length == 0
			return ""
		end
		r = atts.collect do |a, v|
			sprintf('%s="%s"', a, escape_att(v))
		end
		return " " + r.join(" ")
	end
	def render_trim!(inner, trim)
		if trim == 'left'
			inner.lstrip!
		elsif trim == 'right'
			inner.rstrip!
		elsif trim == 'both'
			inner.strip!
		end
	end
	# Attributes
	def render_att_att(e,an,av,v)
		if an =~ Regexp.new("^#{@prefix}-attf-")
			att = an[@prefix.length + 6..-1]
			val=eval_format(av,v)
		elsif an =~ Regexp.new("^#{@prefix}-att-")
			att = an[@prefix.length + 5..-1]
			val=eval_str(av,v)
		else
			o=eval_object(av,v)
			#TODO: Will cause error if object is not an array, maybe we should check if respondto? [] but what to do if not ?
			att=o[0]
			#TODO: Maybe we should check if att is a valid string for an attribute ? But what to do if not ?
			val=o[1]
		end
		#return sprintf(' %s="%s"',att,escape_att(val))
		return {att => val}
	end
	# Tags
	def render_tag_raw(e,t_att,g_att,v)
		r = eval_str(t_att["raw"], v)
		render_trim!(r, t_att["trim"])
		return r
	end
	def render_tag_rawf(e,t_att,g_att,v)
		r = eval_format(t_att["rawf"], v)
		render_trim!(r, t_att["trim"])
		return r
	end
	def render_tag_esc(e,t_att,g_att,v)
		r = eval_str(t_att["esc"], v)
		render_trim!(r, t_att["trim"])
		return escape_text(r)
	end
	def render_tag_escf(e,t_att,g_att,v)
		r = eval_format(t_att["escf"], v)
		render_trim!(r, t_att["trim"])
		return escape_text(r)
	end
	def render_tag_foreach(e,t_att,g_att,v)
		expr=t_att["foreach"]
		enum=eval_object(expr,v)
		if enum
			var=t_att['as']
			if not var
				var=expr.gsub(/[^a-zA-Z0-9]/,'_')
			end
			if t_att["import"]
				d = v
			else
				d = v.clone
			end
			size=-1
 			if enum.respond_to? "length"
				size = enum.length
			elsif enum.respond_to? "entries"
				size = enum.entries.length
			end
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
				rui = render_element(e,g_att,d)
				ru << render_trim!(rui, t_att["trim"])
				index+=1
			end
			return ru.join()
		else
			return "qweb: #{@prefix}-foreach %s not found."%expr
		end
	end
	def render_tag_if(e,t_att,g_att,v)
		if eval_bool(t_att["if"],v)
			return render_element(e, g_att, v, "", t_att["trim"])
		else
			return ""
		end
	end
	def render_tag_call(e,t_att,g_att,v)
		if t_att["import"]
			d = v
		else
			d = v.clone
		end
		d[0] = render_element(e, g_att, d, t_att["trim"])
		return render_context(t_att["call"],d)
	end
	def render_tag_set(e,t_att,g_att,v)
		if t_att["eval"]
			v[t_att["set"]]=eval_object(t_att["eval"],v)
		else
			v[t_att["set"]] = render_element(e, g_att, v, "", t_att["trim"])
		end
		return ""
	end
	def render_tag_ruby(e, t_att, g_att, v)
		code =  render_element(e, g_att, v)
		r =  v.instance_eval(code).to_s
		render_trim!(r, t_att["trim"])
		if t_att["ruby"] == "quiet"
			r = nil
		end
		return r
	end
end

if __FILE__ == $0
	q=QWebRHTML.new("qweb_template.xml").render_rhtml("../views")
end
