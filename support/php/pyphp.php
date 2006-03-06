<?
	#---------------------------------------------------------
	# pyphp, PHP handler
	#---------------------------------------------------------
	#echo "<xmp>";
	function pyphp_init($wsgiapp) {
		if(strlen($wsgiapp)) {
			$wsgifile=$_SERVER["SCRIPT_FILENAME"];
			$sockseed=$_SERVER["SCRIPT_FILENAME"];
		} else {
			$wsgifile="";
			$sockseed=__FILE__;
		}
		$sock="/tmp/pyphp_".substr(md5($sockseed),0,8).".sock";
		$errno=0;
		$errstr="";
		if(!$fs=fsockopen($sock,0,$errno,$errstr)) {
			$pyfile=substr(__FILE__,0,-3)."py";
			$err=0;
			$pyexe="/usr/bin/python";
			$cmdline="$pyexe '$pyfile' '$sock' '$wsgifile' '$wsgiapp'";
#			echo "$cmdline $err $errno $errstr<br>";
			system($cmdline,$err);
			if($err!=0)
				die("php: could not launch server.\n");
			if(!$fs=fsockopen($sock,0))
				die("php: could not connect.\n");
		} 
		socket_set_timeout($fs,20);
		return $fs;
	}
	$pyphp_res=array();
	class PHPResource {
		var $id;
		function PHPResource($res) {
			global $pyphp_res;
			$pyphp_res[]=$res;
			$this->id=sizeof($pyphp_res)-1;
		}
	}
	function pyphp_session_add($key,$val) {
#		$_SESSION[$key]=$val;
# php 4.1 workaround
		$GLOBALS[$key]=$val;
		session_register($key);
	}
	function pyphp_eval($str) {
		return eval($str);
	}
	function pyphp_request() {
		$var=array();
		$var["_SERVER"]=$_SERVER;
		$var["_ENV"]=$_ENV;
		$var["_GET"]=$_GET;
		$var["_POST"]=$_POST;
		$var["_COOKIE"]=$_COOKIE;
		$var["_REQUEST"]=$_REQUEST;
		$var["_FILES"]=$_FILES;
		$var["_SESSION"]=$_SESSION;
		return $var;
	}
	function pyphp_loop($fs) {
		global $pyphp_res;
		while(1) {
			$buf=fread($fs,5);
			if(strlen($buf)==5) {
				$cmd=substr($buf,0,1);
				$size=array_shift(unpack("l",substr($buf,1,4)));
#				echo "php: command $cmd size $size<br>\n";
				if($cmd=="C") {
					$buf="";
					while(strlen($buf)<$size) {
						$tmp=fread($fs,$size-strlen($buf));
						if(strlen($tmp)==0)
							die("php: C underflow.");
						$buf.=$tmp;
					}
					$a=explode("\x00",$buf,2);
					$f=$a[0];
					$in=$a[1];
					$p=unserialize($in);
#					echo "php: call $f ".str_replace("\n"," ",var_export($p,true))."\n";
					for($i=0;$i<sizeof($p);$i++) {
						if(get_class($p[$i])=="phpresource")
							$p[$i]=$pyphp_res[$p[$i]->id];
					}
					$r=call_user_func_array($f,$p);
					if(is_resource($r))
						$r=new PHPResource($r);
					$out=serialize($r);
#					echo "php: return ".str_replace("\n"," ",var_export($r,true))."\n";
					$msg="S".pack("l",strlen($out)).$out;
					$err=fwrite($fs,$msg);
					if($err==-1)
						die("php: C overflow.");
				} elseif($cmd=="W") {
					$recv=0;
					while($recv<$size) {
						$buf=fread($fs,$size-$recv);
						if(strlen($buf)==0)
							die("php: W underflow.");
						echo $buf;
						$recv+=strlen($buf);
					}
				} elseif($cmd=="E") {
					fclose($fs);
					exit;
				}
			} else {
				die("php: timeout. bufsize:".strlen($buf)." buf:".$buf);
			}
		}
	}
	function pyphp_run($wsgiapp="") {
		if (get_magic_quotes_gpc()) {
			$_GET=array_map('stripslashes',$_GET);
			$_POST=array_map('stripslashes',$_POST);
			$_COOKIE=array_map('stripslashes',$_COOKIE);
		}
		session_start();
		pyphp_loop(pyphp_init($wsgiapp));
	}
?>
