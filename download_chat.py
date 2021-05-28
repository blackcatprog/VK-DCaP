import vk_api
import sys
from cfg import token
from logs import *
import requests
from datetime import datetime as dt

def download_chat(user_id, count, _photo=0, _audio=0, _music=0, _document=0):
	#params
	DOWNLOAD_PHOTO = _photo
	DOWNLOAD_AUDIO = _audio
	DOWNLOAD_MUSIC = _music
	DOWNLOAD_DOCUMENT = _document
	#params2.0
	SIZE_PHOTO = 0

	session = vk_api.VkApi(token = token)

	try:
		getHistory = session.method("messages.getHistory", {
			"user_id": user_id,
			"count": count,
			"extended": 1
			})
	except KeyboardInterrupt:
		print(error + "Выход")
	except vk_api.exceptions.ApiError as err:
		err = str(err)
		if err[1] == "5":
			print(error + "Неправильный токен")
			sys.exit(1)
		elif err[1:4] == "100":
			print(error + "Неправильный id пользователя")
			sys.exit(1)

	#get name&photo##########################################################
	name = getHistory["profiles"][0]["first_name"] + " " + getHistory["profiles"][0]["last_name"]
	ava = getHistory["profiles"][0]["photo_100"]
	ava = requests.get(ava)
	with open("ava.jpg", "wb") as ava_:
		ava_.write(ava.content)
	#########################################################################

	###################################################################

	html1 = f'''<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8">
		<title style='font-family: sans-serif'>Чат с {name}</title>
		<style>
		</style>
	</head>
	<body style='background-color: #333;'>
		<div style='width: 750px; margin: 10px auto 10px auto; background-color: #5381B9;border-radius: 10px'>
			<center><img src='ava.jpg' style='border-radius: 100px; margin-top: 20px'></center>
			<center style='padding: 10px; font-family: sans-serif; font-size: 20px; color: #fff'>Чат с {name}</center>
		</div>
		<div style='width: 750px; box-sizing: padding-box; background-color: #5281B9; border-radius: 10px;
		font-family: sans-serif; margin-left: auto; margin-right: auto'>'''

	html2 = ""

	html3 = '''
		</div>
	</body>
</html>'''

	###################################################################
	try:
		for i in range(int(count)):
			getUsers = session.method("users.get", {
				"user_ids": getHistory["items"][i]["from_id"]
			})

			if len(getHistory["items"][i]["attachments"]) >= 1:
				if getHistory["items"][i]["attachments"][0]["type"] == "photo":
					if DOWNLOAD_PHOTO == 0:
						if SIZE_PHOTO == 0:
							what_size_photo = str(input("В каком качестве скачать изображения (s(75px), m(130px), x(604px)): "))
							if what_size_photo == "s":
								SIZE_PHOTO = 5
							elif what_size_photo == "m":
								SIZE_PHOTO = 0
							elif what_size_photo == "x":
								SIZE_PHOTO = 6
						url_photo = getHistory["items"][i]["attachments"][0]["photo"]["sizes"][SIZE_PHOTO]["url"]
						html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
						border-radius: 10px; margin: 10px -50px auto 10px'><img src='{url_photo}' style='border-radius: 10px'><span style='font-size: 10px;
						color: #000; font-weight: bold; margin-left: 5px'>{getUsers[0]["first_name"]}
						</span></div><div style='display: block; padding: 10px; font-size: 10px;
						font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
					elif DOWNLOAD_PHOTO == 1:
						if SIZE_PHOTO == 0:
							what_size_photo = str(input("В каком качестве скачать изображения (s(75px), m(130px), x(604px)): "))
							if what_size_photo == "s":
								SIZE_PHOTO = 5
							elif what_size_photo == "m":
								SIZE_PHOTO = 0
							elif what_size_photo == "x":
								SIZE_PHOTO = 6
						url_photo = getHistory["items"][i]["attachments"][0]["photo"]["sizes"][SIZE_PHOTO]["url"]
						url_photo = requests.get(url_photo)
						name_photo = f"{(dt.fromtimestamp(getHistory['items'][i]['attachments'][0]['photo']['date'])).strftime('%d-%m-%y~%H-%M')}.jpg"
						with open(name_photo, "wb") as file:
							file.write(url_photo.content)
						html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
							border-radius: 10px; margin: 10px -50px auto 10px'> <img src='{name_photo}' style='border-radius: 10px;'>
							<span style='font-size: 10px; color: #000; font-weight: bold;
							margin-left: 5px'>{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px;
							font-size: 10px; font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
				elif getHistory["items"][i]["attachments"][0]["type"] == "audio_message":
					if DOWNLOAD_AUDIO == 0:
						url_audio = getHistory["items"][i]["attachments"][0]["audio_message"]["link_mp3"]
						html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding:
						10px;border-radius: 10px; margin: 10px -50px auto 10px'><audio src='{url_audio}' controls='controls'></audio>
						<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
						{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px; font-size: 10px;
						font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
					elif DOWNLOAD_AUDIO == 1:
						url_audio = getHistory["items"][i]["attachments"][0]["audio_message"]["link_mp3"]
						url_audio = requests.get(url_audio)
						name_audio = f"{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y~%H-%M')}.mp3"
						with open(name_audio, "wb") as file:
							file.write(url_audio.content)
						html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
						border-radius: 10px; margin: 10px -50px auto 10px'><audio src='{name_audio}' controls='controls'></audio>
						<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
						{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px; font-size: 10px;
						font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
				elif getHistory["items"][i]["attachments"][0]["type"] == "audio":
					if DOWNLOAD_MUSIC == 0:
						url_music = getHistory["items"][i]["attachments"][0]["audio"]["url"]
						html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
						border-radius: 10px; margin: 10px -50px auto 10px'><audio src='{url_music}' controls='controls'></audio>
						<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
						{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px; font-size: 10px;
						font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
					elif DOWNLOAD_MUSIC == 1:
						url_music = getHistory["items"][i]["attachments"][0]["audio"]["url"]
						url_music = requests.get(url_music)
						name_music = f"{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y~%H-%M')}.mp3"
						with open(name_music, "wb") as file:
							file.write(url_music.content)
						html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
						border-radius: 10px; margin: 10px -50px auto 10px'><audio src='{name_music}' controls='controls'></audio>
						<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
						{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px; font-size: 10px;
						font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
				elif getHistory["items"][i]["attachments"][0]["type"] == "doc":
					if DOWNLOAD_DOCUMENT == 0:
						url_doc = getHistory["items"][i]["attachments"][0]["doc"]["url"]
						html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
						border-radius: 10px; margin: 10px -50px auto 10px'><audio src='{url_doc}' controls='controls'></audio>
						<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
						{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px; font-size: 10px;
						font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
					elif DOWNLOAD_DOCUMENT == 1:
						url_doc = getHistory["items"][i]["attachments"][0]["doc"]["url"]
						doc_type = getHistory["items"][i]["attachments"][0]["doc"]["ext"]
						url_doc = requests.get(url_doc)
						name_doc = f"{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y~%H-%M')}.{doc_type}"
						if doc_type == "jpg" or "png":
							with open(name_doc, "wb") as file:
								file.write(url_doc.content)
							html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
							border-radius: 10px; margin: 10px -50px auto 10px'><img src='{name_doc}'><span style='font-size: 10px;
							color: #000; font-weight: bold; margin-left: 5px'>{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px; font-size: 10px;
							font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
						elif doc_type == "mp3":
							with open(name_doc, "wb") as file:
								file.write(url_doc.content)
							html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
							border-radius: 10px; margin: 10px -50px auto 10px'><audio src='{name_doc}' controls='controls'></audio>
							<span style='font-size: 10px; color: #000; font-weight: bold;
							margin-left: 5px'>{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px; font-size: 10px;
							font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
			elif len(getHistory["items"][i]["attachments"]) < 1:
				html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
				border-radius: 10px; margin: 0px -50px auto 10px'>{getHistory["items"][i]["text"]}<span style='font-size: 10px;
				color: #000; font-weight: bold; margin-left: 5px'>{getUsers[0]["first_name"]}</span></div><div style='display: block; padding: 10px; font-size: 10px;
						font-weight: bold'>{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y %H:%M')}</div><br>'''
	except KeyboardInterrupt:
		print(error + "Выход")

	html_join = html1 + html2 + html3

	###################################################################
	with open("chat.html", "w", encoding="utf-8") as file:
		file.write(html_join)
		
	print(succes + "Диалог скачан")