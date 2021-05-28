import sys
import argparse as arg
from download_post import download_post
from download_chat import download_chat

#flags##########################################################################################################
pars = arg.ArgumentParser()
pars.add_argument("-cd", dest="cd", help="скачивание диалога")
pars.add_argument("-pd", dest="pd", help="скачивание поста")
pars.add_argument("-c", type=int, dest="count", help="количество постов/диалогов (целое число)")
pars.add_argument("-id", dest="img", help="скачивать фото вместо подставления ссылок", action="store_true")
pars.add_argument("-ad", dest="aud", help="скачивать голосовые сообщения вместо подставления ссылок", action="store_true")
pars.add_argument("-md", dest="mus", help="скачивать музыку вместо подставления ссылок", action="store_true")
pars.add_argument("-dd", dest="doc", help="скачивать документы вместо подставления ссылок", action="store_true")
args = pars.parse_args()
#################################################################################################################

#value_params
count_ = 20
id_ = 0
ad_ = 0
md_ = 0
dd_ = 0
#############

def graphic():
	print("VK-DCaP v1.0.0.4")
	print("Copyright (C) 2021 blackcat")
	print("github repository: github.com/blackcatprog/VK-DCaP\n")

if __name__ == "__main__":
	if len(sys.argv) <= 3:
		print()
	if len(sys.argv) > 1:
		if args.cd:
			if args.count:
				count_ = args.count
				id_ = args.img
				ad_ = args.aud
				md_ = args.mus
				dd_ = args.doc
			download_chat(sys.argv[2], count_, _photo=id_, _audio=ad_, _music=md_, _document=dd_)
		elif args.pd:
			if args.count:
				count_ = args.count
				id_ = args.img
				if args.aud:
					print("В постах не может быть голосовых сообщений")
				md_ = args.mus
				dd_ = args.doc
			download_post(sys.argv[2], count_, _photo=id_, _music=md_, _document=dd_)