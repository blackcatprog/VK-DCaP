import argparse
import sys
import dcap_cfg
from dwn_dlg import dwn_dlg
from dwn_pst import dwn_pst

def main():
	def info_():
		print("Синтаксис: python dcap.py [что скачивать] [параметры]")
		print("\nЧто скачивать:")
		print("-cd [id пользователя/беседы/группы] - переписку")
		print("-pd [id пользователя/группы] - посты")
		print("\nПараметры:")
		print("-c [количество] - количество скачиваемых сообщений (по умолчанию 20)")
		print("-id - скачивать фото")
		print("-q - указать размер скачиваемых изображений: s - 75px, m - 130px, p - 200px, q - 320px, r - 510px, x - 604px, y - 807px, w - 1600px")
		print("-ad - скачивать голосовые сообщения")
		print("-md - скачивать музыку")
		print("-dd - скачивать документы")
		print("-sd - скачивать стикеры")
		print("-f [название папки] - скачивание в папку")
		print("-af - скачать все вложения")
		print("-ul - превращать имена пользователей рядом с сообщенями в ссылки на этих пользователей")
		print("-ud - скачивать аватарки пользователей в беседе")
		print("-sm - оформлять музыку")
		print("-help - краткая документация (вы её сейчас и смотрите :) )")
		sys.exit(1)

	def graphic():
		print(f"VK-DCaP v{dcap_cfg.version}")
		print(f"Copyright (C) 2021 {dcap_cfg.author}")
		print(f"github repository: {dcap_cfg.reposiroty}\n")

	pars = argparse.ArgumentParser()
	pars.add_argument("-cd", dest="chat", help="скачивание диалога")
	pars.add_argument("-pd", dest="post", help="скачивание постов")
	pars.add_argument("-c", type=int, dest="count", help="количество постов/диалогов (целое число)")
	pars.add_argument("-id", dest="img", help="скачивать фото", action="store_true")
	pars.add_argument("-ad", dest="aud", help="скачивать голосовые сообщения", action="store_true")
	pars.add_argument("-md", dest="mus", help="скачивать музыку", action="store_true")
	pars.add_argument("-dd", dest="doc", help="скачивать документы", action="store_true")
	pars.add_argument("-sd", dest="sd", help="скачивать стикеры", action="store_true")
	pars.add_argument("-f", type=str, dest="folder", help="папка для загрузки диалогов/постов", default=0)
	pars.add_argument("-af", dest="all", help="скачать все вложения", action="store_true")
	pars.add_argument("-ul", dest="user_link", help="превращать именами пользователей, отправивших сообщения в ссылки", action="store_true")
	pars.add_argument("-sm", dest="cover", help="оформлять музыку", action="store_true")
	pars.add_argument("-all", dest="all_all", help="скачать весь диалог сразу", action="store_true")
	pars.add_argument("-q", type=str, dest="quality", help="выбрать качество изображений: s - 75px, m - 130px, p - 200px, q - 320px, r - 510px, x - 604px, y - 807px, w - 1600px")
	pars.add_argument("-ud", dest="avs_dwn", help="скачивать аватарки пользователей в беседе", action="store_true")
	pars.add_argument("-help", dest="help", help="краткая документация", action="store_true")
	args = pars.parse_args()

	if args.help:
		info_()
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
			sd_ = args.sd
			f_ = args.folder
			af_ = args.all
			ul_ = args.user_link
			cv_ = args.cover
			all_ = args.all_all
			q_ = args.quality
			ud_ = args.avs_dwn
			dwn_dlg(sys.argv[2], count_, _photo=id_, _audio=ad_, _music=md_, _doc=dd_, _sd=sd_, _folder=f_, _af=af_, _ul=ul_, _cv=cv_, _all=all_, _q=q_, _ud=ud_)
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
			af_ = args.all
			q_ = args.q
			dwn_pst(sys.argv[2], count_, _photo=id_, _music=md_, _doc=dd_, _folder=f_, _af=af_, _q=q_)
