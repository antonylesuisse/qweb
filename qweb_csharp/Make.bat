@echo off
cd D:\agr\inetpub\wwwroot\bin\
D:
IF "%1" == "D:\agr\inetpub\wwwroot\bin\qweb.cs" GOTO QWEB
IF "%1" == "D:\agr\inetpub\wwwroot\bin\Amigrave.cs" GOTO AGR
IF "%1" == "D:\agr\inetpub\wwwroot\bin\Siemens.cs" GOTO SIEMENS
GOTO END 

:QWEB
csc /target:library /out:Almacom.QWeb.dll qweb.cs
goto PAUSE

:AGR
csc /target:library /r:Almacom.QWeb.dll /out:Amigrave.dll Amigrave.cs
goto PAUSE

:SIEMENS
csc /target:library /r:Almacom.QWeb.dll /r:Amigrave.dll /out:Siemens.dll Siemens.cs
goto PAUSE

:PAUSE
pause

:END