Dim action
key = WScript.Arguments.Item(0)

set shell = CreateObject("WScript.Shell")

dim cmd
if key="close" then
	cmd = "%{F4}"
elseif key="pause" then
	cmd = " "
elseif key="backward" then
	cmd = "{LEFT} "
elseif key="down" then
	cmd = "{LEFT}{LEFT} "
elseif key="forward" then
	cmd = "{RIGHT} "
elseif key="up" then
	cmd = "{RIGHT}{RIGHT} "
end if

Wscript.Echo cmd
if shell.AppActivate("Google Chrome") = true then
	shell.SendKeys cmd
end if
