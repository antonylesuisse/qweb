//	 vim:foldmethod=syntax foldcolumn=4 foldnestmax=3 foldlevel=1:
using System;
using System.Xml;
using System.Web;
using System.Reflection;
using System.Data;
using System.Data.Common;
using System.Data.SqlClient;
using System.Collections;
using System.Collections.Specialized;
using System.Text.RegularExpressions;

namespace Almacom.QWeb {
	// ----------------------------------------------------------------
	// QWeb, utils, Xml Template Engine, Statefull Model View Controler
	// ----------------------------------------------------------------
	public class QU {
		public static void rw(Object o) {
			string tmp = (o == null) ? "null" : o.ToString();
			HttpContext.Current.Response.Write(tmp);
		}
		public static void rwl(Object o) {
			string tmp = (o == null) ? "null" : o.ToString();
			HttpContext.Current.Response.Write(tmp + "<br/>");
		}
		public static void rwe(Object o) {
			string tmp = (o == null) ? "null" : o.ToString();
			HttpContext.Current.Response.Write(tmp);
			HttpContext.Current.Response.End();
		}
		public static string var_dump(Object o) {
			if(o==null) {
				return "null";
			} else if(o is string) {
				return String.Format("\"{0}\"",o);
//				return o as string;
			} else if(o is int) {
				return String.Format("{0}",o);
			} else if(o is Array) {
				string r="[";
				string tmp="";
				foreach(Object i in (IEnumerable)o)
					tmp+=var_dump(i)+", ";
				if(tmp.Length>0)
					tmp = tmp.Substring(0,tmp.Length-2);
				r+=tmp;
				return r+" ]";
			} else if(o is Hashtable || o is StringDictionary) {
				string r="Hashtable { ";
				foreach(DictionaryEntry i in (IEnumerable)o) {
					r+=var_dump(i.Key)+": "+var_dump(i.Value)+", ";
				}
				return r+"}";
			} else if(o is IEnumerable) {
				string[] n=o.GetType().FullName.Split('.');
				string r=n[n.Length-1]+" [ ";
				string tmp="";
				foreach(Object i in (IEnumerable)o)
					tmp+=var_dump(i)+", ";
				if(tmp.Length>0)
					tmp = tmp.Substring(0,tmp.Length-2);
				r+=tmp;
				return r+" ]";
			} else {
				return o.ToString();
			}
		}
		public static void print(string s) {
			if(HttpContext.Current!=null)
				HttpContext.Current.Response.Write(s+"<br/>\n");
			else
				Console.WriteLine(s);
		}
		public static void print(object o) {
			print(var_dump(o));
		}
		public static void print(params object[] arg) {
			print(var_dump(arg));
		}
		public static void echo(string s) {
			if(HttpContext.Current!=null)
				HttpContext.Current.Response.Write(s);
			else
				Console.Write(s);
		}
		public static void echo(object o) {
			echo(var_dump(o));
		}
		public static void echo(params object[] arg) {
			echo(var_dump(arg));
		}
		public static void echo(Hashtable h,params object[] arg) {

		}
		public static string query_print(string s, params object[] arg) {
			// %% %
			// %r Raw string
			// %s Quote string
			// %a key='value'
			// %k key,key,key
			// %v 'value,'value','value'

			// Note: If foreach change
			// keep a local hastable of previously browser dictionary with :
			// h[BrowserDict]=>ArrayList of DictionaryEntry
			// if match use array list else browse and add it
			
			string[] src=s.Split('%');
			string q=src[0];
			int i=1,j=0;

			while(i<src.Length) {
				string v=src[i++];
				if(v.Length==0) {
					q+="%";
				} else if(v[0]=='r') {
					q+=arg[j++]+v.Substring(1);
				} else if(v[0]=='s') {
					q+="QUOTE:"+arg[j++]+v.Substring(1);
				} else if(v[0]=='a') {
					string tmp="";
					IDictionary d = (IDictionary)arg[j++];
					foreach(DictionaryEntry en in d)
						tmp+= en.Key + "='" + "QUOTE:"+en.Value + "',";
					tmp=(tmp.Length>0) ? tmp.Substring(1,tmp.Length-2) : "";
					q+=tmp+v.Substring(1);
				} else if(v[0]=='k') {
					string tmp="";
					IDictionary d = (IDictionary)arg[j++];
					foreach(DictionaryEntry en in d)
						tmp+= en.Key+",";
					tmp=(tmp.Length>0) ? tmp.Substring(1,tmp.Length-2) : "";
					q+=tmp+v.Substring(1);
				} else if(v[0]=='v') {
					string tmp="";
					IDictionary d = (IDictionary)arg[j++];
					foreach(DictionaryEntry en in d)
						tmp+= "'"+"QUOTE:"+en.Value+"',";
					tmp=(tmp.Length>0) ? tmp.Substring(1,tmp.Length-2) : "";
					q+=tmp+v.Substring(1);
				} else {
					q+=v;
				}
			}
			return q;

		}
		public static void query(IDbConnection con, int start, int max, string s, params object[] arg) {
/*
			IDbCommand cmd = con.CreateCommand();
			cmd.CommandText = query_print(s,arg);
//			cmd.Parameters.Add("@tmp", SqlDbType.VarChar, 80).Value = "caca ' ' ' ' $ \nState";
//			cmd.ExecuteNonQuery();
			IDataReader q = cmd.ExecuteReader();
			ArrayList r = new ArrayList();
//			while(q.Read())
//				r.Add(q.Value);
			return r;
		}
		public static DataTable query_table(IDbConnection con, int start, int max, string s, params object[] arg) {
			// query_table(con,,0,0,"aze");
			IDbCommand cmd = con.CreateCommand();
			cmd.CommandText = query_print(s,arg);
			SqlDataAdapter da = new SqlDataAdapter(cmd as SqlCommand);
			DataTable dt=(new DataSet()).Tables.Add("test");
			int affected=da.Fill(dt.DataSet, start, max, dt.TableName);
			return dt;
*/
		}
		public static int ToInt(Object i, int v) {
			int r;
			try {
				r = Convert.ToInt32(i);
			} catch {
				r = v;
			}
			return r;
		}
		public static int ToInt(Object i) {
			return ToInt(i, 0);
		}
		class eval_list {
			public ArrayList l=new ArrayList();
			public void clear(int i) {
				l.RemoveRange(0,i);
			}
			public string[] pop() {
				string[] item=this[0];
				l.RemoveAt(0);
				return item;
			}
			public void push(string[] item) {
				l.Insert(0,item);
			}
			public void push(string type, string item) {
				push(new string[] {type,item});
			}
			public void enqueue(string[] item) {
				l.Add(item);
			}
			public void enqueue(string type, string item) {
				enqueue(new string[] {type,item});
			}
			public void replace(int i, string[] item) {
				clear(i);
				push(item);
			}
			public void replace(int i, string type, string item) {
				clear(i);
				push(type,item);
			}
			public string[] this[int i] {
				get {
					if(i>=l.Count) {
						return new string[] {"NULL",""};
					} else {
						return l[i] as string[];
					}
				}
			}
		}
		public static string eval(string expr, Hashtable h) {
			Regex re_sep = new Regex(@"(==|!=|&&|\|\||[./+*\(\)-]| )");
			Regex re_int = new Regex(@"^[0-9]+$");
			Regex re_var = new Regex(@"^\$?[a-zA-Z_][0-9a-zA-Z_]*$");
			Regex re_float = new Regex(@"^\-?\d+\.?\d*$");

			eval_list i=new eval_list();
			eval_list s=new eval_list();

			try {
				// Tokenize
				string[] tokens=re_sep.Split(expr);

				for(int n=0;n<tokens.Length;n++) {
					string token=tokens[n];
					if(token==".") {
						i.enqueue("DOT",token);
					} else if(token=="+") {
						i.enqueue("PLUS",token);
					} else if(token=="-") {
						i.enqueue("MINUS",token);
					} else if(token=="(") {
						i.enqueue("LP",token);
					} else if(token==")") {
						i.enqueue("RP",token);
					} else if(token=="==") {
						i.enqueue("EQUAL",token);
					} else if(token=="!=") {
						i.enqueue("NOT_EQUAL",token);
					} else if(token=="and" || token=="&&") {
						i.enqueue("AND",token);
					} else if(token=="or" || token=="||") {
						i.enqueue("OR",token);
					} else if(re_int.Match(token).Success) {
						i.enqueue("STR",token);
					} else if(re_var.Match(token).Success) {
						Object o=h[token];
						if (o is bool && !(bool)o) o = "";
						i.enqueue("STR",(o==null) ? "" : o.ToString() );
					} else if(token.StartsWith("\"") || token.StartsWith("'")) {
						string term=token.Substring(0,1);
						token=token.Substring(1,token.Length-1);
						while(!token.EndsWith(term))
							token+=tokens[++n];
						i.enqueue("STR",token.Substring(0,token.Length-1));
					}
				}
	//			print("input: ",tokens);
	//			print("input: ",i.l);
	//			print("*************************************");
				// Shift Reduce loop
				while(i.l.Count>0 || s.l.Count>1) {
					//print("input: ",i.l);
					//print("stack: ",s.l);
					//print();
					// REDUCE
					if(s[2][0]=="STR" && s[1][0]=="PLUS" && s[0][0]=="STR") {
						int r = ToInt(s[2][1]) + ToInt(s[0][1]);
						s.replace(3,"STR", r.ToString());
					} else if(s[2][0]=="STR" && s[1][0]=="MINUS" && s[0][0]=="STR") {
						int r = ToInt(s[2][1]) - ToInt(s[0][1]);
						s.replace(3,"STR", r.ToString());
					} else if(s[2][0]=="STR" && s[1][0]=="DOT" && s[0][0]=="STR") {
						s.replace(3,"STR", s[2][1] + s[0][1]);
					} else if(s[2][0]=="STR" && s[1][0]=="EQUAL" && s[0][0]=="STR") {
						s.replace(3,"STR", (s[2][1]==s[0][1]) ? "True" : "");
					} else if(s[2][0]=="STR" && s[1][0]=="NOT_EQUAL" && s[0][0]=="STR") {
						s.replace(3,"STR", (s[2][1]!=s[0][1]) ? "True" : "");
					} else if(s[2][0]=="STR" && s[1][0]=="AND" && s[0][0]=="STR") {
						s.replace(3,"STR", (s[2][1].Length>0 && s[0][1].Length>0) ? "True" : "");
					} else if(s[2][0]=="STR" && s[1][0]=="OR" && s[0][0]=="STR") {
						s.replace(3,"STR", (s[2][1].Length>0 || s[0][1].Length>0) ? "True" : "");
					} else if(s[2][0]=="LP" && s[1][0]=="STR" && s[0][0]=="RP") {
						s.replace(3,"STR", s[1][1] );
					// SHIFT
					} else {
						s.push(i.pop());
					}
				}
	//			print("input: ",i.l);
	//			print("stack: ",s.l);
	//			print("eval",expr,s[0][1]);
				return s[0][1];
			} catch {
				QU.rwe("Error evaluating : <br/><pre>" + expr);
				return "ERROR";
			}
		}
		public static string eval(string expr) {
			return eval(expr,new Hashtable());
		}
		public static bool eval_bool(string expr, Hashtable h) {
			return eval(expr,h).Length>0;
		}
		public static bool eval_bool(string expr) {
			return eval_bool(expr,new Hashtable());
		}
	}
	public class QWebUrl {
		private string _page;
		private Hashtable _args;

