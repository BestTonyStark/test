from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from functools import lru_cache
import requests
import schedule


app = Flask(__name__) #Создаем приложение
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///home.db' #Уточняем, что будем использовать sqlite в качестве бд
db = SQLAlchemy(app)
app.app_context().push() #эта строка нужна не всегда, но иногда бд без этого не создается

#Создаем таблицу Users
class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    balance = db.Column(db.Integer, nullable=False)
    __table_args__ = (CheckConstraint(balance >= 0, name='check_balance_positive'), {})

#главная страница со списком всех пользователей
@app.route('/')
def index():
    users = Users.query.all()
    return render_template('index.html', users=users)

#rout для добавления пользователя
@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        username = request.form['username']
        balance = request.form['balance']
        user = Users(username=username, balance=balance)
        try:
            db.session.add(user)
            db.session.commit()
            return redirect('/')
        except:
            return 'Не получилось добавить пользователя'
    else: 
        return render_template('add.html')
    
#rout для изменения пользователя
@app.route('/update/<int:id>', methods = ['POST', 'GET'])   
def update(id):
    user = Users.query.get(id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.balance = request.form['balance']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'При редактировании дома возникла ошибка'
    else:
        return render_template('update.html', user=user)

#rout для удаления пользователя
@app.route('/delete/<int:id>')
def delete(id):
    user = Users.query.get(id)
    try:
        db.session.delete(user)
        db.session.commit()
        return redirect('/')
    except:
        return 'Не получилось удалить' 

#rout для добавления температуры к балансу пользователя
@app.route('/temp/<int:id>', methods = ['POST', 'GET'])   
def temp(id):
    user = Users.query.get(id)
    if request.method == 'POST':
        user.balance = fetch_weather(request.form['city']) + user.balance
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'При редактировании дома возникла ошибка'
    else:
        return render_template('temp.html')


token = '07507bc3c8207608f132daf5dd0b76dc' #это токен от open_weather 
@lru_cache(maxsize=64)
def fetch_weather(city):
    try:
        r = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={token}&units=metric'
        )
        data = r.json()
        temp = data['main']['temp']
        return temp
    except Exception as ex:
        return ex
def cache_update():
    fetch_weather.cache_clear()
    
schedule.every(10).minutes.do(cache_update) #каждые 10 минут обновляем кэш

#запускаем сайт
if __name__ == "__main__":
    app.run(debug=True)