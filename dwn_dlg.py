import sys
import vk_api
from cfg import token
import requests
from datetime import datetime as dt
import os
import time
import locale
from logs import *

#if in cfg don't have token
if token == "":
	error("Отсутствует токен!")
	sys.exit(1)

#set local language
locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")

#function for authorization in vk.com
def auth():
	global session
	session = vk_api.VkApi(token = token)
	succes("Авторизация!")

#
ALL = 1

#main function
def dwn_dlg(id_, count_, _photo=0, _audio=0, _music=0, _doc=0, _sd=0, _folder=0, _af=0, _ul=0, _cv=0, _all=0):
	global getHistory
	global html2
	global off
	html2 = ""
	off = 0
	auth()
	
	if _all == 0:
		try:
			getHistory = session.method("messages.getHistory", {
				"user_id": id_,
				"count": count_,
				"extended": 1,
				})
			if getHistory["count"] == 0 :
				getHistory = session.method("messages.getHistory", {
					"peer_id": "-" + str(id_),
					"count": count_,
					"extended": 1
					})
				if getHistory["count"] == 0 and len(str(id_)) < 5:
					_id_ = "2000000000"[0:10 - len(str(id_))] + str(id_)
					getHistory = session.method("messages.getHistory", {
						"peer_id": _id_,
						"count": count_,
						"extended": 1
						})
					if getHistory["count"] == 0:
						sys.exit(1)
			elif getHistory["count"] < count_:
				sys.exit(1)
		except KeyboardInterrupt:
			sys.exit(1)
		except vk_api.exceptions.ApiError as err:
			err = str(err)
			if err[1] == "5":
				sys.exit(1)
			elif err[1:4] == "100":
				sys.exit(1)

		succes("Получена история диалога!")

		if len(getHistory["items"]) < count_:
			warn(f"В диалоге нет {count_} сообщений!")
			sys.exit(1)

		type_ = getHistory["conversations"][0]["peer"]["type"]
		if type_ == "chat":
			name = getHistory["conversations"][0]["chat_settings"]["title"]
			succes("Название диалога получено!")
		elif type_ == "user":
			name = getHistory["profiles"][0]["first_name"] + " " + getHistory["profiles"][0]["last_name"]
			succes("Название диалога получено!")
		elif type_ == "group":
			name = getHistory["groups"][0]["name"]
			succes("Название диалога получено!")

		if getHistory["conversations"][0]["peer"]["type"] == "user":
			link_user = "https://vk.com/" + getHistory["profiles"][0]["screen_name"]
			succes("Ссылка на пользователя/группу получена!")
		elif getHistory["conversations"][0]["peer"]["type"] == "chat":
			link_user = "#"
			info("Ссылка на беседу не оставляется!")
		elif getHistory["conversations"][0]["peer"]["type"] == "group":
			link_user = "https://vk.com/" + getHistory["groups"][0]["screen_name"]
			succes("Ссылка на пользователя/группу получена!")
		
		if getHistory["conversations"][0]["peer"]["type"] == "user":
			users = ""
			info("Количество участников недоступно в диалоге с пользователем!")
		elif getHistory["conversations"][0]["peer"]["type"] == "chat":
			users = f"<center style='color: #fff; padding: 10px'>Участиков: {str(getHistory['conversations'][0]['chat_settings']['members_count'])}</center>"
			succes("Количество участников группы/беседы получено!")

		avatar = ""
		try:
			if getHistory["conversations"][0]["peer"]["type"] == "user":
				avatar = getHistory["profiles"][0]["photo_100"]
				avatar = requests.get(avatar)
				succes("Аватарка получена!")
			elif getHistory["conversations"][0]["peer"]["type"] == "chat":
				avatar = getHistory["conversations"][0]["chat_settings"]["photo"]["photo_100"]
				avatar = requests.get(avatar)
				succes("Аватарка получена!")
			elif getHistory["conversations"][0]["peer"]["type"] == "groups":
				avatar = getHistory["groups"][0]["photo_100"]
				avatar = requests.get(avatar)
				succes("Аватарка получена!")
		except KeyError:
			avatar = "templates/avatar.png"
			info("Аватрка отсутствует! Установлена аватарка по умолчанию!")

		try:
			if _folder == 0:
				with open("avatar.jpg", "wb") as avatar_:
					avatar_.write(avatar.content)
					avatar = "avatar.jpg"
			elif _folder != 0:
				with open(f"{_folder}/avatar.jpg", "wb") as avatar_:
					avatar_.write(avatar.content)
					avatar = "avatar.jpg"
			succes("Аватарка скачана!")
		except AttributeError:
			pass

		#html components
		style = '''::-webkit-scrollbar {
					width: 12px;
				}
					 
				::-webkit-scrollbar-track {
						background-color: rgba(0, 0, 0, 0.3)
				}
					 
				::-webkit-scrollbar-thumb {
					-webkit-border: 1px #fff;
					border-radius: 20px;
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
							<title>{name}</title>
							<style>
							{style}
							</style>
						</head>
						<body style='background-color: #333;'>
							<div style='width: 750px; margin: 10px auto 10px auto; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 20px'>
								<center><a href='{link_user}' target='_blank'><img src='{avatar}' style='height: 100px; border-radius: 100px; margin-top: 20px; box-shadow: 0px 0px 10px #000'></a></center>
								<center style='padding: 10px; font-size: 20px; color: #fff'>{name}</center>
								{users}
							</div>
							<div style='width: 750px; box-sizing: padding-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 20px; margin-left: auto; margin-right: auto'>'''

		html2 = ""

		html3 = '''
						</div>
					</body>
				</html>'''

		succes("Html шаблоны созданы!")

		SIZE_PHOTO = 100
		try:
			for i in range(int(count_)):
				try:
					getUsers = session.method("users.get", {
						"user_ids": getHistory["items"][i]["from_id"],
						"fields": "photo_50"
						})
				except IndexError:
					getUsers = session.method("users.get", {
						"user_ids": getHistory[i]["from_id"],
						"fields": "photo_50"})

				if _ul == 1:
					user = f"<a href='https://vk.com/id{getHistory['items'][i]['from_id']}'>{getUsers[0]['first_name']}</a>"
				else:
					user = getUsers[0]["first_name"]

				if type_ == "chat":
					ava_msg = getUsers[0]["photo_50"]
					ava_msg = f"<div style='padding: 5px; float: left'><img src='{ava_msg}' style='border-radius: 50px; height: 50px'></div>"
				else:
					ava_msg = ""

				if len(getHistory["items"][i]["attachments"]) >= 1:
					if getHistory["items"][i]["attachments"][0]["type"] == "photo":
						sms = getHistory["items"][i]["text"]			
						if _photo == 0:
							if SIZE_PHOTO == 100:
								size_photo = str(input("В каком качестве вставлять изображения (s(75px), m(130px), x(604px)): "))
								if size_photo == "s":
									SIZE_PHOTO = 5
								elif size_photo == "m":
									SIZE_PHOTO = 0
								elif size_photo == "x":
									SIZE_PHOTO = 6
								else:
									SIZE_PHOTO = 0

							url_photo = getHistory["items"][i]["attachments"][0]["photo"]["sizes"][SIZE_PHOTO]["url"]

							if getHistory["items"][i]["text"] != "":
								html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
												{sms}<br><br>
												<img src='{url_photo}' style='height: 200px; border-radius: 20px; box-shadow: 0px 0px 10px #000'>
												<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
													{user}
												</span>
											</div>
											<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
												{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
											</div>
											<br>'''
							elif getHistory["items"][i]["text"] == "":
								html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
												<img src='{url_photo}' style='height: 200px; border-radius: 20px; box-shadow: 0px 0px 10px #000'>
												<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
													{user}
												</span>
											</div>
											<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
												{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
											</div>
											<br>'''
						elif _photo == 1:
							size_photo = str(input("В каком качестве скачивать изображения (s(75px), m(130px), x(604px)): "))
							if SIZE_PHOTO == 100:
								size_photo = str(input("В каком качестве вставлять изображения (s(75px), m(130px), x(604px)): "))
								if size_photo == "s":
									SIZE_PHOTO = 5
								elif size_photo == "m":
									SIZE_PHOTO = 0
								elif size_photo == "x":
									SIZE_PHOTO = 6
								else:
									SIZE_PHOTO = 0

							url_photo = requests.get(getHistory["items"][i]["attachments"][0]["photo"]["sizes"][SIZE_PHOTO]["url"])
							name_photo = f"{(dt.fromtimestamp(getHistory['items'][i]['attachments'][0]['photo']['date'])).strftime('%d-%m-%y~%H-%M-%S')}_{getUsers[0]['first_name']}.jpg"
							if _folder == 0:
								with open(name_photo, "wb") as file:
									file.write(url_photo.content)
							elif _folder != 0:
								with open(f"{_folder}/{name_photo}", "wb") as file:
									file.write(url_photo.content)
							if getHistory["items"][i]["text"] != "":
								html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
												{sms}
												<br>
												<img src='{name_photo}' style='height: 200px; border-radius: 20px; box-shadow: 0px 0px 10px #000'>
												<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
													{user}
												</span>
											</div>
											<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
												{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
											</div>
											<br>'''
							elif getHistory["items"][i]["text"] == "":
								html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
												<img src='{name_photo}' style='height: 200px; border-radius: 20px;'>
												<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
													{user}
												</span>
											</div>
											<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
												{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
											</div>
											<br>'''
					elif getHistory["items"][i]["attachments"][0]["type"] == "audio_message":
						sms = getHistory["items"][i]["text"]
						if _audio == 0:
							url_audio = getHistory["items"][i]["attachments"][0]["audio_message"]["link_mp3"]
							if getHistory["items"][i]["text"] != "":
								
								html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
												{sms}
												<br>
												<audio src='{url_audio}' controls='controls'></audio>
												<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
													{user}
												</span>
											</div>
											<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
												{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
											</div>
											<br>'''
							elif getHistory["items"][i]["text"] == "":
								html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
												<audio src='{url_audio}' controls='controls'></audio>
												<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
													{user}
												</span>
											</div>
											<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
												{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
											</div>
											<br>'''
						elif _audio == 1:
							url_audio = requests.get(getHistory["items"][i]["attachments"][0]["audio_message"]["link_mp3"])
							name_audio = f"{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y~%H-%M-%S')}.mp3"
							if _folder == 0:
								with open(name_audio, "wb") as file:
									file.write(url_audio.content)
							elif _folder != 0:
								with open(f"{_folder}/{name_audio}", "wb") as file:
									file.write(url_audio.content)
							if getHistory["items"][i]["text"] != "":
								
								html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
												{sms}
												<br>
												<audio src='{name_audio}' controls='controls'></audio>
												<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
													{user}
												</span>
											</div>
											<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
												{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
											</div>
											<br>'''
							elif getHistory["items"][i]["text"] == "":
								html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
												<audio src='{name_audio}' controls='controls'></audio>
												<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
													{user}
												</span>
											</div>
											<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
												{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
											</div>
											<br>'''
					elif getHistory["items"][i]["attachments"][0]["type"] == "audio":
						sms = getHistory["items"][i]["text"]
						if _music == 0:
							url_music = getHistory["items"][i]["attachments"][0]["audio"]["url"]
							explicit = getHistory['items'][i]['attachments'][0]['audio']['is_explicit']

							if explicit == True:
								explicit = "🅴"
							else:
								explicit = ""

							if getHistory["items"][i]["text"] != "":		
								if _cv != 0:
									photo_music = getHistory['items'][0]['attachments'][0]['audio']['album']['thumb']['photo_135']
									audio_title = getHistory['items'][0]['attachments'][0]['audio']['title']
									artist = getHistory['items'][0]['attachments'][0]['audio']['artist']
									album = getHistory['items'][0]['attachments'][0]['audio']['album']['title']
									if photo_music != "":
										dwn_track_photo = str(input("Скачивать обложки треков (y - да, n - нет): "))
										if dwn_track_photo == "y":
											title = audio_title.split()
											title = ''.join(title)
											title = title + "_" + artist
											if _folder == 0:
												photo_music = requests.get(photo_music)
												with open(f"{title}.jpg", "wb") as file:
													file.write(photo_music.content)
												photo_music = title
											else:
												photo_music = requests.get(photo_music)
												with open(f"{_folder}/{title}.jpg", "wb") as file:
													file.write(photo_music.content)
												photo_music = title
									audio = f'''<div style=''>
													<img src='{photo_music}' style='border-radius: 20px'>
													<span style=''>{audio_title} {explicit}</span>
													<span style=''>{artist}</span>
													<span style=''>{album}</span>
													<audio src='{url_music}' controls='controls'></audio>
												</div>'''

									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													{audio}
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</div>
												<br>'''
								else:
									audio = f"<audio src='{url_music}' controls='controls'></audio>"
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													{sms}
													<br>
													{audio}
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</div>
												<br>'''
							elif getHistory["items"][i]["text"] == "":	
								if _cv != 0:
									photo_music = getHistory['items'][0]['attachments'][0]['audio']['album']['thumb']['photo_135']
									audio_title = getHistory['items'][0]['attachments'][0]['audio']['title']
									artist = getHistory['items'][0]['attachments'][0]['audio']['artist']
									album = getHistory['items'][0]['attachments'][0]['audio']['album']['title']
									if photo_music != "":
										dwn_track_photo = str(input("Скачивать обложки треков (y - да, n - нет): "))
										if dwn_track_photo == "y":
											title = audio_title.split()
											title = ''.join(title)
											title = title + "_" + artist
											if _folder == 0:
												photo_music = requests.get(photo_music)
												with open(f"{title}.jpg", "wb") as file:
													file.write(photo_music.content)
												photo_music = title
											else:
												photo_music = requests.get(photo_music)
												with open(f"{_folder}/{title}.jpg", "wb") as file:
													file.write(photo_music.content)
												photo_music = title
									audio = f'''<div style=''>
													<img src='{photo_music}' style='border-radius: 20px'>
													<span style=''>{audio_title} {explicit}</span>
													<span style=''>{artist}</span>
													<span style=''>{album}</span>
													<audio src='{url_music}' controls='controls'></audio>
												</div>'''

									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													{audio}
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</div>
												<br>'''
								else:
									audio = f"<audio src='{url_music}' controls='controls'></audio>"
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													{audio}
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</div>
												<br>'''
						elif _music == 1:
							url_music = requests.get(getHistory["items"][i]["attachments"][0]["audio"]["url"])
							name_music = f"{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y~%H-%M-%S')}.mp3"
							if getHistory["items"][i]["text"] != "":		
								if _cv != 0:
									photo_music = getHistory['items'][0]['attachments'][0]['audio']['album']['thumb']['photo_135']
									audio_title = getHistory['items'][0]['attachments'][0]['audio']['title']
									artist = getHistory['items'][0]['attachments'][0]['audio']['artist']
									album = getHistory['items'][0]['attachments'][0]['audio']['album']['title']
									if photo_music != "":
										dwn_track_photo = str(input("Скачивать обложки треков (y - да, n - нет): "))
										if dwn_track_photo == "y":
											title = audio_title.split()
											title = ''.join(title)
											title = title + "_" + artist
											if _folder == 0:
												photo_music = requests.get(photo_music)
												with open(f"{title}.jpg", "wb") as file:
													file.write(photo_music.content)
												photo_music = title
											else:
												photo_music = requests.get(photo_music)
												with open(f"{_folder}/{title}.jpg", "wb") as file:
													file.write(photo_music.content)
												photo_music = title
									audio = f'''<div style=''>
													<img src='{photo_music}' style='border-radius: 20px'>
													<span style=''>{audio_title} {explicit}</span>
													<span style=''>{artist}</span>
													<span style=''>{album}</span>
													<audio src='{url_music}' controls='controls'></audio>
												</div>'''

									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													{audio}
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</div>
												<br>'''
								else:
									audio = f"<audio src='{url_music}' controls='controls'></audio>"
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													{sms}
													<br>
													{audio}
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</div>
												<br>'''
							elif getHistory["items"][i]["text"] == "":
								if _cv != 0:
									photo_music = getHistory['items'][0]['attachments'][0]['audio']['album']['thumb']['photo_135']
									audio_title = getHistory['items'][0]['attachments'][0]['audio']['title']
									artist = getHistory['items'][0]['attachments'][0]['audio']['artist']
									album = getHistory['items'][0]['attachments'][0]['audio']['album']['title']
									if photo_music != "":
										dwn_track_photo = str(input("Скачивать обложки треков (y - да, n - нет): "))
										if dwn_track_photo == "y":
											title = audio_title.split()
											title = ''.join(title)
											title = title + "_" + artist
											if _folder == 0:
												photo_music = requests.get(photo_music)
												with open(f"{title}.jpg", "wb") as file:
													file.write(photo_music.content)
												photo_music = title
											else:
												photo_music = requests.get(photo_music)
												with open(f"{_folder}/{title}.jpg", "wb") as file:
													file.write(photo_music.content)
												photo_music = title
									audio = f'''<div style=''>
													<img src='{photo_music}' style='border-radius: 20px'>
													<span style=''>{audio_title} {explicit}</span>
													<span style=''>{artist}</span>
													<span style=''>{album}</span>
													<audio src='{url_music}' controls='controls'></audio>
												</div>'''

									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													{audio}
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</div>
												<br>'''
								else:
									audio = f"<audio src='{url_music}' controls='controls'></audio>"
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													{audio}
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												/div>
												<br>'''
					elif getHistory["items"][i]["attachments"][0]["type"] == "doc":
						sms = getHistory["items"][i]["text"]
						if _doc == 0:
							url_doc = getHistory["items"][i]["attachments"][0]["doc"]["url"]
							if getHistory["items"][i]["text"] != "":
									
								html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
												{sms}
												<br>
												<a href='{url_doc}'>
													ДОКУМЕНТ
												</a>
												<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
													{user}
												</span>
											</div>
											<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
												{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
											</div>
											<br>'''
							elif getHistory["items"][i]["text"] == "":
								
								html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
												<a href='{url_doc}'>
													ДОКУМЕНТ
												</a>
												<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
													{getUsers[0]["first_name"]}
												</span>
											</div>
											<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
												{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
											</div>
											<br>'''
						elif _doc == 1:
							url_doc = getHistory["items"][i]["attachments"][0]["doc"]["url"]
							doc_type = requests.get(getHistory["items"][i]["attachments"][0]["doc"]["ext"])
							name_doc = f"{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y~%H-%M-%S')}.{doc_type}"
							
							if getHistory["items"][i]["text"] != "":
								sms = getHistory["items"][i]["text"]
								if doc_type == "jpg" or doc_type == "png" or doc_type == "bmp":
									
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													{sms}
													<br>
													<img src='{name_doc}'>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</div>
												<br>'''
									if _folder == 0:
										with open(f"name_doc", "wb") as file:
											file.write(url_doc.content)
									elif _folder != 0:
										with open(f"{_folder}/{name_doc}", "wb") as file:
											file.write(url_doc.content)
								elif doc_type == "mp3" or doc_type == "wav" or doc_type == "aac":
										
										html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
														{sms}
														<br>
														<audio src='{name_doc}' controls='controls'></audio>
														<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
															{user}
														</span>
													</div>
													<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
													</div>
													<br>'''

										if _folder == 0:
											with open(name_doc, "wb") as file:
												file.write(url_doc.content)
										elif _folder != 0:
											with open(f"{_folder}/{name_doc}", "wb") as file:
												file.write(url_doc.content)
							elif getHistory["items"][i]["text"] == "":
								if doc_type == "jpg" or doc_type == "png" or doc_type == "bmp":
									
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													{sms}
													<br>
													<img src='{name_doc}'>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</div>
												<br>'''
									if _folder == 0:
										with open(f"name_doc", "wb") as file:
											file.write(url_doc.content)
									elif _folder != 0:
										with open(f"{_folder}/{name_doc}", "wb") as file:
											file.write(url_doc.content)
								elif doc_type == "mp3" or doc_type == "wav" or doc_type == "aac":
									if getHistory["items"][i]["text"] != "":
										
										html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
														{sms}
														<br>
														<audio src='{name_doc}' controls='controls'></audio>
														<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
															{user}
														</span>
													</div>
													<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
													</div>
													<br>'''
										if _folder == 0:
											with open(f"name_doc", "wb") as file:
												file.write(url_doc.content)
										elif _folder != 0:
											with open(f"{_folder}/{name_doc}", "wb") as file:
												file.write(url_doc.content)
					elif getHistory["items"][i]["attachments"][0]["type"] == "poll":
						question = getHistory["items"][i]["attachments"][0]["poll"]["question"]
						answers = getHistory["items"][i]["attachments"][0]["poll"]["answers"]
						answers_ = ""

						for j in range(len(answers)):
							answer = getHistory["items"][i]["attachments"][0]["poll"]["answers"][j]["text"]
							vote = getHistory["items"][i]["attachments"][0]["poll"]["answers"][j]["votes"]
							rate = getHistory["items"][i]["attachments"][0]["poll"]["answers"][j]["rate"]

							answer_html = f'''<div style='width: 200px; height: 20px; background-color: rgba(255, 255, 255, .3); padding: 5px; border-radius: 5px; margin: 5px'>
										<span style='float: keft: margin-left: 10px; font-size: 15px'>{answer} · {vote}</span>
									</div>'''
							answers_ += answer_html

						poll = f'''<div style='color: #fff'>
										<center style='font-weight: bold; font-size: 15px'>ОПРОС</center>
										<center style='padding: 5px'>Вопрос: {question}</center>
										<div>
											{answers_}
										</div>
										<span></span>
									</div>'''
									
						html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 630px; background: linear-gradient(100deg, #ED4976, #3E48E3); padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
										{poll}
										<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
											{user}
										</span>
									</div>
									<div style='display: block; padding: 5px; font-size: 10px;font-weight: bold; margin-left: 5px'>
										{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
									</div>
									<br>'''
					elif getHistory["items"][i]["attachments"][0]["type"] == "money_request":
						comment = getHistory["items"][i]["text"]
						sum_ = getHistory["items"][i]["attachments"][0]["money_request"]["total_amount"]["amount"]
						finish_sum = f"{sum_[:-2:]}.{sum_[-2::]} {getHistory['items'][i]['attachments'][0]['money_request']['total_amount']['currency']['name']}"
						transferred = getHistory["items"][i]["attachments"][0]["money_request"]["transferred_amount"]["amount"]
						finish_post = f"{transferred[:-2:]}.{transferred[-2::]} {getHistory['items'][i]['attachments'][0]['money_request']['transferred_amount']['currency']['name']}"

						money_html = f'''<div style='color: #fff'>
											<span style='font-weight: bold; font-size: 20px'>ДЕНЕЖНЫЙ ЗАПРОС</span><br>
											<span>Сумма: {finish_sum}</span><br>
											<span>Собрано {transferred} из {finish_sum}</span><br>
											<span>Комментарий: {comment}</span>
										</div>'''

						html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 630px; background: linear-gradient(100deg, #ED4976, #3E48E3); padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
										{money_html}
										<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
											{user}
										</span>
									</div>
									<div style='display: block; padding: 5px; font-size: 10px;font-weight: bold; margin-left: 5px'>
										{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
									</div>
									<br>'''
					elif "sticker" in getHistory["items"][i]["attachments"][0]:
						sticker = getHistory["items"][i]["attachments"][0]["sticker"]["images"][1]["url"]
						if _sd == 0:
							html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
											<img src='{sticker}'>
											<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
												{user}
											</span>
										</div>
										<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold'>
											{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
										</div>
										<br>'''
						else:
							sticker = requests.get(sticker)
							stick_name = f"{getHistory['items'][i]['attachments'][0]['sticker']['product_id']}.png"
							html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
											<img src='{stick_name}'>
											<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
												{user}
											</span>
										</div>
										<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold'>
											{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
										</div>
										<br>'''

							if _folder == 0:
								with open(f"{stick_name}", "wb") as file:
									file.write(sticker.content)
							elif _folder != 0:
								with open(f"{_folder}/{stick_name}", "wb") as file:
									file.write(sticker.content)
				else:
					if "action" in getHistory["items"][i]:
						if getHistory["items"][i]["action"]["type"] == "chat_unpin_message":
							name_ = getUsers[0]["first_name"] + " " + getUsers[0]["last_name"]
							msg_ = ""
							if "message" in getHistory["items"][i]:
								msg_ = getHistory["items"][i]["action"]["message"]
							html2 += f'''<div style='display: block; text-align: center; padding: 5px; margin: 0 auto'>
											<span style='weight: bold'>{name_}</span> <span style='weight: liter'>открепил сообщение {msg_}</span>
										</div>
										<br>'''
						elif getHistory["items"][i]["action"]["type"] == "chat_pin_message":
							name_ = getUsers[0]["first_name"] + " " + getUsers[0]["last_name"]
							msg_ = ""
							if "message" in getHistory["items"][i]:
								msg_ = getHistory["items"][i]["action"]["message"]
							html2 += f'''<div style='display: block; text-align: center; padding: 5px; margin: 0 auto'>
											<span style='weight: bold'>{name_}</span> <span style='weight: liter'>закрепил сообщение {msg_}</span>
										</div>
										<br>'''
					else:
						sms = getHistory["items"][i]["text"]
						html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
										<code>{sms}</code>
										<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
											{user}
										</span>
									</div>
									<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold'>
										{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
									</div>
									<br>'''

			html_join = html1 + html2 + html3

			if _folder == 0:
				with open(f"{name}.html", "w", encoding="utf-8") as file:
					file.write(html_join)
					succes("Диалог сохранен!")
			elif _folder != 0:
				with open(f"{_folder}/{name}.html", "w", encoding="utf-8") as file:
					file.write(html_join)
					succes("Диалог сохранен!")
		except KeyboardInterrupt:
			warn("Выход!")
			sys.exit(1)
	elif _all == 1:
		#variables using for downloading all dialog
		v1 = 0
		v2 = 0
		v3 = 0
		v4 = 0
		v5 = 0
		#

		name = ""
		avatar = ""
		while True:
			try:
				getHistory = session.method("messages.getHistory", {
					"user_id": id_,
					"count": 200,
					"extended": 1,
					"offset": off
					})
				if getHistory["count"] == 0 :
					getHistory = session.method("messages.getHistory", {
						"peer_id": "-" + str(id_),
						"count": 200,
						"extended": 1,
						"offset": off
						})
					if getHistory["count"] == 0 and len(str(id_)) < 5:
						_id_ = "2000000000"[0:10 - len(str(id_))] + str(id_)
						getHistory = session.method("messages.getHistory", {
							"peer_id": _id_,
							"count": 200,
							"extended": 1,
							"offset": off
							})
						if getHistory["count"] == 0:
							sys.exit(1)
				elif getHistory["count"] < 200:
					sys.exit(1)
			except KeyboardInterrupt:
				warn("Выход!")
				sys.exit(1)
			except vk_api.exceptions.ApiError as err:
				err = str(err)
				if err[1] == "5":
					sys.exit(1)
				elif err[1:4] == "100":
					sys.exit(1)

			if v5 != 1:
				succes("Получена история диалога!")
				v5 = 1

			if len(getHistory["items"]) < count_:
				warn(f"В диалоге нет {count_} сообщений!")
				sys.exit(1)

			type_ = getHistory["conversations"][0]["peer"]["type"]
			if v1 != 1:
				if name == "":
					if type_ == "chat":
						name = getHistory["conversations"][0]["chat_settings"]["title"]
						succes("Название диалога получено!")
					elif type_ == "user":
						name = getHistory["profiles"][0]["first_name"] + " " + getHistory["profiles"][0]["last_name"]
						succes("Название диалога получено!")
					elif type_ == "group":
						name = getHistory["groups"][0]["name"]
						succes("Название диалога получено!")

				if getHistory["conversations"][0]["peer"]["type"] == "user":
					link_user = "https://vk.com/" + getHistory["profiles"][0]["screen_name"]
					succes("Ссылка на пользователя/группу получена!")
				elif getHistory["conversations"][0]["peer"]["type"] == "chat":
					link_user = "#"
					info("Ссылка на беседу не оставляется!")
				elif getHistory["conversations"][0]["peer"]["type"] == "group":
					link_user = "https://vk.com/" + getHistory["groups"][0]["screen_name"]
					succes("Ссылка на пользователя/группу получена!")
				v1 = 1
			
			if v2 != 1:
				if getHistory["conversations"][0]["peer"]["type"] == "user":
					users = ""
					succes("Количество пользователей получено!")
				elif getHistory["conversations"][0]["peer"]["type"] == "chat":
					users = f"<center style='color: #fff; padding: 10px'>Участиков: {str(getHistory['conversations'][0]['chat_settings']['members_count'])}</center>"
					succes("Количество пользователей получено!")
				v2 = 1

			avatar = ""
			if v3 != 1:
				try:
					if getHistory["conversations"][0]["peer"]["type"] == "user":
						avatar = getHistory["profiles"][0]["photo_100"]
						avatar = requests.get(avatar)
						succes("Аватарка получена!")
					elif getHistory["conversations"][0]["peer"]["type"] == "chat":
						avatar = getHistory["conversations"][0]["chat_settings"]["photo"]["photo_100"]
						avatar = requests.get(avatar)
						succes("Аватарка получена!")
					elif getHistory["conversations"][0]["peer"]["type"] == "groups":
						avatar = getHistory["groups"][0]["photo_100"]
						avatar = requests.get(avatar)
						succes("Аватарка получена!")
				except KeyError:
					avatar = "templates/avatar.png"
					info("Аватарка отсутствует! Установлена аватарка по умолчанию!")

				try:
					if _folder == 0:
						with open("avatar.jpg", "wb") as avatar_:
							avatar_.write(avatar.content)
							avatar = "avatar.jpg"
					elif _folder != 0:
						with open(f"{_folder}/avatar.jpg", "wb") as avatar_:
							avatar_.write(avatar.content)
							avatar = "avatar.jpg"
					succes("Аватарка скачана!")
				except AttributeError:
					pass
				v3 = 1

			#html components
			style = '''::-webkit-scrollbar {
						width: 12px;
					}
						 
					::-webkit-scrollbar-track {
							background-color: rgba(0, 0, 0, 0.3)
					}
						 
					::-webkit-scrollbar-thumb {
						-webkit-border: 1px #fff;
						border-radius: 20px;
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
								<title>{name}</title>
								<style>
								{style}
								</style>
							</head>
							<body style='background-color: #333;'>
								<div style='width: 750px; margin: 10px auto 10px auto; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 20px'>
									<center><a href='{link_user}' target='_blank'><img src='avatar.jpg' style='height: 100px; border-radius: 100px; margin-top: 20px; box-shadow: 0px 0px 10px #000'></a></center>
									<center style='padding: 10px; font-size: 20px; color: #fff'>{name}</center>
									{users}
								</div>
								<div style='width: 750px; box-sizing: padding-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 20px; margin-left: auto; margin-right: auto'>'''

			html3 = '''
							</div>
						</body>
					</html>'''
			
			if v4 != 1:
				succes("Html шаблоны созданы!")
				v4 = 1

			SIZE_PHOTO = 5
			try:
				for i in range(int(200)):
					try:
						getUsers = session.method("users.get", {
							"user_ids": getHistory["items"][i]["from_id"],
							"fields": "photo_50"
							})
					except IndexError:
						getUsers = session.method("users.get", {
							"user_ids": getHistory[i]["from_id"],
							"fields": "photo_50"})

					if _ul == 1:
						user = f"<a href='https://vk.com/id{getHistory['items'][i]['from_id']}'>{getUsers[0]['first_name']}</a>"
					else:
						user = getUsers[0]["first_name"]

					if type_ == "chat":
						ava_msg = getUsers[0]["photo_50"]
						ava_msg = f"<div style='padding: 5px; float: left'><img src='{ava_msg}' style='border-radius: 50px; height: 50px'></div>"
					else:
						ava_msg = ""

					if len(getHistory["items"][i]["attachments"]) >= 1:
						if getHistory["items"][i]["attachments"][0]["type"] == "photo":
							sms = getHistory["items"][i]["text"]			
							if _photo == 0:
								if SIZE_PHOTO == 100:
									size_photo = str(input("В каком качестве вставлять изображения (s(75px), m(130px), x(604px)): "))
									if size_photo == "s":
										SIZE_PHOTO = 5
									elif size_photo == "m":
										SIZE_PHOTO = 0
									elif size_photo == "x":
										SIZE_PHOTO = 6
									else:
										SIZE_PHOTO = 0

								url_photo = getHistory["items"][i]["attachments"][0]["photo"]["sizes"][SIZE_PHOTO]["url"]

								if getHistory["items"][i]["text"] != "":
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													{sms}<br><br>
													<img src='{url_photo}' style='height: 200px; border-radius: 20px; box-shadow: 0px 0px 10px #000'>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</div>
												<br>'''
								elif getHistory["items"][i]["text"] == "":
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													<img src='{url_photo}' style='height: 200px; border-radius: 20px; box-shadow: 0px 0px 10px #000'>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</div>
												<br>'''
							elif _photo == 1:
								size_photo = str(input("В каком качестве скачивать изображения (s(75px), m(130px), x(604px)): "))
								if SIZE_PHOTO == 100:
									size_photo = str(input("В каком качестве вставлять изображения (s(75px), m(130px), x(604px)): "))
									if size_photo == "s":
										SIZE_PHOTO = 5
									elif size_photo == "m":
										SIZE_PHOTO = 0
									elif size_photo == "x":
										SIZE_PHOTO = 6
									else:
										SIZE_PHOTO = 0

								url_photo = requests.get(getHistory["items"][i]["attachments"][0]["photo"]["sizes"][SIZE_PHOTO]["url"])
								name_photo = f"{(dt.fromtimestamp(getHistory['items'][i]['attachments'][0]['photo']['date'])).strftime('%d-%m-%y~%H-%M-%S')}_{getUsers[0]['first_name']}.jpg"
								if _folder == 0:
									with open(name_photo, "wb") as file:
										file.write(url_photo.content)
								elif _folder != 0:
									with open(f"{_folder}/{name_photo}", "wb") as file:
										file.write(url_photo.content)
								if getHistory["items"][i]["text"] != "":
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													{sms}
													<br>
													<img src='{name_photo}' style='height: 200px; border-radius: 20px; box-shadow: 0px 0px 10px #000'>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</div>
												<br>'''
								elif getHistory["items"][i]["text"] == "":
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													<img src='{name_photo}' style='height: 200px; border-radius: 20px;'>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</div>
												<br>'''
						elif getHistory["items"][i]["attachments"][0]["type"] == "audio_message":
							sms = getHistory["items"][i]["text"]
							if _audio == 0:
								url_audio = getHistory["items"][i]["attachments"][0]["audio_message"]["link_mp3"]
								if getHistory["items"][i]["text"] != "":
									
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													{sms}
													<br>
													<audio src='{url_audio}' controls='controls'></audio>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</div>
												<br>'''
								elif getHistory["items"][i]["text"] == "":
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													<audio src='{url_audio}' controls='controls'></audio>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</div>
												<br>'''
							elif _audio == 1:
								url_audio = requests.get(getHistory["items"][i]["attachments"][0]["audio_message"]["link_mp3"])
								name_audio = f"{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y~%H-%M-%S')}.mp3"
								if _folder == 0:
									with open(name_audio, "wb") as file:
										file.write(url_audio.content)
								elif _folder != 0:
									with open(f"{_folder}/{name_audio}", "wb") as file:
										file.write(url_audio.content)
								if getHistory["items"][i]["text"] != "":
									
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													{sms}
													<br>
													<audio src='{name_audio}' controls='controls'></audio>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</div>
												<br>'''
								elif getHistory["items"][i]["text"] == "":
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													<audio src='{name_audio}' controls='controls'></audio>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</div>
												<br>'''
						elif getHistory["items"][i]["attachments"][0]["type"] == "audio":
							sms = getHistory["items"][i]["text"]
							if _music == 0:
								url_music = getHistory["items"][i]["attachments"][0]["audio"]["url"]
								explicit = getHistory['items'][i]['attachments'][0]['audio']['is_explicit']

								if explicit == True:
									explicit = "🅴"
								else:
									explicit = ""

								if getHistory["items"][i]["text"] != "":		
									if _cv != 0:
										photo_music = getHistory['items'][0]['attachments'][0]['audio']['album']['thumb']['photo_135']
										audio_title = getHistory['items'][0]['attachments'][0]['audio']['title']
										artist = getHistory['items'][0]['attachments'][0]['audio']['artist']
										album = getHistory['items'][0]['attachments'][0]['audio']['album']['title']
										if photo_music != "":
											dwn_track_photo = str(input("Скачивать обложки треков (y - да, n - нет): "))
											if dwn_track_photo == "y":
												title = audio_title.split()
												title = ''.join(title)
												title = title + "_" + artist
												if _folder == 0:
													photo_music = requests.get(photo_music)
													with open(f"{title}.jpg", "wb") as file:
														file.write(photo_music.content)
													photo_music = title
												else:
													photo_music = requests.get(photo_music)
													with open(f"{_folder}/{title}.jpg", "wb") as file:
														file.write(photo_music.content)
													photo_music = title
										audio = f'''<div style=''>
														<img src='{photo_music}' style='border-radius: 20px'>
														<span style=''>{audio_title} {explicit}</span>
														<span style=''>{artist}</span>
														<span style=''>{album}</span>
														<audio src='{url_music}' controls='controls'></audio>
													</div>'''

										html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
														{audio}
														<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
															{user}
														</span>
													</div>
													<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
													</div>
													<br>'''
									else:
										audio = f"<audio src='{url_music}' controls='controls'></audio>"
										html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
														{sms}
														<br>
														{audio}
														<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
															{user}
														</span>
													</div>
													<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
													</div>
													<br>'''
								elif getHistory["items"][i]["text"] == "":	
									if _cv != 0:
										photo_music = getHistory['items'][0]['attachments'][0]['audio']['album']['thumb']['photo_135']
										audio_title = getHistory['items'][0]['attachments'][0]['audio']['title']
										artist = getHistory['items'][0]['attachments'][0]['audio']['artist']
										album = getHistory['items'][0]['attachments'][0]['audio']['album']['title']
										if photo_music != "":
											dwn_track_photo = str(input("Скачивать обложки треков (y - да, n - нет): "))
											if dwn_track_photo == "y":
												title = audio_title.split()
												title = ''.join(title)
												title = title + "_" + artist
												if _folder == 0:
													photo_music = requests.get(photo_music)
													with open(f"{title}.jpg", "wb") as file:
														file.write(photo_music.content)
													photo_music = title
												else:
													photo_music = requests.get(photo_music)
													with open(f"{_folder}/{title}.jpg", "wb") as file:
														file.write(photo_music.content)
													photo_music = title
										audio = f'''<div style=''>
														<img src='{photo_music}' style='border-radius: 20px'>
														<span style=''>{audio_title} {explicit}</span>
														<span style=''>{artist}</span>
														<span style=''>{album}</span>
														<audio src='{url_music}' controls='controls'></audio>
													</div>'''

										html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
														{audio}
														<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
															{user}
														</span>
													</div>
													<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
													</div>
													<br>'''
									else:
										audio = f"<audio src='{url_music}' controls='controls'></audio>"
										html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
														{audio}
														<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
															{user}
														</span>
													</div>
													<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
													</div>
													<br>'''
							elif _music == 1:
								url_music = requests.get(getHistory["items"][i]["attachments"][0]["audio"]["url"])
								name_music = f"{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y~%H-%M-%S')}.mp3"
								if getHistory["items"][i]["text"] != "":		
									if _cv != 0:
										photo_music = getHistory['items'][0]['attachments'][0]['audio']['album']['thumb']['photo_135']
										audio_title = getHistory['items'][0]['attachments'][0]['audio']['title']
										artist = getHistory['items'][0]['attachments'][0]['audio']['artist']
										album = getHistory['items'][0]['attachments'][0]['audio']['album']['title']
										if photo_music != "":
											dwn_track_photo = str(input("Скачивать обложки треков (y - да, n - нет): "))
											if dwn_track_photo == "y":
												title = audio_title.split()
												title = ''.join(title)
												title = title + "_" + artist
												if _folder == 0:
													photo_music = requests.get(photo_music)
													with open(f"{title}.jpg", "wb") as file:
														file.write(photo_music.content)
													photo_music = title
												else:
													photo_music = requests.get(photo_music)
													with open(f"{_folder}/{title}.jpg", "wb") as file:
														file.write(photo_music.content)
													photo_music = title
										audio = f'''<div style=''>
														<img src='{photo_music}' style='border-radius: 20px'>
														<span style=''>{audio_title} {explicit}</span>
														<span style=''>{artist}</span>
														<span style=''>{album}</span>
														<audio src='{url_music}' controls='controls'></audio>
													</div>'''

										html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
														{audio}
														<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
															{user}
														</span>
													</div>
													<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
													</div>
													<br>'''
									else:
										audio = f"<audio src='{url_music}' controls='controls'></audio>"
										html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
														{sms}
														<br>
														{audio}
														<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
															{user}
														</span>
													</div>
													<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
													</div>
													<br>'''
								elif getHistory["items"][i]["text"] == "":
									if _cv != 0:
										photo_music = getHistory['items'][0]['attachments'][0]['audio']['album']['thumb']['photo_135']
										audio_title = getHistory['items'][0]['attachments'][0]['audio']['title']
										artist = getHistory['items'][0]['attachments'][0]['audio']['artist']
										album = getHistory['items'][0]['attachments'][0]['audio']['album']['title']
										if photo_music != "":
											dwn_track_photo = str(input("Скачивать обложки треков (y - да, n - нет): "))
											if dwn_track_photo == "y":
												title = audio_title.split()
												title = ''.join(title)
												title = title + "_" + artist
												if _folder == 0:
													photo_music = requests.get(photo_music)
													with open(f"{title}.jpg", "wb") as file:
														file.write(photo_music.content)
													photo_music = title
												else:
													photo_music = requests.get(photo_music)
													with open(f"{_folder}/{title}.jpg", "wb") as file:
														file.write(photo_music.content)
													photo_music = title
										audio = f'''<div style=''>
														<img src='{photo_music}' style='border-radius: 20px'>
														<span style=''>{audio_title} {explicit}</span>
														<span style=''>{artist}</span>
														<span style=''>{album}</span>
														<audio src='{url_music}' controls='controls'></audio>
													</div>'''

										html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
														{audio}
														<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
															{user}
														</span>
													</div>
													<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
													</div>
													<br>'''
									else:
										audio = f"<audio src='{url_music}' controls='controls'></audio>"
										html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
														{audio}
														<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
															{user}
														</span>
													</div>
													<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
													</div>
													<br>'''
						elif getHistory["items"][i]["attachments"][0]["type"] == "doc":
							sms = getHistory["items"][i]["text"]
							if _doc == 0:
								url_doc = getHistory["items"][i]["attachments"][0]["doc"]["url"]
								if getHistory["items"][i]["text"] != "":
										
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													{sms}
													<br>
													<a href='{url_doc}'>
														ДОКУМЕНТ
													</a>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</div>
												<br>'''
								elif getHistory["items"][i]["text"] == "":
									
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													<a href='{url_doc}'>
														ДОКУМЕНТ
													</a>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{getUsers[0]["first_name"]}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</div>
												<br>'''
							elif _doc == 1:
								url_doc = getHistory["items"][i]["attachments"][0]["doc"]["url"]
								doc_type = requests.get(getHistory["items"][i]["attachments"][0]["doc"]["ext"])
								name_doc = f"{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y~%H-%M-%S')}.{doc_type}"
								
								if getHistory["items"][i]["text"] != "":
									sms = getHistory["items"][i]["text"]
									if doc_type == "jpg" or doc_type == "png" or doc_type == "bmp":
										
										html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
														{sms}
														<br>
														<img src='{name_doc}'>
														<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
															{user}
														</span>
													</div>
													<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
													</div>
													<br>'''
										if _folder == 0:
											with open(f"name_doc", "wb") as file:
												file.write(url_doc.content)
										elif _folder != 0:
											with open(f"{_folder}/{name_doc}", "wb") as file:
												file.write(url_doc.content)
									elif doc_type == "mp3" or doc_type == "wav" or doc_type == "aac":
											
											html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
															{sms}
															<br>
															<audio src='{name_doc}' controls='controls'></audio>
															<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
																{user}
															</span>
														</div>
														<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
															{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
														</div>
														<br>'''

											if _folder == 0:
												with open(name_doc, "wb") as file:
													file.write(url_doc.content)
											elif _folder != 0:
												with open(f"{_folder}/{name_doc}", "wb") as file:
													file.write(url_doc.content)
								elif getHistory["items"][i]["text"] == "":
									if doc_type == "jpg" or doc_type == "png" or doc_type == "bmp":
										
										html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
														{sms}
														<br>
														<img src='{name_doc}'>
														<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
															{user}
														</span>
													</div>
													<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
													</div>
													<br>'''
										if _folder == 0:
											with open(f"name_doc", "wb") as file:
												file.write(url_doc.content)
										elif _folder != 0:
											with open(f"{_folder}/{name_doc}", "wb") as file:
												file.write(url_doc.content)
									elif doc_type == "mp3" or doc_type == "wav" or doc_type == "aac":
										if getHistory["items"][i]["text"] != "":
											
											html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
															{sms}
															<br>
															<audio src='{name_doc}' controls='controls'></audio>
															<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
																{user}
															</span>
														</div>
														<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold; margin-left: 5px'>
															{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
														</div>
														<br>'''
											if _folder == 0:
												with open(f"name_doc", "wb") as file:
													file.write(url_doc.content)
											elif _folder != 0:
												with open(f"{_folder}/{name_doc}", "wb") as file:
													file.write(url_doc.content)
						elif getHistory["items"][i]["attachments"][0]["type"] == "poll":
							question = getHistory["items"][i]["attachments"][0]["poll"]["question"]
							answers = getHistory["items"][i]["attachments"][0]["poll"]["answers"]
							answers_ = ""

							for j in range(len(answers)):
								answer = getHistory["items"][i]["attachments"][0]["poll"]["answers"][j]["text"]
								vote = getHistory["items"][i]["attachments"][0]["poll"]["answers"][j]["votes"]
								rate = getHistory["items"][i]["attachments"][0]["poll"]["answers"][j]["rate"]

								answer_html = f'''<div style='width: 200px; height: 20px; background-color: rgba(255, 255, 255, .3); padding: 5px; border-radius: 5px; margin: 5px'>
											<span style='float: keft: margin-left: 10px; font-size: 15px'>{answer} · {vote}</span>
										</div>'''
								answers_ += answer_html

							poll = f'''<div style='color: #fff'>
											<center style='font-weight: bold; font-size: 15px'>ОПРОС</center>
											<center style='padding: 5px'>Вопрос: {question}</center>
											<div>
												{answers_}
											</div>
											<span></span>
										</div>'''
										
							html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 630px; background: linear-gradient(100deg, #ED4976, #3E48E3); padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
											{poll}
											<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
												{user}
											</span>
										</div>
										<div style='display: block; padding: 5px; font-size: 10px;font-weight: bold; margin-left: 5px'>
											{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
										</div>
										<br>'''
						elif getHistory["items"][i]["attachments"][0]["type"] == "money_request":
							comment = getHistory["items"][i]["text"]
							sum_ = getHistory["items"][i]["attachments"][0]["money_request"]["total_amount"]["amount"]
							finish_sum = f"{sum_[:-2:]}.{sum_[-2::]} {getHistory['items'][i]['attachments'][0]['money_request']['total_amount']['currency']['name']}"
							transferred = getHistory["items"][i]["attachments"][0]["money_request"]["transferred_amount"]["amount"]
							finish_post = f"{transferred[:-2:]}.{transferred[-2::]} {getHistory['items'][i]['attachments'][0]['money_request']['transferred_amount']['currency']['name']}"

							money_html = f'''<div style='color: #fff'>
												<span style='font-weight: bold; font-size: 20px'>ДЕНЕЖНЫЙ ЗАПРОС</span><br>
												<span>Сумма: {finish_sum}</span><br>
												<span>Собрано {transferred} из {finish_sum}</span><br>
												<span>Комментарий: {comment}</span>
											</div>'''

							html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 630px; background: linear-gradient(100deg, #ED4976, #3E48E3); padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
											{money_html}
											<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
												{user}
											</span>
										</div>
										<div style='display: block; padding: 5px; font-size: 10px;font-weight: bold; margin-left: 5px'>
											{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
										</div>
										<br>'''
					else:
						if "action" in getHistory["items"][i] and getHistory["items"][i]["action"]["type"] == "chat_unpin_message":
							name_ = getUsers[0]["first_name"] + " " + getUsers[0]["last_name"]
							msg_ = ""
							if "message" in getHistory["items"][i]:
								msg_ = getHistory["items"][i]["action"]["message"]
							html2 += f'''<div style='display: block; text-align: center; padding: 5px; margin: 0 auto'>
											<span style='weight: bold'>{name_}</span> <span style='weight: liter'>открепил сообщение {msg_}</span>
										</div>
										<br>'''
						elif "action" in getHistory["items"][i] and getHistory["items"][i]["action"]["type"] == "chat_pin_message":
							name_ = getUsers[0]["first_name"] + " " + getUsers[0]["last_name"]
							msg_ = ""
							if "message" in getHistory["items"][i]:
								msg_ = getHistory["items"][i]["action"]["message"]
							html2 += f'''<div style='display: block; text-align: center; padding: 5px; margin: 0 auto'>
											<span style='weight: bold'>{name_}</span> <span style='weight: liter'>закрепил сообщение {msg_}</span>
										</div>
										<br>'''
						else:
							sms = getHistory["items"][i]["text"]
							html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
											<code>{sms}</code>
											<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
												{user}
											</span>
										</div>
										<div style='display: block; padding: 5px; font-size: 10px; font-weight: bold'>
											{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
										</div>
										<br>'''

				off += 200
				if getHistory["count"] < 200:
				    off = getHistory["count"]
				elif getHistory["count"] == 0:
				    sys.exit(1)
				    
				html_join = html1 + html2 + html3
			except KeyboardInterrupt:
				warn("Выход!")

			try:
				if _folder == 0:
					with open(f"{name}.html", "w", encoding="utf-8") as file:
						file.write(html_join)
						succes(f"Сохранено {off} сообщений!")
				elif _folder != 0:
					with open(f"{_folder}/{name}.html", "w", encoding="utf-8") as file:
						file.write(html_join)
						succes(f"Сохранено {off} сообщений!")
			except KeyboardInterrupt:
				warn("Выход!")
				sys.exit(1)