		public QWebUrl(string page, string arg) {
			_page=page;
			_args=new Hashtable();
			param_reg(arg);
		}
		public Hashtable param_add(string s) {
			Hashtable h=_args.Clone() as Hashtable;
			if(s.Length>0) {
				foreach(string val in s.Split('&')) {
					string[] expr=val.Split('=');
					h[expr[0]]=expr[1];
				}
			}
			return h;
		}
		public void param_reg(string s) {
			_args=param_add(s);
		}
		public string param_str(Hashtable h) {
			string r="";
			foreach(DictionaryEntry en in h) {
				// TODO rawurlencode(e.Value)
				r+= en.Key + "=" + en.Value + "&amp;";
			}
			return r.Substring(0,r.Length-5);
		}
		public string param_str() {
			return param_str(_args);
		}
		public string href(string s) {
			return "href=\"" + _page + "?" + param_str(param_add(s)) + "\"";
		}
		public string form_action() {
			return "action=\"" + _page + "\"";
		}
		public string form_input(string s) {
			string r="";
			foreach(DictionaryEntry en in param_add(s)) {
				// TODO rawurlencode(e.Value)
				r+="<input type=\"hidden\" name=\""+ en.Key +"\" value=\"" + en.Value + "\">\n";
			}
			return r;
		}
		public StringDictionary Request() {
			HttpContext c = HttpContext.Current;
			StringDictionary Req = new StringDictionary();
			foreach(String k in c.Request.QueryString)
				Req[k] = c.Request.QueryString[k].ToString();
			foreach(String k in c.Request.Form)
				Req[k] = c.Request.Form[k].ToString();
			return Req;
		}
	}
	public class QWebForm  {
		public bool CSVCheckboxes = true;
		public bool Submitted=false;
		public StringDictionary Default=new StringDictionary();
		public StringDictionary Input=new StringDictionary();
		public StringDictionary Error=new StringDictionary();

