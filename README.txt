Список модулей:
flask
flask-sqlalchemy
flask-wtf
flask-login

Схема:
/index			base
/forum			base, form, forum
  /topic (+message)	base, form, topic
/userlist		base, userlist
  /profile		base
/login			base, form
/register		base, form

/info			base