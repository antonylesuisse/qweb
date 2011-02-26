package qweb;

import java.io.*;
import java.text.*;
import java.util.*;
import java.util.jar.*;
import java.util.zip.*;
import java.sql.*;
import javax.servlet.*;
import javax.servlet.http.*;
import org.w3c.dom.*;
import org.python.util.*;
import org.python.core.*;
import org.apache.commons.fileupload.*;
import org.mozilla.javascript.Context;
import org.mozilla.javascript.Scriptable;
import org.mozilla.javascript.ScriptableObject;

public class qweb {
	/*-------------------------------------------------------
	 * Java helpers
	 *-------------------------------------------------------*/
	public static ArrayList j_list(Object o) {
		if(o.getClass().isArray())
			return new ArrayList(Arrays.asList((Object[])o));
		ArrayList r=new ArrayList();
		try {
			Iterator iter=(Iterator)o.getClass().getMethod("iterator",null).invoke(o,null);
			o=iter;
		} catch(Exception ex) {
		}
		try {
			if(Class.forName("java.util.Iterator").isAssignableFrom(o.getClass())) {
				for (Iterator iter=(Iterator)o;iter.hasNext();)
					r.add(iter.next());
				return r;
			} else if(Class.forName("java.util.Enumeration").isAssignableFrom(o.getClass())) {
				for(Enumeration e=(Enumeration)o;e.hasMoreElements();)
					r.add(e.nextElement());
				return r;
			}
		} catch (java.lang.ClassNotFoundException ex) {
		}
		r.add(o);
		return r;
	}
	public static Object j_new(String c) {
		Object o=null;
		if(c!=null) {
			try {
				Class cl=Class.forName(c);
				o=cl.newInstance();
			} catch (java.lang.ClassNotFoundException ex) {
				System.out.println("qweb-new:"+c+" "+ex);
			} catch(IllegalAccessException ex) {
				System.out.println("qweb-new:"+c+" "+ex);
			} catch (java.lang.InstantiationException ex) {
				System.out.println("qweb-new:"+c+" "+ex);
			}
		}
		return o;
	}
	public static void j_load(String jpath) {
		final HashMap cache=new HashMap();
		final HashMap code=new HashMap();
		final ClassLoader cl=new ClassLoader() {
			public Class findClass(String name) {
				byte[] b=(byte[])code.get(name);
				try {
					return defineClass(name, b, 0, b.length);
				} catch(ClassFormatError e) {
				} catch(NoClassDefFoundError e) {
				} catch(NullPointerException e) {
				}
				return null;
			}
		};
		if(cache.get(jpath)==null) {
			try {
				JarFile j=new JarFile(jpath);
				for(Enumeration e=j.entries();e.hasMoreElements();) {
					JarEntry je=(JarEntry)e.nextElement();
					String fn=je.getName();
					if(fn.endsWith(".class") && je.getSize()>0) {
						BufferedInputStream bis=new BufferedInputStream(j.getInputStream(je));
						byte[] data=new byte[(int)je.getSize()];
						bis.read(data,0,(int)je.getSize());
						String cn=fn.substring(0,fn.length()-6).replace('/', '.');
						code.put(cn,data);
					}
				}
				for(Iterator e=code.keySet().iterator();e.hasNext();) {
					String n=(String)e.next();
					cl.loadClass(n);
				}
			} catch(IOException e) {
			} catch(ClassNotFoundException e) {
			}
			cache.put(jpath,"");
		}
	}
    public static Object j_calls(String c,String m, Object[] arg) {
		Class cl=Object.class;
		try {
			cl=Class.forName(c);
		} catch (Exception ex) {
			System.out.println("qweb-calls:"+c+" "+ex);
		}
		Object r=null;
		if(m!=null && arg!=null) {
			try {
				java.lang.reflect.Method[] ml=cl.getMethods();
				for(int i=0; i<ml.length; i++) {
					if(ml[i].getName().equals(m) && ml[i].getParameterTypes().length==arg.length) {
						r=ml[i].invoke(null,arg);
						return r;
					}
				}
			} catch(IllegalAccessException ex) {
				System.out.println("qweb-calls:"+c+"."+m+" "+ex);
			} catch(IllegalArgumentException ex) {
				System.out.println("qweb-calls:"+c+"."+m+" "+ex);
			} catch(java.lang.reflect.InvocationTargetException ex) {
				Throwable t=ex.getTargetException();
				System.out.println("qweb-calls:"+c+"."+m+" "+t);
				t.printStackTrace();
			}
		}
		return r;
	}
	public static Object j_calln(Object o,String m, Object[] arg) {
		Object r=null;
		if(o!=null && m!=null && arg!=null) {
			try {
				java.lang.reflect.Method[] ml=o.getClass().getMethods();
				for(int i=0; i<ml.length; i++) {
					if(ml[i].getName().equals(m) && ml[i].getParameterTypes().length==arg.length) {
						r=ml[i].invoke(o,arg);
						return r;
					}
				}
//				System.out.println("qweb-call:"+o+"."+m+"() NoSuchMethod");
//			} catch(NoSuchMethodException ex) {
//				System.out.println("qweb-call:"+o+"."+m+" "+ex);
			} catch(IllegalAccessException ex) {
				System.out.println("qweb-call:"+o+"."+m+" "+ex);
			} catch(IllegalArgumentException ex) {
				System.out.println("qweb-call:"+o+"."+m+" "+ex);
			} catch(java.lang.reflect.InvocationTargetException ex) {
				Throwable t=ex.getTargetException();
				System.out.println("qweb-call:"+o+"."+m+" "+t);
				t.printStackTrace();
			}
		}
		return r;
	}
	public static Object j_call(Object o,String m) {
		return j_calln(o,m,new Object[0]);
	}
	public static Object j_call(Object o,String m, Object a1) {
		return j_calln(o,m,new Object[] {a1});
	}
	public static Object j_call(Object o,String m, Object a1, Object a2) {
		return j_calln(o,m,new Object[] {a1,a2});
	}
	public static Object j_call(Object o,String m, Object a1, Object a2, Object a3) {
		return j_calln(o,m,new Object[] {a1,a2,a3});
	}
	public static Object j_call(Object o,String m, Object a1, Object a2, Object a3, Object a4) {
		return j_calln(o,m,new Object[] {a1,a2,a3,a4});
	}
	public static Object j_call(Object o,String m, Object a1, Object a2, Object a3, Object a4, Object a5) {
		return j_calln(o,m,new Object[] {a1,a2,a3,a4,a5});
	}
	public static HashMap j_map(Object o) {
		HashMap h=new HashMap();
		try {
			if(Class.forName("java.util.Map").isAssignableFrom(o.getClass())) {
				h=new HashMap((Map)o);
			} else {
				ArrayList l=j_list(o);
				for(Iterator iter=l.iterator();iter.hasNext();) {
					h.put(iter.next(),iter.next());
				}
			}
		} catch (java.lang.ClassNotFoundException ex) {
		}
		return h;
	}
	public static HashMap j_map(Object k1, Object v1) {
		return j_map(j_list(new Object[] {k1,v1}));
	}
	public static HashMap j_map(Object k1, Object v1, Object k2, Object v2) {
		return j_map(j_list(new Object[] {k1,v1,k2,v2}));
	}
	public static HashMap j_map(Object k1, Object v1, Object k2, Object v2, Object k3, Object v3) {
		return j_map(j_list(new Object[] {k1,v1,k2,v2,k3,v3}));
	}
	public static HashMap j_map(Object k1, Object v1, Object k2, Object v2, Object k3, Object v3, Object k4, Object v4) {
		return j_map(j_list(new Object[] {k1,v1,k2,v2,k3,v3,k4,v4}));
	}

