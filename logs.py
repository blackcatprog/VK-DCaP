try:
	from colorama import *
	import time
	import ctypes
	from sys import platform
	import os
except ModuleNotFoundError:
	error("Отсутствует(ют) необходимый(е) модуль(и)")
	sys.exit(1)

# support colors
os.system("")

def info(text):
	print(f"{Style.BRIGHT}{time.strftime('%H:%M:%S')} - [INFO] - {text}{Style.RESET_ALL}")

def success(text):
	print(f"{Style.BRIGHT}{time.strftime('%H:%M:%S')} - {Fore.GREEN}[SUCCESS]{Fore.RESET} - {text}{Style.RESET_ALL}")

def warn(text):
	print(f"{Style.BRIGHT}{time.strftime('%H:%M:%S')} - {Fore.YELLOW}[WARNING]{Fore.RESET} - {text}{Style.RESET_ALL}")

def error(text):
	print(f"{Style.BRIGHT}{time.strftime('%H:%M:%S')} - {Fore.RED}[ERROR]{Fore.RESET} - {text}{Style.RESET_ALL}")