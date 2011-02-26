/*
=================================================================
Woosta's JIF library
(Javascript Interaction Framework)
(c) 2006 Rick Measham (aka Woosta)

Released under the GPL and Perl Artistic Licence
http://perldoc.perl.org/index-licence.html

Latest version of this library lives at
  http://rick.measham.id.au/javascript/jif.js
=================================================================
*/


// For state change information in the status bar
var ReadyState = ['Uninitialised', 'Loading', 'Loaded', 'Interactive', 'Completed'];

// Constants look nicer than strings
var GET  = 'GET';
var POST = 'POST';

// Utility function to get a cross-browser object
function getHTTPObject() {
	var xmlhttp;
	/*@cc_on
	@if (@_jscript_version >= 5)
		try {
			xmlhttp = new ActiveXObject('Msxml2.XMLHTTP');
		} catch (e) {
			try {
				xmlhttp = new ActiveXObject('Microsoft.XMLHTTP');
			} catch (E) {
				xmlhttp = false;
			}
		}
	@else
		xmlhttp = false;
	@end @*/
	if (!xmlhttp && typeof XMLHttpRequest != 'undefined') {
		try {
			xmlhttp = new XMLHttpRequest();
		} catch (e) {
			xmlhttp = false;
		}
	}
	return xmlhttp;
}

/* ================================================================= */
/* jifPost( URL, parameters, successFunction, errorFunction)         */
/* ----------------------------------------------------------------- */
/* Sends a POST request to the given URL with the specified          */
/* parameters. On success the successFunction will be run. If there  */
/* is an error, the errorFunction will be run.                       */
/* ----------------------------------------------------------------- */
/* NOTE on parameters:                                               */
/* parameters can either be given in a flat string style, or an a JS */
/* object. If you supply an object, the parameters will be turned    */
/* into a query string. If you want to use XML rather than a query   */
/* string, use the obj2xml function first:                           */
/* jifPost( URL, obj2xml(yourObj), successFunction, errorFunction )  */
/* ================================================================= */

function jifPost(postURL, plist, fn, errFn) {
	var http = getHTTPObject();

	if (typeof(plist) == 'object')
		plist = obj2query( plist );

	http.open(POST, postURL, true);
	http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	http.setRequestHeader("Content-length", plist.length);
	http.setRequestHeader("Connection", "close");

	http.onreadystatechange = function () {
		window.status = ReadyState[http.readyState] || http.readyState;
		if (http.readyState == 4) {
			if (http.status == 200) {
				fn(http);
			} else {
				if (errFn) {
					errFn(http)
				} else {
					alert("There was a problem loading the file '" + postURL + "':\n" + http.statusText);
				}
			}
		} else {
		}
	}

	http.send(plist);
	return 1;
}

/* ================================================================= */
/* jifGet( URL, parameters, successFunction, errorFunction)          */
/* ----------------------------------------------------------------- */
/* Sends a GET request to the given URL with the specified           */
/* parameters. On success the successFunction will be run. If there  */
/* is an error, the errorFunction will be run.                       */
/* See NOTE on parameters above                                      */
/* ================================================================= */

function jifGet(getURL, plist, fn, errFn) {
	var http = getHTTPObject();

	if (typeof(plist) == 'object')
		plist = obj2query( plist );

	if (plist)
		getURL += ((getURL.indexOf('?') == -1) ? '?' : '&') + plist

	http.open(GET, getURL, true);
	http.onreadystatechange = function () {
		window.status = ReadyState[http.readyState] || http.readyState;
		if (http.readyState == 4) {
			if (http.status == 200) {
//				alert(http.responseText);
				fn(http);
			} else {
				if (errFn) {
					errFn(http)
				} else {
					alert("There was a problem loading the file '" + getURL + "':\n" + http.statusText);
				}
			}
		} else {
		}
	}
	http.send(null);
	return 1;
}

/* ================================================================= */
/* jifReq( Method, URL, parameters, successFunction, errorFunction)  */
/* ----------------------------------------------------------------- */
/* Sends a request to the given URL using the specified method (GET  */
/* or POST) with the specified parameters.                           */
/* ================================================================= */
function jifReq(meth, getURL, plist, fn, errFn) {
	return (meth == POST)
		? jifPost(getURL, plist, fn, errFn)
		: jifGet(getURL, plist, fn, errFn)
}

/* ==================================================================== */
/* jif___JSON( Method, URL, parameters, successFunction, errorFunction) */
/* -------------------------------------------------------------------- */
/* wrappers around jif* that assumes the result to be JSON.             */
/* ==================================================================== */
function jifGetJSON(getURL, plist, fn, errFn){
	jifGet(getURL, plist, function(_){ try { o=parseJSON(_.responseText); fn(o) } catch (e) {  alert('Error converting server response to Javascript: '+e)} } , errFn);
}
function jifPostJSON(getURL, plist, fn, errFn){
	jifPost(getURL, plist, function(_){ try { o=parseJSON(_.responseText); fn(o) } catch (e) {  alert('Error converting server response to Javascript: '+e)} } , errFn);
}
function jifReqJSON(meth, getURL, plist, fn, errFn){
	jifReq(meth, getURL, plist, function(_){ try { o=parseJSON(_.responseText); fn(o) } catch (e) {  alert('Error converting server response to Javascript: '+e)} } , errFn);
}


