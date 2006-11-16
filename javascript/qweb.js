// vim:set noet fdm=syntax fdl=0 fdc=3 fdn=2:
//---------------------------------------------------------
// QWeb javascript
//---------------------------------------------------------
var QWeb={
	templates:{},
	tag:{},
	att:{},
	eval_object:function(e,v){
		return v.eval(e)
	},
	eval_str:function(e,v){
		return e=="0" ? v["0"] : v.eval(e).toString()
	},
	eval_format:function(e,v){
	/*
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
*/
	},
	eval_bool:function(e,v){
		return v.eval(e)?true:false;
	},
	escape_text:function(s){
		return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
	},
	escape_att:function(s){
		return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;")
	},
	render_node:function(e,v){
		var r=""
		if(e.nodeType==3) {
			r=e.data;
		} else if(e.nodeType==1) {
			var g_att={};
			var t_att={};
			var t_render=null;
			var a=e.attributes;
			//ec=e.childNodes;
			//debug(ec.length);
			//for (var i=0; i<ec.length; i++) {
				//debug("node:"+ec[i].nodeType+" "+ec[i].nodeName)
			//}
			for(var i=0; i<a.length; i++) {
				if(a[i].specified) {
					an=a[i].name
					av=a[i].value
					g_att[an]=av
				}
			}
			r=this.render_element(e, t_att, g_att, v)
		} else {
			debug("caca"+e.nodeType);
		}
		return r;
		/*
	def render_node(e,v)
		r=""
		if e.node_type==:text
			r=e.value
		elsif e.node_type==:element
			g_att = {}
			t_render=nil
			t_att={}
			e.attributes.each do |an,av|
				if an =~ @prereg
					n=an[@prelen1..-1]
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
							t_render = n
						end
						t_att[n]=av
					end
				else
					g_att[an]=av
				end
			end
			if t_render:
				r = @tag[t_render].call(e, t_att, g_att, v)
			else
				r = render_element(e, t_att, g_att, v)
			end
		end
		return r
	end
		*/
	},
	render_att:function(e,t_att,g_att,v){
	/*
	def render_att_att(e,an,av,v)
		if an =~ Regexp.new("^#{@prefix}-attf-")
			att = an[@prelen1+5..-1]
			val=eval_format(av,v)
		elsif an =~ Regexp.new("^#{@prefix}-att-")
			att = an[@prelen1+4..-1]
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
	*/
	},
	render_element:function(e,t_att,g_att,v){
		var att="",inner="",ec=e.childNodes;
		for (var i=0; i<ec.length; i++) {
			inner+=this.render_node(ec[i],v)
		}
		for(var an in g_att) {
			av=g_att[an]
			att+=" "+an+'="'+this.escape_att(av)+'"'
		}
		r="<"+e.tagName+att+">"+inner+"</"+e.tagName+">"
		return r
		/*
	def render_element(e, t_att, g_att, v)
		l_inner=[]
		e.each { |n|
			l_inner << render_node(n,v)
		}
		inner=render_trim(l_inner.join(), t_att)
		if e.name==@prefix
			return inner
		elsif inner.length==0
			return sprintf("<%s%s/>", e.name, render_atts(g_att))
		else
			return sprintf("<%s%s>%s</%s>", e.name, render_atts(g_att), inner, e.name)
		end
	end
		*/
	},
	render_tag_caca:function(name,v){
/*
class QWeb
	def render_trim(s, t_att)
		trim = t_att["trim"]
		if !trim
			return s
		elsif trim == 'left'
			return s.lstrip
		elsif trim == 'right'
			return s.rstrip
		elsif trim == 'both'
			return s.strip
		end
	end
	def render_tag_rawf(e,t_att,g_att,v) return render_trim(eval_format(t_att["rawf"], v), t_att) end
	def render_tag_esc(e,t_att,g_att,v) return escape_text(render_trim(eval_str(t_att["esc"], v), t_att)) end
	def render_tag_escf(e,t_att,g_att,v) return escape_text(render_trim(eval_format(t_att["escf"], v), t_att)) end
	def render_tag_foreach(e,t_att,g_att,v)
		expr=t_att["foreach"]
		enum=eval_object(expr,v)
		if enum
			var=t_att['as'] || expr.gsub(/[^a-zA-Z0-9]/,'_')
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
				d["%s_last"%var]=index+1==size
				d["%s_parity"%var]=(index%2==1 ? 'odd' : 'even')
				d.merge!(i) if i.kind_of?(Hash)
				d[var]=i
				ru << render_element(e,t_att,g_att,d)
				index+=1
			end
			return ru.join()
		else
			return "qweb: #{@prefix}-foreach %s not found."%expr
		end
	end
	def render_tag_if(e,t_att,g_att,v)
		if eval_bool(t_att["if"],v)
			return render_element(e, t_att, g_att, v)
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
		d[0] = render_element(e, t_att, g_att, d)
		return render_context(t_att["call"],d)
	end
	def render_tag_set(e,t_att,g_att,v)
		if t_att["eval"]
			v[t_att["set"]]=eval_object(t_att["eval"],v)
		else
			v[t_att["set"]] = render_element(e, t_att, g_att, v)
		end
		return ""
	end
	def render_tag_ruby(e, t_att, g_att, v)
		code =  render_element(e, t_att, g_att, v)
		r=render_trim(v.instance_eval(code).to_s, t_att)
		r="" if t_att["ruby"]=="quiet"
		return r
	end
end
*/
	},
	render_tag_raw:function(e,t_att,g_att,v){
		return this.eval_str(t_att["raw"], v);
	},
	add_template:function(e){
		var ec=[];
		if(e.documentElement) {
			ec=e.documentElement.childNodes
		} else if(e.childNodes) {
			ec=e.childNodes
		}
		for (var i=0; i<ec.length; i++) {
			var n=ec[i];
			if(n.nodeType==1)
				this.templates[n.getAttribute("q-name")]=n;
		}
	},
	render:function(name,v){
		if(e=this.templates[name]) {
			return this.render_node(e,v)
		} else {
			return "template "+name+" not found";
		}
	},
	init:function(name,v){
		re=
		for(var i in this) {
			m="render_tag_name".match(/render_tag_(.*)/)
			if(m) {
			}
		}
	}
}