	/*-------------------------------------------------------
	 * Xml Dom and Zip helpers
	 *-------------------------------------------------------*/

	public static byte[] file_read(File f) {
		byte[] buf=new byte[0];
		try {
			BufferedInputStream bis=new BufferedInputStream(new FileInputStream(f));
			buf=new byte[(int)f.length()];
			bis.read(buf,0,(int)f.length());
			bis.close();
		} catch (IOException e) {
		}
		return buf;
	}
	public static void file_copy(File sf, File df) {
		try {
			new File(df.getParent()).mkdirs();
			java.nio.channels.FileChannel src=new FileInputStream(sf).getChannel();
			java.nio.channels.FileChannel dst=new FileOutputStream(df).getChannel();
			dst.transferFrom(src, 0, src.size());
			src.close();
			dst.close();
		} catch (IOException e) {
		}
	}
	public static ArrayList file_lslr(File dir) {
		ArrayList a=new ArrayList();
		File[] l=dir.listFiles();
		if(l!=null) {
			for(int i=0; i<l.length; i++) {
				File f=l[i];
				a.add(f.getPath());
				if(f.isDirectory())
					a.addAll(file_lslr(f));
			}
		}
		return a;
	}
	public static ArrayList file_lslr(String dir) {
		return file_lslr(new File(dir));
	}
	public static String xml_escape_text(String s) {
		s=s.replaceAll("\\&", "&amp;"); // Must be done first!
		s=s.replaceAll("\\<", "&lt;");
		s=s.replaceAll("\\>", "&gt;");
		return s;
	}
	public static String xml_escape_att(String s) {
		return xml_escape_text(s).replaceAll("\\\"","&quot;");
	}
	public static Document xml_parsefile(String f) {
		try {
			return javax.xml.parsers.DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(new File(f));
		} catch (javax.xml.parsers.ParserConfigurationException e) {
		} catch (org.xml.sax.SAXException e) {
			System.out.println("qweb-xml:"+e);
		} catch (java.io.IOException e) {
		}
		return null;
	}
	public static void xml_write(Document doc, String filename) {
/*
		try {
			// Prepare the DOM document for writing
			Source source = new DOMSource(doc);
			// Prepare the output file
			File file = new File(filename);
			Result result = new StreamResult(file);
			// Write the DOM document to the file
			Transformer xformer = TransformerFactory.newInstance().newTransformer();
			xformer.transform(source, result);
		} catch (TransformerConfigurationException e) {
		} catch (TransformerException e) {
		}
*/
	}
	public static byte[] zip_read(String zip, String name) {
		byte[] buf=new byte[0];
		try {
			java.util.zip.ZipFile f=new java.util.zip.ZipFile(zip);
			java.util.zip.ZipEntry e=f.getEntry(name);
			if(e!=null) {
				buf=new byte[(int)e.getSize()];
				f.getInputStream(e).read(buf);
			}
		} catch(java.io.IOException e) {
			System.out.println("qweb:zip_read:"+e.getMessage());
		}
		return buf;
	}
	public static boolean zip_unzip(String zip, String dest) {
		try {
			ZipFile z=new ZipFile(zip);
			for (Enumeration en=z.entries();en.hasMoreElements();) {
				ZipEntry ze=(ZipEntry)en.nextElement();
				File f=new File(dest,ze.getName());
				if(ze.isDirectory()) {
					f.mkdirs();
				} else {
					byte[] buf=new byte[8192];
					InputStream fi=z.getInputStream(ze);
					FileOutputStream fo=new FileOutputStream(f);
					while (true) {
						int i=fi.read(buf);
						if(i==-1)
							break;
						fo.write(buf,0,i);
					}
				}
			}
		} catch(java.io.IOException e) {
			System.out.println("qweb:zip_unzip:"+e.getMessage());
			return false;
		}
		return true;
	}
	public static String str_ucfirst(String s) {
		return s.substring(0,1).toUpperCase()+s.substring(1);
	}
	public static String str_tojava(String data) {
		StringBuffer out=new StringBuffer();
		StringTokenizer st=new StringTokenizer(data, "_");
		while (st.hasMoreTokens()) {
			String e = (String)st.nextElement();
			out.append(str_ucfirst(e));
		}
		return out.toString();
	}
	public static void js(String s) {
		Context cx = Context.enter();
		try {
			Scriptable scope = cx.initStandardObjects();
			Object result = cx.evaluateString(scope, s, "<cmd>", 1, null);
			System.out.println(cx.toString(result));
//			ScriptableObject.putProperty(scope,"out",Context.javaToJS(System.out, scope));
		} finally {
			Context.exit();
		}
/*		Object fObj = scope.get("f", scope);
		if (!(fObj instanceof Function)) {
			System.out.println("f is undefined or not a function.");
		} else {
			Object functionArgs[] = { "my arg" };
			Function f = (Function)fObj;
			Object result = f.call(cx, scope, scope, functionArgs);
			String report = "f('my args') = " + Context.toString(result);
			System.out.println(report);
		}
*/

	}
	public static boolean url_check(String data) {
		boolean r=true;
		try {
			java.net.URL url=new java.net.URL("http","158.169.131.13",8012,data);
			java.net.HttpURLConnection c=(java.net.HttpURLConnection)url.openConnection();
			c.setRequestProperty("Proxy-Authorization","Basic "+(new sun.misc.BASE64Encoder()).encode("stroolu:papier7".getBytes()));
			c.connect();
			if(c.getResponseCode()==404)
				r=false;
			c.disconnect();
		} catch (java.net.MalformedURLException e) {
			System.out.println("url_read:"+e);
		} catch (IOException e) {
			System.out.println("url_read:"+e);
		}
		return r;
	}

