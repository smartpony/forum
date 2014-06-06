#
# Обработка запросов клиентов
#

from flask import render_template, redirect, url_for, request, abort
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.sqlalchemy import sqlalchemy
func = sqlalchemy.func
from datetime import datetime
import hashlib
import os
import random
import urllib2
from cgi import escape
from math import ceil
from PIL import Image, ImageOps
import re

# Импорт других файлов проекта
from app import app, db, lm
from models import User, ForumTopic, ForumMessage, Mailbox
from forms import TopicForm, MessageForm, LoginForm, RegisterForm, ProfileForm,\
    RecepientForm, SearchForm, FillForm


# --- ОФОРМЛЕНИЕ --------------------------------
# Тем на странице
TOPIC_PER_PAGE = 5
# Сообщений на странице
MESSAGE_PER_PAGE = 5
# Пользователей на странице
USER_PER_PAGE = 10
# Писем на странице
MAIL_PER_PAGE = 5


# --- ПАГИНАЦИЯ ---------------------------------
class Pagination(object):
    # Инициализация
    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    # Количество страниц
    @property
    def pages(self):
        return(int(ceil(float(self.total_count)/self.per_page)))

    # Список номеров страниц, которые будут внизу страницы
    @property
    def pages_list(self):
        if self.pages < 4:
            res = range(1, self.pages+1)
        elif self.page < 3 and self.page+2 < self.pages:
            res = range(1, self.page+3)
        elif self.page < 3 and self.page+2 >= self.pages:
            res = range(1, self.pages+1)
        elif self.page > self.pages-3:
            res = range(self.page-2, self.pages+1)
        else:
            res = range(self.page-2, self.page+3)

        return(res)

    # Номер начального элемента для страницы
    @property
    def first(self):
        if self.page == 1:
            return(0)
        else:
            return((self.page-1)*self.per_page)

    # Номер последнего элемента
    @property
    def last(self):
        if self.page == self.pages:
            # Чтобы в результате был диапазон [число:None] эквивалентно [число:]
            return(None)
        else:
            return(self.page*self.per_page)

    # Заполнена ли последняя страница до конца
    @property
    def last_full(self):
        if self.total_count % self.per_page == 0:
            return(True)
        else:
            return(False)


# --- ФОРМАТИРОВАНИЕ СООБЩЕНИЙ ------------------
def message_format(text, to_html):
    # Замена форумных тегов на HTML
    if to_html:
        text = escape(text)
        text = text.replace('[b]', '<b>').replace('[/b]', '</b>').\
            replace('[i]', '<i>').replace('[/i]', '</i>').\
            replace('[u]', '<u>').replace('[/u]', '</u>')
        text = re.sub('\[a href="(.*)"\](.*)\[/a\]', '<a href="\\1">\\2</a>', text)
        text = re.sub('\[img src="(.*)"\]', '<img src="\\1">', text)
    # Выдача текста для редактирования в виде форумных тегов и с обратным экранированием
    else:
        text = text.replace('<b>', '[b]').replace('</b>', '[/b]').\
            replace('<i>', '[i]').replace('</i>', '[/i]').\
            replace('<u>', '[u]').replace('</u>', '[/u]')
        text = re.sub('<a href="(.*)"\>(.*)</a>', '\[a href="\\1"\]\\2\[/a\]', text)
        text = re.sub('<img src="(.*)">', '\[img src="\\1"\]', text)
    return(text)


# --- ЗАГРУЗКА ПОЛЬЗОВАТЕЛЯ ---------------------
# Кастомный анонимный пользователь с добавлением поля role
class CustomAnonymous():
    role = 65535
    # Методы для работы Flask-login
    def is_authenticated(self):
        return(False)
    def is_active(self):
        return(True)
    def is_anonymous(self):
        return(True)
    def get_id(self):
        return(65535)
    # Вывод при обращении к объекту класса
    def __repr__(self):
        return('<Anonymous>')

# Переопределение анонимного пользователя
lm.anonymous_user = CustomAnonymous