		public QWebForm(XmlElement e, Hashtable def, string pre) {
			CheckSubmit(e);
			Process(e);
			if(def!=null)
				FillDefault(def,pre);
		}

		public void SetDefault(string k, object v) {
			Default[k] = v.ToString();
		}
		public void FillDefault(Hashtable d, string pre) {
			foreach(DictionaryEntry de in d)
				Default[pre + de.Key] = de.Value.ToString();
		}
		public void FillDefault(Hashtable d) {
			FillDefault(d, "");
		}
		public void FillDefault(DataRow dr, string pre) {
			Hashtable d = new Hashtable();
			foreach (DataColumn i in dr.Table.Columns) {
				d[i.ColumnName] = dr[i.ColumnName];
			}
			FillDefault(d, pre);
		}
		public void FillDefault(DataRow dr) {
			FillDefault(dr, "");
		}
		public void FillDefault(DataTable dt, string pre) {
			FillDefault(dt.Rows[0], pre);
		}
		public void FillDefault(DataTable dt) {
			FillDefault(dt, "");
		}

		public void CheckSubmit(XmlElement e) {
			string name,input;

			Hashtable t_att=new Hashtable();
			foreach(XmlAttribute a in e.Attributes) {
				if(a.Name.StartsWith("t-"))
					t_att[a.Name.Substring(2)]=a.Value;
			}

			if((name=(string)t_att["name"]) != null) {
				input=HttpContext.Current.Request[name];
				if(input!=null) Submitted=true;
			}

			foreach(XmlNode n in e.ChildNodes)
				if(n.NodeType==XmlNodeType.Element)
					CheckSubmit(n as XmlElement);
		}