	/*-------------------------------------------------------
	 * QWeb Framework
	 *-------------------------------------------------------*/
	public static class QWebSql {
		public boolean debug=false;
		public int limit=4096;
		public String jdbc="";
		public String user="";
		public String passwd="";
		public Connection conn=null;
		public Result last=null;

		public static class Result {
			public int size;
			public String[][] aa;
			public ArrayList  la;
			public Map[]      am;
			public ArrayList  lm;

			public String[][] getAa() {
				return aa;
			}
			public Map[] getAm() {
				return am;
			}
			public String toString() {
				return lm.toString();
			}
		}

		public QWebSql(String jdbc, String user, String passwd) {
			try {
				Class cl=Class.forName("oracle.jdbc.driver.OracleDriver");
			} catch (java.lang.ClassNotFoundException ex) {
			}
			this.jdbc=jdbc;
			this.user=user;
			this.passwd=passwd;
		}
		public QWebSql(Connection c) {
			conn=c;
		}
		public QWebSql() {
			this("jdbc:oracle:thin:@localhost:1521:testdb","login","passwd");
		}

		private void connect() throws SQLException {
			if(conn==null) {
				conn=java.sql.DriverManager.getConnection(jdbc,user,passwd);
				conn.setAutoCommit(false); 
			}
		}
		public void close() {
			try {
				if(conn!=null)
					conn.close();
			} catch (SQLException e) {
			}
			conn=null;
		}
		protected void finalize()  {
			close();
		}
		public Connection take() {
			return null;
		}
		public void release(Connection c) {
		}
		public int batch(ArrayList q) {
			if(q.size()==0)
				return 0;
			int i=0;
			try {
				connect();
				Statement st=conn.createStatement();
				for(Iterator it=q.iterator();it.hasNext();) {
					String s=(String)it.next();
					if(debug)
						System.out.println("qweb-addbatch: "+q);
					st.addBatch(s);
				}
				int[] r=st.executeBatch();
				for(int j=0;j<r.length;j++)
					i+=r[j]>0?r[j]:0;
				st.close();
				conn.commit();
			} catch (SQLException ex) {
				System.out.println("qweb-sql:"+ex);
				System.out.println("qweb-sql:offending query: "+q);
			}
			return i;
		}
		public int batch(String[] q) {
			return batch(j_list(q));
		}
		public int batch(String q) {
			return batch(q.split(";"));
		}
		public int update(String q) {
			return batch(new String[] {q});
		}
		public Result query(String q) {
			int count=0;
			SimpleDateFormat sdf=new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
			Result r=new Result();
			r.aa=new String[0][];
			r.am=new HashMap[0];
			r.la=new ArrayList();
			r.lm=new ArrayList();
			try {
				connect();
				Statement st=conn.createStatement();
				if(debug)
					System.out.println("qweb-query: "+q);
				ResultSet rs=st.executeQuery(q);
				int width=rs.getMetaData().getColumnCount();
				String[] name=new String[width];
				for(int i=0;i<name.length;i++)
					name[i]=rs.getMetaData().getColumnName(i+1).toLowerCase();
				while(rs.next()) {
					if(count++>=limit)
						break;
					String[] r1=new String[width];
					Map r2=new HashMap();
					for(int i=0;i<width;i++) {
						int ct=rs.getMetaData().getColumnType(i+1);
						if(ct==Types.DATE || ct==Types.TIMESTAMP) {
							r1[i]=(rs.getTimestamp(i+1)==null)?null:sdf.format(rs.getTimestamp(i+1));
						} else {
							r1[i]=rs.getString(i+1);
						}
						r2.put(name[i],r1[i]);
					}
					r.la.add(r1);
					r.lm.add(r2);
				}
				st.close();
			} catch (SQLException ex) {
				System.out.println("qweb-sql:"+ex);
				System.out.println("qweb-sql:offending query: "+q);
			}
			r.aa=(String[][])r.la.toArray(r.aa);
			r.am=(Map[])r.lm.toArray(r.am);
			r.size=r.aa.length;
			last=r;
			return r;
		}
		public Result query() {
			return query("SELECT * FROM all_users");
		}
		public String toString() {
			if(last==null)
				return "QWebSql(\""+jdbc+"\")";
			return last.toString();
		}
	}
	public static class QWebRequest {
		public ServletContext context;
		public HttpServletRequest request;
		public HttpServletResponse response;

		public Writer out;
		public HashMap params;
		public HashMap param;
		public HashMap file;

