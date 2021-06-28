from colorama import *
import time

def info(text):
	print(f"{Style.BRIGHT}{time.strftime('%H:%M:%S')} - [INFO] - {text}")

def succes(text):
	print(f"{Style.BRIGHT}{time.strftime('%H:%M:%S')} - {Fore.GREEN}[SUCCES]{Fore.RESET} - {text}")

def warn(text):
	print(f"{Style.BRIGHT}{time.strftime('%H:%M:%S')} - {Fore.YELLOW}[WARNING]{Fore.RESET} - {text}")

def error(text):
	print(f"{Style.BRIGHT}{time.strftime('%H:%M:%S')} - {Fore.RED}[ERROR]{Fore.RESET} - {text}")