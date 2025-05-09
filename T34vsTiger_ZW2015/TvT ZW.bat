//@ECHO OFF

//REM Deletes all files within the Cache folder in the current directory without prompting for confirmation.
//DEL /Q Cache\*.*

//REM Lists the contents of the current directory.


@ECHO OFF

REM Deletes all files within the Cache folder, *.cache, *.log, and *.html files in the current directory
ECHO Y | DEL /Q Cache\*.*
ECHO Y | DEL /Q *.cache
ECHO Y | DEL /Q *.log
ECHO Y | DEL /Q *.html

start TvsT.exe