		public QWebRequest(ServletContext sc, HttpServletRequest req, HttpServletResponse res) {
			context=sc;
			request=req;
			response=res;
			out=null;
			param=new HashMap();
			params=new HashMap();
			file=new HashMap();
			try {
				if(request.getMethod().equals("GET")) {
					for(Enumeration e=request.getParameterNames(); e.hasMoreElements();) {
						String n=(String)e.nextElement();
						String[] v=request.getParameterValues(n);
//						for(int i=0;i<v.length;i++)
//							v[i]=new String(v[i].getBytes("ISO-8859-1"),"UTF-8");
						params.put(n,v);
						param.put(n,v[0]);
					}
				} else {
					request.setCharacterEncoding("UTF-8");
					if(FileUpload.isMultipartContent(request)) {
						try {
							DiskFileUpload fu=new DiskFileUpload();
							fu.setSizeMax(1024*1024*1024);
							for(Iterator it=fu.parseRequest(request).iterator();it.hasNext();) {
								FileItem fi=(FileItem)it.next();
								if(fi.isFormField()) {
									String n=fi.getFieldName();
									String v=fi.getString("UTF-8");
									params.put(n,new String[] {v});
									param.put(n,v);
								} else {
									try {
										File f=File.createTempFile("upload",null);
										fi.write(f);
										f.deleteOnExit();
										file.put(fi.getFieldName(),new Object[] {fi.getName(),f});
									} catch (Exception ex) {
									}
								}
							}
						}catch(FileUploadException e) {
						}
					} 
					for(Enumeration e=request.getParameterNames(); e.hasMoreElements();) {
						String n=(String)e.nextElement();
						String[] v=request.getParameterValues(n);
						params.put(n,v);
						param.put(n,v[0]);
					}
				}
				if(param.get("debug")!=null) {
					debug();
				}
			} catch(java.io.UnsupportedEncodingException ex) {
			}
		}
		protected void finalize() throws IOException {
			for(Iterator i=file.keySet().iterator();i.hasNext();) {
				Object[] va=(Object[])file.get(i.next());
				((File)va[1]).delete();
			}
			file.clear();
		}
		public void clean() {
			try {
				finalize();
			} catch (IOException ex) {
				System.out.println("Clean:"+ex);
			}
		}
		// Request
		public String getString(String p, String def) {
			String v=(String)param.get(p);
			return (v==null)?def:v;
		}
		public String getString(String p) {
			return getString(p,"");
		}
		public String get(String p) {
			return getString(p);
		}
		public String get(String p, String def) {
			return getString(p,def);
		}
		public Integer getInteger(String p) {
			Integer r=new Integer(0);
			try {
				String v=(String)param.get(p);
				r=new Integer((v==null)?"0":v);
			} catch(java.lang.NumberFormatException e) {
			}
			return r;
		}
		public int getInt(String p) {
			return getInteger(p).intValue();
		}
		public File getFile(String p) {
			Object[] f=(Object[])file.get(p);
			if(f!=null) {
				return (File)f[1];
			}
			return null;
		}
		public String getFileName(String p) {
			Object[] f=(Object[])file.get(p);
			if(f!=null) {
				return (String)f[0];
			}
			return "";
		}
		// Session
		public Object sessionSet(String p,Object o) {
			request.getSession(true).setAttribute(p,o);
			return o;
		}
		public Object sessionGet(String p) {
			return request.getSession(true).getAttribute(p);
		}
		public Object sessionGet(String p, Object def) {
			Object o=request.getSession(true).getAttribute(p);
			if(o==null && def!=null) {
				o=sessionSet(p,def);
			}
			return o;
		}
		public String sessionGetStr(String p, String def) {
			String o=(String)sessionGet(p,def);
			return o==null?"":o;
		}
		public String sessionGetStr(String p) {
			return sessionGetStr(p,null);
		}
		public Integer sessionGetInt(String p, Integer def) {
			Integer val=(Integer)sessionGet(p,def);
			return val==null?new Integer(0):val;
		}
		public Integer sessionGetInt(String p) {
			return sessionGetInt(p,null);
		}
		// Reponse
		public void setContentType(String s) {
			response.setContentType(s);
		}
		public Writer writer() {
			try {
				if(out==null) {
					setContentType("text/html; charset=UTF-8");
					out=response.getWriter();
				}
			} catch (IOException e) {
			}
			return out;
		}
		public void write(String s) {
			try {
				writer().write(s);
			} catch (IOException e) {
			}
		}
		public void println(String s) {
			try {
				writer().write(s+"\n");
			} catch (IOException e) {
			}
		}
		public void debug() {
			println("<br><b>Parameters:</b><br>");
			for(Iterator i=param.keySet().iterator();i.hasNext();) {
				String n=(String)i.next();
				String va=get(n);
				println(n+"="+va+"<br>");
				String s="[";
				for(int j=0;j<va.length();j++) {
					s+=va.charAt(j)+",";
				}
				println(n+"="+s+"]<br>");
			}
			println("<br><b>Files:</b><br>");
			for(Iterator i=file.keySet().iterator();i.hasNext();) {
				String n=(String)i.next();
				Object[] va=(Object[])file.get(n);
				println(n+"= Name:"+va[0]+" Data:"+va[1]+"<br>");
			}
			println("<br><b>context.InitParameters:</b><br>");
			for(Enumeration i=context.getInitParameterNames();i.hasMoreElements();) {
				String n=(String)i.nextElement();
				String va=context.getInitParameter(n);
				println(n+"="+va+"<br>");
			}
			println("<br><b>context.Attributes:</b><br>");
			for(Enumeration i=context.getAttributeNames();i.hasMoreElements();) {
				String n=(String)i.nextElement();
				String va=context.getAttribute(n).toString();
				println(n+"="+va+"<br>");
			}
			println("<br><b>request.Attributes:</b><br>");
			for(Enumeration i=request.getAttributeNames();i.hasMoreElements();) {
				String n=(String)i.nextElement();
				String va=request.getAttribute(n).toString();
				println(n+"="+va+"<br>");
			}
			println("<br><b>System.properties:</b><br>");
				for (Enumeration e=System.getProperties().keys();e.hasMoreElements();) {
				String n=(String)e.nextElement();
				println(n+"="+System.getProperty(n)+"<br>");
			}
		}
	}
	public static class QWebURL {
		String page;
		HashMap arg;
		public QWebURL() {
			page="update";
			arg=new HashMap();
		}
		public HashMap decode(String s) {
			HashMap h=new HashMap();
			String[] l=s.split("\\&");
			for(int i=0;i<l.length;i++) {
				String expr[]=l[i].split("=");
				if(expr.length==2 && expr[0].length()>0 && expr[1].length()>0)
					h.put(expr[0],expr[1]);
			}
			return h;
		}
		public String encode(HashMap h) {
			String r="";
			for(Iterator i=h.entrySet().iterator();i.hasNext();) {
				Map.Entry e=(Map.Entry)i.next();
				r+=e.getKey()+"="+e.getValue()+"&amp;";
			}
			return r.length()<5?"":r.substring(0,r.length()-5);
		}
		public String href(String s) {
			return page+"?"+s;
		}
		public String action(String s) {
			return page;
		}
		public String input(String s) {
			String r="";
			for(Iterator i=decode(s).entrySet().iterator();i.hasNext();) {
				Map.Entry e=(Map.Entry)i.next();
				r+="<input type=\"hidden\" name=\""+e.getKey()+"\" value=\""+xml_escape_att((String)e.getValue())+"\">";
			}
			return r;
		}
		public HashMap request(String s) {
			return new HashMap();
		}
	}
	public static class QWebForm {
		public HashMap defaults;
		public HashMap error;
		public HashMap input;

