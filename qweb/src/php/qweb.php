<?
	include("qwebdom4.php");
	# vim:foldcolumn=3 foldnestmax=2 foldlevel=0:
	#
	# Written by Antony Lesuisse (al@udev.org) in 2004-2005.
	# Public domain.  The author disclaims copyright to this
	# source code.
	#
	#------------------------------------------------------
	# lib: many useful functions for PHP
	#------------------------------------------------------
	# missing var_export function for php < 4.2
	if (!function_exists("var_export")) {
		function var_export() {
			$args = func_get_args();
			$indent = (isset($args[2])) ? $args[2] : '';
			if (is_array($args[0])) {
				$output = 'array ('."\n";
				foreach ($args[0] as $k => $v) {
					if (is_numeric($k))
						$output .= $indent.'  '.$k.' => ';
					else
						$output .= $indent.'  \''.str_replace('\'', '\\\'', str_replace('\\', '\\\\', $k)).'\' => ';
					if(is_array($v))
						$output .= var_export($v, true, $indent.'  ');
					else {
						if (gettype($v) != 'string' && !empty($v))
							$output .= $v.','."\n";
						else
							$output .= '\''.str_replace('\'', '\\\'', str_replace('\\', '\\\\', $v)).'\','."\n";
					}
				}
				$output .= ($indent != '') ? $indent.'),'."\n" : ')';
			} else
				$output = $args[0];
			if ($args[1] == true)
				return $output;
			else
				echo $output;
		}
	}
	function lib_http_404() {
		header("HTTP/1.0 404 Not Found");
		echo "<h1>404 Not Found</h1>";
		exit;
	}
	function lib_http_302($url="http://www.google.com/search?q=love") {
		header('HTTP/1.0 302 Moved Temporarily');
		header("Location: $url");
		exit;
	}
	function lib_microtime() {
		list($usec,$sec)=explode(" ",microtime());
		return (float)$usec+(float)$sec;
	}
	function lib_pwgen($min=6,$max=8) {
		$char="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
		$char="aaabcdeeefghiiijklmnooopqrstuuuvwxyz";
		$pwd="";
		while(strlen($pwd)<rand($min,$max)) {
			$pwd.=$char{rand(0,strlen($char)-1)};
		}
		return $pwd;
	}
	function lib_split($nbr,$l1) {
		$n=sizeof($l1);
		$k=0;
		$l2=array();
		for($i=0;$i<$n;$i++) {
			if($i >= (($k+1)*($n/$nbr))) {
				$k+=1;
			}
			$l2[$k][]=$l1[$i];
		}
		return $l2;
	}
	function lib_readfile($name) {
		$f=fopen($name,"r");
		$r="";
		while(!feof($f))
			$r.=fread($f,65536);
		fclose($f);
		return $r;
	}
	function lib_xml_print($n) {
		$nt=$n->type;
		$nn=$n->tagname;
		$nc=$n->children();
		$nc=$nc?$nc:array();
		if($nt == XML_DOCUMENT_NODE) {
			foreach($nc as $i)
				lib_xml_print($i);
		} if($nt == XML_TEXT_NODE) {
			echo str_replace(">","&gt;",str_replace("<","&lt;",$n->content));
		} elseif($nt == XML_ELEMENT_NODE) {
			$na=$n->attributes();
			$na=$na?$na:array();
			$att="";
			foreach($na as $i) {
				$an=$i->name;
				$av=$i->value;
				$att.=" $an=\"$av\"";
			}
			if(sizeof($nc)) {
				echo "<$nn$att>";
				foreach($nc as $i)
					lib_xml_print($i);
				echo "</$nn>";
			} else {
				echo "<$nn$att/>";
			}
		}
	}
	function lib_str_l1toa($s) {
		return strtr($s,
		"•µ¿¡¬√ƒ≈∆«»… ÀÃÕŒœ–—“”‘’÷ÿŸ⁄€‹›ﬂ‡·‚„‰ÂÊÁËÈÍÎÏÌÓÔÒÚÛÙıˆ¯˘˙˚¸˝ˇäåéöúûü",
		"YuAAAAAAACEEEEIIIIDNOOOOOOUUUUYsaaaaaaaceeeeiiiionoooooouuuuyySOZsozY");
	}
	function lib_stra($s) {
		return preg_replace("/[^0-9A-Za-z _-]/"," ",lib_str_l1toa($s));
	}
	function lib_stru($s) {
		return preg_replace("/[^0-9A-Za-z_]/","_",lib_str_l1toa($s));
	}
	function lib_download($fname,$fstr=0,$fpath="") {
		if(is_string($fstr) and $fsize=strlen($fstr)) {
			header("Content-Type: application/octet-stream");
			header("Content-Type: application/force-download");
			header("Content-Type: application/download");
			header("Content-Disposition: attachment; filename=\"$fname\"");
			header("Content-Transfer-Encoding: binary");
			header("Content-Length: ".$fsize);
			echo $fstr;
			exit;
		} elseif($fsize=filesize($fpath)) {
			#$temp=explode("=",$HTTP_RANGE);
			#$temp2=explode("-",$temp[1]);
			#$offset=$temp2[0];
			if(!$offset)
				$offset=0;
			$fd=fopen($fpath,"rb");
			if($offset==0) {
				header("Content-Disposition: attachment; filename=\"$fname\"");
				header("Content-Transfer-Encoding: binary");
				header("Content-Length: ".$fsize);
			} else {
				header("HTTP/1.1 206 Partial Content");
				header("Content-Range: bytes $offset-".($fsize-1)."/".$fsize);
				header("Content-Length: ".($fsize-$offset));
				header("Connection: close" );
				fseek($fd,$offset);
			}
			header("Content-Type: application/octet-stream");
			header("Content-Type: application/force-download");
			header("Content-Type: application/download");
			fpassthru($fd);
			exit;
		}
		return 1;
	}
	function lib_system() {
		$arg=func_get_args();
		if(is_array($arg[0]))
			$arg=$arg[0];
		$cmd=array_shift($arg);
		foreach($arg as $i) {
			$cmd.=" ''".escapeshellarg($i);;
		}
		system($cmd);
	}
	function lib_popen($arg,$mode) {
		$cmd=array_shift($arg);
		foreach($arg as $i) {
			$cmd.=" ''".escapeshellarg($i);;
		}
		return popen($cmd,$mode);
	}
	# attchments depends on mime-construct(1)
	function lib_mail($mail,$type="text",$fpath="",$fname="",$ftype="application/octet-stream") {
		list($h,$b)=explode("\n\n",trim($mail),2);
		$hl=explode("\n",$h);
		foreach($hl as $i) {
			if(preg_match("/^From: .*?([A-Za-z0-9_.-]+@[A-Za-z0-9.-]+)/",$i,$m))
				$sender=$m[1];
		}
		if($type=="text")
			$type='text/plain; charset="iso-8859-1"';
		elseif($type="html")
			$type='text/html; charset="iso-8859-1"';
		$msg="";
		if(strlen($fpath)==0) {
			$hl[]="MIME-Version: 1.0";
			$hl[]="Content-Type: $type";
			$hl[]="Content-Transfer-Encoding: 8bit";
			foreach($hl as $i)
				$msg.="$i\n";
			$msg.="\n$b";
		} else {
			$c=array("mime-construct","--output","--type",$type,"--encoding","8bit");
			foreach($hl as $i)
				array_splice($c,count($c),0,array("--header",$i));
			array_splice($c,count($c),0,array("--string",$b));
			if(strlen($fname)==0)
				$fname=basename($fpath);
			array_splice($c,count($c),0,array("--type",$ftype,"--encoding","base64","--attachment",$fname,"--file",$fpath));
			$p=lib_popen($c,"r");
			while($t=fread($p,8192))
				$msg.=$t;
			pclose($p);
		}
		if($sender)
			$p=lib_popen(array("/usr/sbin/sendmail","-t","-f",$sender),"w");
		else
			$p=lib_popen(array("/usr/sbin/sendmail","-t"),"w");
#		echo "<pre>$msg</pre>";
		fwrite($p,$msg);
		pclose($p);
	}
	# TODO fix $k should not increment for %%, usr i for src, j for arg i++,j++ right place
	function lib_query_printf() {
		$arg=func_get_args();
		$src=explode("%",array_shift($arg));
		$q=array_shift($src);
		foreach($src as $k=>$v) {
			if($v{0}=="s") {
				$q.=addslashes($arg[$k]).substr($v,1);
			} elseif($v{0}=="r") {
				$q.=$arg[$k].substr($v,1);
			} elseif($v{0}=="a") {
				$tmp="";
				foreach($arg[$k] as $key=>$val)
					$tmp.="$key='".addslashes($val)."',";
				$q.=substr($tmp,0,-1).substr($v,1);
			} elseif(strlen($v)==0) {
				$q.="%";
			} else {
				$q.=$v;
			}
		}
		return $q;
	}
	function lib_query() {
		$arg=func_get_args();
		return mysql_query(call_user_func_array('lib_query_printf',$arg));
	}
	function lib_queryt() {
		$arg=func_get_args();
		echo call_user_func_array('lib_query_printf',$arg);
	}
	function lib_query_fetch() {
		$arg=func_get_args();
		$a=array();
		$q=mysql_query(call_user_func_array('lib_query_printf',$arg));
		while($r=mysql_fetch_assoc($q))
			$a[]=$r;
		return $a;
	}
	function lib_trim($a) {
		$r=array();
		foreach($a as $k=>$v)
			$r[$k]=trim($v);
		return $r;
	}
	function lib_pre() {
		$arg=func_get_args();
		$pre=array_shift($arg);
		$r=array();
		foreach($arg as $a) {
			foreach($a as $k=>$v)
				$r[$pre."_".$k]=$v;
		}
		return $r;
	}
	function lib_suffix() {
		$arg=func_get_args();
		$pre=array_shift($arg)."_";
		$r=array();
		foreach($arg as $a) {
			foreach($a as $k=>$v) {
				$key = strncmp($pre,$k,strlen($pre))==0 ? substr($k,strlen($pre)) : $k;
				$r[$key]=$v;
			}
		}
		return $r;
	}
	function lib_merge($a,$b,$pre) {
	}
	# zipfile handling
	function lib_zip_open($zip,$name) {
		return lib_popen(array("unzip","-p",$zip,$name),"r");
	}
	function lib_zip_readfile($zip,$name) {
		$f=lib_zip_open($zip,$name);
		$r="";
		while(!feof($f))
			$r.=fread($f,65536);
		pclose($f);
		return $r;
	}
	function lib_zip_print($zip,$name) {
		$f=lib_zip_open($zip,$name);
		$c=0;
		while(!feof($f)) {
			$s=fread($f,4096);
			$c+=strlen($s);
			echo $s;
		}
		pclose($f);
		return $c;
	}
	function lib_zip_serve($zip,$name) {
		if(strlen($name)==0)
			$name="index.html";
		if(preg_match("/\\.(gif)$/i",$name,$m)) {
			header("Content-Type: image/gif");
		} elseif(preg_match("/\\.(jpg|jpeg|png)$/i",$name,$m)) {
			header("Content-Type: image/jpeg");
		} elseif(preg_match("/\\.(png)$/i",$name,$m)) {
			header("Content-Type: image/png");
		} elseif(preg_match("/\\.(txt)$/i",$name,$m)) {
			header("Content-Type: text/plain");
		}
		if(lib_zip_print($zip,$name)==0) {
			header("HTTP/1.0 404 Not Found");
			echo "<h1>404 Not Found</h1>";
			exit();
		}
	}
	function lib_zip_example() {
		$s=$_SERVER["PATH_INFO"];
		if(preg_match("!^/(actualite[0-9-]+|dossier[0-9-]+)/(.*)$!",$s,$m)) {
			$zip=$m[1];
			$name=$m[2];
			lib_zip_serve("files/$zip.zip",$name);
		}
	}
	#----------------------------------------------------------
	# qweb: Quick Web Toolkit, url, xml-template, form, smvc
	# globals $qweb_u (url), $qweb_x (template)
	#----------------------------------------------------------
	class qweb_smvc {
		# public
		var $state="";
		# deprecated
		var $state_arg=array();
		# private
		var $q_run=array(),$q_run_i=0,$q_sub=array(),$q_sel;
		# new view context
		var $q_vc;
		function view($a=array()) {
			$a=array_merge($a,$this->q_vc);
			$this->q_vc=0;
			foreach($this->q_state_split($this->state) as $i) {
				$m="s{$i}_view";
				if(method_exists($this,$m)) {
					$args=$this->state_arg;
					array_unshift($args,$a);
					$a=call_user_func_array(array(&$this,$m),$args);
					if(is_string($a))
						return $a;
				}
			}
		}
		function control($arg=0,$vc=array()) {
			if(!is_array($arg))
				$arg=array_merge($_GET,$_POST);
			$this->q_vc=$vc;
			$pri=0;
			$this->q_sel=0;
			foreach($this->q_sub as $k=>$v) {
				$o=& $this->q_sub[$k]["obj"];
				if($o->control($arg) and $v["pri"]>$pri) {
					$this->q_sel=$k;
					$pri=$v["pri"];
				}
			}
			$rc=0;
			$this->q_run=$this->q_state_split($this->state);
			for($i=0;$i<count($this->q_run);$i++) {
				$s1=$this->q_run[$i];
				$m="s{$s1}_control";
				if(method_exists($this,$m)) {
					$this->q_run_i=$i;
					$ret=$this->$m($arg,&$this->q_vc);
					if(is_int($ret) or is_bool($ret)) {
						$rc=$ret;
					} elseif(is_array($ret)) {
						$arg=$r;
					}
				}
			}
			return $rc;
		}
		function q_state_split($state) {
			$r=array("");
			if($state=="")
				return $r;
			$s=explode("_",$state);
			for($i=0;$i<sizeof($s);$i++)
				$r[]="_".join("_",array_slice($s,0,$i+1));
			return $r;
		}
		function q_state_set() {
			$arg=func_get_args();
			$s=array_shift($arg);
			if(count($arg))
				$this->state_arg=$arg;
			$this->state=$s;
			$prev=array_slice($this->q_run,0,$this->q_run_i+1);
			$next=array();
			foreach($this->q_state_split($s) as $i) {
				if(!in_array($i,$prev))
					$next[]=$i;
			}
			array_splice($prev,count($prev),count($prev),$next);
#			array_splice($this->q_run,$this->q_run_i,count($this->q_run),array()); To stop
			$this->q_run=$prev;
		}
		function q_sub_add($name,&$wid,$pri=0) {
			$this->q_sub[$name]=array("obj"=>$wid,"pri"=>$pri);
		}
		function q_sub_del($name) {
			unset($this->q_sub[$name]);
		}
		function q_sub_select() {
			return $this->q_sel;
		}
		function q_sub_view($name=0,$a=array()) {
			if(!is_string($name))
				$name=$this->q_sel;
			if(array_key_exists($name,$this->q_sub)) {
				$o=& $this->q_sub[$name]["obj"];
				return $o->view($a);
			}
		}
		function &q_sub_get($name) {
			if(array_key_exists($name,$this->q_sub)) {
				return $this->q_sub[$name]["obj"];
			}
		}
	}
	class qweb_url {
		var $base,$args;
		function qweb_url($base="index.php",$arg="") {
			$this->base=$base;
			$this->param=array();
			$this->param_reg($arg);
		}
		function param_add($s,$p=0) {
			if($p==0)
				$p=$this->param;
			if(strlen($s)) {
				foreach(explode("&",$s) as $key=>$val) {
					$a=explode("=",$val);
					$p[$a[0]]=$a[1];
				}
			}
			return $p;
		}
		function param_reg($s) {
			$this->param=$this->param_add($s);
		}
		function param_str($p=0) {
			if($p==0)
				$p=$this->param;
			foreach($p as $key=>$val)
				$s.="$key=".rawurlencode($val)."&amp;";
			return substr($s,0,strlen($s)-5);
		}
		function href($i="") {
			return 'href="'.$this->base.'?'.$this->param_str($this->param_add($i)).'"';
		}
		function str($i="",$class="",$title="") {
			if($class)
				$class=" class=\"$class\"";
			if($title)
				$class=" title=\"$title\"";
			return '<a '.$this->href($i)."$class$title>";
		}
		function form_action() {
			return "action=\"".$this->base."\"";
		}
		function form_input($i="") {
			$t=$this->param_add($i);
			foreach($t as $key=>$val)
				$s.="<input type=\"hidden\" name=\"$key\" value=\"".rawurlencode($val)."\">\n";
			return $s;
		}
		function form_get($i="") {
			return "<form method=\"get\" ".$this->form_action().">\n".$this->form_input($i);
		}
		function form_post($i="") {
			return "<form method=\"post\" ".$this->form_action().">\n".$this->form_input($i);
		}
		function form_multi($i="") {
			return "<form enctype=\"multipart/form-data\" method=\"post\" action=\"".$this->base."\">\n".$this->form_input($i);
		}
		function request() {
			return array_merge($_GET,$_POST);
		}
	}