# Функция загружает объект пользователя по его ID,
# который хранится в памяти
@lm.user_loader
def load_user(id):
    return(User.query.get(int(id)))


# --- РЕГИСТРАЦИЯ -------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Форма регистрации
    form = RegisterForm()

    if request.method == 'POST' and form.validate_on_submit():
        # Данные из формы
        user_login = form.login.data
        user_email = form.email.data
        user_password = form.password.data
        user_password_confirm = form.password_confirm.data

        '''if user_password == user_password_confirm:
            user_password = hashlib.sha256(user_password).hexdigest()
        else:
            return(render_template('info.html',
                user=current_user,
                text='"Passwod" and "Confirm password" must be the same'))'''

        user_password = hashlib.sha256(user_password).hexdigest()

        # Код для подтверждения почты
        confirm_code = hex(random.randint(0x000000000000000,0xfffffffffffffff)).rstrip("L").lstrip("0x")

        # Регистрация
        new_user = User(login=user_login,
            password=user_password,
            email=user_email,
            confirm_code=confirm_code)
        db.session.add(new_user)
        db.session.commit()

        # Сообщение об успешной регистрации
        return(render_template('info.html',
            user=current_user,
            text='Confirmation code: \
                <a href="%s">%s</a>' % \
                (url_for('reg_confirm',
                    user=user_login,
                    email=user_email,
                    code=confirm_code),
                confirm_code)))

    # Вернуть страницу
    return(render_template('register.html',
        user=current_user,
        register_form=form))


# --- ПОДТВЕРЖДЕНИЕ ПОЧТЫ ПРИ РЕГИСТРАЦИИ -------
@app.route('/reg_confirm')
def reg_confirm():
    user = request.args.get('user')
    email = request.args.get('email')
    code = request.args.get('code')

    reg_user = User.query.filter_by(login=user).first()

    # Проверка существования объекта
    if not reg_user:
        abort(404)

    # Проверка переданных данных
    if reg_user.email == email and reg_user.confirm_code == code:
        reg_user.confirm_code = ''
        reg_user.active = True
        db.session.commit()

        # Войти под новым пользователем
        login_user(reg_user)

        # Здесь должен быть код, отправляющий письмо
        # <ПУСТО>

        return(render_template('info.html',
            user=current_user,
            text='Registered succesfully with email %s' % current_user.email))
    else:
        return(render_template('info.html',
            user=current_user,
            text='There is an error in your confirmation code.'))


# --- ВХОД ПОЛЬЗОВАТЕЛЯ -------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Форма логина
    form = LoginForm()

    # Если отправлена форма
    if request.method == 'POST':
        # Данные из формы
        user_login = form.login.data
        user_password = form.password.data

        # Найти пользователя в базе по логину и паролю
        user = User.query.filter \
            ((User.login==user_login) & \
            (User.password==hashlib.sha256(user_password).hexdigest())) \
            .first()

        # Если пользователь найден и не заблокирован, войти
        if user and user.is_active():
            login_user(user)
            current_user.last_seen = datetime.utcnow()
            db.session.commit()
            # Вернуться в корень форума
            return(redirect(url_for('forum')))
        # Если пользователь не найден, выдать ошибку
        elif user and not user.is_active():
            return(render_template('info.html',
                user=current_user,
                text='User %s is blocked or not activated yet.' % user.login))
        else:
            return(render_template('info.html',
                user=current_user,
                text='Invalid login or password'))

    # Вернуть страницу
    return(render_template('login.html',
        user=current_user,
        login_form=form))


