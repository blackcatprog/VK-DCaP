try:
	try:
		import sys
		import logs
		import vk_api
		from token_ import token
		import requests
		from datetime import datetime as dt
		import os
		import locale
		import shutil
	except (ModuleNotFoundError, ImportError) as module_error:
		mdl = str(module_error).split("'")
		if mdl[0] == "EXACT_TOKEN_TYPES":
			logs.error(f"Отсутствует токен!")
		else:
			logs.error(f"Отсутствует модуль {mdl}!")
			sys.exit(1)

	# set local language
	locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")

	def auth():
		"""sign in vk.com"""
		global session
		session = vk_api.VkApi(token = token)
		logs.success("Авторизация!")

	def dwn_pst(id_, count_, photo_=0, music_=0, doc_=0, folder_=0, af_=0, q_="", all_=0):
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

		# if have parametr _af (all files), the set in value 1 (download) all variables for download media files
		if af_ == 1:
			photo_, music_, doc_ = 1, 1, 1

		# create folder for saving dialog
		try:
			if folder_ != 0:
				os.mkdir(folder_)
		except FileExistsError:
			logs.info("Такая папка уже существует!")

		if all_ == 0:
			# getting posts history
			try:
				getWall = session.method("wall.get", {
					"domain": id_,
					"offset": off,
					"count": count_,
					"extended": 1,
					"fields": "members_count"
					})
				if getWall["count"] == 0:
					getWall = session.method("wall.get", {
						"owner_id": id_,
						"offset": off,
						"count": count_,
						"extended": 1
						})
					if getWall["count"] == 0:
						getWall = session.method("wall.get", {
							"owner_id": "-" + str(id_),
							"offset": off,
							"count": count_,
							"extended": 1,
							"fields": "members_count"
							})
						if getWall["count"] == 0:
							logs.warn("Пользователь/группа не существует, либо отсутствуют посты!!")
							sys.exit(1)
			except vk_api.exceptions.ApiError as err:
				# logs.error sign in in vk.com
				if str(err)[1] == "5":
					logs.error("Ошибка авторизации! Токен неправильный или срок его действия истёк!")
					sys.exit(1)
				# invalid user/group id
				elif str(err)[1:4] == "100":
					logs.warn("Неправильный id пользователя/группы")
					sys.exit(1)

			# getting name user/group
			if len(getWall["groups"]) >= 1:
				name = getWall["groups"][0]["name"]
				logs.success("Название диалога получено!")
			else:
				name = getWall["profiles"][0]["first_name"] + " " + getWall["profiles"][0]["last_name"]
				logs.success("Название диалога получено!")

			# getting avatar user/group
			if len(getWall["groups"]) >= 1:
				ava = getWall["groups"][0]["photo_100"]
				ava = requests.get(ava)
				logs.success("Аватарка получена!")
			else:
				ava = getWall["profiles"][0]["photo_100"]
				ava = requests.get(ava)
				logs.success("Аватарка получена!")

			# create link on user/group
			if len(getWall["groups"]) >= 1:
				link_user = "https://vk.com/" + getWall["groups"][0]["screen_name"]
				logs.success("Ссылка на группу получена!")
			else:
				link_user = "https://vk.com/" + getWall["profiles"][0]["screen_name"]
				logs.success("Ссылка на пользователя получена!")

			# getting count users (only for groups)
			if "members_count" in getWall["groups"][0].keys():
				users = f"<center style='font-family: sans-serif; color: #fff; padding: 10px'>Участиков: {str(getWall['groups'][0]['members_count'])} </center>"
				logs.success("Количество участников получено!")
			else:
				users = ""
				logs.info("Количество пользователей не получено!")

			# count posts
			posts_count = f"<center style='font-family: sans-serif; color: #fff; padding: 10px'>Всего постов в группе: {str(getWall['count'])} </center>"

			# save avatar
			if folder_ == 0:
				with open("avatar.jpg", "wb") as ava_:
					ava_.write(ava.content)
					logs.success("Аватарка скачана!")
			else:
				with open(f"{folder_}/avatar.jpg", "wb") as ava_:
					ava_.write(ava.content)
					logs.success("Аватарка скачана!")

			# html templates
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
					<center><a href='{link_user}' target='_blank'><img src='avatar.jpg' style='border-radius: 100px; margin-top: 20px; box-shadow: 0px 0px 10px #000'></center></a>
					<center style='padding: 10px; font-family: sans-serif; font-size: 20px; color: #fff'>Посты {name}</center>
					{users}
					{posts_count}
				</div>'''

			html2 = ""

			html3 = '''
			</body>
		</html>'''

			logs.success("HTML шаблоны созданы!")

			# formating dialog
			for i in range(count_):
				j = getWall["items"][i]
				if "attachments" in j.keys():
					if j["attachments"][0]["type"] == "photo":
						if photo_ == 0:
							url_photo = j["attachments"][0]["photo"]["sizes"][SIZE_PHOTO]["url"]
							html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
											<span style='display: inline-block; padding: 10px'>{j["text"]}<br></span>
											<div style="padding: 10px">
												<img src='{url_photo}' style='max-width: 680px; border-radius: 10px; box-shadow: 0px 0px 10px #000'>
											</div>
											<div style='padding: 5px'>
												<span style='display: inline-block; padding: 10px'>
													{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров &ensp; {(dt.fromtimestamp(getWall['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</span>
											</div>
										</div>'''
						elif photo_ == 1:
							url_photo = j["attachments"][0]["photo"]["sizes"][SIZE_PHOTO]["url"]
							url_photo = requests.get(url_photo)
							name_photo = f"{(dt.fromtimestamp(j['attachments'][0]['photo']['date'])).strftime('%d-%m-%y~%H-%M')}.jpg"
							if folder_ == 0:
								with open(name_photo, "wb") as file:
									file.write(url_photo.content)
							else:
								with open(f"{folder_}/{name_photo}", "wb") as file:
									file.write(url_photo.content)
							html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
											<div style="padding: 10px">
												<img src='{name_photo}' style='max-width: 680px; border-radius: 10px; box-shadow: 0px 0px 10px #000'>
											</div>
											<span style='display: inline-block; padding: 10px'>{j["text"]}</span>
											<div style='padding: 5px'>
												<span style='display: inline-block; padding: 10px'>
													{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров &ensp; {(dt.fromtimestamp(getWall['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</span>
											</div>
										</div>'''
					elif j["attachments"][0]["type"] == "audio":
						if music_ == 0:
							urlmusic_ = j["attachments"][0]["audio"]["url"]
							html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
											<audio src='{urlmusic_}' controls='controls' style='padding: 10px'>
											<span style='display: inline-block; padding: 10px'>{j["text"]}</span>
											<div style='padding: 5px'>
												<span style='display: inline-block; padding: 10px'>
													{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров &ensp; {(dt.fromtimestamp(getWall['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</span>
											</div>
										</div>'''
						elif music_ == 1:
							urlmusic_ = j["attachments"][0]["audio"]["url"]
							urlmusic_ = requests.get(urlmusic_)
							namemusic_ = f"{(dt.fromtimestamp(j['date'])).strftime('%d-%m-%y~%H-%M')}.mp3"
							if folder_ == 0:
								with open(namemusic_, "wb") as file:
									file.write(urlmusic_.content)
							else:
								with open(f"{folder_}/{namemusic_}", "wb") as file:
									file.write(urlmusic_.content)
							html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
											<audio src='{namemusic_}' controls='controls' style='padding: 10px'></audio>
											<span style='display: inline-block; padding: 10px'>{j["text"]}</span>
											<div style='padding: 5px'>
												<span style='display: inline-block; padding: 10px'>
													{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров &ensp; {(dt.fromtimestamp(getWall['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</span>
											</div>
										</div>'''
					elif j["attachments"][0]["type"] == "doc":
						if doc_ == 0:
							urldoc_ = j["attachments"][0]["audio"]["url"]
							html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
											<a href='{urldoc_}'>ДОКУМЕНТ</a>
											<div style='padding: 5px'>
												<span style='display: inline-block; padding: 10px'>
													{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров &ensp; {(dt.fromtimestamp(getWall['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</span>
											</div>
										</div>'''
						elif doc_ == 1:
							urldoc_ = j["attachments"][0]["doc"]["url"]
							doc_type = getWall["items"][i]["attachments"][0]["doc"]["ext"]
							urldoc_ = requests.get(urldoc_)
							namedoc_ = f"{(dt.fromtimestamp(j[i]['date'])).strftime('%d-%m-%y~%H-%M')}.{doc_type}"
							if doc_type == "jpg" or "png":
								if folder_ == 0:
									with open(namedoc_, "wb") as file:
										file.write(urldoc_.content)
								else:
									with open(f"{folder_}/{namedoc_}", "wb") as file:
										file.write(urldoc_.content)
								html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
												<img src='{namedoc_}' style='max-width: 680px; padding: 10px; border-radius: 20px'>
												<span style='display: inline-block; padding: 10px'>{j["text"]}</span>
												<div style='padding: 5px'>
													<span style='display: inline-block; padding: 10px'>
														{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров &ensp; {(dt.fromtimestamp(getWall['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
													</span>
												</div>
											</div>'''
							elif doc_type == "mp3":
								if folder_ == 0:
									with open(namedoc_, "wb") as file:
										file.write(urldoc_.content)
								else:
									with open(f"{folder_}/{namedoc_}", "wb") as file:
										file.write(urldoc_.content)
								html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
												<audio src='{namedoc_}' controls='controls' style='padding: 10px'></audio>
												<span style='display: inline-block; padding: 15px'>{j["text"]}</span>
												<div style='padding: 5px'>
													<span style='display: inline-block; padding: 10px'>
														{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров &ensp; {(dt.fromtimestamp(getWall['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
													</span>
												</div>
											</div>'''
					elif j["attachments"][0]["type"] == "video":
						text = j["text"]
						likes = j["likes"]["count"]
						reposts = j["reposts"]["count"]
						views = j["views"]["count"]
						url_photo = j["attachments"][0]["video"]["photo_800"]
						url_photo = requests.get(url_photo)
						name_photo = f"{(dt.fromtimestamp(j['date'])).strftime('%d-%m-%y~%H-%M')}.jpg"
						ss = rf'{j["attachments"][0]["video"]["description"]}'
						if folder_ == 0:
							with open(name_photo, "wb") as file:
								file.write(url_photo.content)
						else:
							with open(f"{folder_}/{name_photo}", "wb") as file:
								file.write(url_photo.content)
						html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
										<div style="padding: 10px">
											<img src='{name_photo}' style='max-width: 680px; border-radius: 10px; box-shadow: 0px 0px 10px #000'>
										</div>
										<div style="padding: 30px">
											{ss}
										</div>
										<span style='display: inline-block; padding: 15px'>{j["text"]}</span>
										<div style='padding: 5px'>
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
									<div style='padding: 5px'>
										<span style='display: inline-block; padding: 10px'>
											{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров &ensp; {(dt.fromtimestamp(getWall['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
										</span>
									</div>
								</div>'''

			# joining all fragments html templates
			html_join = html1 + html2 + html3
			logs.success("Создание HTML страницы завершено!")

			if folder_ == 0:
				with open(f"Посты {name}.html", "w", encoding="utf-8") as file:
					file.write(html_join)
					logs.success("Посты сохранены!")
			else:
				with open(f"{folder_}/Посты {name}.html", "w", encoding="utf-8") as file:
					file.write(html_join)
					logs.success("Посты сохранены!")
		elif all_ == 1:
			off = 0

			while True:
				# getting posts history
				try:
					getWall = session.method("wall.get", {
						"domain": id_,
						"offset": off,
						"count": 100,
						"extended": 1,
						"fields": "members_count"
						})
					if getWall["count"] == 0:
						getWall = session.method("wall.get", {
							"owner_id": id_,
							"offset": off,
							"count": 100,
							"extended": 1
							})
						if getWall["count"] == 0:
							getWall = session.method("wall.get", {
								"owner_id": "-" + str(id_),
								"offset": off,
								"count": 100,
								"extended": 1,
								"fields": "members_count"
								})
							if getWall["count"] == 0:
								logs.warn("Пользователь/группа не существует, либо отсутствуют посты!!")
								sys.exit(1)
				except vk_api.exceptions.ApiError as err:
					# logs.error sign in in vk.com
					if str(err)[1] == "5":
						logs.error("Ошибка авторизации! Токен неправильный или срок его действия истёк!")
						sys.exit(1)
					# invalid user/group id
					elif str(err)[1:4] == "100":
						logs.warn("Неправильный id пользователя/группы")
						sys.exit(1)

				# getting name user/group
				if len(getWall["groups"]) >= 1:
					name = getWall["groups"][0]["name"]
					logs.success("Название диалога получено!")
				else:
					name = getWall["profiles"][0]["first_name"] + " " + getWall["profiles"][0]["last_name"]
					logs.success("Название диалога получено!")
				# getting avatar user/group
				if len(getWall["groups"]) >= 1:
					ava = getWall["groups"][0]["photo_100"]
					ava = requests.get(ava)
					logs.success("Аватарка получена!")
				else:
					ava = getWall["profiles"][0]["photo_100"]
					ava = requests.get(ava)
					logs.success("Аватарка получена!")
				# create link on user/group
				if len(getWall["groups"]) >= 1:
					link_user = "https://vk.com/" + getWall["groups"][0]["screen_name"]
					logs.success("Ссылка на группу получена!")
				else:
					link_user = "https://vk.com/" + getWall["profiles"][0]["screen_name"]
					logs.success("Ссылка на пользователя получена!")
				# getting count users (only for groups)
				if "members_count" in getWall["groups"][0].keys():
					users = f"<center style='font-family: sans-serif; color: #fff; padding: 10px'>Участиков: {str(getWall['groups'][0]['members_count'])} </center>"
					logs.success("Количество участников получено!")
				else:
					users = ""
					logs.info("Количество пользователей не получено!")
				# count posts
				posts_count = f"<center style='font-family: sans-serif; color: #fff; padding: 10px'>Всего постов в группе: {str(getWall['count'])} </center>"
				# save avatar
				if folder_ == 0:
					with open("avatar.jpg", "wb") as ava_:
						ava_.write(ava.content)
						logs.success("Аватарка скачана!")
				else:
					with open(f"{folder_}/avatar.jpg", "wb") as ava_:
						ava_.write(ava.content)
						logs.success("Аватарка скачана!")
				# html templates
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
						<center><a href='{link_user}' target='_blank'><img src='avatar.jpg' style='border-radius: 100px; margin-top: 20px; box-shadow: 0px 0px 10px #000'></center></a>
						<center style='padding: 10px; font-family: sans-serif; font-size: 20px; color: #fff'>Посты {name}</center>
						{users}
						{posts_count}
					</div>'''
				html2 = ""
				html3 = '''
				</body>
			</html>'''
				logs.success("HTML шаблоны созданы!")

				# formating dialog
				for i in range(100):
					j = getWall["items"][i]
					if "attachments" in j.keys():
						if j["attachments"][0]["type"] == "photo":
							try:
								if photo_ == 0:
									url_photo = j["attachments"][0]["photo"]["sizes"][SIZE_PHOTO]["url"]
									html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
													<span style='display: inline-block; padding: 10px'>{j["text"]}<br></span>
													<div style="padding: 10px">
														<img src='{url_photo}' style='max-width: 680px; border-radius: 10px; box-shadow: 0px 0px 10px #000'>
													</div>
													<div style='padding: 5px'>
														<span style='display: inline-block; padding: 10px'>
															{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров &ensp; {(dt.fromtimestamp(getWall['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
														</span>
													</div>
												</div>'''
								elif photo_ == 1:
									url_photo = j["attachments"][0]["photo"]["sizes"][SIZE_PHOTO]["url"]
									url_photo = requests.get(url_photo)
									name_photo = f"{(dt.fromtimestamp(j['attachments'][0]['photo']['date'])).strftime('%d-%m-%y~%H-%M')}.jpg"
									if folder_ == 0:
										with open(name_photo, "wb") as file:
											file.write(url_photo.content)
									else:
										with open(f"{folder_}/{name_photo}", "wb") as file:
											file.write(url_photo.content)
									html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
													<div style="padding: 10px">
														<img src='{name_photo}' style='max-width: 680px; border-radius: 10px; box-shadow: 0px 0px 10px #000'>
													</div>
													<span style='display: inline-block; padding: 10px'>{j["text"]}</span>
													<div style='padding: 5px'>
														<span style='display: inline-block; padding: 10px'>
															{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров &ensp; {(dt.fromtimestamp(getWall['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
														</span>
													</div>
												</div>'''
							except IndexError:
								pass
						elif j["attachments"][0]["type"] == "audio":
							if music_ == 0:
								urlmusic_ = j["attachments"][0]["audio"]["url"]
								html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
												<audio src='{urlmusic_}' controls='controls' style='padding: 10px'>
												<span style='display: inline-block; padding: 10px'>{j["text"]}</span>
												<div style='padding: 5px'>
													<span style='display: inline-block; padding: 10px'>
														{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров &ensp; {(dt.fromtimestamp(getWall['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
													</span>
												</div>
											</div>'''
							elif music_ == 1:
								urlmusic_ = j["attachments"][0]["audio"]["url"]
								urlmusic_ = requests.get(urlmusic_)
								namemusic_ = f"{(dt.fromtimestamp(j['date'])).strftime('%d-%m-%y~%H-%M')}.mp3"
								if folder_ == 0:
									with open(namemusic_, "wb") as file:
										file.write(urlmusic_.content)
								else:
									with open(f"{folder_}/{namemusic_}", "wb") as file:
										file.write(urlmusic_.content)
								html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
												<audio src='{namemusic_}' controls='controls' style='padding: 10px'></audio>
												<span style='display: inline-block; padding: 10px'>{j["text"]}</span>
												<div style='padding: 5px'>
													<span style='display: inline-block; padding: 10px'>
														{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров &ensp; {(dt.fromtimestamp(getWall['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
													</span>
												</div>
											</div>'''
						elif j["attachments"][0]["type"] == "doc":
							if doc_ == 0:
								urldoc_ = j["attachments"][0]["doc"]["url"]
								html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
												<a href='{urldoc_}'>ДОКУМЕНТ</a>
												<div style='padding: 5px'>
													<span style='display: inline-block; padding: 10px'>
														{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров &ensp; {(dt.fromtimestamp(getWall['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
													</span>
												</div>
											</div>'''
							elif doc_ == 1:
								urldoc_ = j["attachments"][0]["doc"]["url"]
								doc_type = getWall["items"][i]["attachments"][0]["doc"]["ext"]
								urldoc_ = requests.get(urldoc_)
								namedoc_ = f"{(dt.fromtimestamp(j[i]['date'])).strftime('%d-%m-%y~%H-%M')}.{doc_type}"
								if doc_type == "jpg" or "png":
									if folder_ == 0:
										with open(namedoc_, "wb") as file:
											file.write(urldoc_.content)
									else:
										with open(f"{folder_}/{namedoc_}", "wb") as file:
											file.write(urldoc_.content)
									html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
													<img src='{namedoc_}' style='max-width: 680px; padding: 10px; border-radius: 20px'>
													<span style='display: inline-block; padding: 10px'>{j["text"]}</span>
													<div style='padding: 5px'>
														<span style='display: inline-block; padding: 10px'>
															{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров &ensp; {(dt.fromtimestamp(getWall['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
														</span>
													</div>
												</div>'''
								elif doc_type == "mp3":
									if folder_ == 0:
										with open(namedoc_, "wb") as file:
											file.write(urldoc_.content)
									else:
										with open(f"{folder_}/{namedoc_}", "wb") as file:
											file.write(urldoc_.content)
									html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
													<audio src='{namedoc_}' controls='controls' style='padding: 10px'></audio>
													<span style='display: inline-block; padding: 15px'>{j["text"]}</span>
													<div style='padding: 5px'>
														<span style='display: inline-block; padding: 10px'>
															{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров &ensp; {(dt.fromtimestamp(getWall['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
														</span>
													</div>
												</div>'''
						elif j["attachments"][0]["type"] == "video":
							text = j["text"]
							likes = j["likes"]["count"]
							reposts = j["reposts"]["count"]
							views = j["views"]["count"]
							try:
								url_photo = j["attachments"][0]["video"]["photo_800"]
								url_photo = requests.get(url_photo)
							except KeyError:
								url_photo = j["attachments"][0]["video"]["photo_320"]
								url_photo = requests.get(url_photo)
							name_photo = f"{(dt.fromtimestamp(j['date'])).strftime('%d-%m-%y~%H-%M')}.jpg"
							ss = rf'{j["attachments"][0]["video"]["description"]}'
							if folder_ == 0:
								with open(name_photo, "wb") as file:
									file.write(url_photo.content)
							else:
								with open(f"{folder_}/{name_photo}", "wb") as file:
									file.write(url_photo.content)
							html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
											<div style="padding: 10px">
												<img src='{name_photo}' style='max-width: 680px; border-radius: 10px; box-shadow: 0px 0px 10px #000'>
											</div>
											<div style="padding: 30px">
												{ss}
											</div>
											<span style='display: inline-block; padding: 15px'>{j["text"]}</span>
											<div style='padding: 5px'>
												<span style='display: inline-block; padding: 10px'>
													{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров &ensp; {(dt.fromtimestamp(getWall['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
												</span>
											</div>
										</div>'''
					elif not "attachments" in j.keys():
						try:
							text = j["text"]
							likes = j["likes"]["count"]
							reposts = j["reposts"]["count"]
							views = j["views"]["count"]
						except:
							pass
						html2 += f'''<div style='margin-bottom: 10px; width: 750px; box-sizing: content-box; background: linear-gradient(to right, #3E608A, #69A3EA); border-radius: 10px; font-family: sans-serif; margin-left: auto; margin-right: auto;'>
										<span style='display: inline-block; padding: 10px'>{j["text"]}</span>
										<div style='padding: 5px'>
											<span style='display: inline-block; padding: 10px'>
												{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["comments"]["count"]} комментариев &ensp; {j["views"]["count"]} просмотров &ensp; {(dt.fromtimestamp(getWall['items'][i]['date'])).strftime('%d %B %Y %H:%M:%S')}
											</span>
										</div>
									</div>'''
				# offset in messages
				off += 100
				if getWall["count"] < 100:
				    off = getWall["count"]
				elif getWall["count"] == 0:
					sys.exit(1)

				# joining all fragments html templates
				html_join = html1 + html2 + html3
				logs.success("Создание HTML страницы завершено!")

			if folder_ == 0:
				with open(f"Посты {name}.html", "w", encoding="utf-8") as file:
					file.write(html_join)
					logs.success(f"Сохранено {off} постов!")
			else:
				with open(f"{folder_}/Посты {name}.html", "w", encoding="utf-8") as file:
					file.write(html_join)
					logs.success(f"Сохранено {off} постов!")

		# delete folder __pycache__ after the work of the program
		try:
			shutil.rmtree("__pycache__")
		except Exception:
			pass
except KeyboardInterrupt:
	logs.warn("Выход!")
	sys.exit(1)