		boolean submitted;
		public HashMap check;
		public QWebForm(Element e, HashMap arg, HashMap def) {
			defaults=new HashMap();
			error=new HashMap();
			input=new HashMap();
			submitted=false;
			check=new HashMap();
			process(e,arg);
			defaults.putAll(def);
		}
		public QWebForm(Element e, HashMap arg) {
			this(e,arg,new HashMap());
		}
		public boolean error_get(String k) {
			return error.get(k)!=null;
		}
		public boolean error_any() {
			return submitted && error.size()>0;
		}
		public boolean input_valid() {
			return submitted && error.size()==0;
		}
		public HashMap input_collect() {
			return input;
		}
		public String display_get(String k) {
			String s=(String)input.get(k);
			if(s==null)
				s=(String)defaults.get(k);
			if(s==null)
				s="";
			return s;
		}
		public void process_node(Element e) {
			HashMap att=new HashMap();
			NamedNodeMap at = e.getAttributes();
			for(int i=0; i<at.getLength(); i++) {
				Attr a=(Attr)at.item(i);
				String an=a.getNodeName();
				String av=a.getNodeValue();
				if(an.startsWith("t-")) {
					att.put(an.substring(2),av);
				}
			}
			if(att.containsKey("value")) {
				if(att.containsKey("name") && ("checkbox".equals(att.get("type")) || "raido".equals(att.get("type")))) {
					if(att.containsKey("selected"))
						defaults.put(att.get("name"),att.get("value"));
				} else if(att.containsKey("select")) {
					if(att.containsKey("selected"))
						defaults.put(att.get("select"),att.get("value"));
				} else if(att.containsKey("name")) {
					defaults.put(att.get("name"),att.get("value"));
				}
			}
			if(att.containsKey("name")) {
				check.put(att.get("name"),att.get("check")==null?"//":att.get("check"));
			}
			NodeList nl=e.getChildNodes();
			for(int i=0;i<nl.getLength();i++) {
				if(nl.item(i).getNodeType()==Node.ELEMENT_NODE) {
					process_node((Element)nl.item(i));
				}
			}
		}
		public void process(Element e, HashMap arg) {
			process_node(e);
			if(check.size()>0) {
				submitted=true;
				for(Iterator it=check.entrySet().iterator();it.hasNext();) {
					Map.Entry en=(Map.Entry)it.next();
					String k=(String)en.getKey();
					String v=(String)en.getValue();
					if(arg.containsKey(k)) {
						String val=((String)arg.get(k)).trim();
						input.put(k,val);
						if("email".equals(v))
							v="/^[^@#!& ]+@[A-Za-z0-9-][.A-Za-z0-9-]{0,64}\\.[A-Za-z]{2,5}$/";
						if(!val.matches(v.substring(1,v.length()-1))) {
							error.put(k,"1");
						}
					} else if(!"optional".equals(v)) {
						submitted=false;
					}
				}
			}
		}
	}
	public static class QWebEval {
		org.apache.taglibs.standard.lang.jstl.VariableResolver r;
		org.apache.taglibs.standard.lang.jstl.ELEvaluator e;
		public QWebEval() {
			r=new org.apache.taglibs.standard.lang.jstl.VariableResolver() {
				public Object resolveVariable(String n, Object c) {
					Map v=(Map)c;
//					System.out.println("Eval.resolv: "+n+" from "+v);
//					Convert python type to java ones
					if("pageContext".equals(n)) {
						return v;
					} else {
						return v.get(n);
					}
				}
			};
			e=new org.apache.taglibs.standard.lang.jstl.ELEvaluator(r,true); // bypasscache
		}
		public Object eval(String expr, Map v, Class type) {
			Object r=null;
			try{
				r=e.evaluate("${"+expr+"}",v,type,null,null);
			} catch(org.apache.taglibs.standard.lang.jstl.ELException ex) {
				System.out.println("Eval.err: "+ex+" :"+type.getName()+": "+expr+"="+r);
			}
//			System.out.println("Eval:"+type.getName()+": "+expr+" = '"+r+"'");
			return r;
		}
		public Object eval_object(String expr, Map v) {
			return eval(expr,v,Object.class);
		}
		public String eval_str(String expr, Map v) {
			if(expr.equals("0")) {
				return (String)v.get(new Integer(0));
			} else {
				return (String)eval(expr,v,String.class);
			}
		}
		public String eval_format(String expr, Map v) {
			String[] s=("a"+expr).split("\\%");
			String r="";
			for(int i=0;i<s.length;i++) {
				if(s[i].length()==0) {
					r+="%";
				} else if(s[i].startsWith("(")) {
					String[] a=s[i].substring(1).split("\\)",2);
					if (a[1].startsWith("e")) {
						r+=xml_escape_att(eval_str(a[0],v)+a[1].substring(1));
					} else if (a[1].startsWith("q")) {
						r+=eval_str(a[0],v).replaceAll("\\'","''")+a[1].substring(1);
					} else {
						r+=eval_str(a[0],v)+a[1].substring(1);
					}
				} else {
					r+=s[i];
				}
			}
			return r.substring(1);
		}
		public boolean eval_bool(String expr, Map v) {
			Boolean b=(Boolean)eval(expr,v,Boolean.class);
//			System.out.println("eval_bool.bool: "+b);
			if(b==null) {
//				String s=(String)eval(expr,v,String.class);
//				System.out.println("eval_bool.str: "+s);
				return false;
			}
			return b.booleanValue();
		}
	}
	public static class QWebXml {
		QWebEval eval=new QWebEval();
		QWebURL url=new QWebURL();
		HashMap tags=new HashMap();
		HashMap tmpl=new HashMap();
		public QWebXml(String f) {
			java.lang.reflect.Method[] meth=this.getClass().getMethods();
			for(int i=0; i<meth.length; i++) {
				if(meth[i].getName().startsWith("render_tag")) {
					tags.put(meth[i].getName().substring("render_tag_".length()),meth[i]);
				}
			}
			xml_add(f);
		}
		public void xml_add(String f) {
			Document doc=xml_parsefile(f);
			Element e=doc.getDocumentElement();
			NodeList nl=e.getChildNodes();
			for(int i=0;i<nl.getLength();i++) {
				Node n=nl.item(i);
				if(n.getNodeType()==Node.ELEMENT_NODE && n.getNodeName().equals("t")) {
					Element et=((Element)n);
					tmpl.put(et.getAttribute("name"),et);
				}
			}
		}
		public QWebForm form(String name,HashMap v, HashMap arg, HashMap def) {
			QWebForm f=null;
			if(tmpl.containsKey(name)) {
				f=new QWebForm((Element)tmpl.get(name),arg,def);
				v.put(new Integer(1),f);
			} 
			return f;
		}
		public QWebForm form(String tname,HashMap v, HashMap arg) {
			return form(tname,v,arg,new HashMap());
		}
		public String render(String name, Map v) {
			if(tmpl.containsKey(name)) {
				return render_node((Element)tmpl.get(name),v);
			} else {
				return "qweb: template "+name+" not found";
			}
		}
		public String render(String name, String key, Object val) {
			HashMap h=new HashMap();
			h.put(key,val);
			return render(name,h);
		}
		public String render(String name) {
			return render(name,new HashMap());
		}
		public String render_node(Node n, Map v) {
			String r="";
			if(n.getNodeType()==Node.TEXT_NODE || n.getNodeType()==Node.CDATA_SECTION_NODE)
				r=n.getNodeValue();
			else if(n.getNodeType()==Node.ELEMENT_NODE) {
				Element e=(Element)n;
				String pre="";
				String t_tag=null;
				String g_att="";
				HashMap t_att=new HashMap();
				NamedNodeMap att = e.getAttributes();
				for(int i=0; i<att.getLength(); i++) {
					Attr a=(Attr)att.item(i);
					String an=a.getNodeName();
					String av=a.getNodeValue();
					if(an.startsWith("t-")) {
						if(an.startsWith("t-if-")) {
							if(eval_bool(av,v))
								g_att+=" "+an.substring(5)+"="+an.substring(5);
						} else if(an.startsWith("t-raw-")) {
							g_att+=" "+an.substring(6)+"=\""+eval_str(av,v)+"\"";
						} else if(an.startsWith("t-rawf-")) {
							g_att+=" "+an.substring(7)+"=\""+eval_format(av,v)+"\"";
						} else if(an.startsWith("t-esc-")) {
							g_att+=" "+an.substring(6)+"=\""+xml_escape_att(eval_str(av,v))+"\"";
						} else if(an.startsWith("t-escf-")) {
							g_att+=" "+an.substring(7)+"=\""+xml_escape_att(eval_format(av,v))+"\"";
						} else if(an.startsWith("t-href-")) {
							g_att+=" "+an.substring(7)+"=\""+url.href(eval_format(av,v))+"\"";
						} else if(an.startsWith("t-href")) {
							g_att+=" "+an.substring(2)+"=\""+url.href(eval_format(av,v))+"\"";
						} else if(an.startsWith("t-action")) {
							String s=eval_format(av,v);
							g_att+=" "+an.substring(2)+"=\""+url.action(s)+"\"";
							pre=url.input(s);
						} else {
							String an2=an.substring(2);
							t_att.put(an2,av);
							if(tags.containsKey(an2)) {
								t_tag=an2;
							}
						}
					} else {
						g_att+=" "+an+"=\""+xml_escape_att(av)+"\"";
					}
				}
				if(t_tag!=null) {
					try {
						Object[] arg=new Object[] {e,g_att,v};
						r=(String)((java.lang.reflect.Method)tags.get(t_tag)).invoke(this,arg);
					} catch(IllegalAccessException ex) {
					} catch(IllegalArgumentException ex) {
					} catch(java.lang.reflect.InvocationTargetException ex) {
					}
				} else {
					r=render_element(e,g_att,v,pre);
				}
			}
			return r;
		}
		public String render_element(Element e, String g_att, Map v, String pre) {
			String g_inner="";
			NodeList nl=e.getChildNodes();
			for(int i=0;i<nl.getLength();i++)
				g_inner+=render_node(nl.item(i),v);
			String name=e.getNodeName();
			if(name.equals("t")) {
				return g_inner;
			} else if(g_inner.length()>0) {
				return "<"+name+g_att+">"+pre+g_inner+"</"+name+">";
			} else {
				return "<"+name+g_att+"/>";
			}
		}
		public String render_element(Element e, String g_att, Map v) {
			return render_element(e,g_att,v,"");
		}

