import vk_api
from cfg import token

def download_post(user, count):
	session = vk_api.VkApi(token = token)

	getWall = session.method("wall.get", {
		"owner_id": user,
		"count": count
		})

	posts_list = []

	for i in range(int(count)):
		post = getWall["items"][i]
		posts_list.append(post)

	html1 = '''<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8">
		<title></title>
		<style>
		</style>
	</head>
	<body style='background-color: #333'>
		<div style='width: 750px; box-sizing: content-box; background-color: #5281B9; border-radius: 10px;
		font-family: sans-serif; margin-left: auto; margin-right: auto; box-shadow: 0px 0px 10px #fff'>'''

	html2 = ""

	html3 = '''
		</div>
	</body>
</html>'''

	for j in posts_list:
		print(j)
		url = ""
		text = ""
		likes = 0
		reposts = 0
		views = 0
		if j["text"] != "":
			if j["attachments"]:
				text = j["text"]
				likes = j["likes"]["count"]
				reposts = j["reposts"]["count"]
				views = j["views"]["count"]
				if j["attachments"][0]["type"] == "photo":
					url = j["attachments"][0]["photo"]["sizes"][0]["url"]
			elif not j["attachments"]:
				text = j["text"]
				likes = j["likes"]["count"]
				reposts = j["reposts"]["count"]
				views = j["views"]["count"]
		elif j["text"] == "":
			if j["attachments"]:
				text = j["text"]
				likes = j["likes"]["count"]
				reposts = j["reposts"]["count"]
				views = j["views"]["count"]
				if j["attachments"][0]["type"] == "photo":
					url = j["attachments"][0]["photo"]["sizes"][0]["url"]
			elif not j["attachments"]:
				text = j["text"]
				likes = j["likes"]["count"]
				reposts = j["reposts"]["count"]
				views = j["views"]["count"]

		html2 += f'''<div style='width: 500px; height: 250px; box-sizing: content-box'>
			<span style=''>
				<img src='{url}' style='padding: 10px>
				{text}
				<span style='display: block; margin-bottom: 0px>
				{likes} лайков
				{reposts} репостов
				{views} просмотров
				</span>
			</span>
		</div>'''

	html_join = html1 + html2 + html3

	with open("post.html", "w", encoding="utf-8") as file:
		file.write(html_join)