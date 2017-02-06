#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
import subprocess


__title__ = "slimerjs"
__version__ = "0.10.2"
__credits__ = [
    "Coder Alpha"
]

def einthusan(python_dir, firefox_dir, url, debug=False):
	output = ""
	try:
		SLIMERJS_PATH = os.path.dirname(os.path.abspath(__file__))
		
		if python_dir == None:
			python_dir = ""
		
		if firefox_dir == None or firefox_dir == "":
			firefox_dir = ""
		else:
			if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
				os.environ["SLIMERJSLAUNCHER"] = firefox_dir
			elif sys.platform == "win32":
				os.environ["SLIMERJSLAUNCHER"] = os.path.join(firefox_dir, 'firefox.exe')
			else:
				os.environ["SLIMERJSLAUNCHER"] = firefox_dir

		if debug:
			if sys.platform == "win32":
				file_cmd = [os.path.join(SLIMERJS_PATH, 'slimerjs.bat'), os.path.join(SLIMERJS_PATH, 'einthusan.js'), url, '-debug true']
			elif sys.platform == "darwin":
				file_cmd = [os.path.join(SLIMERJS_PATH, 'slimerjs'), os.path.join(SLIMERJS_PATH, 'einthusan.js'), url]
			else:
				file_cmd = ['xvfb-run', python_dir, os.path.join(SLIMERJS_PATH, 'slimerjs.py'), os.path.join(SLIMERJS_PATH, 'einthusan.js'), url, '--debug=true']
		else:
			if sys.platform == "win32":
				file_cmd = [os.path.join(SLIMERJS_PATH, 'slimerjs.bat'), os.path.join(SLIMERJS_PATH, 'einthusan.js'), url]
			elif sys.platform == "darwin":
				file_cmd = [os.path.join(SLIMERJS_PATH, 'slimerjs'), os.path.join(SLIMERJS_PATH, 'einthusan.js'), url]
			else:
				file_cmd = ['xvfb-run', python_dir, os.path.join(SLIMERJS_PATH, 'slimerjs.py'), os.path.join(SLIMERJS_PATH, 'einthusan.js'), url]


		output = ""
		if sys.platform == "darwin":
			print file_cmd
			process = subprocess.Popen(file_cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
			output = process.stdout.read()
		else:
			print file_cmd
			process = subprocess.Popen(file_cmd, shell=False, cwd=SLIMERJS_PATH, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			ret = process.wait()
			print('Process returned code {0}'.format(ret))
			output = process.stdout.read()

		return str(output)
	except Exception as err:
		return "error-fail - code execution error - " + str(err) + " " + str(output) + " " + str(file_cmd)

def test():
	print einthusan("/Applications/Firefox.app/Contents/MacOS/firefox","https://einthusan.tv/movie/watch/7757/?lang=hindi", debug=True)
	
#test()