try:
	try:
		import logs
		import sys
		import vk_api
		import locale
		import os
		from token_ import token
		import requests
		from datetime import datetime as dt
		import shutil
	except (ModuleNotFoundError, ImportError) as module_error:
		mdl = str(module_error).split("'")
		if mdl[1] == "EXACT_TOKEN_TYPES":
			logs.error(f"Отсутствует токен!")
		else:
			logs.error(f"Отсутствует модуль {mdl}!")
			sys.exit(1)

	# set local language
	locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")

	def auth():
		"""sign in in vk.com"""
		global session
		session = vk_api.VkApi(token = token)
		logs.success("Авторизация!")

	def dwn_dlg(id_, count_, photo_=0, audio_=0, music_=0, doc_=0, sd_=0, folder_=0, af_=0, ul_=0, cv_=0, all_=0, q_="", ud_=0):
		global getHistory
		global html2
		global off

		html2 = ""
		off = 0
		auth()

		SIZE_PHOTO = 0

		if q_ == "s":
			SIZE_PHOTO = 5
		elif q_ == "m":
			SIZE_PHOTO = 0
		elif q_ == "p":
			SIZE_PHOTO = 2
		elif q_ == "q":
			SIZE_PHOTO = 3
		elif q_ == "r":
			SIZE_PHOTO = 4
		elif q_ == "x":
			SIZE_PHOTO = 7
		elif q_ == "y":
			SIZE_PHOTO = 8
		elif q_ == "w":
			SIZE_PHOTO = 6

		# create folder for saving dialog
		try:
			if folder_ != 0:
				os.mkdir(folder_)
		except FileExistsError:
			logs.info("Папка уже существует!")

		# if have parametr af_ (all files), set value 1 (download) for variables downloading media files
		if af_ == 1:
			photo_, audio_, music_, doc_, sd_ = 1, 1, 1, 1, 1
		
		if count_ > 200:
			logs.warn("Нельзя скачать более 200 сообщений. Вы можете скачать весь диалог сразу, воспользовавшись параметром -all.")
			sys.exit(1)

		if all_ == 0:
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
							logs.warn("Диалог не существует!")
							sys.exit(1)
				# out of program if count message in dialog/chat smaller than in you written
				elif getHistory["count"] < count_:
					logs.warn(f"В диалоге нет {count_} сообщений!")
					sys.exit(1)
			except vk_api.exceptions.ApiError as err:
				# error sign in vk.com
				if str(err)[1] == "5":
					error("Ошибка авторизации! Токен неправильный или срок его действия истёк!")
				# not valid id user/group
				elif str(err)[1:4] == "100":
					logs.warn("Неправильный id пользователя/группы")
					sys.exit(1)

			logs.success("Получена история диалога!")

			# get name dialog
			type_ = getHistory["conversations"][0]["peer"]["type"]
			if type_ == "chat":
				name = getHistory["conversations"][0]["chat_settings"]["title"]
				logs.success("Название диалога получено!")
			elif type_ == "user":
				name = getHistory["profiles"][0]["first_name"] + " " + getHistory["profiles"][0]["last_name"]
				logs.success("Название диалога получено!")
			elif type_ == "group":
				name = getHistory["groups"][0]["name"]
				logs.success("Название диалога получено!")

			# getting link on user and dont't getting on chat
			if getHistory["conversations"][0]["peer"]["type"] == "user":
				link_user = "https://vk.com/" + getHistory["profiles"][0]["screen_name"]
				logs.success("Ссылка на пользователя/группу получена!")
			elif getHistory["conversations"][0]["peer"]["type"] == "chat":
				link_user = "#"
				logs.info("Ссылка на беседу не оставляется!")
			elif getHistory["conversations"][0]["peer"]["type"] == "group":
				link_user = "https://vk.com/" + getHistory["groups"][0]["screen_name"]
				logs.success("Ссылка на пользователя/группу получена!")
			
			# getting count users
			if getHistory["conversations"][0]["peer"]["type"] == "user":
				users = ""
				logs.info("Количество участников недоступно в диалоге с пользователем!")
			elif getHistory["conversations"][0]["peer"]["type"] == "chat":
				users = f"<center style='color: #fff; padding: 10px'>Участиков: {str(getHistory['conversations'][0]['chat_settings']['members_count'])}</center>"
				logs.success("Количество участников группы/беседы получено!")
			else:
				users = ""

			avatar = ""

			try:
				if getHistory["conversations"][0]["peer"]["type"] == "user":
					avatar = getHistory["profiles"][0]["photo_100"]
					avatar = requests.get(avatar)
					logs.success("Аватарка получена!")
				elif getHistory["conversations"][0]["peer"]["type"] == "chat":
					if "photo" in getHistory["conversations"][0]["chat_settings"].keys():
						avatar = getHistory["conversations"][0]["chat_settings"]["photo"]["photo_100"]
						avatar = requests.get(avatar)
						logs.success("Аватарка получена!")
				elif getHistory["conversations"][0]["peer"]["type"] == "groups":
					avatar = getHistory["groups"][0]["photo_100"]
					avatar = requests.get(avatar)
					logs.success("Аватарка получена!")
			except KeyError:
				avatar = ""
				logs.info("Аватрка отсутствует!")

			# download avatar
			if avatar != "":
				try:
					if folder_ == 0:
						with open("avatar.jpg", "wb") as avatar_:
							avatar_.write(avatar.content)
							avatar = "avatar.jpg"
					elif folder_ != 0:
						with open(f"{folder_}/avatar.jpg", "wb") as avatar_:
							avatar_.write(avatar.content)
							avatar = "avatar.jpg"
					logs.success("Аватарка скачана!")
				except AttributeError:
					pass

			# html templates
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

			if avatar != "":
				ava = f"<img src='{avatar}' style='height: 100px; border-radius: 100px; margin-top: 20px; box-shadow: 0px 0px 10px #000'>"
			else:
				ava = "<div style='display: inline-block; margin-top: 10px; width: 100px; height: 100px; border-radius: 200px; background: linear-gradient(to right, #00c6ff, #0072ff); box-shadow: 0px 0px 10px #000;'></div>"

			# count messages
			msgs_count = "<center style='font-family: sans-serif; color: #fff; padding: 10px'>Количество сообщений: " + str(getHistory["count"]) + "</center>"

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
				<center><a href='{link_user}' target='_blank'>{ava}</a></center>
				<center style='padding: 10px; font-size: 20px; color: #fff'>{name}</center>
				{users}
				{msgs_count}
			</div>
			'''

			html2 = '''
		<div style='width: 750px; box-sizing: padding-box; margin: 10px; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 20px; margin-left: auto; margin-right: auto'>'''

			html3 = '''
					</div>
				</body>
			</html>'''

			logs.success("HTML шаблоны созданы!")
			logs.success("Начало форматирования диалога!")

			try:
				for i in range(count_):
					try:
						getUsers = session.method("users.get", {
							"user_ids": getHistory["items"][i]["from_id"],
							"fields": "photo_50"
							})
					except IndexError:
						getUsers = session.method("users.get", {
							"user_ids": getHistory[i]["from_id"],
							"fields": "photo_50"})

					# if have parametr ul_ (user link) replace username on the link to this user
					if ul_ == 1:
						user = f"<a href='https://vk.com/id{getHistory['items'][i]['from_id']}'>{getUsers[0]['first_name']}</a>"
					else:
						user = getUsers[0]["first_name"]

					# getting avatars users in chat
					ava_msg = ""
					if type_ == "chat":
						if ud_ == 0:
							ava_msg = getUsers[0]["photo_50"]
							ava_msg = f"<div style='padding: 5px; float: left'><img src='{ava_msg}' style='border-radius: 50px; height: 50px'></div>"
						# if have parametr ud_ (user download) - download users avatars
						elif ud_ == 1:
							try:
								if folder_ != 0:
									os.mkdir(f"{folder_}/avatars_msgs")
								else:
									os.mkdir("avatars_msgs")
							except FileExistsError:
								pass

							ava_msg_ = getUsers[0]["photo_50"]
							ava_msg_ = requests.get(ava_msg_)
							name_ava_msg = getUsers[0]["first_name"] + getUsers[0]["last_name"] + "_avatar"
							
							try:
								if folder_ == 0:
									with open(f"avatars_msgs/{name_ava_msg}.jpg", "wb") as avatar_msg:
										avatar_msg.write(ava_msg_.content)
										ava_msg = f"<div style='padding: 5px; float: left'><img src='avatars_msgs/{name_ava_msg}.jpg' style='border-radius: 50px; height: 50px'></div>"
								elif folder_ != 0:
									with open(f"{folder_}/avatars_msgs/{name_ava_msg}.jpg", "wb") as avatar_msg:
										avatar_msg.write(ava_msg_.content)
										ava_msg =  f"<div style='padding: 5px; float: left'><img src='avatars_msgs/{name_ava_msg}.jpg' style='border-radius: 50px; height: 50px'></div>"
							except AttributeError:
								pass
					else:
						ava_msg = ""

					# get time edition message
					edit_msg = ""
					if "update_time" in getHistory["items"][i]:
						edit_msg = f"(ред. {(dt.fromtimestamp(getHistory['items'][i]['update_time']).strftime('%d %B %Y %H:%M:%S'))}"

					if len(getHistory["items"][i]["attachments"]) >= 1:
						if getHistory["items"][i]["attachments"][0]["type"] == "photo":
							sms = getHistory["items"][i]["text"]			
							if photo_ == 0:
								url_photo = getHistory["items"][i]["attachments"][0]["photo"]["sizes"][SIZE_PHOTO]["url"]
								if getHistory["items"][i]["text"] != "":
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													{sms}<br><br>
													<img src='{url_photo}' style='height: 150px; border-radius: 20px; box-shadow: 0px 0px 10px #000'>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
												</div>
												<br>'''
								elif getHistory["items"][i]["text"] == "":
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													<img src='{url_photo}' style='height: 150px; border-radius: 20px; box-shadow: 0px 0px 10px #000'>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
												</div>
												<br>'''
							elif photo_ == 1:
								url_photo = requests.get(getHistory["items"][i]["attachments"][0]["photo"]["sizes"][SIZE_PHOTO]["url"])
								name_photo = f"{(dt.fromtimestamp(getHistory['items'][i]['attachments'][0]['photo']['date'])).strftime('%d.%m.%y-%H.%M.%S')}_{getUsers[0]['first_name']}-{getUsers[0]['last_name']}.jpg"
								if folder_ == 0:
									with open(name_photo, "wb") as file:
										file.write(url_photo.content)
								elif folder_ != 0:
									with open(f"{folder_}/{name_photo}", "wb") as file:
										file.write(url_photo.content)
								if getHistory["items"][i]["text"] != "":
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													{sms}
													<br>
													<img src='{name_photo}' style='height: 150px; border-radius: 20px; box-shadow: 0px 0px 10px #000'>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
												</div>
												<br>'''
								elif getHistory["items"][i]["text"] == "":
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													<img src='{name_photo}' style='height: 150px; border-radius: 20px;'>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
												</div>
												<br>'''
						elif getHistory["items"][i]["attachments"][0]["type"] == "audio_message":
							sms = getHistory["items"][i]["text"]
							transcription = getHistory["items"][i]["attachments"][0]["audio_message"]["transcript"]
							if audio_ == 0:
								url_audio = getHistory["items"][i]["attachments"][0]["audio_message"]["link_mp3"]
								if getHistory["items"][i]["text"] != "":
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													{sms}
													<br>
													<audio src='{url_audio}' controls='controls'></audio>
													<br>
													<span>{transcription}</span>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
												</div>
												<br>'''
								elif getHistory["items"][i]["text"] == "":
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													<audio src='{url_audio}' controls='controls'></audio>
													<br>
													<span>{transcription}</span>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
												</div>
												<br>'''
							elif audio_ == 1:
								url_audio = requests.get(getHistory["items"][i]["attachments"][0]["audio_message"]["link_mp3"])
								name_audio = f"{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d.%m.%y-%H.%M.%S')}_{getUsers[0]['first_name']}-{getUsers[0]['last_name']}.mp3"
								if folder_ == 0:
									with open(name_audio, "wb") as file:
										file.write(url_audio.content)
								elif folder_ != 0:
									with open(f"{folder_}/{name_audio}", "wb") as file:
										file.write(url_audio.content)
								if getHistory["items"][i]["text"] != "":
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													{sms}
													<br>
													<audio src='{name_audio}' controls='controls'></audio>
													<br>
													<span>{transcription}</span>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
												</div>
												<br>'''
								elif getHistory["items"][i]["text"] == "":
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													<audio src='{name_audio}' controls='controls'></audio>
													<br>
													<span>{transcription}</span>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
												</div>
												<br>'''
						elif getHistory["items"][i]["attachments"][0]["type"] == "audio":
							sms = getHistory["items"][i]["text"]
							if music_ == 0:
								url_music = getHistory["items"][i]["attachments"][0]["audio"]["url"]
								explicit = getHistory['items'][i]['attachments'][0]['audio']['is_explicit']

								explicit = "🅴" if (explicit == True) else ""

								if getHistory["items"][i]["text"] != "":		
									if cv_ != 0:
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
												if folder_ == 0:
													photo_music = requests.get(photo_music)
													with open(f"{title}.jpg", "wb") as file:
														file.write(photo_music.content)
													photo_music = title
												else:
													photo_music = requests.get(photo_music)
													with open(f"{folder_}/{title}.jpg", "wb") as file:
														file.write(photo_music.content)
													photo_music = title
										audio = f'''<div style=''>
													<div style='padding: 10px; margin: auto auto auto 50px'>
														<div style='padding: 10px; margin: -20px auto auto -70px'>
															<img src='{photo_music}.jpg' style='border-radius: 10px; box-shadow: 0px 0px 10px #000'>
														</div>
														<div style='margin: -80px auto auto 80px; padding: 5px;'>
															<span style=''>Трек: {audio_title}</span><br>
															<span style=''>Артист: {artist}</span><br>
															<span style=''>Альбом: {album}</span><br>
														</div>
													</div>
													<audio src='{url_music}' controls='controls' style='padding: 5px'></audio>
												</div>'''

										html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
														{audio}
														<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
															{user}
														</span>
													</div>
													<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
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
													<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
													</div>
													<br>'''
								elif getHistory["items"][i]["text"] == "":	
									if cv_ != 0:
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
												if folder_ == 0:
													photo_music = requests.get(photo_music)
													with open(f"{title}.jpg", "wb") as file:
														file.write(photo_music.content)
													photo_music = title
												else:
													photo_music = requests.get(photo_music)
													with open(f"{folder_}/{title}.jpg", "wb") as file:
														file.write(photo_music.content)
													photo_music = title
										audio = f'''<div style=''>
													<div style='padding: 10px; margin: auto auto auto 50px'>
														<div style='padding: 10px; margin: -20px auto auto -70px'>
															<img src='{photo_music}.jpg' style='border-radius: 10px; box-shadow: 0px 0px 10px #000'>
														</div>
														<div style='margin: -80px auto auto 80px; padding: 5px;'>
															<span style=''>Трек: {audio_title}</span><br>
															<span style=''>Артист: {artist}</span><br>
															<span style=''>Альбом: {album}</span><br>
														</div>
													</div>
													<audio src='{url_music}' controls='controls' style='padding: 5px'></audio>
												</div>'''
										html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
														{audio}
														<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
															{user}
														</span>
													</div>
													<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
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
													<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
													</div>
													<br>'''
							elif music_ == 1:
								url_music = requests.get(getHistory["items"][i]["attachments"][0]["audio"]["url"])
								name_music = f"{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d.%m.%y-%H.%M.%S')}_{getUsers[0]['first_name']}-{getUsers[0]['last_name']}.mp3"
								if getHistory["items"][i]["text"] != "":		
									if cv_ != 0:
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
												if folder_ == 0:
													photo_music = requests.get(photo_music)
													with open(f"{title}.jpg", "wb") as file:
														file.write(photo_music.content)
													photo_music = title
												else:
													photo_music = requests.get(photo_music)
													with open(f"{folder_}/{title}.jpg", "wb") as file:
														file.write(photo_music.content)
													photo_music = title
										audio = f'''<div style=''>
													<div style='padding: 10px; margin: auto auto auto 50px'>
														<div style='padding: 10px; margin: -20px auto auto -70px'>
															<img src='{photo_music}.jpg' style='border-radius: 10px; box-shadow: 0px 0px 10px #000'>
														</div>
														<div style='margin: -80px auto auto 80px; padding: 5px;'>
															<span style=''>Трек: {audio_title}</span><br>
															<span style=''>Артист: {artist}</span><br>
															<span style=''>Альбом: {album}</span><br>
														</div>
													</div>
													<audio src='{url_music}' controls='controls' style='padding: 5px'></audio>
												</div>'''
										html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
														{audio}
														<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
															{user}
														</span>
													</div>
													<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
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
													<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
													</div>
													<br>'''
								elif getHistory["items"][i]["text"] == "":
									if cv_ != 0:
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
													<div style='padding: 10px; margin: auto auto auto 50px'>
														<div style='padding: 10px; margin: -20px auto auto -70px'>
															<img src='{photo_music}.jpg' style='border-radius: 10px; box-shadow: 0px 0px 10px #000'>
														</div>
														<div style='margin: -80px auto auto 80px; padding: 5px;'>
															<span style=''>Трек: {audio_title}</span><br>
															<span style=''>Артист: {artist}</span><br>
															<span style=''>Альбом: {album}</span><br>
														</div>
													</div>
													<audio src='{url_music}' controls='controls' style='padding: 5px'></audio>
												</div>'''
										html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
														{audio}
														<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
															{user}
														</span>
													</div>
													<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
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
													<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
													/div>
													<br>'''
						elif getHistory["items"][i]["attachments"][0]["type"] == "doc":
							sms = getHistory["items"][i]["text"]
							if doc_ == 0:
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
												<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
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
												<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
												</div>
												<br>'''
							elif doc_ == 1:
								url_doc = getHistory["items"][i]["attachments"][0]["doc"]["url"]
								doc_type = requests.get(getHistory["items"][i]["attachments"][0]["doc"]["ext"])
								name_doc = f"{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d.%m.%y-%H.%M.%S')}_{getUsers[0]['first_name']}-{getUsers[0]['last_name']}.{doc_type}"
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
													<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
													</div>
													<br>'''
										if folder_ == 0:
											with open(f"name_doc", "wb") as file:
												file.write(url_doc.content)
										elif folder_ != 0:
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
														<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
															{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
														</div>
														<br>'''
											if folder_ == 0:
												with open(name_doc, "wb") as file:
													file.write(url_doc.content)
											elif folder_ != 0:
												with open(f"{folder_}/{name_doc}", "wb") as file:
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
													<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
													</div>
													<br>'''
										if folder_ == 0:
											with open(f"name_doc", "wb") as file:
												file.write(url_doc.content)
										elif folder_ != 0:
											with open(f"{folder_}/{name_doc}", "wb") as file:
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
														<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
															{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
														</div>
														<br>'''
											if folder_ == 0:
												with open(f"name_doc", "wb") as file:
													file.write(url_doc.content)
											elif folder_ != 0:
												with open(f"{folder_}/{name_doc}", "wb") as file:
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
											<span style='float: keft: margin-left: 10px; font-size: 15px'>{answer} • {vote}</span>
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
							html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 630px; background-color: #249B87; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
											{poll}
											<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
												{user}
											</span>
										</div>
										<div style='display: block; padding: 5px; font-size: 10px;font-weight: bold; margin-left: 5px'>
											{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
										</div>
										<br>'''
						elif getHistory["items"][i]["attachments"][0]["type"] == "money_request":
							comment = getHistory["items"][i]["text"]
							sum_ = getHistory["items"][i]["attachments"][0]["money_request"]["total_amount"]["amount"]
							finish_sum = f"{sum_[:-2:]}.{sum_[-2::]} {getHistory['items'][i]['attachments'][0]['money_request']['total_amount']['currency']['name']}"
							transferred = getHistory["items"][i]["attachments"][0]["money_request"]["transferred_amount"]["amount"]
							finish_post = f"{transferred[:-2:]}.{transferred[-2::]} {getHistory['items'][i]['attachments'][0]['money_request']['transferred_amount']['currency']['name']}"
							money_html = f'''<div style='color: #fff'>
												<span style='font-weight: bold; font-size: 15px'>ДЕНЕЖНЫЙ ЗАПРОС</span><br>
												<span>Сумма: {finish_sum}</span><br>
												<span>Собрано {transferred} из {finish_sum}</span><br>
												<span>Комментарий: {comment}</span>
											</div>'''
							html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 630px; background-color: #249B87; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
											{money_html}
											<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
												{user}
											</span>
										</div>
										<div style='display: block; padding: 5px; font-size: 10px;font-weight: bold; margin-left: 5px'>
											{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
										</div>
										<br>'''
						elif "sticker" in getHistory["items"][i]["attachments"][0]:
							sticker = getHistory["items"][i]["attachments"][0]["sticker"]["images"][1]["url"]
							if sd_ == 0:
								html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
												<img src='{sticker}'>
												<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
													{user}
												</span>
											</div>
											<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold'>
												{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
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
											<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold'>
												{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
											</div>
											<br>'''
								if folder_ == 0:
									with open(f"{stick_name}", "wb") as file:
										file.write(sticker.content)
								elif folder_ != 0:
									with open(f"{folder_}/{stick_name}", "wb") as file:
										file.write(sticker.content)
					else:
						if "action" in getHistory["items"][i]:
							if getHistory["items"][i]["action"]["type"] == "chat_unpin_message":
								name_ = getUsers[0]["first_name"] + " " + getUsers[0]["last_name"]
								msg_ = ""
								if "message" in getHistory["items"][i]:
									msg_ = getHistory["items"][i]["action"]["message"]
								html2 += f'''<div style='display: block; text-align: center; padding: 5px; margin: 0 auto'>
												<span style='font-weight: bold'>{name_}</span> <span style='font-weight: liter'>открепил сообщение \"{msg_}\"</span>
											</div>
											<br>'''
							elif getHistory["items"][i]["action"]["type"] == "chat_pin_message":
								name_ = getUsers[0]["first_name"] + " " + getUsers[0]["last_name"]
								msg_ = ""
								if "message" in getHistory["items"][i]:
									msg_ = getHistory["items"][i]["action"]["message"]
								html2 += f'''<div style='display: block; text-align: center; padding: 5px; margin: 0 auto'>
												<span style='font-weight: bold'>{name_}</span> <span style='font-weight: liter'>закрепил сообщение \"{msg_}\"</span>
											</div>
											<br>'''
								html1 += f'''<div>
											</div>'''
							elif getHistory["items"][i]["action"]["type"] == "chat_kick_user":
								name_ = getUsers[0]["first_name"] + " " + getUsers[0]["last_name"]
								html2 += f'''<div style='display: block; text-align: center; padding: 5px; margin: 0 auto'>
												<span style='font-weight: bold'>{name_}</span> <span style='font-weight: liter'>покинул(а) чат</span>
											</div>
											<br>'''
						elif len(getHistory["items"][0]["fwd_messages"]) >= 1:
							sms = getHistory["items"][i]["text"]
							html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
											<code>{sms}</code><br>
											<span style="color: red; font-size: 15px; font-weight: bold">ПЕРЕСЛАННЫЕ СООБЩЕНИЯ НЕ ПОДДЕРЖИВАЮТСЯ!</span>
											<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
												{user}
											</span>
										</div>
										<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold'>
											{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
										</div><br>'''
						else:
							sms = getHistory["items"][i]["text"]
							html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
											<code>{sms}</code>
											<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
												{user}
											</span>
										</div>
										<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold'>
											{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
										</div><br>'''

				# joining all fragments html yemplates
				html_join = html1 + html2 + html3
				logs.success("Создание HTML страницы завершено!")

				if folder_ == 0:
					with open(f"{name}.html", "w", encoding="utf-8") as file:
						file.write(html_join)
						logs.success("Диалог сохранен!")
				else:
					with open(f"{folder_}/{name}.html", "w", encoding="utf-8") as file:
						file.write(html_join)
						logs.success("Диалог сохранен!")
			except:
				pass

		elif all_ == 1:
			# variables using for downloading all dialog
			v1 = 0
			v2 = 0
			v3 = 0
			v4 = 0
			v5 = 0
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
					# out of program if count message in dialog/chat smallerthan in you written
					elif getHistory["count"] < count_:
						logs.warn(f"В диалоге нет {count_} сообщений!")
						sys.exit(1)
				except vk_api.exceptions.ApiError as err:
					# error sign in vk.com
					if str(err)[1] == "5":
						logs.error("Ошибка авторизации! Токен неправильный или срок его действия истёк!")
					# not valid id user/group
					elif str(err)[1:4] == "100":
						logs.warn("Неправильный id пользователя/группы")
						sys.exit(1)

				# if log was shown, the will not be displayed
				if v5 != 1:
					logs.success("Получена история диалога!")
					v5 = 1

				# getting name dialog
				type_ = getHistory["conversations"][0]["peer"]["type"]
				# if log was shown, the will not be displayed
				if v1 != 1:
					if name == "":
						if type_ == "chat":
							name = getHistory["conversations"][0]["chat_settings"]["title"]
							logs.success("Название диалога получено!")
						elif type_ == "user":
							name = getHistory["profiles"][0]["first_name"] + " " + getHistory["profiles"][0]["last_name"]
							logs.success("Название диалога получено!")
						elif type_ == "group":
							name = getHistory["groups"][0]["name"]
							logs.success("Название диалога получено!")
					if getHistory["conversations"][0]["peer"]["type"] == "user":
						link_user = "https://vk.com/" + getHistory["profiles"][0]["screen_name"]
						logs.success("Ссылка на пользователя/группу получена!")
					elif getHistory["conversations"][0]["peer"]["type"] == "chat":
						link_user = "#"
						logs.info("Ссылка на беседу не оставляется!")
					elif getHistory["conversations"][0]["peer"]["type"] == "group":
						link_user = "https://vk.com/" + getHistory["groups"][0]["screen_name"]
						logs.success("Ссылка на пользователя/группу получена!")
					v1 = 1
				
				# getting count users
				# if log was shown, the will not be displayed
				if v2 != 1:
					if getHistory["conversations"][0]["peer"]["type"] == "user":
						users = ""
						logs.success("Количество пользователей получено!")
					elif getHistory["conversations"][0]["peer"]["type"] == "chat":
						users = f"<center style='color: #fff; padding: 10px'>Участиков: {str(getHistory['conversations'][0]['chat_settings']['members_count'])}</center>"
						logs.success("Количество пользователей получено!")
					v2 = 1

				avatar = ""
				# getting and saving avatar
				# if log was shown, the will not be displayed
				if v3 != 1:
					try:
						if getHistory["conversations"][0]["peer"]["type"] == "user":
							avatar = getHistory["profiles"][0]["photo_100"]
							avatar = requests.get(avatar)
							logs.success("Аватарка получена!")
						elif getHistory["conversations"][0]["peer"]["type"] == "chat":
							avatar = getHistory["conversations"][0]["chat_settings"]["photo"]["photo_100"]
							avatar = requests.get(avatar)
							logs.success("Аватарка получена!")
						elif getHistory["conversations"][0]["peer"]["type"] == "groups":
							avatar = getHistory["groups"][0]["photo_100"]
							avatar = requests.get(avatar)
							logs.success("Аватарка получена!")
					except KeyError:
						avatar = ""
						logs.info("Аватарка отсутствует!")

					try:
						if folder_ == 0:
							with open("avatar.jpg", "wb") as avatar_:
								avatar_.write(avatar.content)
								avatar = "avatar.jpg"
						else:
							with open(f"{folder_}/avatar.jpg", "wb") as avatar_:
								avatar_.write(avatar.content)
								avatar = "avatar.jpg"
						logs.success("Аватарка скачана!")
					except AttributeError:
						pass
					v3 = 1

				# count posts
				# if log was shown, the will not be displayed
				if v4 != 1:
					msgs_count = "<center style='font-family: sans-serif; color: #fff; padding: 10px'>Всего сообщений в диалоге: " + str(getHistory["count"]) + "</center>"
					v4 = 1

				# html components
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
						{msgs_count}
					</div>
					<div style='width: 750px; box-sizing: padding-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 20px; margin-left: auto; margin-right: auto'>'''

				html3 = '''
								</div>
							</body>
						</html>'''
				
				# if log was shown, the will not be displayed
				if v4 != 1:
					logs.success("HTML шаблоны созданы!")
					v4 = 1

				for i in range(count_):
					edit_msg = ""
					if "update_time" in getHistory["items"][i]:
						edit_msg = (dt.fromtimestamp(getHistory["items"][i]["update_time"])).strftime('%d %B %Y %H:%M:%S')
					if edit_msg != "":
						edit_msg = f"(ред. {edit_msg})"
					
					try:
						getUsers = session.method("users.get", {
							"user_ids": getHistory["items"][i]["from_id"],
							"fields": "photo_50"
							})
					except IndexError:
						getUsers = session.method("users.get", {
							"user_ids": getHistory[i]["from_id"],
							"fields": "photo_50"})
					# if have parametr _ul (user link), the name user replace on the link
					if ul_ == 1:
						user = f"<a href='https://vk.com/id{getHistory['items'][i]['from_id']}'>{getUsers[0]['first_name']}</a>"
					else:
						user = getUsers[0]["first_name"]
					# if type dialog - chat, download user avatars
					if type_ == "chat":
						ava_msg = getUsers[0]["photo_50"]
						ava_msg = f"<div style='padding: 5px; float: left'><img src='{ava_msg}' style='border-radius: 50px; height: 50px'></div>"
					else:
						ava_msg = ""
					if len(getHistory["items"][i]["attachments"]) >= 1:
						if getHistory["items"][i]["attachments"][0]["type"] == "photo":
							sms = getHistory["items"][i]["text"]			
							if photo_ == 0:
								url_photo = getHistory["items"][i]["attachments"][0]["photo"]["sizes"][SIZE_PHOTO]["url"]
								if getHistory["items"][i]["text"] != "":
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													{sms}<br><br>
													<img src='{url_photo}' style='height: 200px; border-radius: 20px; box-shadow: 0px 0px 10px #000'>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
												</div>
												<br>'''
								elif getHistory["items"][i]["text"] == "":
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													<img src='{url_photo}' style='height: 200px; border-radius: 20px; box-shadow: 0px 0px 10px #000'>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
												</div>
												<br>'''
							elif photo_ == 1:
								try:
									url_photo = requests.get(getHistory["items"][i]["attachments"][0]["photo"]["sizes"][SIZE_PHOTO]["url"])
									name_photo = f"{(dt.fromtimestamp(getHistory['items'][i]['attachments'][0]['photo']['date'])).strftime('%d.%m.%y-%H.%M.%S')}_{getUsers[0]['first_name']}-{getUsers[0]['last_name']}.jpg"
								except IndexError:
									url_photo = requests.get(getHistory["items"][i]["attachments"][0]["photo"]["sizes"][0]["url"])
									name_photo = f"{(dt.fromtimestamp(getHistory['items'][i]['attachments'][0]['photo']['date'])).strftime('%d.%m.%y-%H.%M.%S')}_{getUsers[0]['first_name']}-{getUsers[0]['last_name']}.jpg"

								if folder_ == 0:
									with open(name_photo, "wb") as file:
										file.write(url_photo.content)
								else:
									with open(f"{folder_}/{name_photo}", "wb") as file:
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
												<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
												</div>
												<br>'''
								elif getHistory["items"][i]["text"] == "":
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													<img src='{name_photo}' style='height: 200px; border-radius: 20px;'>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
												</div>
												<br>'''
						elif getHistory["items"][i]["attachments"][0]["type"] == "audio_message":
							sms = getHistory["items"][i]["text"]
							transcription = getHistory["items"][i]["attachments"][0]["audio_message"]["transcript"]
							if audio_ == 0:
								url_audio = getHistory["items"][i]["attachments"][0]["audio_message"]["link_mp3"]
								if getHistory["items"][i]["text"] != "":
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													{sms}
													<br>
													<audio src='{url_audio}' controls='controls'></audio>
													<br>
													<span>{transcription}</span>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
												</div>
												<br>'''
								elif getHistory["items"][i]["text"] == "":
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													<audio src='{url_audio}' controls='controls'></audio>
													<br>
													<span>{transcription}</span>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
												</div>
												<br>'''
							elif audio_ == 1:
								url_audio = requests.get(getHistory["items"][i]["attachments"][0]["audio_message"]["link_mp3"])
								name_audio = f"{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d.%m.%y-%H.%M.%S')}_{getUsers[0]['first_name']}-{getUsers[0]['last_name']}.mp3"
								if folder_ == 0:
									with open(name_audio, "wb") as file:
										file.write(url_audio.content)
								else:
									with open(f"{folder_}/{name_audio}", "wb") as file:
										file.write(url_audio.content)
								if getHistory["items"][i]["text"] != "":
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													{sms}
													<br>
													<audio src='{name_audio}' controls='controls'></audio>
													<br>
													<span>{transcription}</span>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
												</div>
												<br>'''
								elif getHistory["items"][i]["text"] == "":
									html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
													<audio src='{name_audio}' controls='controls'></audio>
													<br>
													<span>{transcription}</span>
													<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
														{user}
													</span>
												</div>
												<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
												</div>
												<br>'''
						elif getHistory["items"][i]["attachments"][0]["type"] == "audio":
							sms = getHistory["items"][i]["text"]
							if music_ == 0:
								url_music = getHistory["items"][i]["attachments"][0]["audio"]["url"]
								explicit = getHistory['items'][i]['attachments'][0]['audio']['is_explicit']
								explicit = "🅴" if (explicit == True) else ""
								if getHistory["items"][i]["text"] != "":		
									if cv_ != 0:
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
												if folder_ == 0:
													photo_music = requests.get(photo_music)
													with open(f"{title}.jpg", "wb") as file:
														file.write(photo_music.content)
													photo_music = title
												else:
													photo_music = requests.get(photo_music)
													with open(f"{folder_}/{title}.jpg", "wb") as file:
														file.write(photo_music.content)
													photo_music = title
										audio = f'''<div style=''>
												<div style='padding: 10px; margin: auto auto auto 50px'>
													<div style='padding: 10px; margin: -20px auto auto -70px'>
														<img src='{photo_music}.jpg' style='border-radius: 10px; box-shadow: 0px 0px 10px #000'>
													</div>
													<div style='margin: -80px auto auto 80px; padding: 5px;'>
														<span style=''>Трек: {audio_title}</span><br>
														<span style=''>Артист: {artist}</span><br>
														<span style=''>Альбом: {album}</span><br>
													</div>
												</div>
												<audio src='{url_music}' controls='controls' style='padding: 5px'></audio>
											</div>'''
										html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
														{audio}
														<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
															{user}
														</span>
													</div>
													<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
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
													<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
													</div>
													<br>'''
								elif getHistory["items"][i]["text"] == "":	
									if cv_ != 0:
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
												if folder_ == 0:
													photo_music = requests.get(photo_music)
													with open(f"{title}.jpg", "wb") as file:
														file.write(photo_music.content)
													photo_music = title
												else:
													photo_music = requests.get(photo_music)
													with open(f"{folder_}/{title}.jpg", "wb") as file:
														file.write(photo_music.content)
													photo_music = title
										audio = f'''<div style=''>
												<div style='padding: 10px; margin: auto auto auto 50px'>
													<div style='padding: 10px; margin: -20px auto auto -70px'>
														<img src='{photo_music}.jpg' style='border-radius: 10px; box-shadow: 0px 0px 10px #000'>
													</div>
													<div style='margin: -80px auto auto 80px; padding: 5px;'>
														<span style=''>Трек: {audio_title}</span><br>
														<span style=''>Артист: {artist}</span><br>
														<span style=''>Альбом: {album}</span><br>
													</div>
												</div>
												<audio src='{url_music}' controls='controls' style='padding: 5px'></audio>
											</div>'''
										html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
														{audio}
														<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
															{user}
														</span>
													</div>
													<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
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
													<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
													</div>
													<br>'''
							elif music_ == 1:
								url_music = requests.get(getHistory["items"][i]["attachments"][0]["audio"]["url"])
								name_music = f"{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d.%m.%y-%H.%M.%S')}_{getUsers[0]['first_name']}-{getUsers[0]['last_name']}.mp3"
								if getHistory["items"][i]["text"] != "":		
									if cv_ != 0:
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
												if folder_ == 0:
													photo_music = requests.get(photo_music)
													with open(f"{title}.jpg", "wb") as file:
														file.write(photo_music.content)
													photo_music = title
												else:
													photo_music = requests.get(photo_music)
													with open(f"{folder_}/{title}.jpg", "wb") as file:
														file.write(photo_music.content)
													photo_music = title
										audio = f'''<div style=''>
												<div style='padding: 10px; margin: auto auto auto 50px'>
													<div style='padding: 10px; margin: -20px auto auto -70px'>
														<img src='{photo_music}.jpg' style='border-radius: 10px; box-shadow: 0px 0px 10px #000'>
													</div>
													<div style='margin: -80px auto auto 80px; padding: 5px;'>
														<span style=''>Трек: {audio_title}</span><br>
														<span style=''>Артист: {artist}</span><br>
														<span style=''>Альбом: {album}</span><br>
													</div>
												</div>
												<audio src='{url_music}' controls='controls' style='padding: 5px'></audio>
											</div>'''
										html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
														{audio}
														<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
															{user}
														</span>
													</div>
													<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
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
													<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
													</div>
													<br>'''
								elif getHistory["items"][i]["text"] == "":
									if cv_ != 0:
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
												if folder_ == 0:
													photo_music = requests.get(photo_music)
													with open(f"{title}.jpg", "wb") as file:
														file.write(photo_music.content)
													photo_music = title
												else:
													photo_music = requests.get(photo_music)
													with open(f"{folder_}/{title}.jpg", "wb") as file:
														file.write(photo_music.content)
													photo_music = title
										audio = f'''<div style=''>
												<div style='padding: 10px; margin: auto auto auto 50px'>
													<div style='padding: 10px; margin: -20px auto auto -70px'>
														<img src='{photo_music}.jpg' style='border-radius: 10px; box-shadow: 0px 0px 10px #000'>
													</div>
													<div style='margin: -80px auto auto 80px; padding: 5px;'>
														<span style=''>Трек: {audio_title}</span><br>
														<span style=''>Артист: {artist}</span><br>
														<span style=''>Альбом: {album}</span><br>
													</div>
												</div>
												<audio src='{url_music}' controls='controls' style='padding: 5px'></audio>
											</div>'''
										html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
														{audio}
														<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
															{user}
														</span>
													</div>
													<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
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
													<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
													</div>
													<br>'''
						elif getHistory["items"][i]["attachments"][0]["type"] == "doc":
							sms = getHistory["items"][i]["text"]
							if doc_ == 0:
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
												<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
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
												<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
													{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
												</div>
												<br>'''
							elif doc_ == 1:
								url_doc = getHistory["items"][i]["attachments"][0]["doc"]["url"]
								doc_type = requests.get(getHistory["items"][i]["attachments"][0]["doc"]["ext"])
								name_doc = f"{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d.%m.%y-%H.%M.%S')}_{getUsers[0]['first_name']}-{getUsers[0]['last_name']}.{doc_type}"
								if getHistory["items"][i]["text"] != "":
									sms = getHistory["items"][i]["text"]
									if doc_type == "jpg" or doc_type == "png" or doc_type == "bmp":
										html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
														{sms}
														<br>
														<img src='{name_doc}' style='height: 80px'>
														<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
															{user}
														</span>
													</div>
													<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
													</div>
													<br>'''
										if folder_ == 0:
											with open(f"name_doc", "wb") as file:
												file.write(url_doc.content)
										else:
											with open(f"{folder_}/{name_doc}", "wb") as file:
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
														<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
															{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
														</div>
														<br>'''
											if folder_ == 0:
												with open(name_doc, "wb") as file:
													file.write(url_doc.content)
											else:
												with open(f"{folder_}/{name_doc}", "wb") as file:
													file.write(url_doc.content)
								elif getHistory["items"][i]["text"] == "":
									if doc_type == "jpg" or doc_type == "png" or doc_type == "bmp":
										html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
														{sms}
														<br>
														<img src='{name_doc}' style='height: 80px'>
														<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
															{user}
														</span>
													</div>
													<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
														{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
													</div>
													<br>'''
										if folder_ == 0:
											with open(f"name_doc", "wb") as file:
												file.write(url_doc.content)
										else:
											with open(f"{folder_}/{name_doc}", "wb") as file:
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
														<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold; margin-left: 5px'>
															{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
														</div>
														<br>'''
											if folder_== 0:
												with open(f"name_doc", "wb") as file:
													file.write(url_doc.content)
											else:
												with open(f"{folder_}/{name_doc}", "wb") as file:
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
							html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 630px; background-color: #249B87; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
											{poll}
											<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
												{user}
											</span>
										</div>
										<div style='display: block; padding: 5px; font-size: 10px;font-weight: bold; margin-left: 5px'>
											{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
										</div>
										<br>'''
						elif getHistory["items"][i]["attachments"][0]["type"] == "money_request":
							comment = getHistory["items"][i]["text"]
							sum_ = getHistory["items"][i]["attachments"][0]["money_request"]["total_amount"]["amount"]
							finish_sum = f"{sum_[:-2:]}.{sum_[-2::]} {getHistory['items'][i]['attachments'][0]['money_request']['total_amount']['currency']['name']}"
							transferred = getHistory["items"][i]["attachments"][0]["money_request"]["transferred_amount"]["amount"]
							finish_post = f"{transferred[:-2:]}.{transferred[-2::]} {getHistory['items'][i]['attachments'][0]['money_request']['transferred_amount']['currency']['name']}"
							money_html = f'''<div style='color: #fff'>
												<span style='font-weight: bold; font-size: 15px'>ДЕНЕЖНЫЙ ЗАПРОС</span><br>
												<span>Сумма: {finish_sum}</span><br>
												<span>Собрано {transferred} из {finish_sum}</span><br>
												<span>Комментарий: {comment}</span>
											</div>'''
							html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 630px; background-color: #249B87; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
											{money_html}
											<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
												{user}
											</span>
										</div>
										<div style='display: block; padding: 5px; font-size: 10px;font-weight: bold; margin-left: 5px'>
											{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
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
						elif len(getHistory["items"][0]["fwd_messages"]) >= 1:
							sms = getHistory["items"][i]["text"]
							html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
											<code>{sms}</code><br>
											<span style="color: red; font-size: 15px; font-weight: bold">ПЕРЕСЛАННЫЕ СООБЩЕНИЯ НЕ ПОДДЕРЖИВАЮТСЯ!</span>
											<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
												{user}
											</span>
										</div>
										<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold'>
											{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
										</div><br>'''
						else:
							sms = getHistory["items"][i]["text"]
							html2 += f'''{ava_msg}<div style='display: inline-block; max-width: 600px; background-color: #D6E1E7; padding: 10px; border-radius: 20px; margin: 10px -50px auto 5px'>
											<code>{sms}</code>
											<span style='font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
												{user}
											</span>
										</div>
										<div style='display: block; padding: 5px; font-size: 12px; font-weight: bold'>
											{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')} {edit_msg}
										</div>
										<br>'''
				# offset in messages
				off += 200
				if getHistory["count"] < 200:
				    off = getHistory["count"]
				elif getHistory["count"] == 0:
				    sys.exit(1)
				    
				# joining all fragments html templates
				html_join = html1 + html2 + html3
				logs.success("Создание HTML страницы завершено!")

				if folder_ == 0:
					with open(f"{name}.html", "w", encoding="utf-8") as file:
						file.write(html_join)
						logs.success(f"Сохранено {off} сообщений!")
				else:
					with open(f"{folder_}/{name}.html", "w", encoding="utf-8") as file:
						file.write(html_join)
						logs.success(f"Сохранено {off} сообщений!")

		# delete folder __pycache__ after the work of the program
		try:
			shutil.rmtree("__pycache__")
		except Exception:
			pass
except KeyboardInterrupt:
	logs.warn("Выход!")
	sys.exit(1)