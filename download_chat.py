import vk_api
from cfg import token
import requests

def download_chat(user_id, count):
	session = vk_api.VkApi(token = token)

	getHistory = session.method("messages.getHistory", {
		"user_id": user_id,
		"count": count
		})

	messages = []

	html1 = '''<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8">
		<title></title>
		<style>
		</style>
	</head>
	<body style='background-color: #333;'>
		<div style='width: 750px; box-sizing: content-box; background-color: #5281B9; border-radius: 10px;
		font-family: sans-serif; margin-left: auto; margin-right: auto; box-shadow: 0px 0px 10px #fff'>'''

	html2 = ""

	html3 = '''
		</div>
	</body>
</html>'''
	
	for i in range(count):
		getUsers = session.method("users.get", {
			"user_ids": getHistory["items"][i]["from_id"]
		})

		message = getHistory["items"][i]["text"] + f"-{getUsers[0]['first_name']}" + f"|{getUsers[0]['id']}"
		messages.append(message)

	print(messages)

	for j in messages:
		html2 += "<div style='display: inline-block; max-width: 700px; background-color: #D6E1E7; padding: 10px; border-radius: 10px; margin: 10px -50px auto 10px'>" + j.split("-")[0] + "<span style='font-size: 10px; color: linear-gradient(to right, #000, #fff); font-weight: bold; margin-left: 5px'> " + j.split("-")[1].split("|")[0] + "</span></div><br>"

	html_join = html1 + html2 + html3

	with open("chat.html", "w", encoding="utf-8") as file:
		file.write(html_join)