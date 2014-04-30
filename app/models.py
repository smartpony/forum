#
# Описание модели БД для ORM
#

# Импорт главного объекта БД
from app import app, db
# Полнотекстовый поиск
from flask.ext import whooshalchemy

from datetime import datetime


# Пользователи
class User(db.Model):
    __tablename__ = 'User'

    # ID пользователя
    id = db.Column(db.Integer, primary_key=True)
    # Логин
    login = db.Column(db.Text, unique=True, nullable=False)
    # Пароль
    password = db.Column(db.Text, nullable=False)

    # Код подтверждения почты при регистрации
    confirm_code = db.Column(db.Text)
    # Блокировка/неподтверждённая регистрация
    active = db.Column(db.Boolean, default=False)
    # Статус (0 - админ, 1 - модератор, 2 - пользователь)
    role = db.Column(db.Integer, default=2, nullable=False)

    # Почта
    email = db.Column(db.Text, nullable=False)
    # Город
    city = db.Column(db.Text, default='unknown')
    # Страна
    country = db.Column(db.Text, default='unknown')
    # Аватар, 0 - /static/avatar/system_anonymous.jpg,
    # 1 - /static/avatar/user_username.ext
    db_avatar = db.Column(db.Boolean, default=False)

    # Количество тем
    topic_count = db.Column(db.Integer, default=0)
    # Количество сообщений
    message_count = db.Column(db.Integer, default=0)

    # Дата регистрации
    reg_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # Дата последнего входа
    last_seen = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Методы для работы Flask-login
    def is_authenticated(self):
        return(True)
    def is_active(self):
        return(self.active)
    def is_anonymous(self):
        return(False)
    def get_id(self):
        return(unicode(self.id))

    # Вернуть нужную строчку для аватара
    @property
    def avatar(self):
        if self.db_avatar:
            if self.active:
                return('/static/avatar/user_%s.png' % self.login)
            else:
                return('/static/avatar/user_%s_blocked.png' % self.login)
        else:
            if self.active:
                return('/static/avatar/system_anonymous.png')
            else:
                return('/static/avatar/system_anonymous_blocked.png')

    # Вернуть нужную строчку для уменьшенного аватара
    @property
    def avatar_thumb(self):
        if self.db_avatar:
            return('/static/avatar/user_%s_thumb.png' % self.login)
        else:
            return('/static/avatar/system_anonymous_thumb.png')

    # Вернуть количество непрочитанных писем
    @property
    def unread_mail(self):
        count = 0
        for message in self.mail_all.filter(Mailbox.directory=='0'):
            if not message.read:
                count += 1
        return(count)

    # Вывод при обращении к объекту класса
    def __repr__(self):
        return('<User ID%d>' % self.id)


# Темы форума
class ForumTopic(db.Model):
    __tablename__ = 'ForumTopic'

    # ID темы
    id = db.Column(db.Integer, primary_key=True)
    # Название темы
    name = db.Column(db.Text, nullable=False)
    # Автор и последний редактор (обратная связь с таблицей пользователей)
    author_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    editor_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    author = db.relationship('User',
        foreign_keys=[author_id],
        backref=db.backref('topic', lazy='dynamic'))
    editor = db.relationship('User', foreign_keys=[editor_id])
    # Первый пост
    time_first = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # Последний пост
    time_last = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # Просмотры
    views = db.Column(db.Integer, default=0, nullable=False)

    # Вывод при обращении к объекту класса
    def __repr__(self):
        return('<Topic ID%d>' % self.id)


# Сообщения форума
class ForumMessage(db.Model):
    __tablename__ = 'ForumMessage'
    __searchable__ = ['text']

    # ID сообщения
    id = db.Column(db.Integer, primary_key=True)
    # ID топика (обратная связь с таблицей тем)
    topic_id = db.Column(db.Integer, db.ForeignKey(ForumTopic.id))
    topic = db.relationship('ForumTopic',
        backref=db.backref('message', cascade='delete', lazy='dynamic'))
    # Автор и последний редактор (обратная связь с таблицей пользователей)
    author_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    editor_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    author = db.relationship('User',
        foreign_keys=[author_id],
        backref=db.backref('message', lazy='dynamic'))
    editor = db.relationship('User', foreign_keys=[editor_id])
    # Текст
    text = db.Column(db.Text, nullable=False)
    # Время постинга
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # Время изменения
    date_edit = db.Column(db.DateTime)

    # Вывод при обращении к объекту класса
    def __repr__(self):
        return('<Message ID%d>' % self.id)


# Личные сообщения
class Mailbox(db.Model):
    __tablename__ = 'Mailbox'

    # ID сообщения
    id = db.Column(db.Integer, primary_key=True)
    # Пользователь, в ящике которого хранится сообщение
    owner_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    owner = db.relationship('User',
        foreign_keys=[owner_id],
        backref=db.backref('mail_all', lazy='dynamic'))
    # Папка, в которой хранится сообщение
    # 0 - входящие, 1 - отправленные, 2 - архив, 3 - корзина
    directory = db.Column(db.Integer, nullable=False)
    # Автор
    sender_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    sender = db.relationship('User',
        foreign_keys=[sender_id],
        backref=db.backref('mail_sent', lazy='dynamic'))
    # Получатель
    recipient_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    recipient = db.relationship('User',
        foreign_keys=[recipient_id],
        backref=db.backref('mail_recieved', lazy='dynamic'))
    # Тема
    subject = db.Column(db.Text)
    # Текст
    text = db.Column(db.Text, nullable=False)
    # Время отправки
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # Прочитано получателем
    read = db.Column(db.Boolean, default=False)
    
    # Вывод при обращении к объекту класса
    def __repr__(self):
        return('<Personal message ID%d>' % self.id)

# Занесение индексов в базу для полнотекстового поиска
whooshalchemy.whoosh_index(app, ForumMessage)