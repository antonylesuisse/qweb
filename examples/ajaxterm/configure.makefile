build:
	true

install:
	install -d "%(bin)s"
	install -d "%(lib)s"
	install ajaxterm.bin "%(bin)s/ajaxterm"
	install ajaxterm.css ajaxterm.html ajaxterm.js ajaxterm.py sarissa.js sarissa_dhtml.js "%(lib)s"
	install ajaxterm.initd "/etc/init.d/ajaxterm"

clean:
	rm ajaxterm.bin
	rm ajaxterm.initd
	rm Makefile

