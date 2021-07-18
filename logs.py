try:
	from colorama import *
	import time
except ModuleNotFoundError:
	error("Отсутствует(ют) необходимый(е) модуль(и)")
	sys.exit(1)

def info(text):
	print(f"{Style.BRIGHT}{time.strftime('%H:%M:%S')} - [INFO] - {text}{Style.RESET_ALL}")

def succes(text):
	print(f"{Style.BRIGHT}{time.strftime('%H:%M:%S')} - {Fore.GREEN}[SUCCES]{Fore.RESET} - {text}{Style.RESET_ALL}")

def warn(text):
	print(f"{Style.BRIGHT}{time.strftime('%H:%M:%S')} - {Fore.YELLOW}[WARNING]{Fore.RESET} - {text}{Style.RESET_ALL}")

def error(text):
	print(f"{Style.BRIGHT}{time.strftime('%H:%M:%S')} - {Fore.RED}[ERROR]{Fore.RESET} - {text}{Style.RESET_ALL}")