# --- ФОРУМ -------------------------------------
@app.route('/')
@app.route('/forum', methods=['GET', 'POST'])
def forum(page=1):
    # Нужная страница
    if request.args.get('page'):
        page = int(request.args.get('page'))

    # Разбиение на страницы
    pagination = Pagination(page, TOPIC_PER_PAGE, ForumTopic.query.count())

    # Форма для постинга сообщений
    form_topic = TopicForm()
    form_message = MessageForm()

    # Если отправлена форма постинга
    if request.method == 'POST' and form_topic.validate_on_submit() and form_message.validate_on_submit():
        # Данные из формы c применением форматирования
        data_topic = form_topic.topic.data
        data_message = message_format(form_message.message.data, True)
        # Создание темы и обновление счётчиков у пользователя
        new_topic = ForumTopic(name=data_topic, author_id=current_user.id)
        current_user.message_count += 1
        current_user.topic_count += 1
        db.session.add(new_topic)
        # Коммит в этом месте нужен, чтобы появился ID
        db.session.commit()
        # Создание сообщения
        new_mes = ForumMessage(topic_id=new_topic.id, author_id=current_user.id, text=data_message)
        db.session.add(new_mes)
        db.session.commit()
        return(redirect(url_for('topic', topic_id=str(new_topic.id))))

    # Выборка всех тем с счётчиком сообщений для каждой
    # Подзапрос
    all_topics_subq = db.session.query(
        ForumMessage.topic_id, func.count(ForumMessage.id).label('mes_count')).\
        group_by(ForumMessage.topic_id).\
        subquery()
    # Основной запрос
    all_topics = db.session.query(
        ForumTopic, all_topics_subq.c.mes_count).\
        join(all_topics_subq, ForumTopic.id == all_topics_subq.c.topic_id).\
        order_by(ForumTopic.time_last.desc()).all()

    # Вернуть страницу
    return(render_template('forum.html',
        user=current_user,
        all_topics=all_topics,
        form_topic=form_topic,
        form_message=form_message,
        pagination=pagination))


# --- ТЕМА НА ОТДЕЛЬНОЙ СТРАНИЦЕ ----------------
@app.route('/forum/topic/show/<topic_id>', methods=['GET', 'POST'])
def topic(topic_id, page=1):
    # Объект текущего топика
    current_topic = ForumTopic.query.get(topic_id)

    # Нужная страница
    if request.args.get('page'):
        page = int(request.args.get('page'))

    # Проверка существования объекта
    if not current_topic:
        abort(404)

    # Форма добавления нового сообщения
    form_message = MessageForm()

    # Разбиение на страницы
    pagination = Pagination(page, MESSAGE_PER_PAGE, current_topic.message.count())

    # Если отправлена форма постинга
    if request.method == 'POST' and form_message.validate_on_submit():
        # Данные из формы c применением форматирования
        data_message = message_format(form_message.message.data, True)
        # Создание сообщения
        new_mes = ForumMessage(topic_id=topic_id, author_id=current_user.id, text=data_message)
        current_topic.time_last = datetime.utcnow()
        current_user.message_count += 1
        db.session.add(new_mes)
        # Запись последнего автора темы
        ForumTopic.query.get(topic_id).editor_id = current_user.id
        db.session.commit()

        # Вернуть последнюю страницу
        if pagination.last_full:
            return(redirect(url_for('topic', topic_id=topic_id, page=pagination.pages+1)))
        else:
            return(redirect(url_for('topic', topic_id=topic_id, page=pagination.pages)))

    # Счётчик просмотров +1
    current_topic.views += 1
    db.session.commit()

    # Вернуть страницу
    return(render_template('topic.html',
        user=current_user,
        topic=current_topic,
        form_message=form_message,
        pagination=pagination))


# --- УДАЛЕНИЕ ТЕМ ------------------------------
# Примечание: сообщения топика каскадно удаляются
# следом за топиком (см. model.py)
@app.route('/forum/topic/delete/<topic_id>')
@login_required
def delete_topic(topic_id):
    del_topic = ForumTopic.query.get(topic_id)

    # Проверка существования объекта
    if not del_topic:
        abort(404)

    # Является ли пользователь автором топика или админом/модером
    if del_topic.author == current_user or current_user.role < 2:
        # Убавить счётчики
        del_topic.author.topic_count -= 1
        for del_message in del_topic.message:
            del_message.author.message_count -=1
        db.session.delete(del_topic)
        db.session.commit()
    # Если пользователь не является автором, выдать ошибку
    else:
        return(render_template('info.html',
            user=current_user,
            text="You can't delete topic if you are not it's author"))

    # Вернуться в корень форума
    return(redirect(url_for('forum')))


