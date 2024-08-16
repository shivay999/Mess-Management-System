import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import create_engine
from models import db,Master,meal,menu,mealh
from sqlalchemy import func
from datetime import date, datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)
engine = create_engine('sqlite:///database.db', echo=True)
Session = sessionmaker(bind=engine)
# Routes
@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/back_view_menu')
def back_view_menu():
    return redirect(url_for('admin_dashboard'))

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email and password:
            user = Master.query.filter_by(email=email, password=password).first()
        if user:
            session['id'] = user.id
            session['user_name'] = user.name
            session['role_id'] = user.role_id  # Store the user's name in the session
            db.session.commit()
            if user.role_id == 1:
                return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard route
            if user.role_id == 2:
                return redirect(url_for('student_dashboard'))
            elif user.role_id == 0:
                return redirect(url_for('student_dashboard'))  # Redirect to user dashboard route
        else:
            return render_template('welcome.html', error="Invalid email or password")
    return render_template('welcome.html')


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('signin'))

@app.route('/admin_dashboard')
def admin_dashboard():
    # Fetch counts for each meal type from the database
    # Fetch counts for each meal type from the database
    hostel_b_count = db.session.query(mealh.Number_of_meals).filter_by(meal_type='breakfast').scalar()
    hostel_l_count = db.session.query(mealh.Number_of_meals).filter_by(meal_type='lunch').scalar()
    hostel_d_count = db.session.query(mealh.Number_of_meals).filter_by(meal_type='dinner').scalar()
    print(hostel_b_count)
    breakfast_count = db.session.query(func.count(meal.id)).filter(meal.meal_type == 'Breakfast').scalar() + hostel_b_count
    lunch_count = db.session.query(func.count(meal.id)).filter(meal.meal_type == 'Lunch').scalar() + hostel_l_count
    dinner_count = db.session.query(func.count(meal.id)).filter(meal.meal_type == 'Dinner').scalar() + hostel_d_count
    user_name = session.get('user_name', 'Unknown') 
    print(lunch_count)
    print(dinner_count)
    
    return render_template('admin_dashboard.html', 
                           breakfast_count=breakfast_count, 
                           lunch_count=lunch_count, 
                           dinner_count=dinner_count,
                           user_name=user_name)


@app.route('/view_menu')
def student_dashboard():
    # Fetch all menu items from the database
    '''menu_items = menu.query.all()
    return render_template('view_menu.html', menu_items=menu_items)'''
    today = datetime.today().strftime('%A')
    #mwnu_items = db.session.query(menu).filter(menu.day_of_week==today).all()
    #print(mwnu_items)
    print(today)
    menu_today = menu.query.filter_by(day_of_week=today).first()
    student_id = session['id']
    role_id = session['role_id']
    user_name = session.get('user_name', 'Unknown')  # Retrieve the user's name from the session
    disabled_meals = session.get(f'disabledMeals_{student_id}', [])
    return render_template('student_dashboard.html', role_id=role_id,items=menu_today, today=today, disabled_meals=disabled_meals, user_name=user_name)

@app.route('/view_admin')
def view_admin():
    menu_items = menu.query.all()
    return render_template('view_menu.html', menu_items=menu_items)

@app.route('/select_meal', methods=['POST'])
def select_meal():
    if 'id' not in session:
        return redirect(url_for('signin'))  # Redirect to sign-in if student not logged in
    else:
        if(request.method=='POST'):
            meal_type = request.form.get('meal_type')
            student_id = session['id']
            new_meal = meal(student_id=student_id, meal_type=meal_type, date=date.today())
            db.session.add(new_meal)
            db.session.commit()
            disabled_meals_key = f'disabledMeals_{student_id}'
            if disabled_meals_key not in session:
               session[disabled_meals_key] = []
            session[disabled_meals_key].append(meal_type)
            #session['disabledMeals'].append(meal_type)
            flash(f'{meal_type.capitalize()} selected successfully!', 'success')
            return redirect(url_for('student_dashboard'))


    
        
