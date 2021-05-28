import vk_api
from cfg import *
from logs import *
import requests
from colorama import Fore

def download_post(user_id, count, _photo=0, _music=0, _document=0):
	#params
	DOWNLOAD_PHOTO = _photo
	DOWNLOAD_MUSIC = _music
	DOWNLOAD_DOCUMENT = _document

	session = vk_api.VkApi(token = token)

	try:
		getWall = session.method("wall.get", {
			"owner_id": user_id,
			"count": count,
			"extended": 1
			})
	except vk_api.exceptions.ApiError as err:
		getWall = session.method("wall.get", {
			"owner_id": "-"+user_id,
			"count": count,
			"extended": 1
			})
	except vk_api.exceptions.ApiError as err:
		err = str(err)
		if err[1] == "5":
			print(error + " - Неправильный токен")
		sys.exit(1)

	name = getWall["profiles"][0]["first_name"] + " " + getWall["profiles"][0]["last_name"]

	html1 = f'''<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8">
		<title>Посты {name}</title>
		<style>
		</style>
	</head>
	<body style='background-color: #333'>
		<div style='width: 750px; margin: 10px auto 10px auto; background-color: #5381B9;border-radius: 10px'>
			<center style='padding: 10px; font-family: sans-serif; font-size: 20px; color: #fff'>Посты {name}</center>
		</div>
		<div style='width: 750px; box-sizing: content-box; background-color: #5281B9; border-radius: 10px;
		font-family: sans-serif; margin-left: auto; margin-right: auto;'>'''

	html2 = ""

	html3 = '''
		</div>
	</body>
</html>'''

	for i in range(count):
		j = getWall["items"][i]
		if len(j["attachments"]) < 1:
				text = j["text"]
				likes = j["likes"]["count"]
				reposts = j["reposts"]["count"]
				views = j["views"]["count"]
		elif len(j["attachments"]) >= 1:
			if j["attachments"][0]["type"] == "photo":
				if DOWNLOAD_PHOTO == 0:
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
					html2 += f'''<div style='width: 500px; height: 250px; box-sizing: content-box'><span style=''><img src='{url_photo}'
						style='padding: 10px; border-radius: 20px'>{j["text"]}<div style='padding: 10px'><span style='display: inline-block; padding: 10px'>
						{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["views"]["count"]} просмотров
						</span></div></span></div>'''
				elif DOWNLOAD_PHOTO == 1:
					if SIZE_PHOTO == 0:
							what_size_photo = str(input("В каком качестве скачать изображения (s(75px), m(130px), x(604px)): "))
							if what_size_photo == "s":
								SIZE_PHOTO = 5
							elif what_size_photo == "m":
								SIZE_PHOTO = 0
							elif what_size_photo == "x":
								SIZE_PHOTO = 6
					url_photo = j["attachments"][0]["photo"]["sizes"][SIZE_PHOTO]["url"]
					url_photo = requests.get(url_photo)
					name_photo = f"{(dt.fromtimestamp(getHistory['items'][i]['attachments'][0]['photo']['date'])).strftime('%d-%m-%y~%H-%M')}.jpg"
					with open(name_photo, "wb") as file:
						file.write(url_photo.content)
					html2 += f'''<div style='width: 500px; height: 250px; box-sizing: content-box'><span style=''><img src='{name_photo}'
						style='padding: 10px; border-radius: 20px'>{j["text"]}<div style='padding: 10px'><span style='display: inline-block; padding: 10px'>
						{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["views"]["count"]} просмотров
						</span></div></span></div>'''
			elif j["attachments"][0]["type"] == "audio":
				if DOWNLOAD_MUSIC == 0:
					url_music = getHistory["items"][i]["attachments"][0]["audio"]["url"]
					html2 += f'''<div style='width: 500px; height: 250px; box-sizing: content-box'><span style=''><audio src='{name_music}'
						controls='controls' style='padding: 10px'>{j["text"]}<div style='padding: 10px'><span style='display: inline-block; padding: 10px'>
						{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["views"]["count"]} просмотров
						</span></div></span></div>'''
				elif DOWNLOAD_MUSIC == 1:
					url_music = getHistory["items"][i]["attachments"][0]["audio"]["url"]
					url_music = requests.get(url_music)
					name_music = f"{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y~%H-%M')}.mp3"
					with open(name_music, "wb") as file:
						file.write(url_music.content)
					html2 += f'''<div style='width: 500px; height: 250px; box-sizing: content-box'><span style=''><audio src='{name_music}'
						controls='controls' style='padding: 10px'>{j["text"]}</audio><div style='padding: 10px'><span style='display: inline-block; padding: 10px'>
						{j["likes"]["count"]} лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["views"]["count"]} просмотров
						</span></div></span></div>'''
			elif j["attachments"][0]["type"] == "doc":
				if DOWNLOAD_DOCUMENT == 0:
					url_document = getHistory["items"][i]["attachments"][0]["audio"]["url"]
					html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
					border-radius: 10px; margin: 10px -50px auto 10px'><audio src='{url_music}' controls='controls'></audio>
					<span style='padding: 10px; font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
					{getUsers[0]["first_name"]}</span></div><br>'''
				elif DOWNLOAD_DOCUMENT == 1:
					url_doc = getHistory["items"][i]["attachments"][0]["doc"]["url"]
					doc_type = getHistory["items"][i]["attachments"][0]["doc"]["ext"]
					url_doc = requests.get(url_doc)
					name_doc = f"{(dt.fromtimestamp(getHistory['items'][i]['date'])).strftime('%d-%m-%y~%H-%M')}.{doc_type}"
					if doc_type == "jpg" or "png":
						with open(name_doc, "wb") as file:
							file.write(url_doc.content)
						html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
						border-radius: 10px; margin: 10px -50px auto 10px'><img src='{name_doc}' style='padding: 10px; border-radius: 20px'>
						{j["text"]}<div style='padding: 10px'><span style='display: inline-block; padding: 10px'>{j["likes"]["count"]}
						лайков &ensp; {j["reposts"]["count"]} репостов &ensp; {j["views"]["count"]} просмотров</span></div></span></div>'''
					elif doc_type == "mp3":
						with open(name_doc, "wb") as file:
							file.write(url_doc.content)
						html2 += f'''<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px;
						border-radius: 10px; margin: 10px -50px auto 10px'><audio src='{name_doc}' controls='controls'></audio>
						<span style='padding: 10px; font-size: 10px; color: #000; font-weight: bold; margin-left: 5px'>
					{getUsers[0]["first_name"]}</span></div><br>'''

	html_join = html1 + html2 + html3

	with open("post.html", "w", encoding="utf-8") as file:
		file.write(html_join)

	print(succes + "Пост(ы) скачан(ы)")