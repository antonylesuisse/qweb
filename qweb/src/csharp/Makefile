INC=-r System.Web.dll -r System.Data.dll

all:
	make qweb
	./qweb.exe
#	make amigrave
#	make siemens
	sudo /etc/init.d/mono-xsp restart

qweb:
	mcs -target:library -out:/tmp/Almacom.QWeb.dll qweb.cs ${INC}
	mv /tmp/Almacom.QWeb.dll bin/
	mcs -target:exe -out:bin/qweb.exe qweb.cs ${INC}

amigrave:
	mcs -target:library -out:/tmp/Amigrave.dll Amigrave.cs -r System.Web.dll -r System.Data.dll -r System.Drawing.dll -r Almacom.QWeb.dll
	mv /tmp/Amigrave.dll .

siemens:
	mcs -target:library -out:/tmp/Siemens.dll Siemens.cs -r System.Web.dll -r System.Data.dll -r Almacom.QWeb.dll -r Amigrave.dll
	mv /tmp/Siemens.dll .