@app.route('/cancel_meal', methods=['POST'])
def cancel_meal():
   
    if 'id' not in session:
        return redirect(url_for('signin'))

    meal_type = request.form.get('meal_type')
    student_id = session['id']

    # Find the meal associated with the student and meal type
    meal_to_delete = meal.query.filter_by(student_id=student_id, meal_type=meal_type, date=date.today()).first()
    if meal_to_delete:
        db.session.delete(meal_to_delete)
        db.session.commit()

        # Update the disabled meals for the current user
        disabled_meals_key = f'disabledMeals_{student_id}'
        if disabled_meals_key in session:
            session[disabled_meals_key].remove(meal_type)
        
        flash(f'{meal_type.capitalize()} canceled successfully!', 'success')
    else:
        flash(f'Failed to cancel {meal_type.capitalize()}. Meal not found.', 'danger')

    return redirect(url_for('student_dashboard'))

@app.route('/cancel_meal_h', methods=['POST'])
def cancel_meal_h():
    print('Hi Hostelite')
    if 'id' not in session:
        return redirect(url_for('signin'))

    meal_type = request.form.get('meal_type')
    print(meal_type)
    student_id = session['id']
    if(meal_type=='Breakfast'):
    
            db.session.query(mealh).filter(mealh.meal_type == 'breakfast').update({mealh.Number_of_meals : mealh.Number_of_meals-1})
            db.session.commit()
            #return jsonify({'message': 'Meal cancelled successfully'})
    if(meal_type=='Lunch'):
            print('I work in breakfast')
            db.session.query(mealh).filter(mealh.meal_type == 'lunch').update({mealh.Number_of_meals : mealh.Number_of_meals-1})
            db.session.commit()
            #return jsonify({'message': 'Meal cancelled successfully'})
    if(meal_type=='Dinner'):
            print('I work in dinner')
            db.session.query(mealh).filter(mealh.meal_type == 'dinner').update({mealh.Number_of_meals : mealh.Number_of_meals-1})
            db.session.commit()
            #return jsonify({'message': 'Meal cancelled successfully'})
    # Find the meal associated with the student and meal type
    
        # Update the disabled meals for the current user
    disabled_meals_key = f'disabledMeals_{student_id}'
    if disabled_meals_key in session:
            session[disabled_meals_key].remove(meal_type)
        
            flash(f'{meal_type.capitalize()} canceled successfully!', 'success')

    return redirect(url_for('student_dashboard'))

@app.route('/edit_menu/<int:menu_id>', methods=['GET', 'POST'])
def edit_menu(menu_id):
    menu_item = menu.query.get_or_404(menu_id)
    if request.method == 'POST':
        menu_item.day_of_week = request.form['day_of_week']
        menu_item.breakfast = request.form['breakfast']
        menu_item.lunch = request.form['lunch']
        menu_item.dinner = request.form['dinner']
        db.session.commit()
        return redirect(url_for('view_admin'))
    return render_template('edit_menu.html', menu_item=menu_item)      
    
@app.route('/management_dashboard')
def management_dashboard():
    # Fetch counts for each meal type from the database
    #breakfast_count = meal.query.filter_by(meal_type='breakfast').count()
    #lunch_count = meal.query.filter_by(meal_type='lunch').count()
    #dinner_count = meal.query.filter_by(meal_type='dinner').count()
    breakfast_count = db.session.query(meal.Number_of_meals).filter(meal.meal_type == 'Breakfast').scalar()
    lunch_count = db.session.query(meal.Number_of_meals).filter(meal.meal_type == 'Lunch').scalar()
    dinner_count = db.session.query(meal.Number_of_meals).filter(meal.meal_type == 'Dinner').scalar()
    print(breakfast_count,lunch_count,dinner_count)
    print(breakfast_count)
    print(lunch_count)
    return render_template('admin_dashboard.html', 
                           breakfast_count=breakfast_count, 
                           lunch_count=lunch_count, 
                           dinner_count=dinner_count)

@app.route('/view_menu')
def view_menu():
    # Fetch all menu items from the database
    menu_items = menu.query.all()
    return render_template('view_menu.html', menu_items=menu_items)

if __name__ == '__main__':
    app.run(debug=True)