{
/*
Testing
/*
version   version([number])      Get or set JavaScript version number
options   options([option ...])  Get or toggle JavaScript options
load      load(['foo.js' ...])   Load files named by string arguments
readline  readline()             Read a single line from stdin
print     print([exp ...])       Evaluate and print expressions
help      help([name ...])       Display usage and help messages
quit      quit()                 Quit the shell
gc        gc()                   Run the garbage collector
trap      trap([fun, [pc,]] exp) Trap bytecode execution
untrap    untrap(fun[, pc])      Remove a trap
line2pc   line2pc([fun,] line)   Map line number to PC
pc2line   pc2line(fun[, pc])     Map PC to line number
build     build()                Show build date and time
clear     clear([obj])           Clear properties of object
intern    intern(str)            Internalize str in the atom table
clone     clone(fun[, scope])    Clone function object
seal      seal(obj[, deep])      Seal object, or object graph if deep
getpda    getpda(obj)            Get the property descriptors for obj
getslx    getslx(obj)            Get script line extent
toint32   toint32(n)             Testing hook for JS_ValueToInt32

var Test={
	"name": "value",
	"fun": function(arg) {
		print("arg+"+arg);
		print(this);
		this.caca=2;
		print(this.caca);
	},
	"fun2": function(arg) {
		print("fun2:"+this.caca);
	},
};

print(Test)
print(Test.name)
print(Test.fun)
bound=Test.fun
bound.apply(Test)
Test.fun2()
print(this.caca)
var T2=function() { }
T2.cacazezr=2
print(typeof T2)

*/
}

