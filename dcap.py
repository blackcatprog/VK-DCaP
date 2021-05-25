import sys
from download_post import download_post
from download_chat import download_chat

def graphic():
	print("VK-DCaP v1.0.0.1")
	print("Copyright (C) 2021 blackcat")
	print("author on github: github.com/blackcatprog")
	print("vk-dcap repository: github.com/VK-DCaP\n")

if __name__ == "__main__":
	if len(sys.argv) <= 1:
		graphic()
	if len(sys.argv) > 1:
		if sys.argv[1] == "-cd":
			download_chat(sys.argv[2], int(sys.argv[3]))
		elif sys.argv[1] == "-pd":
			download_post(sys.argv[2], sys.argv[3])