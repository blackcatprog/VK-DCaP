try:
	import sys
	import vk_api
	from cfg import token
	from logs import *
	import requests
	from datetime import datetime as dt
	import os
	import time
except KeyboardInterrupt:
	print(error + "Выход")
	sys.exit(1)

def download_chat(id_, count, _photo=0, _audio=0, _music=0, _document=0, _folder=0, _log=0):
	DOWNLOAD_PHOTO = _photo
	DOWNLOAD_AUDIO = _audio
	DOWNLOAD_MUSIC = _music
	DOWNLOAD_DOCUMENT = _document
	SIZE_PHOTO = 0
	FOLDER = _folder
	LOG = _log

	#авторизация вконтакте
	session = vk_api.VkApi(token = token)
	
	if LOG != 0:
		print(succes + "Авторизация успешна")

	#проверяем, создана ли папка с указанным именем,и если создана, то скачиваем всё в неё
	try:
		if FOLDER != 0:
			os.mkdir(FOLDER)
	except FileExistsError:
		print(error + "Такая папка уже существует")

	#получаем историю диалога
	try:
		getHistory = session.method("messages.getHistory", {
			"peer_id": id_,
			"count": count,
			"extended": 1
			})
		if getHistory["count"] == 0:
			getHistory = session.method("messages.getHistory", {
				"peer_id": "-" + id_,
				"count": count,
				"extended": 1
				})
			if getHistory["count"] == 0:
				print(error + "Диалог не существует или удалён")
				sys.exit(1)
		elif getHistory["count"] < count:
			print(error + f"В указанном диалоге нет {count} сообщений")
			sys.exit(1)
	except KeyboardInterrupt:
		print(error + "Выход")
		sys.exit(1)
	except vk_api.exceptions.ApiError as err:
		err = str(err)
		if err[1] == "5":
			print(error + "Неправильный токен")
			sys.exit(1)
		elif err[1:4] == "100":
			print(error + "Неправильный id пользователя")
			sys.exit(1)

	if LOG != 0:
		print(succes + "История диалога получена успешно")

	#получаем имя пользователя/навзание беседы в зависимости от типа диалога
	if getHistory["conversations"][0]["peer"]["type"] == "chat":
		name = getHistory["conversations"][0]["chat_settings"]["title"]
	elif getHistory["conversations"][0]["peer"]["type"] == "user":
		name = getHistory["profiles"][0]["first_name"] + " " + getHistory["profiles"][0]["last_name"]
	elif getHistory["conversations"][0]["peer"]["type"] == "group":
		name = getHistory["groups"][0]["name"]

	#получаем ссылку на пользователя, если диалог с ним, и ничего не получаем, если это беседа
	if getHistory["conversations"][0]["peer"]["type"] == "user":
		link_user = "https://vk.com/" + getHistory["profiles"][0]["screen_name"]
	elif getHistory["conversations"][0]["peer"]["type"] == "chat":
		link_user = "#"
		print(warn + "В данный момент ссылка на беседу не добавляется")
	elif getHistory["conversations"][0]["peer"]["type"] == "group":
		link_user = "https://vk.com/" + getHistory["groups"][0]["screen_name"]

	#получаем аватарку пользователя/беседы
	ava = ""
	if getHistory["conversations"][0]["peer"]["type"] == "user":
		ava = getHistory["profiles"][0]["photo_100"]
		ava = requests.get(ava)
	elif getHistory["conversations"][0]["peer"]["type"] == "chat":
		ava = getHistory["conversations"][0]["chat_settings"]["photo"]["photo_100"]
		ava = requests.get(ava)
	elif getHistory["conversations"][0]["peer"]["type"] == "groups":
		ava = getHistory["groups"][0]["photo_100"]
		ava = requests.get(ava)

	#если указана папка для сохранения, аватарка сохраняется в неё
	if FOLDER == 0:
		with open("ava.jpg", "wb") as ava_:
			ava_.write(ava.content)
	elif FOLDER != 0:
		with open(f"{FOLDER}/ava.jpg", "wb") as ava_:
			ava_.write(ava.content)

	#получаем количество участников, сели это беседа, и ничего не получаем, если чат с пользователем
	if getHistory["conversations"][0]["peer"]["type"] == "user":
		users = ""
	elif getHistory["conversations"][0]["peer"]["type"] == "chat":
		users = "<center style='font-family: sans-serif; color: #fff; padding: 10px'>Участиков: " + str(getHistory["conversations"][0]["chat_settings"]["members_count"]) + "</center>"
	
	if LOG != 0:
		print(succes + "Информация о пользователе/беседе собрана успешно")

	html1 = f'''<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8">
		<title style='font-family: sans-serif'>{name}</title>
		<style>
		</style>
	</head>
	<body style='background-color: #333;'>
		<div style='width: 750px; margin: 10px auto 10px auto; background-color: #5381B9; border-radius: 10px'>
			<center><a href='{link_user}' target='_blank'><img src='ava.jpg' style='border-radius: 100px; margin-top: 20px'></a></center>
			<center style='padding: 10px; font-family: sans-serif; font-size: 20px; color: #fff'>{name}</center>
			{users}
		</div>
		<div style='width: 750px; box-sizing: padding-box; background-color: #5281B9; border-radius: 10px;
		font-family: sans-serif; margin-left: auto; margin-right: auto'>'''

	html2 = ""

	html3 = '''
		</div>
	</body>
</html>'''

	#форматируем диалог
	try:
		for i in range(int(count)):
			getUsers = session.method("users.get", {
				"user_ids": getHistory["items"][i]["from_id"]
			})

			if len(getHistory["items"][i]["attachments"]) >= 1:
				pass

				if getHistory["items"][i]["attachments"][0]["type"] == "photo":
					if getHistory["items"][i]["text"][0:4] == "https" or getHistory["items"][i]["text"][0:4] == "http":
						sms = f"<a href='{getHistory['items'][i]['text']}'>{getHistory['items'][i]['text']}</a>"
					else:
						sms = getHistory["items"][i]["text"]
					
					if DOWNLOAD_PHOTO == 0:
						if SIZE_PHOTO == 0:
							what_size_photo = str(input("В каком качестве вставлять изображения (s(75px), m(130px), x(604px)): "))
							if what_size_photo.strip() == "s":
								SIZE_PHOTO = 5
							elif what_size_photo.strip() == "m":
								SIZE_PHOTO = 0
							elif what_size_photo.strip() == "x":
								SIZE_PHOTO = 6
						url_photo = getHistory["items"][i]["attachments"][0]["photo"]["sizes"][SIZE_PHOTO]["url"]
						if getHistory["items"][i]["text"] != "":
							html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
							border-radius: 10px; margin: 10px -50px auto 10px'>{sms}<br><img src='{url_photo}'
							style='height: 200px; border-radius: 10px'><span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>{getUsers[0]["first_name"]}
							</span></div><div style='display: block; padding: 10px; font-size: 10px; font-weight: bold'>
							{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
						elif getHistory["items"][i]["text"] == "":
							html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
							border-radius: 10px; margin: 10px -50px auto 10px'><img src='{url_photo}' style='height: 200px; border-radius: 10px'>
							<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>{getUsers[0]["first_name"]}
							</span></div><div style='display: block; padding: 10px; font-size: 10px; font-weight: bold'>
							{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
					elif DOWNLOAD_PHOTO == 1:
						if SIZE_PHOTO == 0:
							what_size_photo = str(input("В каком качестве скачивать изображения (s(75px), m(130px), x(604px)): "))
							if what_size_photo.strip() == "s":
								SIZE_PHOTO = 5
							elif what_size_photo.strip() == "m":
								SIZE_PHOTO = 0
							elif what_size_photo.strip() == "x":
								SIZE_PHOTO = 6
						url_photo = getHistory["items"][i]["attachments"][0]["photo"]["sizes"][SIZE_PHOTO]["url"]
						url_photo = requests.get(url_photo)
						name_photo = f"{(dt.fromtimestamp(getHistory['items'][i]['attachments'][0]['photo']['date'])).strftime('%d-%m-%y~%H-%M')}.jpg"
						if FOLDER == 0:
							with open(name_photo, "wb") as file:
								file.write(url_photo.content)
						elif FOLDER != 0:
							with open(f"{FOLDER}/{name_photo}", "wb") as file:
								file.write(url_photo.content)
						if getHistory["items"][i]["text"] != "":
							html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
							border-radius: 10px; margin: 10px -50px auto 10px'>{sms}<br><img src='{name_photo}'
							style='height: 200px; border-radius: 10px;'><span style='font-size: 10px; color: #000; font-weight: bold;
							margin-left: 5px'>{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px;
							font-size: 10px; font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
						elif getHistory["items"][i]["text"] == "":
							html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
							border-radius: 10px; margin: 10px -50px auto 10px'><img src='{name_photo}'
							style='height: 200px; border-radius: 10px;'><span style='font-size: 10px; color: #000; font-weight: bold;
							margin-left: 5px'>{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px;
							font-size: 10px; font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
				elif getHistory["items"][i]["attachments"][0]["type"] == "audio_message":
					if DOWNLOAD_AUDIO == 0:
						url_audio = getHistory["items"][i]["attachments"][0]["audio_message"]["link_mp3"]
						if getHistory["items"][i]["text"] != "":
							html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding:
							10px;border-radius: 10px; margin: 10px -50px auto 10px'>{sms}<br><audio src='{url_audio}'
							controls='controls'></audio><span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
							{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px; font-size: 10px;
							font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
						elif getHistory["items"][i]["text"] == "":
							html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding:
							10px;border-radius: 10px; margin: 10px -50px auto 10px'><audio src='{url_audio}'
							controls='controls'></audio><span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
							{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px; font-size: 10px;
							font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
					elif DOWNLOAD_AUDIO == 1:
						url_audio = getHistory["items"][i]["attachments"][0]["audio_message"]["link_mp3"]
						url_audio = requests.get(url_audio)
						name_audio = f"{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y~%H-%M')}.mp3"
						if FOLDER == 0:
							with open(name_audio, "wb") as file:
								file.write(url_audio.content)
						elif FOLDER != 0:
							with open(f"{FOLDER}/{name_audio}", "wb") as file:
								file.write(url_audio.content)
						if getHistory["items"][i]["text"] != "":
							html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
							border-radius: 10px; margin: 10px -50px auto 10px'>{sms}<br><audio src='{name_audio}'
							controls='controls'></audio><span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
							{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px; font-size: 10px;
							font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
						elif getHistory["items"][i]["text"] == "":
							html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
							border-radius: 10px; margin: 10px -50px auto 10px'><audio src='{name_audio}'
							controls='controls'></audio><span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
							{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px; font-size: 10px;
							font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
				elif getHistory["items"][i]["attachments"][0]["type"] == "audio":
					if DOWNLOAD_MUSIC == 0:
						url_music = getHistory["items"][i]["attachments"][0]["audio"]["url"]
						if getHistory["items"][i]["text"] != "":
							html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
							border-radius: 10px; margin: 10px -50px auto 10px'>{sms}<br><audio src='{url_music}'
							controls='controls'></audio><span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
							{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px; font-size: 10px;
							font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
						elif getHistory["items"][i]["text"] == "":	
							html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
							border-radius: 10px; margin: 10px -50px auto 10px'><audio src='{url_music}'
							controls='controls'></audio><span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
							{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px; font-size: 10px;
							font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
					elif DOWNLOAD_MUSIC == 1:
						url_music = getHistory["items"][i]["attachments"][0]["audio"]["url"]
						url_music = requests.get(url_music)
						name_music = f"{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y~%H-%M')}.mp3"
						if FOLDER == 0:
							with open(name_music, "wb") as file:
								file.write(url_music.content)
						elif FOLDER != 0:
							with open(f"{FOLDER}/{name_music}", "wb") as file:
								file.write(url_music.content)
						if getHistory["items"][i]["text"] != "":
							html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
							border-radius: 10px; margin: 10px -50px auto 10px'>{sms}<br><audio src='{name_music}' 
							controls='controls'></audio><span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
							{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px; font-size: 10px;
							font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
						elif getHistory["items"][i]["text"] == "":
							html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
							border-radius: 10px; margin: 10px -50px auto 10px'><audio src='{name_music}' 
							controls='controls'></audio><span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
							{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px; font-size: 10px;
							font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
				elif getHistory["items"][i]["attachments"][0]["type"] == "doc":
					if DOWNLOAD_DOCUMENT == 0:
						url_doc = getHistory["items"][i]["attachments"][0]["doc"]["url"]
						if getHistory["items"][i]["text"] != "":
							html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
							border-radius: 10px; margin: 10px -50px auto 10px'>{sms}<br><a href='{url_doc}'>
							ДОКУМЕНТ</a><span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
							{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px; font-size: 10px;
							font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
						elif getHistory["items"][i]["text"] == "":
							html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
							border-radius: 10px; margin: 10px -50px auto 10px'><a href='{url_doc}'>
							ДОКУМЕНТ</a><span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
							{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px; font-size: 10px;
							font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
					elif DOWNLOAD_DOCUMENT == 1:
						url_doc = getHistory["items"][i]["attachments"][0]["doc"]["url"]
						doc_type = getHistory["items"][i]["attachments"][0]["doc"]["ext"]
						url_doc = requests.get(url_doc)
						name_doc = f"{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y~%H-%M')}.{doc_type}"
						if doc_type == "jpg" or "png" or "bmp":
							if FOLDER == 0:
								with open(name_doc, "wb") as file:
									file.write(url_doc.content)
							elif FOLDER != 0:
								with open(f"{FOLDER}/{name_doc}", "wb") as file:
									file.write(url_doc.content)
							if getHistory["items"][i]["text"] != "":
								html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
								border-radius: 10px; margin: 10px -50px auto 10px'>{sms}<br><img src='{name_doc}'>
								<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>{getUsers[0]["first_name"]}
								</span></div><div style='display: block; padding: 10px; font-size: 10px; font-weight: bold'>
								{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
							elif getHistory["items"][i]["text"] == "":
								html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
								border-radius: 10px; margin: 10px -50px auto 10px'><img src='{name_doc}'>
								<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>{getUsers[0]["first_name"]}
								</span></div><div style='display: block; padding: 10px; font-size: 10px; font-weight: bold'>
								{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
						elif doc_type == "mp3" or "wav" or "aac":
							if FOLDER == 0:
								with open(name_doc, "wb") as file:
									file.write(url_doc.content)
							elif FOLDER != 0:
								with open(f"{FOLDER}/{name_doc}", "wb") as file:
									file.write(url_doc.content)
							if getHistory["items"][i]["text"] != "":
								html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
								border-radius: 10px; margin: 10px -50px auto 10px'>{sms}<br><audio src='{name_doc}'
								controls='controls'></audio><span style='font-size: 10px; color: #000; font-weight: bold;
								margin-left: 5px'>{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px; font-size: 10px;
								font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
							elif getHistory["items"][i]["text"] == "":
								html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
								border-radius: 10px; margin: 10px -50px auto 10px'><audio src='{name_doc}'
								controls='controls'></audio><span style='font-size: 10px; color: #000; font-weight: bold;
								margin-left: 5px'>{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px; font-size: 10px;
								font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
						else:
							if getHistory["items"][i]["text"] != "":
								html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
								border-radius: 10px; margin: 10px -50px auto 10px'>{sms}<br><a href='{url_doc}'>
								НЕПОДДЕРЖИВАЕМЫЙ ТИП ДОКУМЕНТА</a><span style='font-size: 10px; color: #000; font-weight: bold;
								margin-left: 5px'>{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px;
								font-size: 10px;font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
							elif getHistory["items"][i]["text"] == "":
								html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
								border-radius: 10px; margin: 10px -50px auto 10px'><a href='{url_doc}'></a><span style='font-size: 10px; color: #000; font-weight: bold;
								margin-left: 5px'>{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px; font-size: 10px;
								font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
			elif len(getHistory["items"][i]["attachments"]) < 1:
				if getHistory["items"][i]["text"][0:4] == "https" or getHistory["items"][i]["text"][0:4] == "http":
					sms = f"<a href='{getHistory['items'][i]['text']}'>{getHistory['items'][i]['text']}</a>"
				else:
					sms = getHistory["items"][i]["text"]
					html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
					border-radius: 10px; margin: 0px -50px auto 10px'>{sms}<span style='font-size: 10px;
					color: #000; font-weight: bold; margin-left: 5px'>{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px; font-size: 10px;
					font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
	except KeyboardInterrupt:
		print(error + "Выход")
		sys.exit(1)
	
	if LOG != 0:
		print(succes + "Диалог отформатирован успешно")

	#соединяем все части html кода
	html_join = html1 + html2 + html3

	#если указана папка для сохранения, то файл скачивается в неё
	if FOLDER == 0:
		with open("chat.html", "w", encoding="utf-8") as file:
			file.write(html_join)
			if LOG != 0:
				print(succes + "Диалог скачан")
	elif FOLDER != 0:
		with open(f"{FOLDER}/chat.html", "w", encoding="utf-8") as file:
			file.write(html_join)
			if LOG != 0:
				print(succes + "Диалог скачан")