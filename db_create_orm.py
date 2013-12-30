#
# Создание базы и таблиц через SQLAlchemy
#

# Импорт модели
from app import db

# Создание базы согласно заданной модели
db.create_all()