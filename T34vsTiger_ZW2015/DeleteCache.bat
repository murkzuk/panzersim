
::
:: Deletes All files in the Current Directory
::    With Prompts and Warnings
::
::  (Hidden, System, and Read-Only Files are Not Affected)
::
@ECHO OFF

ECHO Y | DEL Cache *.cache                           `.' Represents the Current Directory.
DIR
