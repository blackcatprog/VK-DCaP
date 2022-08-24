try:
	try:
		import argparse
		import sys
		import logs
		import shutil
		import dcap_cfg
		from urllib.request import urlopen
		from dwn_dlg import dwn_dlg
		from dwn_pst import dwn_pst
	except ModuleNotFoundError:
		logs.error("Отсутствует(ют) необходимый(е) модуль(и)!")
		sys.exit(1)

	def main():
		def check_connection():
			try:
				urlopen("https://google.com")
			except Exception as e:
				logs.error("Нет подключения к интернету!")
				sys.exit(1)

		def info_():
			"""short info about arguments"""
			print('''Синтаксис: python dcap.py [что скачивать] [параметры]
	\nЧто скачивать:
	-cd [id пользователя/беседы/группы] - переписку
	-pd [id пользователя/группы] - посты
	\nПараметры:
	-c [количество] - количество скачиваемых сообщений (по умолчанию 20)
	-id - скачивать фото
	-q - указать размер скачиваемых изображений: s - 75px, m - 130px, p - 200px, q - 320px, r - 510px, x - 604px, y - 807px, w - 1600px
	-ad - скачивать голосовые сообщения
	-md - скачивать музыку
	-dd - скачивать документы
	-sd - скачивать стикеры
	-f [название папки] - скачивание в папку
	-af - скачать все вложения
	-ul - превращать имена пользователей рядом с сообщенями в ссылки на этих пользователей
	-ud - скачивать аватарки пользователей в беседе
	-sm - оформлять музыку
	-help - краткая документация (вы её сейчас и смотрите :) )''')
			try:
				shutil.rmtree("__pycache__")
			except Exception:
				pass
			sys.exit(1)

		def graphic():
			"""main inforation about program"""
			print(f"VK-DCaP v{dcap_cfg.version}")
			print(f"Copyright (C) 2021 {dcap_cfg.author}")
			print(f"github repository: {dcap_cfg.repository}")
			try:
				shutil.rmtree("__pycache__")
			except Exception:
				pass

		pars = argparse.ArgumentParser()
		pars.add_argument("-cd", "--chat-download", dest="chat", help="скачивание диалога")
		pars.add_argument("-pd", "--post-download", dest="post", help="скачивание постов")
		pars.add_argument("-c", "--count", type=int, dest="count", help="количество постов/диалогов (целое число)")
		pars.add_argument("-id", "--image-download", dest="img", help="скачивать фото", action="store_true")
		pars.add_argument("-ad", "--audio-download", dest="aud", help="скачивать голосовые сообщения", action="store_true")
		pars.add_argument("-md", "--music-download", dest="mus", help="скачивать музыку", action="store_true")
		pars.add_argument("-dd", "--document-download", dest="doc", help="скачивать документы", action="store_true")
		pars.add_argument("-sd", "--sticker-download", dest="sd", help="скачивать стикеры", action="store_true")
		pars.add_argument("-f", "--folder", type=str, dest="folder", help="папка для загрузки диалогов/постов", default=0)
		pars.add_argument("-af", "--all-files", dest="all", help="скачать все вложения", action="store_true")
		pars.add_argument("-ul", "--user-link", dest="user_link", help="превращать именами пользователей, отправивших сообщения в ссылки", action="store_true")
		pars.add_argument("-sm", "--style-music", dest="cover", help="оформлять музыку", action="store_true")
		pars.add_argument("-all", "--all-dialog", dest="all_all", help="скачать весь диалог сразу", action="store_true")
		pars.add_argument("-q", "--quality", type=str, dest="quality", help="выбрать качество изображений: s - 75px, m - 130px, p - 200px, q - 320px, r - 510px, x - 604px, y - 807px, w - 1600px")
		pars.add_argument("-ud", "--user-download", dest="avs_dwn", help="скачивать аватарки пользователей в беседе", action="store_true")
		pars.add_argument("-help", dest="help", help="краткая документация", action="store_true")
		args = pars.parse_args()

		if args.help:
			info_()
			sys.exit(1)
		elif len(sys.argv) < 2:
			graphic()
		elif len(sys.argv) > 2:
			check_connection()
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
				dwn_dlg(sys.argv[2], count_, photo_=id_, audio_=ad_, music_=md_, doc_=dd_, sd_=sd_, folder_=f_, af_=af_, ul_=ul_, cv_=cv_, all_=all_, q_=q_, ud_=ud_)
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
				all_ = args.all_all
				af_ = args.all
				q_ = args.quality
				dwn_pst(sys.argv[2], count_, photo_=id_, music_=md_, doc_=dd_, folder_=f_, af_=af_, q_=q_, all_=all_)
except KeyboardInterrupt:
	logs.warn("Выход!")
	sys.exit(1)