/*
    IE7, version 0.9 (alpha) (2005-08-19)
    Copyright: 2004-2005, Dean Edwards (http://dean.edwards.name/)
    License: http://creativecommons.org/licenses/LGPL/2.1/
*/
// modelled after: http://www.mozilla.org/xmlextras/

function XMLHttpRequest() {
    // IE6 has a better version
    var $LIB = /MSIE 5/.test(navigator.userAgent) ? "Microsoft" : "Msxml2";
    return new ActiveXObject($LIB + ".XMLHTTP");
};

function DOMParser() {/* empty constructor */};
DOMParser.prototype = {
    toString: function() {return "[object DOMParser]"},
    parseFromString: function($str, $contentType) {
        var $xmlDocument = new ActiveXObject("Microsoft.XMLDOM");
        $xmlDocument.loadXML($str);
        return $xmlDocument;
    },
    // not supported
    parseFromStream: new Function,
    baseURI: ""
};

function XMLSerializer() {/* empty constructor */};
XMLSerializer.prototype = {
    toString: function() {return "[object XMLSerializer]"},
    serializeToString: function($root) {
        return $root.xml || $root.outerHTML;
    },
    // not supported
    serializeToStream: new Function
};

