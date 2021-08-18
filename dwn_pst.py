try:
	try:
		import sys
		import vk_api
		from token import token
		import requests
		from datetime import datetime as dt
		import os
		import locale
		from logs import *
		import shutil
	except (ModuleNotFoundError, ImportError) as module_error:
		mdl = str(module_error).split("'")[1]
		error(f"Отсутствует необходимый модуль {mdl}!")
		sys.exit(1)

	def auth():
		"""sign in vk.com"""
		global session
		session = vk_api.VkApi(token = token)
		succes("Авторизация!")

	def dwn_pst(id_, count_, _photo=0, _music=0, _doc=0, _folder=0, _af=0, _q=""):

		SIZE_PHOTO = 0

		if _q == "s":
			SIZE_PHOTO = 5
		elif _q == "m":
			SIZE_PHOTO = 0
		elif _q == "p":
			SIZE_PHOTO = 2
		elif _q == "q":
			SIZE_PHOTO = 3
		elif _q == "r":
			SIZE_PHOTO = 4
		elif _q == "x":
			SIZE_PHOTO = 7
		elif _q == "y":
			SIZE_PHOTO = 8
		elif _q == "w":
			SIZE_PHOTO = 6

		#if have parametr _af (all files), the set in value 1 (download) all variables for download media files
		if _af == 1:
			_photo, _music, _doc = 1, 1, 1

		auth()

		#create folder for saving dialog
		try:
			if _folder != 0:
				os.mkdir(_folder)
		except FileExistsError:
			info("Такая папка уже существует!")

		#getting posts history
		try:
			getWall = session.method("wall.get", {
				"domain": id_,
				"count": count_,
				"extended": 1,
				"fields": "members_count"
				})
			if getWall["count"] == 0:
				getWall = session.method("wall.get", {
					"owner_id": id_,
					"count": count_,
					"extended": 1
					})
				if getWall["count"] == 0:
					getWall = session.method("wall.get", {
						"owner_id": "-" + str(id_),
						"count": count_,
						"extended": 1,
						"fields": "members_count"
						})
					if getWall["count"] == 0:
						warn("Пользователь/группа не существует, либо отсутствуют посты!!")
						sys.exit(1)
		except vk_api.exceptions.ApiError as err:
			err = str(err)
			#error sign in in vk.com
			if err[1] == "5":
				error("Ошибка авторизации! Токен неправильный или срок его действия истёк!")
				sys.exit(1)
			#invalid id user/group
			elif err[1:4] == "100":
				warn("Неправильный id пользователя/группы")
				sys.exit(1)

		#getting name user/group
		if len(getWall["groups"]) >= 1:
			name = getWall["groups"][0]["name"]
			succes("Название диалога получено!")
		else:
			name = getWall["profiles"][0]["first_name"] + " " + getWall["profiles"][0]["last_name"]
			succes("Название диалога получено!")

		#getting avatar user/group
		if len(getWall["groups"]) >= 1:
			ava = getWall["groups"][0]["photo_100"]
			ava = requests.get(ava)
			succes("Аватарка получена!")
		else:
			ava = getWall["profiles"][0]["photo_100"]
			ava = requests.get(ava)
			succes("Аватарка получена!")

		#create link on user/group
		if len(getWall["groups"]) >= 1:
			link_user = "https://vk.com/" + getWall["groups"][0]["screen_name"]
			succes("Ссылка на группу получена!")
		else:
			link_user = "https://vk.com/" + getWall["profiles"][0]["screen_name"]
			succes("Ссылка на пользователя получена!")

		#getting count users (only for groups)
		if "members_count" in getWall["groups"][0].keys():
			users = "<center style='font-family: sans-serif; color: #fff; padding: 10px'>Участиков: " + str(getWall["groups"][0]["members_count"]) + "</center>"
			succes("Количество участников получено!")
		else:
			users = ""
			info("Количество пользователей не получено!")

		#count posts
		posts_count = "<center style='font-family: sans-serif; color: #fff; padding: 10px'>Количество постов: " + str(getWall["count"]) + "</center>"

		#save avatar
		if _folder == 0:
			with open("avatar.jpg", "wb") as ava_:
				ava_.write(ava.content)
				succes("Аватарка скачана!")
		elif _folder != 0:
			with open(f"{_folder}/avatar.jpg", "wb") as ava_:
				ava_.write(ava.content)
				succes("Аватарка скачана!")

		#html templates
		style = '''::-webkit-scrollbar {
	    width: 12px;
	}
	 
	::-webkit-scrollbar-track {
	    background-color: rgba(0, 0, 0, 0.3)
	}
	 
	::-webkit-scrollbar-thumb {
	    border-radius: 10px;
	    background-color: #fff;
	    -webkit-box-shadow: inset 0 0 6px rgba(0,0,0,0.5); 
	}

	* {
		font-family: sans-serif;
	}'''

		html1 = f'''<!DOCTYPE html>
	<html>
		<head>
			<meta charset="utf-8">
			<title>Посты {name}</title>
			<style>
			{style}
			</style>
		</head>
		<body style='background-color: #333'>
			<div style='width: 750px; margin: 10px auto 10px auto; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px'>
				<center><a href='{link_user}' target='_blank'><img src='ava.jpg' style='border-radius: 100px; margin-top: 20px; box-shadow: 0px 0px 10px #000'></center></a>
				<center style='padding: 10px; font-family: sans-serif; font-size: 20px; color: #fff'>Посты {name}</center>
				{users}
				{posts_count}
			</div>'''

		html2 = ""

		html3 = '''
		</body>
	</html>'''

		succes("HTML шаблоны созданы!")

		#formating dialog
		for i in range(int(count_)):
			j = getWall["items"][i]
			if "attachments" in j.keys():
				if j["attachments"][0]["type"] == "photo":
					if _photo == 0:
						url_photo = j["attachments"][0]["photo"]["sizes"][SIZE_PHOTO]["url"]
						html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
										<span style='display: inline-block; padding: 10px'>{j["text"]}<br></span>
										<div style="padding: 10px">
											<img src='{url_photo}' style='max-width: 680px; border-radius: 10px; box-shadow: 0px 0px 10px #000'>
										</div>
										<div style='padding: 10px'>
											<span style='display: inline-block; padding: 10px'>
												{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров &ensp; {(dt.fromtimestamp(getWall['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
											</span>
										</div>
									</div>'''
					elif _photo == 1:
						url_photo = j["attachments"][0]["photo"]["sizes"][SIZE_PHOTO]["url"]
						url_photo = requests.get(url_photo)
						name_photo = f"{(dt.fromtimestamp(j['attachments'][0]['photo']['date'])).strftime('%d-%m-%y~%H-%M')}.jpg"
						if _folder == 0:
							with open(name_photo, "wb") as file:
								file.write(url_photo.content)
						elif _folder != 0:
							with open(f"{_folder}/{name_photo}", "wb") as file:
								file.write(url_photo.content)
						html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
										<div style="padding: 10px">
											<img src='{name_photo}' style='max-width: 680px; border-radius: 10px; box-shadow: 0px 0px 10px #000'>
										</div>
										<span style='display: inline-block; padding: 10px'>{j["text"]}</span>
										<div style='padding: 10px'>
											<span style='display: inline-block; padding: 10px'>
												{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров &ensp; {(dt.fromtimestamp(getWall['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
											</span>
										</div>
									</div>'''
				elif j["attachments"][0]["type"] == "audio":
					if _music == 0:
						url_music = j["attachments"][0]["audio"]["url"]
						html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
										<audio src='{url_music}' controls='controls' style='padding: 10px'>
										<span style='display: inline-block; padding: 10px'>{j["text"]}</span>
										<div style='padding: 10px'>
											<span style='display: inline-block; padding: 10px'>
												{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров &ensp; {(dt.fromtimestamp(getWall['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
											</span>
										</div>
									</div>'''
					elif _music == 1:
						url_music = j["attachments"][0]["audio"]["url"]
						url_music = requests.get(url_music)
						name_music = f"{(dt.fromtimestamp(j['date'])).strftime('%d-%m-%y~%H-%M')}.mp3"
						if _folder == 0:
							with open(name_music, "wb") as file:
								file.write(url_music.content)
						elif _folder != 0:
							with open(f"{_folder}/{name_music}", "wb") as file:
								file.write(url_music.content)
						html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
										<audio src='{name_music}' controls='controls' style='padding: 10px'></audio>
										<span style='display: inline-block; padding: 10px'>{j["text"]}</span>
										<div style='padding: 10px'>
											<span style='display: inline-block; padding: 10px'>
												{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров &ensp; {(dt.fromtimestamp(getWall['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
											</span>
										</div>
									</div>'''
				elif j["attachments"][0]["type"] == "doc":
					if _doc == 0:
						url_doc = j["attachments"][0]["audio"]["url"]
						html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
										<a href='{url_doc}'>ДОКУМЕНТ</a>
										<div style='padding: 10px'>
											<span style='display: inline-block; padding: 10px'>
												{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров &ensp; {(dt.fromtimestamp(getWall['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
											</span>
										</div>
									</div>'''
					elif _doc == 1:
						url_doc = j["attachments"][0]["doc"]["url"]
						doc_type = getWall["items"][i]["attachments"][0]["doc"]["ext"]
						url_doc = requests.get(url_doc)
						name_doc = f"{(dt.fromtimestamp(j[i]['date'])).strftime('%d-%m-%y~%H-%M')}.{doc_type}"
						if doc_type == "jpg" or "png":
							if _folder == 0:
								with open(name_doc, "wb") as file:
									file.write(url_doc.content)
							elif _folder != 0:
								with open(f"{_folder}/{name_doc}", "wb") as file:
									file.write(url_doc.content)
							html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
											<img src='{name_doc}' style='max-width: 680px; padding: 10px; border-radius: 20px'>
											<span style='display: inline-block; padding: 10px'>{j["text"]}</span>
											<div style='padding: 10px'>
												<span style='display: inline-block; padding: 10px'>
													{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров &ensp; {(dt.fromtimestamp(getWall['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</span>
											</div>
										</div>'''
						elif doc_type == "mp3":
							if _folder == 0:
								with open(name_doc, "wb") as file:
									file.write(url_doc.content)
							elif _folder != 0:
								with open(f"{_folder}/{name_doc}", "wb") as file:
									file.write(url_doc.content)
							html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
											<audio src='{name_doc}' controls='controls' style='padding: 10px'></audio>
											<span style='display: inline-block; padding: 10px'>{j["text"]}</span>
											<div style='padding: 10px'>
												<span style='display: inline-block; padding: 10px'>
													{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров &ensp; {(dt.fromtimestamp(getWall['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</span>
											</div>
										</div>'''
			elif not "attachments" in j.keys():
				text = j["text"]
				likes = j["likes"]["count"]
				reposts = j["reposts"]["count"]
				views = j["views"]["count"]
				html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
								<span style='display: inline-block; padding: 10px'>{j["text"]}</span>
								<div style='padding: 10px'>
									<span style='display: inline-block; padding: 10px'>
										{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров &ensp; {(dt.fromtimestamp(getWall['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
									</span>
								</div>
							</div>'''

		#joining all fragments html templates
		html_join = html1 + html2 + html3

		succes("Создание HTML страницы завершено!")

		if _folder == 0:
			with open(f"Посты {name}.html", "w", encoding="utf-8") as file:
				file.write(html_join)
				succes("Посты сохранены!")
		elif _folder != 0:
			with open(f"{_folder}/Посты {name}.html", "w", encoding="utf-8") as file:
				file.write(html_join)
				succes("Посты сохранены!")

		#delete folder __pycache__ after the work of the program
		try:
			shutil.rmtree("__pycache__")
		except Exception:
			pass
except KeyboardInterrupt:
	warn("Выход!")
	sys.exit(1)