# admin.py
from wtforms.validators import Optional
from flask_wtf.file import FileAllowed, FileRequired
from flask import render_template, request, redirect, url_for, flash, abort,current_app
from flask_login import login_required, current_user
from functools import wraps
import os
from functools import wraps
from werkzeug.utils import secure_filename
from app import app, db, allowed_file, ALLOWED_EXTENSIONS
from Resort.models import User, Booking, RoomType, Room, ExtraService, GuestOption
from Resort.forms  import (
    UserForm, RoomTypeForm,
    ExtraServiceForm, GuestOptionForm
)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated

# --- Dashboard ---
@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    stats = {
        'Users':          User.query.count(),
        'Bookings':       Booking.query.count(),
        'Room Types':     RoomType.query.count(),
        'Rooms':          Room.query.count(),
        'Extras':         ExtraService.query.count(),
        'Guest Options':  GuestOption.query.count(),
    }
    return render_template('admin/dashboard.html', stats=stats)

# --- Users CRUD ---
@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/create', methods=['GET','POST'])
@login_required
@admin_required
def admin_create_user():
    form = UserForm()
    if form.validate_on_submit():
        u = User(name=form.name.data,
                 email=form.email.data,
                 role=form.role.data)
        u.set_password(form.password.data)
        db.session.add(u)
        db.session.commit()
        flash('User created.', 'success')
        return redirect(url_for('admin_users'))
    return render_template('admin/user_form.html', form=form, title='Create User')

@app.route('/admin/users/edit/<int:user_id>', methods=['GET','POST'])
@login_required
@admin_required
def admin_edit_user(user_id):
    u = User.query.get_or_404(user_id)
    form = UserForm(obj=u)
    # on edit, password is optional
    form.password.validators = []
    if form.validate_on_submit():
        u.name  = form.name.data
        u.email = form.email.data
        u.role  = form.role.data
        if form.password.data:
            u.set_password(form.password.data)
        db.session.commit()
        flash('User updated.', 'success')
        return redirect(url_for('admin_users'))
    return render_template('admin/user_form.html', form=form, title='Edit User')

@app.route('/admin/users/delete/<int:user_id>')
@login_required
@admin_required
def admin_delete_user(user_id):
    u = User.query.get_or_404(user_id)
    db.session.delete(u)
    db.session.commit()
    flash('User deleted.', 'warning')
    return redirect(url_for('admin_users'))

# --- Room Types CRUD ---
@app.route('/admin/room_types')
@login_required
@admin_required
def admin_room_types():
    types = RoomType.query.all()
    return render_template('admin/room_types.html', room_types=types)

@app.route('/admin/room_types/create', methods=['GET','POST'])
@login_required
@admin_required
def admin_create_room_type():
    form = RoomTypeForm()
    if form.validate_on_submit():
        # — save main image —
        main = form.main_image.data
        name_main = secure_filename(main.filename)
        main.save(os.path.join(app.config['UPLOAD_FOLDER'], name_main))

        # — save gallery images —
        gallery_filenames = []
        for f in form.gallery_images.data:
            if f and allowed_file(f.filename):
                fn = secure_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                gallery_filenames.append(fn)

        rt = RoomType(
            name=form.name.data,
            description=form.description.data,
            base_price=form.base_price.data,
            max_guests=form.max_guests.data,
            main_image=name_main,
            gallery_images=','.join(gallery_filenames),
            features=form.features.data,
            is_luxury=form.is_luxury.data,
            luxury_label=form.luxury_label.data
        )
        db.session.add(rt)
        db.session.commit()
        flash('Room type created!', 'success')
        return redirect(url_for('admin_room_types'))

    return render_template('admin/room_type_form.html', form=form, title='Create Room Type')

