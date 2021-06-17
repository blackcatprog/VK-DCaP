try:
	import vk_api
	from cfg import *
	import requests
	import os
	import sys
	from colorama import Fore
	from datetime import datetime as dt
except KeyboardInterrupt:
	print(error + "Выход")
	sys.exit(1)
except ModuleNotFoundError as err:
	err = str(err)
	err = err.split("'", 2)
	print(error + f"Не установлен модуль {err[1]}!")
	sys.exit(1)

def dwn_pst(id_, count, _photo=0, _music=0, _document=0, _folder=0, _af=0):
	DOWNLOAD_PHOTO = _photo
	DOWNLOAD_MUSIC = _music
	DOWNLOAD_DOCUMENT = _document
	SIZE_PHOTO = 0
	FOLDER = _folder
	LOG = _log

	if _af == 1:
		DOWNLOAD_PHOTO, DOWNLOAD_MUSIC, DOWNLOAD_DOCUMENT = 1, 1, 1

	#авторизация вконтакте
	session = vk_api.VkApi(token = token)

	try:
		if FOLDER != 0:
			os.mkdir(FOLDER)
	except FileExistsError:
		print(warn + "Такая папка уже существует!")

	#получение истории постов
	try:
		getWall = session.method("wall.get", {
			"domain": id_,
			"count": count,
			"extended": 1,
			"fields": "members_count"
			})
		if getWall["count"] == 0:
			getWall = session.method("wall.get", {
				"owner_id": id_,
				"count": count,
				"extended": 1
				})
			if getWall["count"] == 0:
				getWall = session.method("wall.get", {
					"owner_id": "-" + str(id_),
					"count": count,
					"extended": 1,
					"fields": "members_count"
					})
				if getWall["count"] == 0:
					print(error + "Пользователь/группа не существует!")
					sys.exit(1)
	except KeyboardInterrupt:
		print(error + "Выход!")
		sys.exit(1)
	except vk_api.exceptions.ApiError as err:
		err = str(err)
		if err[1] == "5":
			print(error + "Неправильный токен")
			sys.exit(1)
		elif err[1:4] == "100":
			print(error + "Неправильный id пользователя/группы")
			sys.exit(1)

	#получаем имя пользователя/группы
	if len(getWall["groups"]) >= 1:
		name = getWall["groups"][0]["name"]
	else:
		name = getWall["profiles"][0]["first_name"] + " " + getWall["profiles"][0]["last_name"]

	#получаем автарку пользователя/группы
	if len(getWall["groups"]) >= 1:
		ava = getWall["groups"][0]["photo_100"]
		ava = requests.get(ava)
	else:
		ava = getWall["profiles"][0]["photo_100"]
		ava = requests.get(ava)

	#создаём ссылку на пользователя/руппу
	if len(getWall["groups"]) >= 1:
		link_user = "https://vk.com/" + getWall["groups"][0]["screen_name"]
	else:
		link_user = "https://vk.com/" + getWall["profiles"][0]["screen_name"]

	#получаем количество участников (для групп)
	if "members_count" in getWall["groups"][0].keys():
		users = "<center style='font-family: sans-serif; color: #fff; padding: 10px'>Участиков: " + str(getWall["groups"][0]["members_count"]) + "</center>"
	else:
		users = ""

	#если указана папка для сохранения, аватарка сохраняется в неё
	if FOLDER == 0:
		with open("ava.jpg", "wb") as ava_:
			ava_.write(ava.content)
	elif FOLDER != 0:
		with open(f"{FOLDER}/ava.jpg", "wb") as ava_:
			ava_.write(ava.content)

	style = '''::-webkit-scrollbar {
    width: 12px;
}
 
::-webkit-scrollbar-track {
    background-color: rgba(0, 0, 0, 0.3)
}
 
::-webkit-scrollbar-thumb {
    border-radius: 10px;
    background-color: #6A7CEC;
    -webkit-box-shadow: inset 0 0 6px rgba(0,0,0,0.5); 
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
		</div>'''

	html2 = ""

	html3 = '''
	</body>
</html>'''

	#форматируем диалог
	try:
		for i in range(count):
			j = getWall["items"][i]
			if "attachments" in j.keys():
				if j["attachments"][0]["type"] == "photo":
					if DOWNLOAD_PHOTO == 0:
						if SIZE_PHOTO == 0:
							what_size_photo = str(input("В каком качестве скачать изображения (s(75px), m(130px), x(604px)): "))
							if what_size_photo == "s":
								SIZE_PHOTO = 5
							elif what_size_photo == "m":
								SIZE_PHOTO = 0
							elif what_size_photo == "x":
								SIZE_PHOTO = 6
						url_photo = j["attachments"][0]["photo"]["sizes"][SIZE_PHOTO]["url"]
						html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
										<span style='display: inline-block; padding: 10px'>{j["text"]}<br></span>
										<div style="padding: 10px">
											<img src='{url_photo}' style='height: 100px; border-radius: 10px; box-shadow: 0px 0px 10px #000'>
										</div>
										<div style='padding: 10px'>
											<span style='display: inline-block; padding: 10px'>
												{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров
											</span>
										</div>
									</div>'''
					elif DOWNLOAD_PHOTO == 1:
						if SIZE_PHOTO == 0:
							what_size_photo = str(input("В каком качестве скачивать изображения (s(75px), m(130px), x(604px)): "))
							if what_size_photo == "s":
								SIZE_PHOTO = 5
							elif what_size_photo == "m":
								SIZE_PHOTO = 0
							elif what_size_photo == "x":
								SIZE_PHOTO = 6
						url_photo = j["attachments"][0]["photo"]["sizes"][SIZE_PHOTO]["url"]
						url_photo = requests.get(url_photo)
						name_photo = f"{(dt.fromtimestamp(j['attachments'][0]['photo']['date'])).strftime('%d-%m-%y~%H-%M')}.jpg"
						if FOLDER == 0:
							with open(name_photo, "wb") as file:
								file.write(url_photo.content)
						elif FOLDER != 0:
							with open(f"{FOLDER}/{name_photo}", "wb") as file:
								file.write(url_photo.content)
						html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
										<div style="padding: 10px">
											<img src='{name_photo}' style='height: 100px; border-radius: 10px; box-shadow: 0px 0px 10px #000'>
										</div>
										<span style='display: inline-block; padding: 10px'>{j["text"]}</span>
										<div style='padding: 10px'>
											<span style='display: inline-block; padding: 10px'>
												{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров
											</span>
										</div>
									</div>'''
				elif j["attachments"][0]["type"] == "audio":
					if DOWNLOAD_MUSIC == 0:
						url_music = j["attachments"][0]["audio"]["url"]
						html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
										<audio src='{url_music}' controls='controls' style='padding: 10px'>
										<span style='display: inline-block; padding: 10px'>{j["text"]}</span>
										<div style='padding: 10px'>
											<span style='display: inline-block; padding: 10px'>
												{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров
											</span>
										</div>
									</div>'''
					elif DOWNLOAD_MUSIC == 1:
						url_music = j["attachments"][0]["audio"]["url"]
						url_music = requests.get(url_music)
						name_music = f"{(dt.fromtimestamp(j['date'])).strftime('%d-%m-%y~%H-%M')}.mp3"
						if FOLDER == 0:
							with open(name_music, "wb") as file:
								file.write(url_music.content)
						elif FOLDER != 0:
							with open(f"{FOLDER}/{name_music}", "wb") as file:
								file.write(url_msuic.content)
						html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
										<audio src='{name_music}' controls='controls' style='padding: 10px'></audio>
										<span style='display: inline-block; padding: 10px'>{j["text"]}</span>
										<div style='padding: 10px'>
											<span style='display: inline-block; padding: 10px'>
												{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров
											</span>
										</div>
									</div>'''
				elif j["attachments"][0]["type"] == "doc":
					if DOWNLOAD_DOCUMENT == 0:
						url_doc = j["attachments"][0]["audio"]["url"]
						html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
										<a href='{url_doc}'>ДОКУМЕНТ</a>
										<div style='padding: 10px'>
											<span style='display: inline-block; padding: 10px'>
												{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров
											</span>
										</div>
									</div>'''
					elif DOWNLOAD_DOCUMENT == 1:
						url_doc = j["attachments"][0]["doc"]["url"]
						doc_type = getHistory["items"][i]["attachments"][0]["doc"]["ext"]
						url_doc = requests.get(url_doc)
						name_doc = f"{(dt.fromtimestamp(j[i]['date'])).strftime('%d-%m-%y~%H-%M')}.{doc_type}"
						if doc_type == "jpg" or "png":
							if FOLDER == 0:
								with open(name_doc, "wb") as file:
									file.write(url_doc.content)
							elif FOLDER != 0:
								with open(f"{FOLDER}/{name_doc}", "wb") as file:
									file.write(url_doc.content)
							html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
											<img src='{name_doc}' style='padding: 10px; border-radius: 20px'>
											<span style='display: inline-block; padding: 10px'>{j["text"]}</span>
											<div style='padding: 10px'>
												<span style='display: inline-block; padding: 10px'>
													{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров
												</span>
											</div>
										</div>'''
						elif doc_type == "mp3":
							if FOLDER == 0:
								with open(name_doc, "wb") as file:
									file.write(url_doc.content)
							elif FOLDER != 0:
								with open(f"{FOLDER}/{name_doc}", "wb") as file:
									file.write(url_doc.content)
							html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
											<audio src='{name_doc}' controls='controls' style='padding: 10px'></audio>
											<span style='display: inline-block; padding: 10px'>{j["text"]}</span>
											<div style='padding: 10px'>
												<span style='display: inline-block; padding: 10px'>
													{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров
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
										{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров
									</span>
								</div>
							</div>'''
	except KeyboardInterrupt:
		print(error + "Выход")
		sys.exit(1)

	#соединяем все части html кода
	html_join = html1 + html2 + html3

	#если указана папка для сохранения, то файл скачивается в неё
	if FOLDER == 0:
		with open(f"Посты_{name}.html", "w", encoding="utf-8") as file:
			file.write(html_join)
	elif FOLDER != 0:
		with open(f"{FOLDER}/Посты_{name}.html", "w", encoding="utf-8") as file:
			file.write(html_join)
