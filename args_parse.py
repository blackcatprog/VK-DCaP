import argparse
import sys
import dcap_cfg
from dwn_dlg import dwn_dlg
from dwn_pst import dwn_pst

def main():

	def info():
		print("Синтаксис: python dcap.py [что скачивать] [параметры]")
		print("")
		print("Что скачивать:")
		print("-cd [id пользователя/беседы/группы] - переписку")
		print("-pd [id пользователя/группы] - посты")
		print("")
		print("Параметры:")
		print("-c [количество] - количество скачиваемых сообщений (по умолчанию 20)")
		print("-id - скачивать фото (по умолчанию в виде ссылок)")
		print("-ad - скачивать голосовые сообщения (по умолчанию в виде ссылок)")
		print("-md - скачивать музыку (по умолчанию в виде ссылок)")
		print("-dd - скачивать документы (по умолчанию в виде ссылок)")
		print("-f [название папки] - скачивание в папку")
		print("-af - скачать все вложения")
		print("-ul - превращать имена пользователей рядом с сообщенями в ссылки на этих пользователей")
		print("-sm - оформлять музыку")
		print("-log - логи о работе программы")
		print("-help - краткая документация (вы её сейчас и смотрите :) )")
		sys.exit(1)

	def graphic():
		print(f"VK-DCaP v{dcap_cfg.version}")
		print(f"Copyright (C) 2021 {dcap_cfg.author}")
		print("github repository: github.com/blackcatprog/VK-DCaP\n")

	pars = argparse.ArgumentParser()
	pars.add_argument("-cd", dest="chat", help="скачивание диалога")
	pars.add_argument("-pd", dest="post", help="скачивание поста")
	pars.add_argument("-c", type=int, dest="count", help="количество постов/диалогов (целое число)")
	pars.add_argument("-id", dest="img", help="скачивать фото вместо подставления ссылок", action="store_true")
	pars.add_argument("-ad", dest="aud", help="скачивать голосовые сообщения вместо подставления ссылок", action="store_true")
	pars.add_argument("-md", dest="mus", help="скачивать музыку вместо подставления ссылок", action="store_true")
	pars.add_argument("-dd", dest="doc", help="скачивать документы вместо подставления ссылок", action="store_true")
	pars.add_argument("-f", type=str, dest="folder", help="папка для загрузки диалогов/постов", default=0)
	pars.add_argument("-af", dest="all", help="скачать все вложения", action="store_true")
	pars.add_argument("-ul", dest="user_link", help="превращать именами пользователей, отправивших сообщения в ссылки", action="store_true")
	pars.add_argument("-sm", dest="cover", help="оформлять музыку", action="store_true")
	pars.add_argument("-all", dest="all_all", help="", action="store_true")
	pars.add_argument("-log", dest="log", help="логи о работе программы", action="store_true")
	pars.add_argument("-help", dest="help", help="краткая документация", action="store_true")
	args = pars.parse_args()

	if args.help:
		info()
		sys.exit(1)
	elif len(sys.argv) < 2:
		graphic()
	elif len(sys.argv) > 2:
		if args.chat:
			if args.count:
				count_ = args.count
			else:
				count_ = 20
			id_ = args.img
			ad_ = args.aud
			md_ = args.mus
			dd_ = args.doc
			f_ = args.folder
			lg_ = args.log
			af_ = args.all
			ul_ = args.user_link
			cv_ = args.cover
			all_ = args.all_all
			dwn_dlg(sys.argv[2], count_, _photo=id_, _audio=ad_, _music=md_, _doc=dd_, _folder=f_, _af=af_, _ul=ul_, _cv=cv_, _all=all_)
		elif args.post:
			if args.count:
				count_ = args.count
			else:
				count_ = 20
			id_ = args.img
			if args.aud:
				pass
			md_ = args.mus
			dd_ = args.doc
			f_ = args.folder
			lg_ = args.log
			af_ = args.all
			dwn_pst(sys.argv[2], count_, _photo=id_, _music=md_, _doc=dd_, _folder=f_, _af=af_)
