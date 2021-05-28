from colorama import Fore
import ctypes

#support colors
kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

error = Fore.RED + "[ОШИБКА]" + Fore.RESET + " - "
succes = Fore.GREEN + "[УСПЕШНО]" + Fore.RESET + " - "