		public void Process(XmlElement e) {
			string val,name;
			string check,input;

			Hashtable t_att=new Hashtable();
			foreach(XmlAttribute a in e.Attributes)
				if(a.Name.StartsWith("t-"))
					t_att[a.Name.Substring(2)]=a.Value;

			if((val=(string)t_att["value"]) != null) {
				if( (name=(string)t_att["name"]) != null && ( ((string)t_att["type"])=="checkbox" || ((string)t_att["type"])=="radio" ) ) {
					if(t_att.ContainsKey("selected"))
						Default[name]=val;
				} else if((name=(string)t_att["select"]) != null) {
					 if(t_att.ContainsKey("selected"))
						Default[name]=val;
				} else if((name=(string)t_att["name"]) !=null) {
					 Default[name]=val;
				}
			}

			if((name=(string)t_att["name"]) != null) {
				input=HttpContext.Current.Request[name];
				if (Submitted) {
					if((check=t_att["check"] as string) == null)
						check="//";
					if(check=="email")
						check=@"/^[^@#!& ]+@[A-Za-z0-9-][.A-Za-z0-9-]{0,64}\.[A-Za-z]{2,5}$/";
	//#					if($tv["notrim"])
	//#						$val=$v[$name];
	//#					else
	//#						$val=trim($v[$name]);
					if (input != null) Input[name]=input;
					check=check.Substring(1,check.Length-2);
					if(!Regex.IsMatch(input == null ? "" : input,check))
						SetError(name);
				}
			}

			foreach(XmlNode n in e.ChildNodes)
				if(n.NodeType==XmlNodeType.Element)
					Process(n as XmlElement);

		}

		public void SetError(string k) {
			Error[k] = "true";
		}
		public void SetError(string[] k) {
			foreach (string i in k)
				Error[i] = "true";
		}
		public void ClearError(string k) {
			Error.Remove(k);
		}
		public void ClearError(string[] k) {
			foreach (string i in k)
				Error.Remove(i);
		}
		public bool GetError(string k) {
			return Error.ContainsKey(k);
		}
		public bool GetError(string[] k) {
			foreach (string s in k)
				if (GetError(s)) return true;
			return false;
		}
		public bool AnyError() {
			return Error.Count >= 1 && Submitted;
		}

