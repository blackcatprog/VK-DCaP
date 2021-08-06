try:
	import sys
	from args_parse import *
	from logs import *
except ModuleNotFoundError:
	error("Отсутствует(ют) необходимый(е) модуль(и)")
	sys.exit(1)
	
try:
	if __name__ == "__main__":
		main()
except KeyboardInterrupt:
	warn("Выход!")
	sys.exit(1)