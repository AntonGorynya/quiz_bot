# Telegram и VK боты для викторины
Боты собой представляют викторину в чате.
### Как установить

После чего создайте файл **.env** вида:
```
TG_TOKEN='<Ваш токен>'
```
Python3 должен быть уже установлен. 
Затем используйте `pip` (или `pip3`, есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```
Скачайте [архив с вопросами](https://dvmn.org/media/modules_dist/quiz-questions.zip) и распакуйте в папку со скриптом

### Пример запуска

Ниже представлен пример запуска для получения количества переходов по Битли ссылке
```
> python ./main.py 

```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).