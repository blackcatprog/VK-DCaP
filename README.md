<p align="center"><img src="logo.png" height="120"></p>
<h1 align="center">VK-DCaP</h1>
<p align="center">
<a href="https://github.com/blackcatprog/VK-DCaP/releases"><img src="https://img.shields.io/github/v/release/blackcatprog/VK-DCaP?color=important"></a>
<a href="https://github.com/blackcatprog/VK-DCaP/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green" height="20"></a>
<img src="https://img.shields.io/badge/Platforms-Windows%20%7C%20Android%20%7C%20Linux-blue" height="20">
</p>

<video src="video.mkv" controls width="320" height="240">
</video>

Получите токен от вконтакте:
1) Установите все необходимые модули "pip install -r requirements.txt"
1) [Перейдите на этот сайт](https://vkhost.github.io)
2) Выберите vk admin, нажмите разрешить
3) Скопируйте токен в адресной строке от token= до &expires

Вставьте свой токен в переменную token в файле token (токен должен быть в кавычках)

Перейдите в папку, которую вы распаковали из архива.

Базовый синтаксис:

```
python dcap.py [что скачивать] [id пользователя/беседы/группы] -c [количество сообщений/постов (по умолчанию 20)] [параметры]

Что скачивать:
-cd                   чат
-pd                   посты

Параметры:
-id                   скачивать фото вместо подстановки ссылок
-q [качество]         указать размер скачиваемых изображений: s - 75px, m - 130px, p - 200px, q - 320px, r - 510px, x - 604px, y - 807px, w - 1600px
-ad                   скачивать голосовые сообщения вместо подстановки ссылок
-md                   скачивать музыку вместо подстановки ссылок
-dd                   скачивать документы вместо подстановки ссылок
-f [название папки]   скачивание диалога/поста(ов) в указанную папку
-af                   скачать все вложения
-ul                   превращать имена пользователей рядом с сообщениями в ссылки на этих пользователей
-sm                   оформлять сообщения с музыкой
-ud                   скачивать аватарки пользователей в беседе
-all                  скачать весь диалог
-help                 краткая документация
```