		public Object eval_object(String expr, Map v) {
			return eval.eval_object(expr,v);
		}
		public String eval_str(String expr, Map v) {
			return eval.eval_str(expr,v);
		}
		public String eval_format(String expr, Map v) {
			return eval.eval_format(expr,v);
		}
		public boolean eval_bool(String expr, Map v) {
			return eval.eval_bool(expr,v);
		}

		public String render_tag_raw(Element e, String g_att, Map v) {
			return eval_str(e.getAttribute("t-raw"),v);
		}
		public String render_tag_esc(Element e, String g_att, Map v) {
			return xml_escape_text(eval_str(e.getAttribute("t-esc"),v));
		}
		public String render_tag_rawf(Element e, String g_att, Map v) {
			return eval_format(e.getAttribute("t-rawf"),v);
		}
		public String render_tag_escf(Element e, String g_att, Map v) {
			return xml_escape_text(eval_format(e.getAttribute("t-escf"),v));
		}
		public String render_tag_foreach(Element e, String g_att, Map v) {
			String r="";
			String name=e.getAttribute("t-foreach");
			Object enu=eval_object(name,v);
			if(enu!=null) {
				String var=name.replace('.','_');
				HashMap d=new HashMap(v);
				int size=-1;
				if(enu.getClass().isArray())
					enu=new ArrayList(Arrays.asList((Object[])enu));
				try { size=((Integer)enu.getClass().getMethod("size",null).invoke(enu,null)).intValue(); } catch(Exception ex) { }
				// Add support for sql resultSet
				// Add support for Ibatis Results ?
				Iterator iter=null;
				try { iter=(Iterator)enu.getClass().getMethod("iterator",null).invoke(enu,null); } catch(Exception ex) { }
				if(iter!=null) {
					d.put(var+"_all",enu);
					d.put(var+"_size",new Integer(size));
					for (int index=0; iter.hasNext(); index++) {
						Object i=iter.next();
						d.put(var+"_value",i);
						d.put(var+"_index",new Integer(index));
						d.put(var+"_first",new Boolean(index==0));
						d.put(var+"_even",new Integer(index%2));
						d.put(var+"_odd",new Integer((index+1)%2));
						d.put(var+"_last",new Boolean(index+1==size));
						if(Map.class.isInstance(i)) {
							d.putAll((Map)i);
						} else {
							d.put(var,i);
						}
						r+=render_element(e,g_att,d);
					}
				} else {
					r="qweb: t-foreach "+name+" not iterable.";
				}
			} else {
				r="qweb: t-foreach "+name+" not found.";
			}
			return r;
		}
		public String render_tag_if(Element e, String g_att, Map v) {
			if(eval_bool(e.getAttribute("t-if"),v))
				return render_element(e,g_att,v);
			return "";
		}
		public String render_tag_call(Element e, String g_att, Map v) {
			HashMap d=new HashMap(v);
			d.put(new Integer(0),render_element(e,g_att,d));
			return render_node((Element)tmpl.get(e.getAttribute("t-call")),d);
		}
		public String render_tag_arg(Element e, String g_att, Map v) {
			v.put(e.getAttribute("t-arg"),render_element(e,g_att,v));
			return "";
		}
		public String render_tag_type(Element e, String g_att, Map v) {
			String r="";
			String type=e.getAttribute("t-type");
			String name=e.getAttribute("t-name");
			QWebForm f=(QWebForm)v.get(new Integer(1));
			if(f!=null) {
				String css="form_valid";
				if(f.error_get(name)) {
					css="form_error";
				}
				if("text".equals(type) || "password".equals(type)) {
					g_att+=" type=\""+type+"\" name=\""+name+"\" value=\""+xml_escape_att(f.display_get(name))+"\" class=\""+css+"\"";
					r=render_element(e,g_att,v);
				}
				if("textarea".equals(type)) {
					g_att+=" name=\""+name+"\" class=\""+css+"\"";
					r="<"+type+g_att+">"+xml_escape_text(f.display_get(name))+"</"+type+">";
				}
			}
			/*
			if type=="checkbox" or type=="radio":
				v1=t_att["value"]
				v2=form.display_get(name)
				if len(v2) and v1==v2:
					check='"checked"'
				else:
					check=''
				val=cgi.escape(v1,True)
				g_att+=' type="%s" name="%s" value="%s" class="%s"%s'%(type,name,val,css,check)
				r=self.render_element(e,g_att,v)
			if type=="select":
				g_att+=' name="%s"'%(name)
				r=self.render_element(e,g_att,v)
			return r
			*/
			return r;
		}
		public String render_tag_select(Element e, String g_att, Map v) {
			/*
			def render_tag_select(self,e,t_att,g_att,v):
				name=str(t_att["select"])
				v1=t_att["value"]
				v2=v[1].display_get(name)
				if len(v2) and v1==v2:
					selected=' selected="selected"'
				else:
					selected=''
				val=cgi.escape(v1,True)
				g_att+=' value="%s"%s'%(val,selected);
				return self.render_element(e,g_att,v)
		*/
			String r="";
			r=render_element(e,g_att,v);
			return r;
		}