# --- РЕДАКТИРОВАНИЕ СООБЩЕНИЙ ------------------
@app.route('/forum/message/edit/<message_id>', methods=['GET', 'POST'])
@login_required
def edit_message(message_id):
    edit_message = ForumMessage.query.get(message_id)

    # Проверка существования объекта
    if not edit_message:
        abort(404)

    # Форма постинга сообщения
    form_message = MessageForm()

    # Если отправлена форма постинга
    if request.method == 'POST' and form_message.validate_on_submit():
        # Данные из формы c применением форматирования
        edit_message.text = message_format(form_message.message.data, True)
        # Отметка о дате изменения
        edit_message.date_edit =  datetime.utcnow()
        # Отметка о последнем редакторе
        edit_message.editor_id = current_user.id
        db.session.commit()
        # Вернуть страницу топика
        return(redirect(url_for('topic', topic_id=edit_message.topic_id)))

    # Является ли пользователь автором сообщения или админом/модером
    if edit_message.author == current_user or current_user.role < 2:
        # Вывод старого сообщения в форме
        form_message.message.data = edit_message.text.replace('<', '[').replace('>', ']')
        # Вывод странички
        return(render_template('message_edit.html',
            user=current_user,
            message=edit_message,
            form_message=form_message))
    # Если нет, то выдать ошибку
    else:
        return(render_template('info.html',
            user=current_user,
            text="You can't edit message if you are not it's author"))


# --- УДАЛЕНИЕ СООБЩЕНИЙ ------------------------
@app.route('/forum/message/delete/<message_id>')
@login_required
def delete_message(message_id):
    del_mes = ForumMessage.query.get(message_id)
    topic_id = del_mes.topic_id

    # Проверка существования объекта
    if not del_mes:
        abort(404)

    # Является ли пользователь автором сообщения или админом/модером
    if del_mes.author == current_user or current_user.role < 2:
        db.session.delete(del_mes)
        db.session.commit()
        # Если сообщение было последним, то удалить топик и вернуться в корень форума
        if not ForumTopic.query.get(topic_id).message.all():
            db.session.delete(ForumTopic.query.get(topic_id))
            db.session.commit()
            return(redirect(url_for('forum')))            
        # Вернуться на страницу, откуда было вызвано удаление
        # (если это было последнее сообщение темы, то возврат в корень форума)
        return(redirect(request.referrer))
    # Если пользователь не является автором, выдать ошибку
    else:
        return(render_template('info.html',
            user=current_user,
            text="You can't delete message if you are not it's author"))

    # Вернуться на страницу, откуда было вызвано удаление
    return(redirect(request.referrer))


# --- ПОИСК ПО ФОРУМУ ---------------------------
@app.route('/search', methods=['GET', 'POST'])
def forum_search():
    search_form = SearchForm()
    
    if request.method == 'POST' and search_form.validate_on_submit():
        string = search_form.words.data
        res = ForumMessage.query.whoosh_search(string).all()
        # Выделить искомые слова зелёным
        res_colored = [[]]
        for each in res:
            res_colored += [each.text.replace(string, '<div class="found">' + string + '</div>')]
        return(render_template('search_result.html',
            user=current_user,
            results=res,
            message_colored=res_colored))

    return(render_template('search.html',
        user=current_user,
        search_form=search_form))


