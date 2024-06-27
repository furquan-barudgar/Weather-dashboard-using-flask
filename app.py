import sqlite3

from unicodedata import name
from flask import Flask, redirect,render_template,request,redirect,url_for,flash
import requests
from flask_sqlalchemy import SQLAlchemy
#configurations
app=Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///weather.db"
app.config["SQLALCHEMY_TRACK_MODIFICATION"]=False
app.config["SECRET_KEY"]="jaapuchkeaa"
db=SQLAlchemy(app)

#database model
class City(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50),nullable=False)
#check if city is valid
def get_weather_data(city):
        url=f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid=5e3714dd5a147a961891daf1ac553f77"
        r=requests.get(url).json()
        return r

#routing

#home page
@app.route("/")
def index_get():
    cities=City.query.all()

    weather_data=[]

    for city in cities:
        r=get_weather_data(city.name)
        weather= {
                "city":city.name,
                "temperature":r["main"]["temp"] ,
                "pressure":r["main"]["pressure"] ,
                "country":r["sys"]["country"] ,
                "description": r["weather"][0]["description"],
                "icon":r["weather"][0]["icon"],
                "feels_like":r["main"]["feels_like"],
                "temp_min":r["main"]["temp_min"],
                "temp_max":r["main"]["temp_max"]
                 }
        weather_data.append(weather)

    return render_template("index.html",weather_data=weather_data)

#home page
@app.route("/", methods=["POST"])
def index_post():
        err_msg=""
        new_city=request.form.get("city")
        if new_city:
            existing_city=City.query.filter_by(name=new_city.capitalize()).first()
            if not existing_city:
                new_city_data=get_weather_data(new_city)
                if new_city_data["cod"]==200:
                    nw_city_obj=City(name=new_city.capitalize())
                    db.session.add(nw_city_obj)
                    db.session.commit()
                else:
                    err_msg="City doesn't exist in the world" 
            else:
                err_msg="City Already Added"
        if err_msg:
            flash(err_msg,"error")
        else:
            flash("City Added Successfully")

        return redirect(url_for("index_get"))

@app.route("/delete/<name>")
def delete_city(name):
    city=City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()
    flash(f"Successfully Deleted {city.name}","success")
    return redirect(url_for("index_get"))