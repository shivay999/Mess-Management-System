import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Master(db.Model):
    __tablename__ = 'master'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role_id = db.Column(db.Integer,nullable=False)

class menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    breakfast = db.Column(db.String(100), nullable=False)
    lunch = db.Column(db.String(100), nullable=False)
    dinner = db.Column(db.String(100), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False)

class meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer,db.ForeignKey('master.id'),nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)  # e.g., breakfast, lunch, dinner
    date = db.Column(db.Date, nullable=False)

class mealh(db.Model):
    meal_type = db.Column(db.String(20), nullable=False,primary_key=True)
    Number_of_meals= db.Column(db.Integer, nullable=False)

 

    #student = db.relationship('Master', back_populates='meal')


    
