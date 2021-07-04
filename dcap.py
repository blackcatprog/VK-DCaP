import sys
from args_parse import *
from logs import *
from urllib.request import urlopen

#check interbet connection
try:
	url = urlopen("https://google.com")
except Exception:
	error("Нет подключения к интернету!")
	sys.exit(1)

try:
	if __name__ == "__main__":
		main()
except KeyboardInterrupt:
	warn("Выход!")
	sys.exit(1)