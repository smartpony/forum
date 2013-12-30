#
# Обработка запросов клиентов
#

from flask import render_template, redirect, url_for, request
from flask.ext.login import login_user, logout_user, current_user, login_required
from datetime import datetime
import hashlib

# Импорт других файлов проекта
from app import app, db, lm
from models import User, ForumTopic, ForumMessage
from forms import PostingForm, LoginForm, RegisterForm, ProfileForm


# --- ЗАГРУЗКА ПОЛЬЗОВАТЕЛЯ ---------------------
# Функция загружает объект пользователя по его ID,
# который хранится в памяти
@lm.user_loader
def load_user(id):
    return(User.query.get(int(id)))


# --- СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ ---------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Форма регистрации
    form = RegisterForm()

    # Если отправлена форма
    if request.method == 'POST':
        # Данные из формы
        user_login = form.login.data
        user_email = form.email.data
        user_password = form.password.data
        user_password_confirm = form.password_confirm.data

        if user_password == user_password_confirm:
            user_password = hashlib.sha256(user_password).hexdigest()
        else:
            return(render_template('info.html',
                title='Register',
                user=current_user,
                text='"Passwod" and "Confirm password" must be the same'))
            
        # Регистрация
        new_user = User(login=user_login,
            password=user_password,
            email=user_email)
        db.session.add(new_user)
        db.session.commit()

        # Войти под новым пользователем
        login_user(new_user)

        # Сообщение об успешной регистрации
        return(render_template('info.html',
            title='Register',
            user=current_user,
            text='Registered succesfully'))

    # Вернуть страницу
    return(render_template('register.html',
        title='Register',
        user=current_user,
        register_form=form))


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

        # Если пользователь найден, войти
        if user is not None:
            login_user(user)
            current_user.last_seen = datetime.utcnow()
            db.session.commit()
            # Вернуться в корень форума
            return(redirect(url_for('forum')))
        # Если пользователь не найден, выдать ошибку
        else:
            return(render_template('info.html',
                title='Login error',
                user=current_user,
                text='Invalid login or password'))

    # Вернуть страницу
    return(render_template('login.html',
        title='Login',
        user=current_user,
        login_form=form))


# --- КОРЕНЬ ------------------------------------
@app.route('/')
@app.route('/index')
def index():
    return(render_template('index.html',
        title='Home',
        user=current_user))


# --- ФОРУМ -------------------------------------
@app.route('/forum', methods=['GET', 'POST'])
def forum():
    # Форма для постинга сообщений
    form = PostingForm()

    # Если отправлена форма постинга
    if request.method == 'POST':
        # Данные из формы
        form_topic = form.topic.data
        form_message = form.message.data
        # Создание темы и обновление счётчиков у пользователя
        new_topic = ForumTopic(name=form_topic, author_id=current_user.id)
        current_user.message_count += 1
        current_user.topic_count += 1
        db.session.add(new_topic)
        # Коммит в этом месте нужен, чтобы появился ID
        db.session.commit()
        # Создание сообщения
        new_mes = ForumMessage(topic_id=new_topic.id, author_id=current_user.id, text=form_message)
        db.session.add(new_mes)
        db.session.commit()
        return(redirect('/forum/topic_'+str(new_topic.id)))

    # Выбрать все темы из базы с обратной сортировкой по последнему времени изменения
    all_topics = ForumTopic.query.order_by(ForumTopic.time_last.desc()).all()
    # Счётчики сообщений, время создания и последнего ответа,
    # счётчик просмотров для каждой темы
    count_mes = {}
    for topic in all_topics:
        count_mes[topic.id] = len(ForumTopic.query.get(topic.id).message)

    # Вернуть страницу
    return(render_template('forum.html',
        title='Forum',
        user=current_user,
        all_topics=all_topics,
        count=count_mes,
        new_topic=form))


# --- ТЕМА НА ОТДЕЛЬНОЙ СТРАНИЦЕ ----------------
@app.route('/forum/topic_<topic_id>', methods=['GET', 'POST'])
def topic(topic_id):
    # Форма добавления нового сообщения
    form = PostingForm()

    # Объект текущего топика
    current_topic = ForumTopic.query.get(topic_id)

    # Если отправлена форма постинга
    if request.method == 'POST':
        # Данные из формы
        form_message = form.message.data
        # Создание сообщения
        new_mes = ForumMessage(topic_id=topic_id, author_id=current_user.id, text=form_message)
        current_topic.time_last = datetime.utcnow()
        current_user.message_count += 1
        db.session.add(new_mes)
        # Запись последнего автора темы
        ForumTopic.query.get(topic_id).editor_id = current_user.id
        db.session.commit()
        return(redirect('/forum/topic_' + topic_id))

    # Счётчик просмотров +1
    current_topic.views += 1
    db.session.commit()

    # Выборка сообщений
    topic_name = current_topic.name
    topic_messages = ForumTopic.query.get(topic_id).message

    # Вернуть страницу
    return(render_template('topic.html',
        title='Topic: ' + current_topic.name,
        user=current_user,
        name=current_topic.name,
        topic_messages=topic_messages,
        add_message=form))


# --- УДАЛЕНИЕ ТЕМ ------------------------------
@app.route('/delete_t<topic_id>')
def delete_topic(topic_id):
    del_topic = ForumTopic.query.get(topic_id)
    db.session.delete(del_topic)
    db.session.commit()
    # Вернуться в корень форума
    return(redirect(url_for('forum')))


# --- УДАЛЕНИЕ СООБЩЕНИЙ ------------------------
@app.route('/delete_m<message_id>')
def delete_message(message_id):
    del_mes = ForumMessage.query.get(message_id)
    topic_id = del_mes.topic_id
    db.session.delete(del_mes)
    db.session.commit()
    # Если сообщение было последним, то удалить топик и вернуться в корень форума
    if ForumTopic.query.get(topic_id).message == []:
        db.session.delete(ForumTopic.query.get(topic_id))
        db.session.commit()
        return(redirect(url_for('forum')))
    # Вернуться на страницу, откуда было вызвано удаление
    # (если это было последнее сообщение темы, то возврат в корень форума)
    return(redirect(request.referrer))


# --- ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ ----------------------
@app.route('/profile_<user_id>')
def user_profile(user_id):
    user = User.query.get(user_id)
    # Вернуть страницу
    return(render_template('profile.html',
        title='User: '+user.login,
        user=current_user,
        profile=user,
        avatar='anonymous.jpg'))


# --- СВОЙ ПРОФИЛЬ ------------------------------
@app.route('/my_profile')
@login_required
def my_profile():
    # Вернуть страницу
    return(render_template('profile.html',
        title='User: '+current_user.login,
        user=current_user,
        profile=current_user,
        avatar=current_user.avatar))


# --- РЕДАКТИРОВАНИЕ ПРОФИЛЯ --------------------
@app.route('/profile_edit', methods=['GET', 'POST'])
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
        # Сохранение данных
        db.session.commit()
        # Редирект на страницу профиля
        return(redirect(url_for('my_profile')))

    # Вернуть страницу
    return(render_template('profile_edit.html',
        title='Edit profile',
        user=current_user,
        avatar='anonymous.jpg',
        profile_form=form))


# --- СПИСОК ПОЛЬЗОВАТЕЛЕЙ ----------------------
@app.route('/userlist')
def userlist():
    users_list = User.query.all()
    return(render_template('/userlist.html',
        title='Users list',
        user=current_user,
        users_list=users_list))


# --- ВЫХОД -------------------------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return(render_template('info.html',
        title='Logout',
        user=current_user,
        text='Logged out'))

# GIT test