		public String render_tag_error(Element e, String g_att, Map v) {
			QWebForm f=(QWebForm)v.get(new Integer(1));
			if(f!=null && f.error_get(e.getAttribute("t-error"))) {
				return render_element(e,g_att,v);
			}
			return "";
		}
		public String render_tag_valid(Element e, String g_att, Map v) {
			QWebForm f=(QWebForm)v.get(new Integer(1));
			if(f!=null && f.input_valid()) {
				return render_element(e,g_att,v);
			}
			return "";
		}
		public String render_tag_invalid(Element e, String g_att, Map v) {
			QWebForm f=(QWebForm)v.get(new Integer(1));
			if(f!=null && f.error_any()) {
				return render_element(e,g_att,v);
			}
			return "";
		}
	}
	public static class QWebControl {
		public Object control(Object self, String jump, Object[] arg) {
			HashMap done=new HashMap();
			ArrayList todo=null;
			while(true) {
				if(jump!=null) {
					String tmp="";
					todo=new ArrayList();
					String[] s=jump.split("_");
					for(int i=0; i<s.length; i++) {
						tmp+=s[i];
						if(!done.containsKey(tmp))
							todo.add(tmp);
						tmp+="_";
					}
					jump=null;
				} else if(todo.size()>0) {
					String m=(String)todo.get(0);
					todo.remove(0);
					done.put(m,m);
					java.lang.reflect.Method[] meth=self.getClass().getMethods();
					for(int i=0; i<meth.length; i++) {
						if(meth[i].getName().equals(m)) {
							try {
								Object r=meth[i].invoke(self,arg);
								if(r!=null)
									jump=(String)r;
							} catch(IllegalAccessException e) {
								System.out.println("qweb-control:"+m+":IllegalAccessException:"+e);
							} catch(IllegalArgumentException e) {
								System.out.println("qweb-control:"+m+":IllegalArgumentException:"+e);
							} catch(java.lang.reflect.InvocationTargetException e) {
								String n=e.getTargetException().getClass().getName();
								System.out.println("qweb-control:"+m+":"+n+":"+e.getTargetException());
								e.getTargetException().printStackTrace();
							}
						}
					}
				} else {
					break;
				}
			}
			return todo;
		}
	}
	public static class QWebPy {
		public static Object load(ServletContext sc) {
			String pp;
			PythonInterpreter pi=null;
			Object o=sc.getAttribute("app.pi");
			if(o==null) {
				try {
					pp=sc.getRealPath("WEB-INF/test");
					String cp=".";
					String[] lib=(new File(sc.getRealPath("WEB-INF/lib"))).list();
					for(int i=0;i<lib.length;i++) {
						if(lib[i].endsWith(".jar"))
							cp+=File.pathSeparator+sc.getRealPath("WEB-INF/lib/"+lib[i]);
					}
					cp+=File.pathSeparator+sc.getRealPath("WEB-INF/classes");
					Properties p=new Properties();
					p.setProperty("python.cachedir",System.getProperty("java.io.tmpdir")+File.separator+"temp");
					p.setProperty("python.path",pp);
					p.setProperty("java.class.path",cp);
					PythonInterpreter.initialize(System.getProperties(),p,null);
					pi=new PythonInterpreter();
					pi.exec("print 'hello'");
					sc.setAttribute("app.pp",pp);
					sc.setAttribute("app.pi",pi);
				} catch (PyException e) {
					System.out.println("pi:except "+e);
				}
				return pi;
			} else {
				return o;
			}
		}
		public static void exec(ServletContext sc, String s) {
			PythonInterpreter pi=(PythonInterpreter)load(sc);
			pi.exec(s);
		}
		public static void execfile(ServletContext sc, String s) {
			PythonInterpreter pi=(PythonInterpreter)load(sc);
			if(s.indexOf(File.separator)==-1) {
				pi.execfile(sc.getAttribute("app.pp")+File.separator+"file.py");
			} else {
				pi.execfile(s);
			}
		}
		public static Object call(ServletContext sc, String s, Object a1) {
			PythonInterpreter pi=(PythonInterpreter)load(sc);
			PyFunction pf=(PyFunction)pi.get(s);
			return pf.__call__(new PyJavaInstance(a1));
		}
		public static Object call(ServletContext sc, String s, Object a1, Object a2) {
			PythonInterpreter pi=(PythonInterpreter)load(sc);
			PyFunction pf=(PyFunction)pi.get(s);
			return pf.__call__(new PyJavaInstance(a1),new PyJavaInstance(a2));
		}
		public static Object call(ServletContext sc, String s, Object a1, Object a2, Object a3) {
			// pi.set("a1",sc); pi.set("a2",req); pi.set("a3",res); pi.exec("UpdateManager().process(a1,a2,a3)");
			PythonInterpreter pi=(PythonInterpreter)load(sc);
			PyFunction pf=(PyFunction)pi.get(s);
			return pf.__call__(new PyJavaInstance(a1),new PyJavaInstance(a2),new PyJavaInstance(a3));
		}
		public static Object tojava(ServletContext sc, String s, String c) {
			try {
				PythonInterpreter pi=(PythonInterpreter)load(sc);
				PyObject po=pi.get(s);
				Object o=po.__tojava__(Class.forName(c));
				if (o == Py.NoConversion)
					return null;
				return o;
			} catch(java.lang.ClassNotFoundException e) {
				return null;
			}
		}
	}

	public static void main(String[] s) {
//		QWebControl c=new QWebControl();
//		c.control(c,"test_love",new String[]{"test",null,null,null});
//		QWebXml x=new QWebXml("qweb.xml");
//		HashMap v=new HashMap();
//		v.put("title","SEX");
//		HashMap t2=new HashMap();
//		t2.put("sex","Love");
//		v.put("a",new Object[] {"1","2","3",t2});
//		v.put("al",new ArrayList());
//		QWebSql q=new QWebSql();
//		q.query();
//		System.out.println(q.resmap[0]);
//		String str=x.render("page","user",q);
//		Object str=j_new("java.lang.String");
//		System.out.println(str);
//		System.out.println(j_list(j_list(System.getProperties())));
//		System.out.println(j_call(str,"toUpperCase"));
//		zip_unzip("test.zip",".");
//		System.out.println(q);
//		System.out.println(q.resmap[0].get("USERNAME"));
		System.out.println((new QWebEval()).eval_format("cac%(a)qa12345'1234",j_map("a","1234'5678")));
		System.out.println(url_check("http://google.com/"));
		System.out.println(url_check("http://google.com/pipi"));
	}

}