# --- СПИСОК ПОЛЬЗОВАТЕЛЕЙ ----------------------
@app.route('/userlist')
def userlist(page=1):
    # Нужная страница
    if request.args.get('page'):
        page = int(request.args.get('page'))

    # Разбиение на страницы
    pagination = Pagination(page, USER_PER_PAGE, User.query.count())

    # Аргументы сортировки из GET-запроса
    sort_field = request.args.get('sort')
    sort_order = request.args.get('desc')

    # Сортировка по дате последней активности
    if sort_field == 'last_seen' and sort_order == 'True':
        users_list = User.query.order_by(User.last_seen.desc()).all()
    elif sort_field == 'last_seen':
        users_list = User.query.order_by(User.last_seen).all()
    # Сортировка по дате регистрации
    elif sort_field == 'reg_date' and sort_order == 'True':
        users_list = User.query.order_by(User.reg_date.desc()).all()
    elif sort_field == 'reg_date':
        users_list = User.query.order_by(User.reg_date).all()
    # Сортировка по количеству тем
    elif sort_field == 'topics' and sort_order == 'True':
        users_list = User.query.order_by(User.topic_count.desc()).all()
    elif sort_field == 'topics':
        users_list = User.query.order_by(User.topic_count).all()
    # Сортировка по количеству сообщений
    elif sort_field == 'messages' and sort_order == 'True':
        users_list = User.query.order_by(User.message_count.desc()).all()
    elif sort_field == 'messages':
        users_list = User.query.order_by(User.message_count).all()
    # Регистронезависимая сортировка по логину
    elif sort_field == 'login' and sort_order == 'True':
        users_list = User.query.order_by(User.login.collate('NOCASE').desc()).all()
    else:
        users_list = User.query.order_by(User.login.collate('NOCASE')).all()

    # Вернуть страницу
    return(render_template('/userlist.html',
        user=current_user,
        users_list=users_list,
        pagination=pagination))


# --- ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ ----------------------
@app.route('/profile/<user_id>')
def user_profile(user_id):
    user = User.query.get(user_id)

    # Проверка существования объекта
    if not user:
        abort(404)

    # Вернуть страницу
    return(render_template('profile.html',
        user=current_user,
        profile=user))


# --- СВОЙ ПРОФИЛЬ ------------------------------
@app.route('/profile/me')
@login_required
def my_profile():
    # Вернуть страницу
    return(render_template('profile.html',
        user=current_user,
        profile=current_user))


# --- РЕДАКТИРОВАНИЕ ПРОФИЛЯ --------------------
@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # Форма редактирования профиля
    form = ProfileForm()

    # Если отправлена форма постинга
    if request.method == 'POST':
        # Данные из формы
        current_user.city = form.city.data
        current_user.country = form.country.data
        current_user.email = form.email.data
        db.session.commit()

        # Загружен ли новый аватар
        # Примечание: аватар из интернета не тестировался из-за прокси на работе
        input_path = form.avatar_from_hdd.data or form.avatar_from_inet.data
        if input_path:
            if form.avatar_from_hdd.data:
                file = form.avatar_from_hdd.data
                file_ext = file.filename.split('.')[-1].lower()
                avatar_inet = False
            else:
                file = urllib2.urlopen(input_path).read()
                file_ext = input_path.split('.')[-1].lower()
                avatar_inet = True

            # Проверить расширение файла
            allowed_file_ext = ('jpg', 'jpeg', 'gif', 'png')
            # Если расширение допустимое, то удалить старые файлы, закачать
            # новый аватар, сделать для него превью и поставить пользователю
            if '.' in file.filename and file_ext in allowed_file_ext:
                if not current_user.avatar:
                    os.remove('app' + current_user.avatar)
                    os.remove('app' + current_user.avatar_thumb)
                path_to_file = 'app/static/avatar/user_' + current_user.login + '.' + file_ext
                file.save(path_to_file)
                current_user.db_avatar = True
                db.session.commit()
                # Превью
                # Конвертирование в RGB из-за того, что индексированные изображения
                # сильно теряют в качестве при ресайзе
                avatar = Image.open(path_to_file).convert('RGB')
                os.remove(path_to_file)
                # Обрезать до квадрата (порядок для кропа - лево, верх, право, низ)
                # и уменьшить до 150х150
                av_size = avatar.size
                delta = abs(av_size[0] - av_size[1])
                if av_size[0] > av_size[1]:
                    box = (delta/2, 0, delta/2 + av_size[1], av_size[1])
                else:
                    box = (0, delta/2, av_size[0], delta/2 + av_size[0])
                avatar = avatar.crop(box).resize((150,150), Image.ANTIALIAS)
                avatar.save('app' + current_user.avatar)
                # Создание прозрачности по кругу через заготовленную маску,
                # маска должна быть не RGB, а в градациях серого, это можно сделать
                # на ходу, добавив в конец .convert('L'), или заранее (как здесь)
                mask = Image.open('app/static/avatar/system_alpha.png')
                avatar.thumbnail(mask.size, Image.ANTIALIAS)
                avatar.putalpha(mask)
                avatar.save('app' + current_user.avatar_thumb)
                # Аватар заблокированного пользователя
                avatar = Image.open(path_to_file)
                text = Image.open('app/static/avatar/system_blocked.png')
                # Осветление - смещение всех значений цветов для каждой точки на 100
                avatar_light = avatar.point(lambda x: x+100)
                # Вставка текста поверх картинки, аргументы - вставка, координаты, маска
                avatar_light.paste(text, (0, 0), text)
                avatar_light.save('app' + current_user.avatar.rstrip('.png') + '_blocked.png')

        # Редирект на страницу профиля
        return(redirect(url_for('my_profile')))

    # Вернуть страницу
    return(render_template('profile_edit.html',
        user=current_user,
        profile_form=form))


