#
# Создание базы и таблиц через SQLAlchemy
#

# Импорт модели
from app import db

# Создание базы согласно заданной модели
db.create_all()

# Создание админа и модератора с соответствующими правами
from app import db
from app.models import User
import hashlib

ADMIN_EMAIL = 'admin@mail.local'
MODER_EMAIL = 'moderator@mail.local'
USER_EMAIL = 'user@mail.local'
PASSWORD = '1'

# Админ
admin = User(login='Administrator',
    role=0,
    password=hashlib.sha256(PASSWORD).hexdigest(),
    email=ADMIN_EMAIL,
    db_avatar=True)
db.session.add(admin)
# Модер
moder = User(login='Moderator',
    role=1,
    password=hashlib.sha256(PASSWORD).hexdigest(),
    email=MODER_EMAIL,
    db_avatar=True)
db.session.add(moder)
# Просто пользователь
user = User(login='user',
    role=2,
    password=hashlib.sha256(PASSWORD).hexdigest(),
    email=USER_EMAIL)
db.session.add(user)

db.session.commit()