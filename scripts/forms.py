from wtforms import StringField, SubmitField, EmailField, PasswordField, BooleanField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm


class RegisterForm(FlaskForm):
    name = StringField('Имя')
    surname = StringField('Фамилия', validators=[DataRequired()])
    nickname = StringField('Ник', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    pass1 = PasswordField('Пароль', validators=[DataRequired()])
    pass2 = PasswordField('Повтор', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    nickname = StringField('Ник')
    password = PasswordField('Пароль')
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

