from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import BooleanField, FileField, PasswordField, StringField, SubmitField, ValidationError, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo

from .models.user import User

class RegistrationForm(FlaskForm):
    name = StringField('ФИО', validators=[DataRequired(), Length(min = 2, max = 100)])
    login = StringField('Логин', validators=[DataRequired(), Length(min = 2, max = 20)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    avatar = FileField('Загрузити фото', validators=[FileAllowed(['jpg','jpeg','png'])])
    submit = SubmitField('Зарегистрирооваться')
    
    def validate_login(self, login):
        user = User.query.filter_by(login=login.data).first()
        if user:
            raise ValidationError('Данное имя пользователя занято. Пожалуйста, выберете другое...')
        
class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired(), Length(min = 2, max = 20)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
    
class StudentForm(FlaskForm):
    student = SelectField('student', choices=[], render_kw={'class':'form-control'})
    
class TeacherForm(FlaskForm):
    teacher = SelectField('student', choices=[], render_kw={'class':'form-control'})
    