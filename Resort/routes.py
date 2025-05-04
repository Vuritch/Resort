from flask import render_template, request, redirect, url_for, flash, session
from Resort.models import  db, User,Room, ExtraService, Booking, BookingExtraService,RoomType,GuestOption
from Resort.forms import LoginForm, RegisterForm
from app import app
from datetime import timedelta, datetime
from functools import wraps
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask-Login


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
            
        new_user = User(name=form.name.data, email=form.email.data)
        new_user.set_password(form.password.data)
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
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            session['show_welcome'] = True
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            # DON'T redirect here — keep rendering with flash

  

    return render_template('login.html', form=form)




@app.route("/booking", methods=['GET', 'POST'])
@login_required
def booking():
    today = datetime.now().date().isoformat()
    room_types = RoomType.query.options(db.joinedload(RoomType.rooms)).all()
    extra_services = ExtraService.query.all()
    dining_extras = ExtraService.query.filter_by(type='dining').all()
    service_extras = ExtraService.query.filter_by(type='service').all()
    bed_extras = ExtraService.query.filter_by(type='bed').all()
    guest_options = GuestOption.query.\
         order_by(GuestOption.adult_count, GuestOption.child_count).all()
    if request.method == 'POST':
        try:
            # basic form fields
            room_type_id = int(request.form['room_type_id'])
            check_in  = datetime.strptime(request.form['check_in'], '%Y-%m-%d').date()
            check_out = datetime.strptime(request.form['check_out'], '%Y-%m-%d').date()
            special_requests = request.form.get('special_requests','')

            # fetch the selected GuestOption by its ID
            guest_option_id = int(request.form['guests'])
            guest_opt = GuestOption.query.get(guest_option_id)
            if not guest_opt:
                flash("Invalid guest selection.", "danger")
                return redirect(url_for('booking'))

            adults   = guest_opt.adult_count
            children = guest_opt.child_count
            total    = adults + children


            # load room_type and enforce max_guests
            room_type = RoomType.query.get(room_type_id)
            if not room_type:
                flash("Room type not found.", "danger")
                return redirect(url_for('booking'))
            if total > room_type.max_guests:
                flash(f"That room holds up to {room_type.max_guests} guests only.", "warning")
                return redirect(url_for('booking'))

            # extras/dining/bed as before …
            extras       = request.form.getlist('extras')
            dining_pkg   = request.form.get('dining_package')
            # … split out bed_pref and service_extras …

            # financials from hidden inputs
            room_rate    = float(request.form.get('room_rate', 0))
            taxes_and_fees = float(request.form.get('taxes_and_fees',0))
            dining_total = float(request.form.get('dining_total',0))
            services_total = float(request.form.get('services_total',0))
            total_price  = float(request.form.get('total_price',0))
            
            # pick an available room
            room = Room.query.filter_by(room_type_id=room_type_id, is_available=True).first()
            if not room:
                flash("No available rooms of that type.", "danger")
                return redirect(url_for('booking'))

            # create booking
            booking = Booking(
                user_id=current_user.id,
                room_id=room.id,
                check_in=check_in,
                check_out=check_out,
                bed_preference=request.form.get('bed_preference',''),
                dining_package = ExtraService.query.get(int(dining_pkg)).name if dining_pkg else None,
                room_rate=room_rate,
                taxes_and_fees=taxes_and_fees,
                dining_total=dining_total,
                services_total=services_total,
                total_price=total_price,
                
                # new columns (if you added them)
                num_adults=adults,
                num_children=children,

                special_requests=special_requests,
                status='pending'
            )
            db.session.add(booking)
            db.session.flush()  # so booking.id exists

            # record each child’s age category
            for age_cat in request.form.getlist('child_ages'):
                db.session.add(BookingGuest(booking_id=booking.id, age=age_cat))

            # optionally, record adults as BookingGuest rows (if you want names later)
            # for _ in range(adults):
            #     db.session.add(BookingGuest(booking_id=booking.id, age=18))

            # link service extras as before
            for e_id in [int(x) for x in extras]:
                svc = ExtraService.query.get(e_id)
                if svc and svc.type=='service':
                    db.session.add(BookingExtraService(
                        booking_id=booking.id,
                        extra_service_id=svc.id
                    ))

            # mark room unavailable
            room.is_available = False
            db.session.commit()

            flash("Booking successful! Check your email for confirmation.", "success")
            return redirect(url_for('booking'))

        except Exception as e:
            db.session.rollback()
            flash("Error processing booking: " + str(e), "danger")
            return redirect(url_for('booking'))

    return render_template(
        "booking.html",
        title="Book Your Stay",
        today=today,
        room_types=room_types,
        dining_extras=dining_extras,
        service_extras=service_extras,
        bed_extras=bed_extras,
         guest_options=guest_options
    )