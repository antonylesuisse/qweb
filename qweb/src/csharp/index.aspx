<%@ Page language="C#" Debug="true"%>
<%@ import namespace="System.Collections" %>
<%@ import namespace="System.Xml" %>
<%@ Register TagPrefix="Qweb" Namespace="Almacom.QWeb" assembly="Almacom.QWeb" %>
<%@ Register TagPrefix="Amigrave" Namespace="Amigrave" assembly="Amigrave" %>

<script runat="server">
/*
public class QwebExt : AgrQwebExt {
	public string ext_asap_help(QWebXml xml, XmlElement e, string t_val, Hashtable t_att, string g_att, Hashtable h)  {
		string tmp = "<a href=\"javascript:void(0);\" ";
		tmp += String.Format("onmouseover=\"return overlib('{0}',", xml.render_element(e,g_att,h));
		tmp += String.Format("CAPTION, '{0}'", t_val);
		if (t_att["ext_asap_help_mode"] != null) tmp += String.Format(", {0}", t_att["ext_asap_help_mode"]);
		tmp += ");\" onmouseout=\"return nd();\"><img src=\"/common/img/help.gif\" width=\"12\" height=\"13\" alt=\"{1}\" border=\"0\"></a>";
		return tmp;
	}

	public string ext_fold(QWebXml xml, XmlElement e, string t_val, Hashtable t_att, string g_att, Hashtable h)  {
		string tmp, html_class = "";
		if (t_att["ext_fold_class"] != null) html_class = String.Format(" class=\"{0}\"", t_att["ext_fold_class"]);
		tmp = String.Format("<a href=\"javascript:void(0)\" onclick=\"agr_div_fold(this);\"{2}>{0}</a><div style=\"display:none;\">{1}</div>", t_val, xml.render_element(e,g_att,h), html_class);
		return tmp;
	}
}
*/


public class MyApp : qweb_smvc {
	public HttpSessionState _session = HttpContext.Current.Session;
	private string APP_CODE;

	public MyApp(string code) {
		APP_CODE = code;
		Xml = new QWebXml();
		Xml.xml_add(agr.mappath("test.xml"));
		Xml.xml_reload();
		Xml.Url = new QWebUrl("index.aspx","lang=fr&aze=12");
	}

	public Object s_control(HttpContext c, Hashtable h) {
		if (c.Request["p"] == "about") {
			QState = "about";
		} else if (c.Request["p"] == "products") {
			QState = "products";
		} else {
			QState = "home";
		}
		return null;
	}
	public Object s_view(Hashtable h) {
		return null;
	}

	public Object s_home_control(HttpContext c, Hashtable h) {
		qweb_util.print(Req);
		QWebForm f=Xml.form("home");
		if(c.Request["button"]!=null && f.input_valid()) {
			qweb_util.print(f.input_collect());
			QState="about";
		}

/*
		QWebForm f=xml.form("home");
		if(c.Request["button"]!=null)) {
			if(!verity(c.Request["button"]))
				f.error_set("button");
			if(f.input_valid()) {
				qweb_util.print(f.input_collect());
				// 
				QState="about";
			}
		}
*/

		h["form"]=f;
		return null;
	}
	public Object s_home_view(Hashtable h) {
		return Xml.render("home", h);
	}

	public Object s_about_control(HttpContext c, Hashtable h) {
		return null;
	}
	public Object s_about_view(Hashtable h) {
		return Xml.render("about", h);
	}


}
</script>
<%
	if (Session["TEST"] is MyApp)
		Session["TEST"] = null;
	if (Session["TEST"] == null)
		Session["TEST"] = new MyApp("TEST");
	MyApp myapp = (MyApp)Session["TEST"];
	myapp.control();
	Response.Write(myapp.view());
// vim:syntax=cs:
%>