		public void SetInput(string k, object v) {
			Input[k] = v.ToString();
		}
		public string GetInput(string k) {
			return Input[k];
		}
		public void ClearInput(string k) {
			Input.Remove(k);
		}
		public bool ValidInput() {
			return Error.Count == 0 && Submitted;
		}
		public StringDictionary CollectInput(string pre) {
			StringDictionary r=new StringDictionary();
			foreach (DictionaryEntry de in Input) {
				r[pre + de.Key] = de.Value.ToString();
			}
			return r;
		}
		public StringDictionary CollectInput() {
			return CollectInput("");
		}
		public StringDictionary CollectInput(string pre, string[] l) {
			StringDictionary r = new StringDictionary();
			foreach (string i in l) {
				r[pre + i.Trim()] = Input[i.Trim()];
			}
			return r;
		}
		public StringDictionary CollectInput(string[] l) {
			return CollectInput("", l);
		}
		

		public string GetDisplay(string k) {
			if (Input.ContainsKey(k)) {
				return Input[k];
			} else if (Default.ContainsKey(k)) {
				return Default[k];
			} else {
				return "";
			}
		}

/*
		public class Fields {
			private Hashtable h;
			public Fields(Hashtable hash) { h=hash; }
			public Hashtable Hash  { get { return h; } set { h.Clear(); foreach(DictionaryEntry de in value) { h[de.Key]=de.Value; } } }
			public string this[string name] { get { return h[name] as string; } set { h[name]=value; } }
		}
		public Fields Default { get { return new Fields(f_def); } }
		public Fields Input { get { return new Fields(f_val); } }
		public Fields Display { get { return new Fields(f_val); } }
		public Fields Error { get { return new Fields(f_err); } }
		public bool Valid { get { return f_err.Count==0; } }
		public string this[string name] { get { return Input[name]; } set { Input[name]=value; } }

*/
	}
	public class QWebXml {
		// private
		public Hashtable m_t=new Hashtable();
		public Hashtable f_t=new Hashtable();
		public ArrayList ext=new ArrayList();
		// public
		public QWebUrl Url;
		public QWebForm Form;

		public QWebXml(XmlDocument xml) {
			xml_add(xml);
		}
		public QWebXml(string fname) {
			xml_add(fname);
		}
		public QWebXml() {
		}

		public void xml_add(XmlDocument x) {
			x.PreserveWhitespace=true;
			foreach(XmlNode i in x.DocumentElement.ChildNodes) {
				if(i.Name=="t") {
					string name=((XmlElement)i).GetAttribute("name");
					m_t[name]=i;
				}
			}
		}
		public void xml_add(string fname) {
			f_t[f_t.Count] = fname;
			XmlDocument x = new XmlDocument();
			x.Load(fname);
			xml_add(x);
		}
		public void xml_reload() {
			foreach (Object i in f_t.Keys) {
				XmlDocument x = new XmlDocument();
				x.Load((string)f_t[i]);
				xml_add(x);
			}
		}

		public void ext_add(Object o) {
			ext.Add(o);
		}

