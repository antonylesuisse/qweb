#!/usr/bin/ruby
# vim:set noet fdm=syntax fdl=0 fdc=3 fdn=2:

require "qweb"

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
		if an =~ Regexp.new("^#{@prefix}-attf-")
			return " #{an[@prefix.length + 6..-1]}=\"<%=h \"#{av}\" %>\""
		elsif an =~ Regexp.new("^#{@prefix}-att-")
			return " #{an[@prefix.length + 5..-1]}=\"<%=h (#{av}).to_s %>\""
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
		inner1="#{n}_last=#{n}_index+1==#{n}_size; #{n}_parity=(#{n}_index%2==1 ? 'odd' : 'even');\n%>#{inner}<%\n#{n}_index+=1;"
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