# --- БЛОКИРОВКА ПОЛЬЗОВАТЕЛЯ -------------------
@app.route('/profile/<user_id>/block')
@login_required
def block_user(user_id):
    user = User.query.get(user_id)

    # Проверка существования объекта
    if not user:
        abort(404)

    # Нельзя трогать себя
    if user != current_user:
        user.active = False
        db.session.commit()
        return(redirect(request.referrer))
    else:
        abort(404)


# --- РАЗБЛОКИРОВКА ПОЛЬЗОВАТЕЛЯ ----------------
@app.route('/profile/<user_id>/unblock')
@login_required
def unblock_user(user_id):
    user = User.query.get(user_id)

    # Проверка существования объекта
    if not user:
        abort(404)

    # Нельзя трогать себя
    if user != current_user:
        user.active = True
        db.session.commit()
        return(redirect(request.referrer))
    else:
        abort(404)    


# --- ЛИЧНЫЕ СООБЩЕНИЯ --------------------------
@app.route('/mailbox')
@login_required
def mailbox(page=1, box='inbox'):
    # Нужный ящик
    if request.args.get('box'):
        if request.args.get('box') in ['inbox', 'sent', 'archive', 'trash']:
            box = request.args.get('box')
        else:
            abort(404)
    # Нужная страница
    if request.args.get('page'):
        page = int(request.args.get('page'))

    # Все сообщения для текущего пользователя в указанном ящике
    if box == 'inbox':
        messages = current_user.mail_all.filter(Mailbox.directory=='0').\
            order_by(Mailbox.date.desc()).all()
    elif box == 'sent':
        messages = current_user.mail_all.filter(Mailbox.directory=='1').\
            order_by(Mailbox.date.desc()).all()
    elif box == 'archive':
        messages = current_user.mail_all.filter(Mailbox.directory=='2').\
            order_by(Mailbox.date.desc()).all()
    elif box == 'trash':
        messages = current_user.mail_all.filter(Mailbox.directory=='3').\
            order_by(Mailbox.date.desc()).all()

    # Разбиение на страницы
    pagination = Pagination(page, MAIL_PER_PAGE, len(messages))

    return(render_template('mailbox.html',
        user=current_user,
        box=box,
        messages=messages,
        pagination=pagination))


