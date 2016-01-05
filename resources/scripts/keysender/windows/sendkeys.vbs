Dim action
windowName = WScript.Arguments.Item(0)
key = WScript.Arguments.Item(1)

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
elseif key="maximize" then
	cmd = "% x"
end if

if shell.AppActivate(windowName) = true then
	shell.SendKeys cmd
end if
