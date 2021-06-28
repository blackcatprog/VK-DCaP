import sys
from args_parse import *
from logs import *

try:
	if __name__ == "__main__":
		main()
except KeyboardInterrupt:
	warn("Выход!")
	sys.exit(1)