		public string render_element(XmlElement e, string g_att, Hashtable h /* , string pre */ ) {
			string g_inner="";
			foreach(XmlNode i in e.ChildNodes) {
				g_inner+=render_node(i,h);
			}
			if(e.Name=="t") {
				return g_inner;
			} else {
				if(g_inner.Length>0) {
					return "<" + e.Name + g_att + ">" + g_inner + "</" + e.Name + ">";
				} else {
					return "<" + e.Name + g_att + "/>";
				}
			}
		}
		public string render_tag_raw(XmlElement e, string t_val, Hashtable t_att, string g_att, Hashtable h)  {
			string r;
			string format=e.GetAttribute("t-format");
			if(t_val=="0")
				r=h["0"] as string;
			else
				r=QU.eval(t_val,h);
			if (format.Length != 0) {
				if (format == "ucfirst")
					r=char.ToUpper(r[0]) + r.Substring(1);
				else if (format == "upper")
					r=r.ToUpper();
				else if (format == "lower")
					r=r.ToLower();
				else
					r=String.Format(format, r);
			}
			return r;
		}
		public string render_tag_esc(XmlElement e, string t_val, Hashtable t_att, string g_att, Hashtable h)  {
			string r;
			string format=e.GetAttribute("t-format");
			if(t_val=="0")
				r=h["0"] as string;
			else
				r=QU.eval(t_val,h);
			if (format.Length != 0) {
				if (format == "ucfirst")
					r=char.ToUpper(r[0]) + r.Substring(1);
				else if (format == "upper")
					r=r.ToUpper();
				else if (format == "lower")
					r=r.ToLower();
				else
					r=String.Format(format, r);
			}
			return HttpUtility.HtmlEncode(r);
		}
		public string render_tag_href(XmlElement e, string t_val, Hashtable t_att, string g_att, Hashtable h)  {
			return QU.eval(t_val,h);
		}
		// TODO add tval+_enum _enum_last _enum_even
		public string render_tag_foreach(XmlElement e, string t_val, Hashtable t_att, string g_att, Hashtable h_orig)  {
			Hashtable h=new Hashtable(h_orig);
			string r="";
			if (h[t_val] is DataTable) {
				DataTable list=h[t_val] as DataTable;
				if (list.Columns == null || list.Rows.Count == 0) return r;
				int i=0;
				foreach (DataRow row in list.Rows) {
					foreach(DataColumn col in list.Columns)
						h[col.ColumnName]=row[col.ColumnName];
					h[t_val+"_index"]=i++;
					r+=render_element(e,g_att,h);
				}
			} else {
				IEnumerable list=h[t_val] as IEnumerable;
				if(list==null)
					return "qweb: t-foreach "+t_val+" not found.";
				int i=0;
				foreach(IDictionary each in list)  {
					foreach(DictionaryEntry each_e in each)
						h[each_e.Key]=each_e.Value;
					h[t_val+"_index"]=i++;
					r+=render_element(e,g_att,h);
				}
			}
			return r;
		}
		public string render_tag_if(XmlElement e, string t_val, Hashtable t_att, string g_att, Hashtable h)  {
			if(QU.eval_bool(t_val,h))
				return render_element(e,g_att,h);
			else
				return "";
		}
		public string render_tag_call(XmlElement e, string t_val, Hashtable t_att, string g_att, Hashtable h_orig)  {
			Hashtable h;
			if(e.HasAttribute("t-import"))
				h=h_orig;
			else
				h=new Hashtable(h_orig);
			foreach(XmlNode i in e.ChildNodes) {
				if(i is XmlElement) {
					XmlElement ie = (XmlElement)i;
					if(ie.HasAttribute("t-arg"))
						h[ie.GetAttribute("t-arg")]=render_element(ie,g_att,h);
				}
			}
			h["0"]=render_element(e,g_att,h);
			return Render(t_val,h);
		}
		public string render_tag_set(XmlElement e, string t_val, Hashtable t_att, string g_att, Hashtable h)  {
			h[t_val]=render_element(e,g_att,h);
			return "";
		}
		public string render_tag_type(XmlElement e, string t_val, Hashtable t_att, string g_att, Hashtable h)  {
			QWebForm f=h["form"] as QWebForm;
			string r="";
			string name=t_att["name"] as string;
			string css=f.GetError(name) ? "form_error" : "form_valid";
			if(t_val=="text" || t_val=="password") {
				string val=HttpUtility.HtmlEncode(f.GetDisplay(name));
				g_att+=String.Format(" type=\"{0}\" name=\"{1}\" value=\"{2}\" class=\"{3}\"",t_val,name,val,css);
				r=render_element(e,g_att,h);
			} else if(t_val=="textarea") {
				string val=HttpUtility.HtmlEncode(f.GetDisplay(name));
				g_att+=String.Format(" name=\"{0}\" class=\"{1}\"",name,css);
				r=String.Format("<{0}{1}>{2}</{3}>",t_val,g_att,val,t_val);
			} else if(t_val=="checkbox" || t_val=="radio") {
				string val=e.GetAttribute("t-value");
				if(val==null)
					val="";
				string check="";
				if (f.CSVCheckboxes) {
					string[] comp = f.GetDisplay(name).Split(',');
					if (Array.IndexOf(comp, val) != -1) {
						check=" checked=\"checked\"";
					}
				} else {
					if(val==f.GetDisplay(name))
						check=" checked=\"checked\"";
				}
				g_att+=String.Format(" type=\"{0}\" name=\"{1}\" value=\"{2}\" class=\"{3}\"{4}",t_val,name,val,css,check);
				r=render_element(e,g_att,h);
			}
			return r;
		}
		public string render_tag_select(XmlElement e, string t_val, Hashtable t_att, string g_att, Hashtable h)  {
			QWebForm f=h["form"] as QWebForm;
			string r="";
			string val=e.GetAttribute("t-value");
			if(val==null)
				val="";
			string selected="";
			if(val==f.GetDisplay(t_val))
				selected=" selected=\"selected\"";
			g_att+=String.Format(" value=\"{0}\"{1}",val,selected);
			r=render_element(e,g_att,h);
			return r;
		}
		public string render_tag_name(XmlElement e, string t_val, Hashtable t_att, string g_att, Hashtable h)  {
			return render_element(e,g_att+" name=\""+t_val+"\"",h);
		}
		public string render_tag_error(XmlElement e, string t_val, Hashtable t_att, string g_att, Hashtable h)  {
			QWebForm f=h["form"] as QWebForm;
			if(f.GetError(t_val))
				return render_element(e,g_att,h);
			else
				return "";
		}
		public string render_tag_invalid(XmlElement e, string t_val, Hashtable t_att, string g_att, Hashtable h)  {
			if (h["form"] == null) QU.rwe("QWeb: No form was found in the Hashtable");
			QWebForm f=h["form"] as QWebForm;
			if(f.AnyError())
				return render_element(e,g_att,h);
			else
				return "";
		}

