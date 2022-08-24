try:
	try:
		import sys
		import logs
		from args_parse import *
	except ModuleNotFoundError:
		logs.error("Отсутствует(ют) необходимый(е) модуль(и)!")
		sys.exit(1)
		
	if __name__ == "__main__":
		main()
except KeyboardInterrupt:
	logs.warn("Выход!")
	sys.exit(1)