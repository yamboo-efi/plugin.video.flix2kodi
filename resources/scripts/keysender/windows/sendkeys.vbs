Dim action
windowName = WScript.Arguments.Item(0)
key = WScript.Arguments.Item(1)

set shell = CreateObject("WScript.Shell")


strPath = WScript.ScriptFullName

Set objFSO = CreateObject("Scripting.FileSystemObject")

Set objFile = objFSO.GetFile(strPath)
strFolder = objFSO.GetParentFolderName(objFile)

dim cmd
dim cmd2
dim handled
cmd=""
handled = 0

shell.Run strFolder+"\winxdotool.exe ""+windowName+"" mousemove 960 540", 0, false
WScript.Sleep(200)
shell.Run strFolder+"\winxdotool.exe ""+windowName+"" click", 0, false

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
	cmd = "% "
elseif key="toggle_lang0" then
    shell.Run strFolder+"\winxdotool.exe ""+windowName+"" mousemove 1630 980", 0, false
    WScript.Sleep(200)
    shell.Run strFolder+"\winxdotool.exe ""+windowName+"" mousemove 1430 835", 0, false
    WScript.Sleep(200)
    shell.Run strFolder+"\winxdotool.exe ""+windowName+"" click", 0, false

    handled = true
elseif key="toggle_lang1" then
    shell.Run strFolder+"\winxdotool.exe ""+windowName+"" mousemove 1630 980", 0, false
    WScript.Sleep(200)
    shell.Run strFolder+"\winxdotool.exe ""+windowName+"" mousemove 1430 875", 0, false
    WScript.Sleep(200)
    shell.Run strFolder+"\winxdotool.exe ""+windowName+"" click", 0, false

    handled = 1
elseif key="toggle_sub0" then
    shell.Run strFolder+"\winxdotool.exe ""+windowName+"" mousemove 1630 980", 0, false
    WScript.Sleep(200)
    shell.Run strFolder+"\winxdotool.exe ""+windowName+"" mousemove 1630 835", 0, false
    WScript.Sleep(200)
    shell.Run strFolder+"\winxdotool.exe ""+windowName+"" click", 0, false

    handled = 1
elseif key="toggle_sub1" then
    shell.Run strFolder+"\winxdotool.exe ""+windowName+"" mousemove 1630 980", 0, false
    WScript.Sleep(200)
    shell.Run strFolder+"\winxdotool.exe ""+windowName+"" mousemove 1630 875", 0, false
    WScript.Sleep(200)
    shell.Run strFolder+"\winxdotool.exe ""+windowName+"" click", 0, false

    handled = 1
else
    Wscript.Echo "unknown key: "+key
    handled = 1
end if

if handled = 0 then
    if shell.AppActivate(windowName) = true then
        Wscript.Sleep 500
        shell.SendKeys cmd

        if cmd2 <> "" then
                Wscript.Sleep 500
                shell.SendKeys cmd2
        end if
    end if
end if
