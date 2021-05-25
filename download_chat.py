import vk_api
from cfg import token
import requests

def download_chat(user_id, count):
	session = vk_api.VkApi(token = token)

	getHistory = session.method("messages.getHistory", {
		"user_id": user_id,
		"count": count,
		})

	###################################################################

	#для заголовка
	'''<div style='width: 750px; margin: 10px auto 10px auto; background-color: #5381B9;
		border-radius: 10px'>
			<center style='padding: 10px; font-family: sans-serif; font-size: 20px; color: #fff'>Чат с {name}</center>
		</div>'''

	html1 = f'''<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8">
		<title></title>'''

	html2 = f'''
		<style>
		</style>
	</head>
	<body style='background-color: #333;'>
		<div style='width: 750px; box-sizing: padding-box; background-color: #5281B9; border-radius: 10px;
		font-family: sans-serif; margin-left: auto; margin-right: auto'>'''

	html3 = ""

	html4 = '''
		</div>
	</body>
</html>'''
	###################################################################
	
	for i in range(count):
		getUsers = session.method("users.get", {
			"user_ids": getHistory["items"][i]["from_id"]
		})

		if len(getHistory["items"][i]["attachments"]) >= 1:
			if getHistory["items"][i]["attachments"][0]["type"] == "photo":
				url_photo = getHistory["items"][i]["attachments"][0]["photo"]["sizes"][0]["url"]
				html3 += "<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px; border-radius: 10px; margin: 10px -50px auto 10px'>" + f"<img src='{url_photo}'>" + "<span style='font-size: 10px; color: linear-gradient(to right, #000, #fff); font-weight: bold; margin-left: 5px'> " + getUsers[0]["first_name"] + "</span></div><br>"
			elif getHistory["items"][i]["attachments"][0]["type"] == "audio_message":
				url_audio = getHistory["items"][i]["attachments"][0]["audio_message"]["link_mp3"]
				html3 += "<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px; border-radius: 10px; margin: 10px -50px auto 10px'>" + f"<audio src='{url_audio}' controls='controls'></audio>" + "<span style='font-size: 10px; color: linear-gradient(to right, #000, #fff); font-weight: bold; margin-left: 5px'> " + getUsers[0]["first_name"] + "</span></div><br>"
		elif len(getHistory["items"][i]["attachments"]) < 1:
			html3 += "<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px; border-radius: 10px; margin: 10px -50px auto 10px'>" + getHistory["items"][i]["text"] + "<span style='font-size: 10px; color: linear-gradient(to right, #000, #fff); font-weight: bold; margin-left: 5px'> " + getUsers[0]["first_name"] + "</span></div><br>"

	html_join = html1 + html2 + html3 + html4

	###################################################################
	with open("chat.html", "w", encoding="utf-8") as file:
		file.write(html_join)