		public string render_node(XmlNode n, Hashtable h) {
			string r="";
			if(n.NodeType==XmlNodeType.Text || n.NodeType==XmlNodeType.Whitespace || n.NodeType==XmlNodeType.CDATA) {
				r=n.Value;
			} else if(n.NodeType==XmlNodeType.Element) {
				XmlElement e = n as XmlElement;
				string g_att="";
				string t_att_first=null;
				Hashtable t_att=new Hashtable();
				foreach(XmlAttribute a in e.Attributes) {
					if(a.Name.StartsWith("t-")) {
						if(a.Name.StartsWith("t-att")) {
							string myval = QU.eval(a.Value,h);
							g_att+= " " + a.Name.Substring(6) + "=\"" + HttpUtility.HtmlEncode(myval) + "\"";
						} else {
							t_att[a.Name.Substring(2)]=a.Value;
							if (t_att_first == null)
								t_att_first = a.Name.Substring(2);
						}
					} else {
						g_att+=" "+a.Name+"=\""+HttpUtility.HtmlEncode(a.Value)+"\"";
					}
				}
				if(t_att.Count > 0) {
					string val;
					if ( (val=t_att["raw"] as string) != null) {
						r=render_tag_raw(e,val,t_att,g_att,h);
					} else if ( (val=t_att["esc"] as string) != null) {
						r=render_tag_esc(e,val,t_att,g_att,h);
					} else if ( (val=t_att["foreach"] as string) != null) {
						r=render_tag_foreach(e,val,t_att,g_att,h);
					} else if ( (val=t_att["if"] as string) != null) {
						r=render_tag_if(e,val,t_att,g_att,h);
					} else if ( (val=t_att["call"] as string) != null) {
						r=render_tag_call(e,val,t_att,g_att,h);
					} else if ( (val=t_att["set"] as string) != null) {
						r=render_tag_set(e,val,t_att,g_att,h);
					} else if ( (val=t_att["type"] as string) != null) {
						r=render_tag_type(e,val,t_att,g_att,h);
					} else if ( (val=t_att["select"] as string) != null) {
						r=render_tag_select(e,val,t_att,g_att,h);
					} else if ( (val=t_att["name"] as string) != null) {
						r=render_tag_name(e,val,t_att,g_att,h);
					} else if ( (val=t_att["error"] as string) != null) {
						r=render_tag_error(e,val,t_att,g_att,h);
					} else if ( (val=t_att["invalid"] as string) != null) {
						r=render_tag_invalid(e,val,t_att,g_att,h);
					} else  {
						val=t_att[t_att_first] as string;
						t_att_first=t_att_first.Replace("-","_");
						if (t_att_first.StartsWith("ext_")) {
							foreach(Object ex in ext) {
								if(ex.GetType().GetMethod(t_att_first)!=null) {
									Object o=ex.GetType().GetMethod(t_att_first).Invoke(ex, new Object[] {this, e,val,t_att,g_att,h});
									if(o is string)
										r=(string)o;
								}
							}
						}
					}
				} else {
					r=render_element(e,g_att,h);
				}
			}
			return r;
		}
		public string Render(string name, Hashtable h) {
			if(m_t.ContainsKey(name)) {
				return render_element((XmlElement)m_t[name],"", h);
			} else {
				return "qweb template \""+name+"\" not found";
			}
		}
		public string Render(string name) {
			return Render(name, new Hashtable());
		}

