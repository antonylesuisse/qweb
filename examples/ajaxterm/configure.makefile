build:
	true

install:
	install -d "%(bin)s"
	install -d "%(lib)s"
	install ajaxterm.bin "%(bin)s/ajaxterm"
	install ajaxterm.css ajaxterm.html ajaxterm.js qweb.py ajaxterm.py sarissa.js sarissa_dhtml.js "%(lib)s"
	install ajaxterm.initd "%(etc)s/init.d/ajaxterm"
	gzip -c ajaxterm.1 > ajaxterm.1.gz
	install -d "%(man)s"
	install ajaxterm.1.gz "%(man)s"

clean:
	rm ajaxterm.bin
	rm ajaxterm.initd
	rm ajaxterm.1.gz
	rm Makefile