@app.route('/admin/room_types/edit/<int:type_id>', methods=['GET','POST'])
@login_required
@admin_required
def admin_edit_room_type(type_id):
    rt = RoomType.query.get_or_404(type_id)
    form = RoomTypeForm(obj=rt)
    # Make files optional on edit
    form.main_image.validators = [Optional(), FileAllowed(ALLOWED_EXTENSIONS,'Only images!')]
    if form.validate_on_submit():
        # if a new main image was uploaded:
        if form.main_image.data:
            main = form.main_image.data
            name_main = secure_filename(main.filename)
            main.save(os.path.join(app.config['UPLOAD_FOLDER'], name_main))
            rt.main_image = name_main

        # if new gallery files:
        if form.gallery_images.data:
            gallery = []
            for f in form.gallery_images.data:
                if f and allowed_file(f.filename):
                    fn = secure_filename(f.filename)
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                    gallery.append(fn)
            rt.gallery_images = ','.join(gallery)

        # other fields:
        rt.name         = form.name.data
        rt.description  = form.description.data
        rt.base_price   = form.base_price.data
        rt.max_guests   = form.max_guests.data
        rt.features     = form.features.data
        rt.is_luxury    = form.is_luxury.data
        rt.luxury_label = form.luxury_label.data

        db.session.commit()
        flash('Room type updated!', 'success')
        return redirect(url_for('admin_room_types'))

    return render_template('admin/room_type_form.html', form=form, title='Edit Room Type')

@app.route('/admin/room_types/delete/<int:type_id>')
@login_required
@admin_required
def admin_delete_room_type(type_id):
    rt = RoomType.query.get_or_404(type_id)
    db.session.delete(rt)
    db.session.commit()
    flash('Room type deleted.', 'warning')
    return redirect(url_for('admin_room_types'))

# --- Extra Services CRUD ---
@app.route('/admin/extra_services')
@login_required
@admin_required
def admin_extra_services():
    services = ExtraService.query.all()
    return render_template('admin/extra_services.html', services=services)

@app.route('/admin/extra_services/create', methods=['GET','POST'])
@login_required
@admin_required
def admin_create_extra_service():
    form = ExtraServiceForm()
    if form.validate_on_submit():
        es = ExtraService(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            type=form.type.data
        )
        db.session.add(es)
        db.session.commit()
        flash('Extra service created.', 'success')
        return redirect(url_for('admin_extra_services'))
    return render_template('admin/extra_service_form.html', form=form, title='Create Extra Service')

@app.route('/admin/extra_services/edit/<int:svc_id>', methods=['GET','POST'])
@login_required
@admin_required
def admin_edit_extra_service(svc_id):
    es = ExtraService.query.get_or_404(svc_id)
    form = ExtraServiceForm(obj=es)
    if form.validate_on_submit():
        form.populate_obj(es)
        db.session.commit()
        flash('Extra service updated.', 'success')
        return redirect(url_for('admin_extra_services'))
    return render_template('admin/extra_service_form.html', form=form, title='Edit Extra Service')

@app.route('/admin/extra_services/delete/<int:svc_id>')
@login_required
@admin_required
def admin_delete_extra_service(svc_id):
    es = ExtraService.query.get_or_404(svc_id)
    db.session.delete(es)
    db.session.commit()
    flash('Extra service deleted.', 'warning')
    return redirect(url_for('admin_extra_services'))

# --- Guest Options CRUD ---
@app.route('/admin/guest_options')
@login_required
@admin_required
def admin_guest_options():
    opts = GuestOption.query.all()
    return render_template('admin/guest_options.html', opts=opts)

@app.route('/admin/guest_options/create', methods=['GET','POST'])
@login_required
@admin_required
def admin_create_guest_option():
    form = GuestOptionForm()
    if form.validate_on_submit():
        go = GuestOption(
            adult_count=form.adult_count.data,
            child_count=form.child_count.data,
            label=form.label.data
        )
        db.session.add(go)
        db.session.commit()
        flash('Guest option created.', 'success')
        return redirect(url_for('admin_guest_options'))
    return render_template('admin/guest_option_form.html', form=form, title='Create Guest Option')

@app.route('/admin/guest_options/edit/<int:opt_id>', methods=['GET','POST'])
@login_required
@admin_required
def admin_edit_guest_option(opt_id):
    go = GuestOption.query.get_or_404(opt_id)
    form = GuestOptionForm(obj=go)
    if form.validate_on_submit():
        form.populate_obj(go)
        db.session.commit()
        flash('Guest option updated.', 'success')
        return redirect(url_for('admin_guest_options'))
    return render_template('admin/guest_option_form.html', form=form, title='Edit Guest Option')

@app.route('/admin/guest_options/delete/<int:opt_id>')
@login_required
@admin_required
def admin_delete_guest_option(opt_id):
    go = GuestOption.query.get_or_404(opt_id)
    db.session.delete(go)
    db.session.commit()
    flash('Guest option deleted.', 'warning')
    return redirect(url_for('admin_guest_options'))
