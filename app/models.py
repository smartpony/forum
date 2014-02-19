#
# Описание модели БД для ORM
#

# Импорт главного объекта БД
from app import db

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

    # Статус (0 - админ, 1 - модератор, 2 - пользователь)
    role = db.Column(db.Integer, default=2, nullable=False)

    # Почта
    email = db.Column(db.Text, nullable=False)
    # Город
    city = db.Column(db.Text, default='unknouwn')
    # Страна
    country = db.Column(db.Text, default='unknouwn')
    # Аватар
    avatar = db.Column(db.Text, default='/static/avatar/anonymous.jpg')

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
        return(True)
    def is_anonymous(self):
        return(False)
    def get_id(self):
        return(unicode(self.id))

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