# --- ЛИЧНОЕ СООБЩЕНИЕ НА ОТДЕЛЬНОЙ СТРАНИЦЕ ----
@app.route('/mailbox/message/show/<message_id>')
@login_required
def mail_read(message_id):
    message = Mailbox.query.get(message_id)

    # Проверка существования объекта
    if not message:
        abort(404)

    # Пометить как прочитанное
    if not message.read:
        message.read = True
        db.session.commit()

    # Является ли пользователь владельцем сообщения
    if message.owner == current_user:
        return(render_template('mail_read.html',
            user=current_user,
            message=message))
    else:
        return(render_template('info.html',
            user=current_user,
            text="You can't view message if you are not it's owner"))


# --- НАПИСАТЬ ЛИЧНОЕ СООБЩЕНИЕ -----------------
@app.route('/mailbox/message/new', methods=['GET', 'POST'])
@login_required
def mail_write(reply=None):
    # Форма для нового сообщения
    form_recepient = RecepientForm()
    form_subject = TopicForm()
    form_message = MessageForm()

    # Если отправлена форма с новым сообщением
    if request.method == 'POST' and \
        form_recepient.validate_on_submit() and \
        form_subject.validate_on_submit() and \
        form_message.validate_on_submit():
            # Данные из формы c применением форматирования
            data_recipient = form_recepient.recepient.data
            data_subject = form_subject.topic.data
            data_message = message_format(form_message.message.data, True)
            # От кого и кому отправлено сообщение
            sender_id = current_user.id
            recipient_id = User.query.filter_by(login=data_recipient).first()
            if recipient_id:
                recipient_id = recipient_id.id
            else:
                return(render_template('info.html',
                    user=current_user,
                    text='No such user'))
            # Создание сообщений в отправленных у посылающего и
            # во входящих у того, кому адресовано письмо
            new_message = Mailbox(sender_id=current_user.id,
                owner_id=sender_id,
                directory=1,
                recipient_id=recipient_id,
                subject=data_subject,
                text=data_message,
                read=True)
            db.session.add(new_message)
            new_message = Mailbox(sender_id=current_user.id,
                owner_id=recipient_id,
                directory=0,
                recipient_id=recipient_id,
                subject=data_subject,
                text=data_message)
            db.session.add(new_message)
            db.session.commit()
            # Перейти в отправленные
            return(redirect(url_for('mailbox', box='sent')))

    # Заполнение полей надо делать после проверки отправки, иначе
    # form_message.message.data останется =quote и не перезапишется
    # теми данными, которые ввёл пользователь

    # Если это ответное сообщение
    reply = request.args.get('reply')
    recepient = ''
    subject = ''
    if reply:
        previous_message = Mailbox.query.get(reply)
        recepient = previous_message.sender.login
        subject = 'Re: ' + previous_message.subject
        text = message_format(previous_message.text, False)
        quote = ''
        for line in text.split('\n'):
            if line[:3] == '>> ':
                quote += '>> ' + line + '\n'
            else:
                for i in range(0, len(line), 50):
                    quote += '>> ' + line[i:i+50] + '\n'
        quote += '\n'
        form_message.message.data = quote

    # Все пользователей для выбора в качестве адреса
    all_users = User.query.all()

    return(render_template('mail_write.html',
        user=current_user,
        recepient=recepient,
        subject=subject,
        form_recepient=form_recepient,
        form_subject=form_subject,
        form_message=form_message,
        all_users=all_users))


# --- ПЕРЕМЕСТИТЬ СООБЩЕНИЕ В ДРУГУЮ ПАПКУ ------
@app.route('/mailbox/message/move/<directory>/<message_id>')
@login_required
def mail_move(directory, message_id):
    message = Mailbox.query.get(message_id)

    # Проверка существования объекта
    if not message or not directory in ['0', '1', '2', '3']:
        abort(404)

    # Является ли пользователь владельцем сообщения
    if message.owner == current_user:
        # Окончательное удаление (перемещение из корзины в корзину)
        if message.directory == 3 and directory == 3:
            db.session.delete(message)
        # Просто перемещение в указанную папку
        else:
            message.directory = directory
        db.session.commit()
        # Вернуться на страницу, откуда было вызвано удаление
        # (если это было последнее сообщение темы, то возврат в корень форума)
        return(redirect(request.referrer))
    # Если пользователь не является автором, выдать ошибку
    else:
        return(render_template('info.html',
            user=current_user,
            text="You are not owner of this message"))

    # Вернуться на страницу, откуда было вызвано удаление
    return(redirect(request.referrer))


