import sys
import vk_api
from cfg import token
import requests
from datetime import datetime as dt
import os
import time
import locale
from logs import *

#function for authorization in vk.com
def auth():
	global session
	session = vk_api.VkApi(token = token)
	succes("Авторизация!")

#####################################
def dwn_pst(id_, count_, _photo=0, _music=0, _doc=0, _folder=0, _af=0, _q=""):

	SIZE_PHOTO = 0

	if _q == "s":
		SIZE_PHOTO == 5
	elif _q == "m":
		SIZE_PHOTO == 0
	elif _q == "p":
		SIZE_PHOTO == 2
	elif _q == "q":
		SIZE_PHOTO == 3
	elif _q == "r":
		SIZE_PHOTO == 4
	elif _q == "x":
		SIZE_PHOTO == 7
	elif _q == "y":
		SIZE_PHOTO == 8
	elif _q == "w":
		SIZE_PHOTO == 6
	else:
		pass

	if _af == 1:
		_photo, _music, _doc = 1, 1, 1

	auth()

	try:
		if _folder != 0:
			os.mkdir(_folder)
	except FileExistsError:
		info("Такая папка уже существует!")

	#get posts history
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
					error("Пользователь/группа не существует, либо отсутствуют посты!!")
					sys.exit(1)
	except KeyboardInterrupt:
		warn("Выход!")
		sys.exit(1)
	except vk_api.exceptions.ApiError as err:
		err = str(err)
		if err[1] == "5":
				error("Ошибка авторизации! Токен неправильный или срок его действия истёк!")
				vkhost = str(input("Получить токен (y - да, n - нет) : "))
				if vkhost.strip() == "y":
					vkhost_ = webbrowser.open("https://vkhost.github.io")
					sys.exit(1)
				elif vkhost.strip() == "n":
					sys.exit(1)
				else:
					info("Непонимаю вас!")
					sys.exit(1)
		elif err[1:4] == "100":
			error("Неправильный id пользователя/группы")
			sys.exit(1)

	#get name user/group
	try:
		if len(getWall["groups"]) >= 1:
			name = getWall["groups"][0]["name"]
			succes("Название диалога получено!")
		else:
			name = getWall["profiles"][0]["first_name"] + " " + getWall["profiles"][0]["last_name"]
			succes("Название диалога получено!")
	except KeyboardInterrupt:
		warn("Выход!")
		sys.exit(1)

	#get avatar user/group
	try:
		if len(getWall["groups"]) >= 1:
			ava = getWall["groups"][0]["photo_100"]
			ava = requests.get(ava)
			succes("Аватарка получена!")
		else:
			ava = getWall["profiles"][0]["photo_100"]
			ava = requests.get(ava)
			succes("Аватарка получена!")
	except KeyboardInterrupt:
		warn("Выход!")
		sys.exit(1)

	#create link on user/group
	try:
		if len(getWall["groups"]) >= 1:
			link_user = "https://vk.com/" + getWall["groups"][0]["screen_name"]
			succes("Ссылка на группу получена!")
		else:
			link_user = "https://vk.com/" + getWall["profiles"][0]["screen_name"]
			succes("Ссылка на пользователя получена!")
	except KeyboardInterrupt:
		warn("Выход!")
		sys.exit(1)

	#get count users (only for groups)
	try:
		if "members_count" in getWall["groups"][0].keys():
			users = "<center style='font-family: sans-serif; color: #fff; padding: 10px'>Участиков: " + str(getWall["groups"][0]["members_count"]) + "</center>"
			succes("Количество участников получено!")
		else:
			users = ""
			info("Количество пользователей не получено!")
	except KeyboardInterrupt:
		warn("Выход!")
		sys.exit(1)

	#count posts
	try:
		posts_count = "<center style='font-family: sans-serif; color: #fff; padding: 10px'>Количество постов: " + str(getWall["count"]) + "</center>"
	except KeyboardInterrupt:
		warn("Выход!")
		sys.exit(1)

	#если указана папка для сохранения, аватарка сохраняется в неё
	try:
		if _folder == 0:
			with open("ava.jpg", "wb") as ava_:
				ava_.write(ava.content)
				succes("Аватарка скачана!")
		elif _folder != 0:
			with open(f"{_folder}/ava.jpg", "wb") as ava_:
				ava_.write(ava.content)
				succes("Аватарка скачана!")
	except KeyboardInterrupt:
		warn("Выход!")
		sys.exit(1)

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
			{posts_count}
		</div>'''

	html2 = ""

	html3 = '''
	</body>
</html>'''

	succes("Html шаблоны созданы!")

	#formating dialog
	try:
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
								file.write(url_msuic.content)
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
	except KeyboardInterrupt:
		warn("Выход!")
		sys.exit(1)

	#joined all fragments html templates
	html_join = html1 + html2 + html3

	try:
		if _folder == 0:
			with open(f"Посты_{name}.html", "w", encoding="utf-8") as file:
				file.write(html_join)
				succes("Посты сохранены!")
		elif _folder != 0:
			with open(f"{_folder}/Посты_{name}.html", "w", encoding="utf-8") as file:
				file.write(html_join)
				succes("Посты сохранены!")
	except KeyboardInterrupt:
		warn("Выход!")
		sys.exit(1)