		public QWebForm form(string name, Hashtable def, string pre) {
			return new QWebForm((XmlElement)m_t[name], def, pre);
		}
		public QWebForm form(string name, Hashtable def) {
			return form(name, def, "");
		}
		public QWebForm form(string name) {
			return form(name, null);
		}

	}
	public class QWebSmvc {
		private string _state="";
		private Hashtable _v;
		private ArrayList _run_todo=new ArrayList();
		private Hashtable _run_done=new Hashtable();

		public bool debug = false;
		public QWebXml Xml;
		public StringDictionary Req;

		public string[] q_state_split(string state) {
			ArrayList r=new ArrayList(new string[] {"s_"});
			if(state=="")
				return (string[])r.ToArray(typeof(string));
			string tmp="s_";
			foreach(string s in state.Split('_')) {
				tmp+=s+"_";
				r.Add(tmp);
			}
			return (string[])r.ToArray(typeof(string));
		}
		public string QState {
			get { 
				return _state;
			}
			set {
				_state=value;
				if (debug) QU.rw("<b>Changing state to : " + _state + "</b><br/>");
				_run_todo.Clear();
				foreach(string s in q_state_split(value)) {
					if(!_run_done.ContainsKey(s))
						_run_todo.Add(s);
				}
			}
		}
		public int control() {
			HttpContext c=HttpContext.Current;
			if(Xml!=null && Xml.Url!=null) {
				Req=Xml.Url.Request();
			} else {
				Req=new StringDictionary();
				foreach(String k in c.Request.QueryString)
					Req[k] = c.Request.QueryString[k];
				foreach(String k in c.Request.Form)
					Req[k] = c.Request.Form[k];
			}
			if (debug) QU.rw("<b>Starting with state : " + _state + "</b><br/>");
			_v=new Hashtable();
			_run_done=new Hashtable();
			_run_todo=new ArrayList(q_state_split(QState));
			while(_run_todo.Count>0) {
				string s=(string)_run_todo[0];
				string m=s+"control";
				_run_todo.RemoveAt(0);
				_run_done[s]=1;
				if (debug) QU.rw("Executing control state :" + m + "<br/>");
				MethodInfo mi =GetType().GetMethod(m);
				if(mi!=null)
					mi.Invoke(this, new Object[] {c,_v});
			}
			return 0;
		}
		public string view() {
			foreach(string s in q_state_split(QState)) {
				string m=s+"view";
				if (debug) QU.rw("Executing view state : " + m + "<br/>");
				if(GetType().GetMethod(m)!=null) {
					Object o=GetType().GetMethod(m).Invoke(this, new Object[] {_v});
					if(o is string)
						return (string)o;
				}
			}
			return "qweb: no view returned a string.";
		}

	}

	public class Test {
		public static void Main(string[] arg) {

			QWebXml xml=new QWebXml("test.xml");
			Hashtable h=new Hashtable();
			Hashtable[] res=new Hashtable[] {new Hashtable(), new Hashtable()};
			res[0]["name"] = "caca";
			res[0]["desc"] = "cagreergerggregerca";
			res[1]["name"] = "pipi";
			res[1]["desc"] = "cttrhrtthagreergerggregerca";
			h["list"]=res;
			h["file"]="test.xml";
			h["var"]="123";
			h["test"]="you email is <lesuisse@gmail.com> et double \"  et simple ' amp &  qdsfqsf ";
			Console.WriteLine(xml.Render("about",h));

//			Console.WriteLine("Hello World"+eval("love + hate-2+2*6+5/8==3"));

//			Hashtable h=new Hashtable();
//			h["var"]="123";
//			h["file"]="test.xml";
//#			Console.WriteLine("Hello World"+QU.eval("var == \"45 + 23 \" . \"salut \" ",h));
//			Console.WriteLine("eval: "+QU.eval("(file == \" azea aze .xml\" ) or (var == \"123\")  ",h));
//			Hashtable h=new Hashtable();
//			QU.query_print("hello '%s' and '%s' and %a SQLsyntax INSERT (%k) values (%v)",1,2,h,h,h);
/*
			XmlDocument x = new XmlDocument();
			x.Load("test.xml");
			Console.WriteLine(x.BaseURI);
*/
		}
	}
}

