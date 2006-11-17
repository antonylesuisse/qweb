// vim:set noet fdm=syntax fdl=0 fdc=3 fdn=2:
//---------------------------------------------------------
// QWeb javascript
//---------------------------------------------------------
var QWeb={
	templates:{},
	prefix:"t",
	reg:"",
	tag:{},
	att:{},
	eval_object:function(e,v){
		// TODO if v[e] return v[e]
		with(v) return eval(e);
	},
	eval_str:function(e,v){
		return e=="0" ? v["0"] : this.eval_object(e,v).toString()
	},
	eval_format:function(e,v){
	/*
	%s %(sfsqdf)s #{z#erzer}
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
		return this.eval_object(e,v)?true:false;
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
			for(var i=0; i<a.length; i++) {
				// TODO if from HTMLDOM if(a[i].specified) {
				var an=a[i].name,av=a[i].value;
				var m,n;
				if(m=an.match(this.reg)) {
					n=m[1]
					if(n=="eval") {
						n=m[2].substring(1)
						av=this.eval_str(av, v)
					}
					if(f=this.att[n]) {
						this[f](e,t_att,g_att,v,m[2],av)
					} else if(f=this.tag[n]) {
						t_att[n]=av
						t_render=f
					}
				} else {
					g_att[an]=av
				}
			}
			if (t_render) {
				r = this[t_render](e, t_att, g_att, v)
			} else {
				r = this.render_element(e, t_att, g_att, v)
			}
		} 
		return r;
	},
	render_element:function(e,t_att,g_att,v){
		var inner="",ec=e.childNodes;
		for (var i=0; i<ec.length; i++) {
			inner+=this.render_node(ec[i],v)
		}
		if(e.tagName==this.prefix) {
			return inner;
		} else {
			var att="";
			for(var an in g_att) {
				av=g_att[an]
				att+=" "+an+'="'+this.escape_att(av)+'"'
			}
			r="<"+e.tagName+att+">"+inner+"</"+e.tagName+">"
			return r
		}
		/*
		inner=render_trim(l_inner.join(), t_att)
		elsif inner.length==0
			return sprintf("<%s%s/>", e.name, render_atts(g_att))
		else
			return sprintf("<%s%s>%s</%s>", e.name, render_atts(g_att), inner, e.name)
		end
		*/
	},
	render_att_attf:function(e,t_att,g_att,v){
	},
	render_att_att:function(e,t_att,g_att,v,ext,av){
		if(ext) {
			g_att[ext.substring(1)]=this.eval_str(av,v)
		} else {
			o=this.eval_object(av,v)
			g_att[o[0]]=o[1]
		}
	},
	render_tag_rawf:function(e,t_att,g_att,v){
	},
	render_tag_raw:function(e,t_att,g_att,v){
		return this.eval_str(t_att["raw"], v);
	},
	render_tag_escf:function(e,t_att,g_att,v){
	},
	render_tag_esc:function(e,t_att,g_att,v){
		return this.escape_text(this.eval_str(t_att["esc"], v));
	},
	render_tag_if:function(e,t_att,g_att,v){
		return this.eval_bool(t_att["if"],v) ? this.render_element(e, t_att, g_att, v) : ""
	},
	render_tag_caca:function(name,v){
/*
class QWeb
	render_tag_set:function(e,t_att,g_att,v){
		var ev;
		if(ev=t_att["eval"])
			v[t_att["set"]]=eval_object(ev,v)
		else
			v[t_att["set"]] = render_element(e, t_att, g_att, v)
		end
		return ""
	},
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
	end
	def render_trim(s, t_att)
		trim = t_att["trim"]
		if !trim return s elsif trim == 'left' return s.lstrip elsif trim == 'right' return s.rstrip elsif trim == 'both' return s.strip
		end
	end
	def render_tag_rawf(e,t_att,g_att,v) return render_trim(eval_format(t_att["rawf"], v), t_att) end
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
	def render_tag_ruby(e, t_att, g_att, v)
		code =  render_element(e, t_att, g_att, v)
		r=render_trim(v.instance_eval(code).to_s, t_att)
		r="" if t_att["ruby"]=="quiet"
		return r
	end
end
*/
	},
	hash:function(){
		var l=[]
		for(var i in this) {
			if(m=i.match(/render_tag_(.*)/)) {
				this.tag[m[1]]=i
				l.push(m[1])
			} else if(m=i.match(/render_att_(.*)/)) {
				this.att[m[1]]=i
				l.push(m[1])
			}
		}
		// TODO sort l
		var s="^"+this.prefix+"-(eval|"+l.join("|")+")(.*)$"
		this.reg=new RegExp(s);
	},
	load_xml:function(s){
		var xml;
		if(s[0]=="<") {
			/*
			if(window.DOMParser){
				mozilla
			if(!window.DOMParser){
				}else if(Sarissa.getDomDocument && Sarissa.getDomDocument() && "loadXML" in Sarissa.getDomDocument()){
				IE
					DOMParser.prototype.parseFromString = function(sXml, contentType){
						var doc = Sarissa.getDomDocument();
						doc.loadXML(sXml);
						return doc;
					};
				};
				if(_SARISSA_IS_SAFARI){
					DOMParser.prototype.parseFromString = function(sXml, contentType){
						if(contentType.toLowerCase() != "application/xml"){
							throw "Cannot handle content type: \"" + contentType + "\"";
						};
						var xmlhttp = new XMLHttpRequest();
						xmlhttp.open("GET", "data:text/xml;charset=utf-8," + encodeURIComponent(str), false);
						xmlhttp.send(null);
						return xmlhttp.responseXML;
					};
			};
		*/
		} else {
			var req,ie;
			if(window.XMLHttpRequest) {
				req = new XMLHttpRequest();
			} else if(ie=window.ActiveXObject) {
				try { req = new ie("Msxml2.XMLHTTP"); } catch(e) { try { req = new ie("Microsoft.XMLHTTP"); } catch(e) { } }
			}
			if(req) {
				req.open("GET", s, false);
				req.send(null);
				//if ie r.setRequestHeader("If-Modified-Since", "Sat, 1 Jan 2000 00:00:00 GMT");
				xml=req.responseXML;
				return xml;
			}
		}
	},
	add_template:function(e){
		this.hash()
		if(typeof(e)=="string") {
			e=this.load_xml(e)
		}
		var ec=[];
		if(e.documentElement) {
			ec=e.documentElement.childNodes
		} else if(e.childNodes) {
			ec=e.childNodes
		}
		for (var i=0; i<ec.length; i++) {
			var n=ec[i];
			if(n.nodeType==1) {
				var name=n.getAttribute(this.prefix+"-name")
				this.templates[name]=n;
			}
		}
	},
	render:function(name,v){
		if(e=this.templates[name]) {
			return this.render_node(e,v)
		} else {
			return "template "+name+" not found";
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