/* ================================================================= */
/* obj2xml( javascriptObject )                                       */
/* ----------------------------------------------------------------- */
/* This utility function turns a javascript object into tagged xml   */
/* (ie, all tags, no attributes)                                     */
/* ================================================================= */
function obj2xml(obj, basename) {
	if(!basename) basename = 'opt';
	var RV = '<'+basename+'>';
	for(var X in obj) {
		//alert(obj[X].constructor);
		if (typeof(obj[X]) == 'object' && obj[X].constructor == Array) {
			for (n in obj[X])
				RV += '<' + X + '>' + encodeURI( obj[X][n] ) + '</' + X + '>';
		} else if (typeof(obj[X]) == 'object') {
			RV += obj2xml(obj[X], X);
		} else {
			RV += '<' + X + '>' + encodeURI( obj[X] ) + '</' + X + '>';
		}
	}
	RV += '</' + basename + '>';
	return RV
}

/* ================================================================= */
/* obj2query( javascriptObject )                                     */
/* ----------------------------------------------------------------- */
/* This utility function turns a javascript object into a useful     */
/* query string for sending via jif requests above                   */
/* ================================================================= */
function obj2query(obj) {
	var RV = '';
	for(var X in obj) {
		if (typeof(obj[X]) == 'object' && obj[X].constructor == Array) {
			for (n in obj[X])
				RV += '&' + X + '=' + encodeURI( obj[X][n] );
		} else if (typeof(obj[X]) == 'object') {
			RV += '&' + X + '=' + escape( obj2query(obj[X]) );
		} else {
			RV += '&' + X + '=' + escape( obj[X] );
		}
	}
	return RV.replace(/^&/,'');
}


/* ================================================================= */
/* form2obj( formIDorEntity )                                        */
/* ----------------------------------------------------------------- */
/* This utility function turns aDOM form into an object useful with  */
/* any of the above two functions                                    */
/* EXAMPLE:

	<form action="http://www.example.com/" method="POST" onsubmit="return !jifReq(this.method, this.action, obj2query( form2obj( this ) ), function(){ alert( http.responseText ) }">
		<input type="text" name="first">
		<input type="text" name="last">
		<input type="password" name="password">
		<input type="submit">
	</form>

	This example will attempt to submit the form via jif, but if it
	doesn't work, it will submit it via a regular submit. Of course,
	if that's not what you want, then do it another way :)

/* ================================================================= */
function form2obj(theForm) {
	var RV = new FormObject();
	if (typeof(theForm) == 'string')
		theForm = document.getElementById(theForm);
	if (theForm) {
		for (var X = 0; X < theForm.elements.length; X++) {
			var El = theForm.elements[X];
			if (El.name) {
				if ((El.tagName == 'INPUT' && El.type.match(/^text|hidden|password$/i)) || El.tagName == 'TEXTAREA' || (El.type.match(/^checkbox|radio$/i) && El.checked))
					RV.smartPush( El.name, El.value )
				else if (El.tagName == 'SELECT')
					RV.smartPush( El.name, El.options[El.selectedIndex].value )
			}
		}
	}
	return RV.object;
}

// Utility object so we have a smart push
function FormObject() { this.object = new Object() }
FormObject.prototype.smartPush = function( n, v ) {
	if (this.object[n]) {
		if (typeof(this[n]) == 'object')
			this.object[n].push( v )
		else
			this.object[n] = new Array( this.object[n], v );
	} else {
		this.object[n] = v
	}
}

// These two functions taken from json.js from http://www.json.org/

function parseJSON (theSource) {
    try {
        return eval('X=(' + theSource + ')');
    } catch (e) {
        throw(e); // yeah yeah. why bother catching it in the first place?
    }
};

(function () {
    var m = {
            '\b': '\\b',
            '\t': '\\t',
            '\n': '\\n',
            '\f': '\\f',
            '\r': '\\r',
            '"' : '\\"',
            '\\': '\\\\'
        },
        s = {
            array: function (x) {
                var a = ['['], b, f, i, l = x.length, v;
                for (i = 0; i < l; i += 1) {
                    v = x[i];
                    f = s[typeof v];
                    if (f) {
                        v = f(v);
                        if (typeof v == 'string') {
                            if (b) {
                                a[a.length] = ',';
                            }
                            a[a.length] = v;
                            b = true;
                        }
                    }
                }
                a[a.length] = ']';
                return a.join('');
            },
            'boolean': function (x) {
                return String(x);
            },
            'null': function (x) {
                return "null";
            },
            number: function (x) {
                return isFinite(x) ? String(x) : 'null';
            },
            object: function (x) {
                if (x) {
                    if (x instanceof Array) {
                        return s.array(x);
                    }
                    var a = ['{'], b, f, i, v;
                    for (i in x) {
                        v = x[i];
                        f = s[typeof v];
                        if (f) {
                            v = f(v);
                            if (typeof v == 'string') {
                                if (b) {
                                    a[a.length] = ',';
                                }
                                a.push(s.string(i), ':', v);
                                b = true;
                            }
                        }
                    }
                    a[a.length] = '}';
                    return a.join('');
                }
                return 'null';
            },
            string: function (x) {
                if (/["\\\x00-\x1f]/.test(x)) {
                    x = x.replace(/([\x00-\x1f\\"])/g, function(a, b) {
                        var c = m[b];
                        if (c) {
                            return c;
                        }
                        c = b.charCodeAt();
                        return '\\u00' +
                            Math.floor(c / 16).toString(16) +
                            (c % 16).toString(16);
                    });
                }
                return '"' + x + '"';
            }
        };

    Object.prototype.toJSONString = function () {
        return s.object(this);
    };

    Array.prototype.toJSONString = function () {
        return s.array(this);
    };
})();