# --- ЗАПОЛНИТЬ ФОРУМ СООБЩЕНИЯМИ ---------------
@app.route('/fill', methods=['GET', 'POST'])
@login_required
def fill():
    fill_form = FillForm()

    if request.method == 'POST':
        FILE = 'text.txt'
        file_size = os.stat(FILE).st_size

        topics_number = int(fill_form.topics.data)
        messages_number = int(fill_form.messages.data)

        # Создать тему
        def make_topic(file_str, file_size):
            '''
            Функция открывает файл со случайным смещением и
            и возвращает от 1 до 3 слов, идущих подряд
            '''
            
            random.seed()
            offset = random.randint(0, file_size-1)
            file = open(file_str)
            file.seek(offset)

            topic = ''
            started = False
            end = [' ', '.', '!', '?', '\n']
            number = random.randint(1, 4)
            for line in file:
                for char in line:
                    # Если слово ещё не началось
                    if not started:
                        if char not in end:
                            continue
                        else:
                            started = True
                    # Если предложение уже в записи
                    else:
                        # Ждать один из символов окончания предложения
                        if char in end:
                            topic += char
                            number -= 1
                            break
                        # Если не конец, то продолжать записывать предложение
                        else:
                            topic += char            
                if not number and started and topic[-1] in end:
                    topic = topic.replace('\n', ' ')[:-1]
                    return(topic)

        # Создать сообщение
        def make_message(file_str, file_size):
            '''
            Функция открывает файл со случайным смещением и
            и возвращает от 1 до 8 предложений, идущих подряд
            '''
            
            random.seed()
            offset = random.randint(0, file_size-1)
            file = open(file_str)
            file.seek(offset)
            
            message = ''
            started = False
            end = ['.', '!', '?']
            number = random.randint(1, 8)
            for line in file:
                for char in line:
                    # Если предложение ещё не началось
                    if not started:
                        if char not in end:
                            continue
                        else:
                            started = True
                    # Если предложение уже в записи
                    else:
                        # Ждать один из символов окончания предложения
                        if char in end:
                            message += char
                            number -= 1
                            break
                        # Если не конец, то продолжать записывать предложение
                        else:
                            message += char            
                if not number and started and message[-1] in end:
                    message = message.replace('\n', ' ')
                    if message[0] == ' ':
                        message = message[1:]
                    return(message)

        # Выборка всех пользователей для использования в качестве авторов
        all_users = User.query.all()

        for t_count in range(random.randint(1, topics_number+1)):
            # Создание топика
            author=random.choice(all_users)
            new_topic = ForumTopic(name=make_topic(FILE, file_size),
                author_id=author.id)
            author.message_count += 1
            author.topic_count += 1
            db.session.add(new_topic)
            # Коммит в этом месте нужен, чтобы появился ID
            db.session.commit()
            # Создание сообщений
            for m_count in range(random.randint(1, messages_number+1)):
                author=random.choice(all_users)
                new_mes = ForumMessage(topic_id=new_topic.id,
                    author_id=author.id,
                    text=make_message(FILE, file_size))
                author.message_count += 1
                db.session.add(new_mes)
            db.session.commit()

        return(redirect(request.referrer))

    return(render_template('fill.html',
        user=current_user,
        form=fill_form))


# --- ВЫХОД -------------------------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return(render_template('info.html',
        user=current_user,
        text='Logged out'))


# --- ОШИБКА 401 --------------------------------
@app.errorhandler(401)
def error_401(error_code):
    return(render_template('401.html',
        user=current_user))


# --- ОШИБКА 404 --------------------------------
@app.errorhandler(404)
def error_404(error_code):
    return(render_template('404.html',
        user=current_user))