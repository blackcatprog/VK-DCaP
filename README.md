<p align="center"><img src="logo.png" height="120"></p>
<h1 align="center">VK-DCaP</h1>
<p align="center">
<a href="https://github.com/blackcatprog/VK-DCaP/releases"><img src="https://img.shields.io/github/v/release/blackcatprog/VK-DCaP?color=important"></a>
<a href="https://github.com/blackcatprog/VK-DCaP/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green" height="20"></a>
<img src="https://img.shields.io/badge/Platforms-Windows%20%7C%20Android%20%7C%20Linux-blue" height="20">
</p>

Получите токен от вконтакте:
1) [Перейдите на этот сайт](vkhost.github.io)
2) Выберите vk admin, нажмите разрешить
3) Скопируйте токен в адресной строке от token= до &expires

Вставьте свой токен в переменную token в файле cfg (токен должен быть в кавычках)

Перейдите в папку, которую вы распаковали из архива.

Базовый синтаксис:

```
python dcap.py [что скачивать] [id пользователя/группы] -c [количество сообщений/постов (по умолчанию 20)] [параметры]

Что скачивать:
-cd                   чат
-pd                   посты

Параметры:
-id                   скачивать фото вместо подстановки ссылок
-ad                   скачивать голосовые сообщения вместо подстановки ссылок
-md                   скачивать музыку вместо подстановки ссылок
-dd                   скачивать документы вместо подстановки ссылок
-f [название папки]   скачивание диалога/поста(ов) в указанную папку
-log                  отчёт о работе программы
```