#	TODO add input SUMIBT -> submitted, Missing-defined ?
	class qweb_form {
		function qweb_form($name,$def=0,$pre="") {
			$this->v_sumitted=0;
			$this->v_def=array();
			$this->v_input=array();
			$this->v_error=array();
			$this->process($name);
			if(is_array($def))
				$this->default_fill($def,$pre);
		}
		function default_empty() {
			return sizeof($this->v_input)==0;
		}
		function default_set($k,$v) {
			echo "";
			$this->v_def[$k]=$v;
		}
		function default_fill($a,$pre="") {
			foreach($a as $name=>$v)
				$this->default_set($pre.$name,$v);
		}
		function process_node($n,$v) {
			$nt=$n->type;
			$nn=$n->tagname;
			$nc=$n->children();
			$nc=$nc?$nc:array();
			if($nt == XML_ELEMENT_NODE) {
				$na=$n->attributes();
				$na=$na?$na:array();
				$tv=array();
				foreach($na as $i) {
					$an=$i->name;
					$av=$i->value;
					if(strncmp("t-",$an,2)==0)
						$tv[substr($an,2)]=$av;
				}
				if($value=$tv["value"]) {
					if($name=$tv["name"] and ($tv["type"]=="checkbox" or $tv["type"]=="radio")) {
						if($tv["selected"])
							$this->v_def[$name]=$value;
					} elseif($name=$tv["select"]) {
						if($tv["selected"])
							$this->v_def[$name]=$value;
					} elseif($name=$tv["name"]) {
						$this->v_def[$name]=$value;
					}
				}
				if($name=$tv["name"]) {
					if(array_key_exists($name,$v)) {
						$this->v_submitted=1;
						if(!($check=$tv["check"]))
							$check="";
						if($check=="email")
							$check='/^[^@#!& ]+@[A-Za-z0-9-][.A-Za-z0-9-]{0,64}\\.[A-Za-z]{2,5}$/';
						if($tv["notrim"])
							$val=$v[$name];
						else
							$val=trim($v[$name]);
						$this->v_input[$name]=$val;
						if($check and (!preg_match($check,$val))) {
							$this->v_error[$name]=1;
						}
					}
				}
				foreach($nc as $i)
					$this->process_node($i,$v);
			}
		}
		function process($name,$v=0) {
			global $qweb_x;
			if(!$v)
				$v = array_merge($_GET,$_POST);
			$x=$qweb_x->xml_template($name);
			$this->process_node($x,$v);
		}
		function error_set($k) {
			$this->v_error[$k]=1;
		}
		function error_clear($k) {
			unset($this->v_error[$k]);
		}
		function error_get($k) {
			return $this->v_error[$k];
		}
		function error_any() {
			return (sizeof($this->v_error)!=0) and $this->v_submitted;
		}
		function input_set($k,$v) {
			$this->v_input[$k]=$v;
		}
		function input_get($k) {
			return $this->v_input[$k];
		}
		function input_valid() {
			return (sizeof($this->v_error)==0) and $this->v_submitted;
		}
		function input_collect($pre="") {
			$n=strlen($pre);
			$x=array();
			foreach($this->v_input as $name=>$v)
				$x[substr($name,$n)]=$v;
			return $x;
		}
		function display_get($name) {
			if(array_key_exists($name,$this->v_input))
				return $this->v_input[$name];
			else
				return $this->v_def[$name];
		}
	}
	class qweb_xml {
		var $template=array();
		function qweb_xml($xml="") {
			if($xml)
				$this->load($xml);
		}
		function load($xml) {
			if(strncmp($xml,"<?xml",5)==0)
				$n0=xmldoc($xml);
			else
				$n0=xmldocfile($xml);
			$n1=$n0->children();
			foreach($n1 as $j) {
				$n2=$j->children();
				foreach($n2 as $i) {
					if($i->type==XML_ELEMENT_NODE and $i->tagname=="t") {
						$ia=$i->attributes();
						if(($ia[0]->name=="name") or ($ia[0]->name=="form")) {
							$this->template[$ia[0]->value]=$i;
						} 
					}
				}
			}
		}
		function xml_template($te) {
			if(array_key_exists($te,$this->template))
				return $this->template[$te];
			else
				die("template: $te missing.");
		}
		function xml_eval($dic,$_expr) {
			extract($dic);
			return eval("return $_expr;");
		}
		function xml_element($nn,$att,$nc,$dic,$trim=0,$pre="") {
			$g_inner="";
			foreach($nc as $i)
				$g_inner.=$this->xml_node($i,$dic);
			if($trim)
				$g_inner=trim($g_inner);
			if($nn=="t") {
				return $g_inner;
			} elseif(sizeof($nc) or strlen($pre)) {
				return "<$nn$att>$pre$g_inner</$nn>";
			} else {
				return "<$nn$att/>";
			}
		}
		function xml_node($n,$dic) {
			global $qweb_u;
			$r="";
			$nt=$n->type;
			$nn=$n->tagname;
			$nc=$n->children();
			$nc=$nc?$nc:array();
			if($nt == XML_TEXT_NODE) {
				$r.=utf8_decode($n->content);
			} elseif($nt == XML_ELEMENT_NODE) {
				$na=$n->attributes();
				$na=$na?$na:array();
				$att="";
				$tv=array();
				$trim=0;
				foreach($na as $i) {
					$an=$i->name;
					$av=$i->value;
					if(strncmp("t-",$an,2)==0) {
						if(strncmp("t-att-",$an,6)==0) {
							$an=substr($an,6);
							$av=$this->xml_eval($dic,$av);
							$av=htmlspecialchars($av);
							$att.=" $an=\"$av\"";
						} elseif(strncmp("t-href",$an,6)==0) {
							$att.=' '.$qweb_u->href($this->xml_eval($dic,"\"$av\""));
						} elseif(strncmp("t-trim",$an,6)==0) {
							$trim=$av;
						} else {
							$tv[substr($an,2)]=$av;
						}
					} else {
						$att.=" $an=\"".htmlspecialchars(utf8_decode($av)).'"';
					}
				}
				if($tv) {
					if($tv["raw"]=="0") {
						$r.=$dic[0];
					} elseif($e=$tv["rawf"]) {
						$r.=sprintf($e,$this->xml_eval($dic,$tv["raw"]));
					} elseif($e=$tv["raw"]) {
						$r.=$this->xml_eval($dic,$e);
					} elseif($e=$tv["escf"]) {
						$r.=htmlentities(sprintf($e,$this->xml_eval($dic,$tv["esc"])));
					} elseif($e=$tv["esc"]) {
						$r.=htmlentities($this->xml_eval($dic,$e));
					} elseif($e=$tv["action"]) {
						$att.=' '.$qweb_u->form_action();
						$input=$qweb_u->form_input($this->xml_eval($dic,"\"$e\""));
						$r.=$this->xml_element($nn,$att,$nc,$dic,$trim,$input);
					} elseif($e=$tv["if"]) {
						if($this->xml_eval($dic,$e))
							$r.=$this->xml_element($nn,$att,$nc,$dic,$trim);
					} elseif($e=$tv["foreach"]) {
						if(!array_key_exists($e,$dic)) {
							echo "template: var $e not found.";
						} else {
							foreach($dic[$e] as $i)
								$r.=$this->xml_element($nn,$att,$nc,array_merge($dic,$i),$trim);
						}
					} elseif($e=$tv["call"]) {
						$tmp="";
						$arg=array();
						foreach($nc as $i) {
							if($i->type==XML_ELEMENT_NODE and $i->tagname=="t") {
								$ia=$i->attributes();
								$ia=$ia?$ia:array();
								foreach($ia as $j) {
									if($j->name=="t-arg") {
										$ic=$i->children();
										$ic=$ic?$ic:array();
										$arg[$j->value]=$this->xml_element("t","",$ic,$dic);
									}
								}
							}
							$tmp.=$this->xml_node($i,$dic);
						}
						if($p=$tv["prefix"]) {
							$dic=lib_suffix($p,$dic);
						}
						$dic=array_merge($dic,$arg);
						$dic[0]=$tmp;
						$r.=$this->render($e,array_merge($dic,$arg));
					} elseif($e=$tv["inc"]) {
						$f=fopen($e,"r");
						while(!feof($f))
							$r.=fread($f,8192);
						fclose($f);
					# Forms attributes
					} elseif($e=$tv["type"]) {
						$form=$dic[$tv["form"]] or $form=$dic["form"];
						$name=$tv["name"];
						$class=$form->error_get($name) ? "form_error" : "form_valid";
						if($e=="text" or $e=="password") {
							$value=htmlentities($form->display_get($name));
							$att.=" type=\"$e\" name=\"$name\" value=\"$value\" class=\"$class\"";
							$r.=$this->xml_element($nn,$att,$nc,$dic);
						} elseif($e=="textarea") {
							$value=htmlentities($form->display_get($name));
							$att.=" name=\"$name\" class=\"$class\"";
							$r.="<$nn$att>$value</$nn>";
						} elseif($e=="checkbox" or $e=="radio") {
							$value=$tv["value"];
							$checked="";
							if($value==$form->display_get($name))
								$checked=" checked=\"checked\"";
							$att.=" type=\"$e\" name=\"$name\" value=\"$value\" class=\"$class\"$checked";
							$r.=$this->xml_element($nn,$att,$nc,$dic);
						}
					} elseif($e=$tv["select"]) {
						$name=$e;
						$form=$dic[$tv["form"]] or $form=$dic["form"];
						$value=$tv["value"];
						$selected="";
						if($value==$form->display_get($name))
							$selected=" selected=\"selected\"";
						$att.=" value=\"$value\"$selected";
						$r.=$this->xml_element($nn,$att,$nc,$dic);
					} elseif($e=$tv["name"]) {
						$att.=" name=\"$e\"";
						$r.=$this->xml_element($nn,$att,$nc,$dic);
					} elseif($e=$tv["error"]) {
						$form=$tv["form"] ? $dic[$tv["form"]] : $dic["form"];
						if($form->error_get($e))
							$r.=$this->xml_element($nn,$att,$nc,$dic);
					} elseif($e=$tv["invalid"]) {
						$invalid=0;
						if($form=$dic[$e] and $form->error_any())
							$r.=$this->xml_element($nn,$att,$nc,$dic);
					}
				} else {
					$r.=$this->xml_element($nn,$att,$nc,$dic,$trim);
				}
			}
			return $r;
		}
		function render($name,$dic=array()) {
			return $this->xml_node($this->xml_template($name),$dic);
		}
	}
	function qweb_xml_render($name,$dic=array()) {
		global $qweb_x;
		return $qweb_x->render($name,$dic);
	}
	function qweb_xml_enum($l) {
		if($s=sizeof($l)) {
			$l[0]['enum_first']=1;
			$l[$s-1]['enum_last']=1;
			$l[$s-1]['enum_lastonly']=($s!=1);
			for($i=0;$i<$s;$i++) {
				$l[$i]['enum']=$i;
				$l[$i]['enum_size']=$s;
				$l[$i]['enum_middle']=(($i!=0)and($i!=$s-1));
			}
			$l[(int)(($s-1)/2)]['enum_half']=1;
		}
		return $l;
	}
	function qweb_xml_pager($num,$step,$cur=0,$max=5) {
		$a=array();
		$a["pager_tot_val"]=$num;
		$a["pager_tot_page"]=$tot_page=(int)ceil($num/$step);
		$a["pager_cur_val"]=$cur;
		$a["pager_cur_val1"]=$num?$cur+1:0;
		$a["pager_cur_page"]=$cur_page=(int)floor($cur/$step);
		$a["pager_cur_page1"]=$cur_page+1;
		$a["pager_cur_end"]=max(0,min($cur+$step-1,$num-1));
		$a["pager_cur_end1"]=min($cur+$step,$num);
		if($cur_page==0) {
			$a["pager_prev"]=0;
		} else {
			$a["pager_prev"]=1;
			$a["pager_prev_page"]=$cur_page-1;
			$a["pager_prev_val"]=($cur_page-1)*$step;
		}
		if($tot_page<=$cur_page+1) {
			$a["pager_next"]=0;
		} else {
			$a["pager_next"]=1;
			$a["pager_next_page"]=$cur_page+1;
			$a["pager_next_val"]=($cur_page+1)*$step;
		}
		$l=array();
		$begin=$cur_page-$max;
		$end=$cur_page+$max;
		if($begin<0)
			$end-=$begin;
		if($end>$tot_page)
			$begin-=($end-$tot_page);
		for($i=max(0,$begin); $i<min($end,$tot_page); $i++) {
			$b=array();
			$b["pager_page"]=$i;
			$b["pager_page1"]=$i+1;
			$b["pager_val"]=$i*$step;
			$b["pager_sel"]=($cur_page==$i);
			$b["pager_sep"]=($tot_page!=$i+1);
			$l[]=$b;
		}
		$a["pager_active"]=sizeof($l)>1;
		$a["pager_list"]=$l;
		return $a;
	}
	function qweb_url_init($base,$arg) {
		global $qweb_u;
		$qweb_u=new qweb_url($base,$arg);
	}
	function qweb_xml_init($xml) {
		global $qweb_x;
		$qweb_x=new qweb_xml($xml);
	}

	class qweb_control {
		function control($start,&$argo) {
			$arg=array();
			for($i=0;$i<count($argo);$i++) {
				$s=&$argo[$i];
				array_push($arg,&$s);
			}
			$done=array();
			$todo=null;
			while(1) {
				if(!is_array($todo)) {
					$tmp="";
					$todo=array();
					foreach(explode("_",$start) as $i) {
						$tmp.="${i}_";
						if(!array_key_exists(substr($tmp,0,-1),$done))
							$todo[]=substr($tmp,0,-1);
					}
				} elseif (count($todo)) {
					$i=array_shift($todo);
					$done[$i]=1;
					if(method_exists($this,$i)) {
						$a=call_user_func_array(array(&$this,$i),$arg);
						if(is_string($a)) {
							$todo=null;
							$start=$a;
						}
					}
				} else {
					break;
				}
			}
		}
	}

?>
