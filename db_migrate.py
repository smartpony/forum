#
# Запуск приложения (standalone)
#

# Порядок выполнения миграции:
# python db_migrate.py db init       инициализация системы (только первый раз)
# python db_migrate.py db migrate    создать новый скрипт миграции
# python db_migrate.py db upgrade    перейти на новую весрию
# Справка по всем командам:
# python db_migrate.py db --help

# Импорт сервера приложения и объекта ОРМ
from app import app, db

# Модули для миграции БД
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

# Инициализация утилиты миграции БД
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

# Запуск скрипта через менеджер скриптов
manager.run()