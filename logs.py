try:
	from colorama import *
	import time
	import ctypes
	from sys import platform
except ModuleNotFoundError:
	error("Отсутствует(ют) необходимый(е) модуль(и)")
	sys.exit(1)

#support colors
if platform[0:3].lower() == "win":
	kernel32 = ctypes.windll.kernel32
	kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

def info(text):
	print(f"{Style.BRIGHT}{time.strftime('%H:%M:%S')} - [INFO] - {text}{Style.RESET_ALL}")

def succes(text):
	print(f"{Style.BRIGHT}{time.strftime('%H:%M:%S')} - {Fore.GREEN}[SUCCES]{Fore.RESET} - {text}{Style.RESET_ALL}")

def warn(text):
	print(f"{Style.BRIGHT}{time.strftime('%H:%M:%S')} - {Fore.YELLOW}[WARNING]{Fore.RESET} - {text}{Style.RESET_ALL}")

def error(text):
	print(f"{Style.BRIGHT}{time.strftime('%H:%M:%S')} - {Fore.RED}[ERROR]{Fore.RESET} - {text}{Style.RESET_ALL}")