#!/bin/python3

import os
from datetime import datetime
import time
import pytz
from pwd import getpwuid
import grp
import argparse



##
##	HELPER
##

#
#Parse arguments from CLI
#
def parseargs():
	global args
	parser = argparse.ArgumentParser()
	parser.add_argument("-l", "--long", help="increases output information", action="store_true")
	parser.add_argument("-a", "--all", help="displays all files inside the directory", action="store_true")
	parser.add_argument("path", nargs="*", help="path/s to be traversed")
	args = parser.parse_args()


#
#prints text Bold
#
def printbold(text):
	boldstart = '\033[1m'
	boldend =  '\033[0m'
	print(f"{boldstart}{text}:{boldend}")


#
#print out proper file access string from octal
#
def octaltostring(oct):
	ownership = str()
	for digit in str(oct):
		if digit == "7":
			ownership += "rwx"
		elif digit == "6":
			ownership += "rw-"
		elif digit == "5":
			ownership += "r-x"
		elif digit == "4":
			ownership += "r--"
		elif digit == "3":
			ownership += "-wx"
		elif digit == "2":
			ownership += "-w-"
		elif digit == "1":
			ownership += "--x"
		elif digit == "0":
			ownership += "---"
	return ownership


#files
#
#format unix timestamp to proper date string
#
def datestring(unix):
	#check if unix timestamp is older than 6 months
	delta = time.time() - 15780000
	if unix < delta:
		return pytz.timezone("UTC").localize(datetime.fromtimestamp(unix)).astimezone(pytz.timezone("UTC")).strftime('%b  %e  %Y')		#-d 
	return pytz.timezone("UTC").localize(datetime.fromtimestamp(unix)).astimezone(pytz.timezone("UTC")).strftime('%b  %e %H:%M')		#-d 
	return moddate

#
#check if file is dir or file, if file return -, else return d
#
def dircheck(file):
	if os.path.isfile(file):
		return "-"
	elif os.path.islink(file):
		return "l"
	else:
		return "d"


#
#reads out owner and group from file
#
def getownerandgroup(file):
	owner = getpwuid(os.stat(file).st_uid).pw_name
	group = grp.getgrgid(os.stat(".").st_gid)[0]
	return owner + " " + group


#
#prints verbose information about file
#
def printverbose(file, path):
	filepath = os.path.join(path, file)
	mask = oct(os.stat(os.path.join(path, file)).st_mode)[-3:]
	if " " in file:
		filename = "'" + file + "'"
		print(f"{dircheck(filepath)}{octaltostring(mask):12}{os.stat(filepath).st_nlink:2} {getownerandgroup(filepath):17} {os.path.getsize(filepath):8} {datestring(os.path.getmtime(filepath)):15} {filename:20}")
	else:
		print(f"{dircheck(filepath)}{octaltostring(mask):12}{os.stat(filepath).st_nlink:2} {getownerandgroup(filepath):17} {os.path.getsize(filepath):8} {datestring(os.path.getmtime(filepath)):15} {file:20}")


#
#calculate blocksize for files in directory
#
def calcblocks(files, path="."):
	size = 0
	for file in files:
		try:
			size += os.lstat(os.path.join(path, file)).st_blocks * 0.5
		except Exception as e:
			print(f"\033[91m{path} may not be valid. {e}\033[0m")
	#add blocksize for default dirs if flag is set
	if args.all:
		try:
			size += os.stat('.').st_blocks * 0.5
			size += os.stat('..').st_blocks * 0.5
		except Exception as e:
			print(f"\033[91m . / .. may not be valid. {e}\033[0m")

	return size


#
#print parent and current dirs
#
def printdefaultdirs():
	if args.all:
		print(f"{dircheck('.')}{octaltostring(oct(os.stat('.').st_mode)[-3:]):12}{os.stat('.').st_nlink:2} {getownerandgroup('.'):17} {os.path.getsize('.'):8} {datestring(os.path.getmtime('.')):15} {'.':20}")
		print(f"{dircheck('..')}{octaltostring(oct(os.stat('..').st_mode)[-3:]):12}{os.stat('..').st_nlink:2} {getownerandgroup('..'):17} {os.path.getsize('..'):8} {datestring(os.path.getmtime('..')):15} {'..':20}")


##
##	ACTUAL LS Logic
##

#
#print elements in path SHORT
#
def printelementsshort():
	#no path has been specified, use current dir
	if len(args.path) == 0:
		filestring = str()
		files = os.listdir()
		files = sorted(files, key=str.casefold)
		if args.all:
			filestring+= ". .. "
		for file in files:
			#print all dirs
			if args.all:
				if " " in file:
					filestring += "'" + file + "' "
				else:
					filestring += file + " "
			#only print visible dirs
			else:
				if not file.startswith("."):
					if " " in file:
						filestring += "'" + file + "' "
					else:
						filestring += file + " "
		print(filestring)
        #path has been specified, iterate through all of them and print content
	else:
		for path in args.path:
			filestring = str()
			try:
				printbold(path)
				files = os.listdir(path)
				files = sorted(files, key=str.casefold)
				if args.all:
					filestring+= ". .. "
				for file in files:
					#print all dirs
					if args.all:
						if " " in file:
							filestring += "'" + file + "' "
						else:
							filestring += file + " "
					#only print visible dirs
					else:
						if not file.startswith("."):
							if " " in file:
								filestring += "'" + file + "' "
							else:
								filestring += file + " "
			except Exception as e:
				print(f"\033[91m{path} may not be valid. {e}\033[0m")
			print(filestring)
			if not args.path[-1] == path:
				print()


#
#print elements in path with more details
#
def printelementslong():
	#single path given 
	if len(args.path) == 0:
		files = os.listdir()
		print(f"total: {calcblocks(files)}")
		files = os.listdir()
		files = sorted(files, key=str.casefold)
		#add . and .. dirs
		if args.all:
			printdefaultdirs()
		for file in files:
					try:
						#print all dirs
						if args.all:
							printverbose(file, os.getcwd())
						#print only visible dirs
						else:
							if not file.startswith("."):
								printverbose(file, os.getcwd())
					except Exception as e:
						print(f"\033[91m{path}{file} may not be valid. {e} \033[0m")
	else:
		# multiple paths given
		for path in args.path:
			printbold(path)
			files = os.listdir(path)
			files = sorted(files, key=str.casefold)
			print(f"total: {calcblocks(files, path)}")
			#add . and .. dirs
			if args.all:
				printdefaultdirs()
			for file in files:
				try:
					#print all dirs
						if args.all:
							printverbose(file, path)
						#print only visible dirs
						else:
							if not file.startswith("."):
								printverbose(file, path)
				except Exception as e:
					print(f"\033[91m{path}{file} may not be valid. {e} \033[0m")
			if not args.path[-1] == path:
				print()
		


#
#run ls using python functions
#
def ls():
	#get args from console
	parseargs()
	#no l function args have been used
	if not args.long:
		printelementsshort()
	#l function args have been used
	else:
		if args.long:
			printelementslong()


if __name__ == "__main__":
	ls()