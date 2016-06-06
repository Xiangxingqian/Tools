@echo off

rem parse xml file
java -jar apktool\apktoolV2.jar d resources %1.apk -f -o %1
rem parse code
"C:\Program Files (x86)\HaoZip"\HaoZipC e %1.apk -o%1 classes.dex *.arsc 
dex\dex2jar.bat %1\classes.dex



