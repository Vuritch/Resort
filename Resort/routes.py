from flask import render_template, request, redirect, url_for, flash, session
from Resort.models import db, User, Booking
from Resort.forms import LoginForm, RegisterForm
from app import app
from datetime import timedelta, datetime
from functools import wraps
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please login to access the booking page.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    name = None
    welcome_message = None
    if current_user.is_authenticated:
        name = current_user.name
        
        if 'show_welcome' in session:
            welcome_message = True
            session.pop('show_welcome', None)
    return render_template('index.html', name=name, welcome_message=welcome_message,title='Home')

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # No changes needed here
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email already registered. Please use a different email or login.", "danger")
            return render_template("register.html", form=form)
            
        new_user = User(name=form.name.data, email=form.email.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))
    
    return render_template("register.html", form=form,title='Register')

@app.route('/logout')
def logout():
    logout_user()  # Use Flask-Login's logout_user function
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email, password=password).first()

        if user:
            login_user(user, remember=form.remember.data)  # Use Flask-Login's login_user
            session["show_welcome"] = True
            
            if form.remember.data:
                app.permanent_session_lifetime = timedelta(days=30)
            
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html', form=form,title='Login')

# The custom login_required decorator is now removed, using Flask-Login's instead

@app.route("/booking", methods=['GET', 'POST'])
@login_required  # Using Flask-Login's login_required decorator
def booking():
    if request.method == 'POST':
        try:
            # Get basic form data
            check_in = datetime.strptime(request.form.get('check_in'), '%Y-%m-%d').date()
            check_out = datetime.strptime(request.form.get('check_out'), '%Y-%m-%d').date()
            room_type = request.form.get('room_type')
            guests = request.form.get('guests')
            
            # Get additional form data
            child_ages = ','.join(request.form.getlist('child_ages')) if request.form.getlist('child_ages') else None
            bed_preference = request.form.get('bed_preference')
            special_requests = request.form.get('special_requests')
            
            # Get extras (dining and services)
            extras = request.form.getlist('extras')
            dining_package = next((extra for extra in extras if extra in ['breakfast', 'halfboard', 'fullboard']), None)
            airport_transfer = 'airport' in extras
            spa_package = 'spa' in extras
            romantic_package = 'romantic' in extras
            
            # Get price breakdown
            room_rate = float(request.form.get('room_rate', 0))
            taxes_and_fees = float(request.form.get('taxes_and_fees', 0))
            dining_total = float(request.form.get('dining_total', 0))
            services_total = float(request.form.get('services_total', 0))
            total_price = float(request.form.get('total_price'))
            
          
            # Create new booking
            new_booking = Booking(
                user_id=current_user.id,  # Use current_user instead of session
                room_type=room_type,
                check_in=check_in,
                check_out=check_out,
                guests=guests,
                child_ages=child_ages,
                bed_preference=bed_preference,
                dining_package=dining_package,
                airport_transfer=airport_transfer,
                spa_package=spa_package,
                romantic_package=romantic_package,
                room_rate=room_rate,
                taxes_and_fees=taxes_and_fees,
                dining_total=dining_total,
                services_total=services_total,
                total_price=total_price,
                special_requests=special_requests,
                status='pending'
            )
            
            # Save to database
            db.session.add(new_booking)
            db.session.commit()
            
            # Send confirmation
            flash('''Booking request submitted successfully! 
                  We will confirm your reservation shortly. 
                  A confirmation email will be sent to your registered email address.''', 'success')
            return redirect(url_for('booking'))
            
        except Exception as e:
            db.session.rollback()
            # Print detailed error information
            import traceback
            print("Booking Error Details:")
            print(str(e))
            print("Traceback:")
            print(traceback.format_exc())
            flash('An error occurred while processing your booking. Please try again.', 'danger')
            return redirect(url_for('booking'))
        
    # For GET request, pass today's date to template for date validation
    today = datetime.now().date().isoformat()
    return render_template('booking.html', title='Book Your Stay', today=today)