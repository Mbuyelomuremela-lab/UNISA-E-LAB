import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import User, Lab, Province, Asset, Visitor, LoginActivity, EventAnnouncement, db
from datetime import datetime
from services.security import generate_secure_password

admin_bp = Blueprint('admin', __name__, template_folder='../templates')


def is_system_admin():
    return current_user.is_authenticated and current_user.role == 'system_admin'


def is_admin_or_system_admin():
    return current_user.is_authenticated and current_user.role in ('admin', 'system_admin')


def admin_only(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not is_admin_or_system_admin():
            flash('Unauthorized access.', 'danger')
            return redirect(url_for('auth.login'))
        return fn(*args, **kwargs)
    return wrapper


@admin_bp.route('/admin/overview')
@login_required
@admin_only
def overview():
    province_id = request.args.get('province')
    lab_id = request.args.get('lab')
    asset_type = request.args.get('asset_type')
    visitor_category = request.args.get('visitor_category')
    date = request.args.get('date')

    assets = Asset.query
    visitors = Visitor.query

    if province_id:
        assets = assets.join(Lab).filter(Lab.province_id == province_id)
        visitors = visitors.join(Lab).filter(Lab.province_id == province_id)
    if lab_id:
        assets = assets.filter(Asset.lab_id == lab_id)
        visitors = visitors.filter(Visitor.lab_id == lab_id)
    if asset_type:
        assets = assets.filter(Asset.asset_type == asset_type)
    if visitor_category:
        visitors = visitors.filter(Visitor.category == visitor_category)
    if date:
        visitors = visitors.filter(db.func.date(Visitor.check_in) == date)

    total_users = User.query.count()
    trainee_count = User.query.filter_by(role='intern').count()
    hq_count = User.query.filter(User.role.in_(['admin', 'system_admin'])).count()
    working_count = User.query.filter_by(status='working').count()
    resigned_count = User.query.filter_by(status='resigned').count()

    total_labs = Lab.query.count()
    active_labs = db.session.query(Lab.id).join(User).filter(
        User.role == 'intern', User.status == 'working'
    ).distinct().count()
    inactive_labs = total_labs - active_labs

    provinces = Province.query.order_by(Province.name).all()
    labs = Lab.query.order_by(Lab.name).all()
    categories = ['educator', 'principal', 'deputy', 'UNISA student', 'school learner', 'other']
    asset_types = sorted({a.asset_type for a in Asset.query.all()})

    assets_by_type = db.session.query(
        Asset.asset_type,
        db.func.count(Asset.id)
    ).group_by(Asset.asset_type).all()

    assets_by_lab = db.session.query(
        Lab.name,
        db.func.count(Asset.id)
    ).join(Asset).group_by(Lab.id).all()

    visitor_counts_by_province = db.session.query(
        Province.name,
        db.func.count(Visitor.id)
    ).select_from(Visitor).join(Lab).join(Province).group_by(Province.id).all()

    visitor_counts_by_lab = db.session.query(
        Lab.name,
        db.func.count(Visitor.id)
    ).join(Visitor).group_by(Lab.id).all()

    visitor_counts_by_category = db.session.query(
        Visitor.category,
        db.func.count(Visitor.id)
    ).group_by(Visitor.category).all()

    current_date = date or datetime.utcnow().date().isoformat()
    visitors_today = Visitor.query.filter(db.func.date(Visitor.check_in) == current_date).count()

    labs_by_province = []
    for province in provinces:
        total = len(province.labs)
        active = sum(
            1
            for lab in province.labs
            if any(intern.role == 'intern' and intern.status == 'working' for intern in lab.interns)
        )
        labs_by_province.append({
            'province': province,
            'total': total,
            'active': active,
            'inactive': total - active,
        })

    stats = {
        'total_users': total_users,
        'trainee_count': trainee_count,
        'hq_count': hq_count,
        'working_count': working_count,
        'resigned_count': resigned_count,
        'total_assets': assets.count(),
        'total_visitors': visitors.count(),
        'total_labs': total_labs,
        'active_labs': active_labs,
        'inactive_labs': inactive_labs,
        'current_date': current_date,
        'visitors_today': visitors_today,
    }

    recent_visitors = visitors.order_by(Visitor.check_in.desc()).limit(12).all()

    return render_template(
        'admin/overview.html',
        stats=stats,
        provinces=provinces,
        labs=labs,
        categories=categories,
        asset_types=asset_types,
        assets_by_type=assets_by_type,
        assets_by_lab=assets_by_lab,
        labs_by_province=labs_by_province,
        visitor_counts_by_province=visitor_counts_by_province,
        visitor_counts_by_lab=visitor_counts_by_lab,
        visitor_counts_by_category=visitor_counts_by_category,
        recent_visitors=recent_visitors,
        selected_province=province_id,
        selected_lab=lab_id,
        selected_asset_type=asset_type,
        selected_visitor_category=visitor_category,
        selected_date=date,
    )


def allowed_event_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EVENT_EXTENSIONS']


@admin_bp.route('/admin/events', methods=['GET', 'POST'])
@login_required
@admin_only
def events():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        file = request.files.get('poster_file')

        if not file or file.filename == '':
            flash('Please select an image or PDF poster to upload.', 'danger')
            return redirect(url_for('admin.events'))

        filename = secure_filename(file.filename)
        if not allowed_event_file(filename):
            flash('Only PNG, JPG, JPEG, GIF, and PDF files are allowed.', 'danger')
            return redirect(url_for('admin.events'))

        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        upload_path = os.path.join(current_app.config['EVENT_UPLOAD_FOLDER'], unique_filename)
        file.save(upload_path)

        event = EventAnnouncement(
            title=title or 'Upcoming announcement',
            description=description,
            filename=unique_filename,
            content_type=file.content_type,
            active=True,
        )
        db.session.add(event)
        db.session.commit()
        flash('Event poster uploaded successfully.', 'success')
        return redirect(url_for('admin.events'))

    events = EventAnnouncement.query.order_by(EventAnnouncement.created_at.desc()).all()
    return render_template('admin/events.html', events=events)


@admin_bp.route('/admin/events/<int:event_id>/delete', methods=['POST'])
@login_required
@admin_only
def delete_event(event_id):
    event = EventAnnouncement.query.get_or_404(event_id)
    event_path = os.path.join(current_app.config['EVENT_UPLOAD_FOLDER'], event.filename)
    if os.path.exists(event_path):
        os.remove(event_path)
    db.session.delete(event)
    db.session.commit()
    flash('Event poster deleted successfully.', 'info')
    return redirect(url_for('admin.events'))


@admin_bp.route('/admin/users', methods=['GET', 'POST'])
@login_required
@admin_only
def users():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        role = request.form.get('role')
        status = request.form.get('status') or 'working'
        lab_id = request.form.get('lab_id') or None

        if not full_name or not email or not role:
            flash('Full name, email and role are required.', 'danger')
            return redirect(url_for('admin.users'))

        if current_user.role == 'admin' and role != 'intern':
            flash('Admins can only create intern users.', 'danger')
            return redirect(url_for('admin.users'))

        if User.query.filter_by(email=email).first():
            flash('A user with this email already exists.', 'danger')
            return redirect(url_for('admin.users'))

        password = generate_secure_password(7)
        user = User(
            full_name=full_name,
            email=email,
            role=role,
            status=status,
            lab_id=lab_id,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        session['new_user_credentials'] = {
            'email': email,
            'password': password,
            'full_name': full_name,
        }
        flash('User created successfully. Credentials are shown below.', 'success')
        return redirect(url_for('admin.users'))

    new_user_credentials = session.pop('new_user_credentials', None)
    reset_user_credentials = session.pop('reset_user_credentials', None)
    if current_user.role == 'admin':
        users = User.query.filter_by(role='intern').order_by(User.full_name).all()
    else:
        users = User.query.order_by(User.full_name).all()
    labs = Lab.query.order_by(Lab.name).all()
    status_options = ['working', 'resigned']
    return render_template(
        'admin/users.html',
        users=users,
        labs=labs,
        status_options=status_options,
        new_user_credentials=new_user_credentials,
        reset_user_credentials=reset_user_credentials,
    )


@admin_bp.route('/admin/users/<int:user_id>/edit', methods=['POST'])
@login_required
@admin_only
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.role == 'admin' and user.role != 'intern':
        flash('Admins can only edit intern users.', 'danger')
        return redirect(url_for('admin.users'))

    new_role = request.form.get('role')
    new_status = request.form.get('status') or 'working'
    if current_user.role == 'admin' and new_role != 'intern':
        flash('Admins can only assign the intern role.', 'danger')
        return redirect(url_for('admin.users'))

    user.full_name = request.form.get('full_name')
    user.email = request.form.get('email').strip().lower()
    user.role = new_role
    user.status = new_status
    user.lab_id = request.form.get('lab_id') or None
    db.session.commit()
    flash('User updated successfully.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/admin/users/<int:user_id>/reset', methods=['POST'])
@login_required
@admin_only
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.role == 'admin' and user.id != current_user.id and user.role != 'intern':
        flash('Admins can only reset passwords for interns or themselves.', 'danger')
        return redirect(url_for('admin.users'))

    new_password = generate_secure_password(7)
    user.set_password(new_password)
    db.session.commit()

    session['reset_user_credentials'] = {
        'email': user.email,
        'password': new_password,
        'full_name': user.full_name,
    }
    flash('Password reset successfully. Credentials are shown below.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/admin/users/add', methods=['POST'])
@login_required
@admin_only
def add_user():
    return users()


@admin_bp.route('/admin/users/reset-password/<int:user_id>', methods=['POST'])
@login_required
@admin_only
def reset_user_password(user_id):
    return reset_password(user_id)


@admin_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_only
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.role == 'admin' and user.role != 'intern':
        flash('Admins can only delete intern users.', 'danger')
        return redirect(url_for('admin.users'))

    # Remove any associated login activity records explicitly to avoid foreign key issues.
    LoginActivity.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'info')
    return redirect(url_for('admin.users'))


@admin_bp.route('/admin/assets', methods=['GET', 'POST'])
@login_required
@admin_only
def assets():
    if request.method == 'POST':
        asset = Asset(
            name=request.form.get('name'),
            serial_number=request.form.get('serial_number'),
            unisa_number=request.form.get('unisa_number'),
            asset_type=request.form.get('asset_type'),
            condition=request.form.get('condition'),
            availability=request.form.get('availability'),
            comments=request.form.get('comments'),
            lab_id=request.form.get('lab_id')
        )
        db.session.add(asset)
        db.session.commit()
        flash('Asset added successfully.', 'success')
        return redirect(url_for('admin.assets'))

    province = request.args.get('province')
    lab = request.args.get('lab')
    status = request.args.get('availability')
    condition = request.args.get('condition')
    asset_type = request.args.get('asset_type')

    query = Asset.query.join(Lab)
    if province:
        query = query.filter(Lab.province_id == province)
    if lab:
        query = query.filter(Asset.lab_id == lab)
    if status:
        query = query.filter(Asset.availability == status)
    if condition:
        query = query.filter(Asset.condition == condition)
    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)

    assets = query.order_by(Asset.updated_at.desc()).all()
    labs = Lab.query.order_by(Lab.name).all()
    provinces = Province.query.order_by(Province.name).all()
    asset_types = sorted({a.asset_type for a in Asset.query.all()})
    conditions = ['good', 'slow', 'bad']
    statuses = ['available', 'moved', 'stolen', 'unavailable']
    return render_template(
        'admin/assets.html',
        assets=assets,
        labs=labs,
        provinces=provinces,
        asset_types=asset_types,
        conditions=conditions,
        statuses=statuses,
        selected_province=province,
        selected_lab=lab,
        selected_status=status,
        selected_condition=condition,
        selected_asset_type=asset_type,
    )


@admin_bp.route('/admin/assets/<int:asset_id>/edit', methods=['POST'])
@login_required
@admin_only
def edit_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    asset.name = request.form.get('name')
    asset.serial_number = request.form.get('serial_number')
    asset.unisa_number = request.form.get('unisa_number')
    asset.asset_type = request.form.get('asset_type')
    asset.condition = request.form.get('condition')
    asset.availability = request.form.get('availability')
    asset.comments = request.form.get('comments')
    asset.lab_id = request.form.get('lab_id')
    db.session.commit()
    flash('Asset updated successfully.', 'success')
    return redirect(url_for('admin.assets'))


@admin_bp.route('/admin/assets/<int:asset_id>/delete', methods=['POST'])
@login_required
@admin_only
def delete_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    db.session.delete(asset)
    db.session.commit()
    flash('Asset deleted successfully.', 'info')
    return redirect(url_for('admin.assets'))


@admin_bp.route('/admin/visitors')
@login_required
@admin_only
def visitors():
    province = request.args.get('province')
    lab = request.args.get('lab')
    category = request.args.get('category')
    month = request.args.get('month')
    year = request.args.get('year')

    query = Visitor.query.join(Lab)
    if province:
        query = query.filter(Lab.province_id == province)
    if lab:
        query = query.filter(Visitor.lab_id == lab)
    if category:
        query = query.filter(Visitor.category == category)
    if month:
        query = query.filter(db.extract('month', Visitor.check_in) == int(month))
    if year:
        query = query.filter(db.extract('year', Visitor.check_in) == int(year))

    visitors = query.order_by(Visitor.check_in.desc()).all()
    provinces = Province.query.order_by(Province.name).all()
    labs = Lab.query.order_by(Lab.name).all()
    categories = ['educator', 'principal', 'deputy', 'UNISA student', 'school learner', 'other']
    return render_template('admin/visitors.html', visitors=visitors, provinces=provinces, labs=labs, categories=categories)


@admin_bp.route('/admin/login-activity')
@login_required
@admin_only
def login_activity():
    province = request.args.get('province')
    lab = request.args.get('lab')
    date = request.args.get('date')

    query = LoginActivity.query.join(User).join(Lab)
    if province:
        query = query.filter(Lab.province_id == province)
    if lab:
        query = query.filter(LoginActivity.lab_id == lab)
    if date:
        query = query.filter(db.func.date(LoginActivity.timestamp) == date)

    logs = query.order_by(LoginActivity.timestamp.asc()).all()

    activity = {}
    for log in logs:
        day = log.timestamp.date().isoformat()
        key = (log.user_id, day)
        if key not in activity:
            activity[key] = {
                'user_name': log.user.full_name,
                'lab_name': log.lab.name if log.lab else 'Unknown',
                'date': day,
                'first_login': log.timestamp,
                'last_logout': log.timestamp,
                'geo_passed': log.geo_passed,
            }
        else:
            if log.timestamp < activity[key]['first_login']:
                activity[key]['first_login'] = log.timestamp
            if log.timestamp > activity[key]['last_logout']:
                activity[key]['last_logout'] = log.timestamp
            if log.geo_passed:
                activity[key]['geo_passed'] = True

    activity_rows = sorted(
        activity.values(),
        key=lambda item: (item['date'], item['user_name']),
        reverse=True,
    )

    provinces = Province.query.order_by(Province.name).all()
    labs = Lab.query.order_by(Lab.name).all()
    return render_template(
        'admin/login_activity.html',
        activity_rows=activity_rows,
        provinces=provinces,
        labs=labs,
        selected_province=province,
        selected_lab=lab,
        selected_date=date,
    )


@admin_bp.route('/admin/labs', methods=['GET', 'POST'])
@login_required
@admin_only
def labs():
    if request.method == 'POST':
        name = request.form.get('name')
        province_id = request.form.get('province_id')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        address = request.form.get('address')
        description = request.form.get('description')

        if not name or not province_id or not latitude or not longitude:
            flash('Lab name, province, latitude and longitude are required.', 'danger')
            return redirect(url_for('admin.labs'))

        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            flash('Latitude and longitude must be valid numbers.', 'danger')
            return redirect(url_for('admin.labs'))

        lab = Lab(
            name=name,
            province_id=province_id,
            latitude=latitude,
            longitude=longitude,
            address=address,
            description=description,
        )
        db.session.add(lab)
        db.session.commit()
        flash('Lab added successfully.', 'success')
        return redirect(url_for('admin.labs'))

    labs = Lab.query.order_by(Lab.name).all()
    provinces = Province.query.order_by(Province.name).all()
    return render_template('admin/labs.html', labs=labs, provinces=provinces)


@admin_bp.route('/admin/labs/<int:lab_id>/edit', methods=['POST'])
@login_required
@admin_only
def edit_lab(lab_id):
    lab = Lab.query.get_or_404(lab_id)
    lab.name = request.form.get('name')
    lab.province_id = request.form.get('province_id')
    lab.latitude = float(request.form.get('latitude') or lab.latitude)
    lab.longitude = float(request.form.get('longitude') or lab.longitude)
    lab.address = request.form.get('address')
    lab.description = request.form.get('description')
    db.session.commit()
    flash('Lab updated successfully.', 'success')
    return redirect(url_for('admin.labs'))


@admin_bp.route('/admin/labs/<int:lab_id>/delete', methods=['POST'])
@login_required
@admin_only
def delete_lab(lab_id):
    lab = Lab.query.get_or_404(lab_id)
    if lab.interns or lab.assets or lab.visitors:
        flash('Cannot delete a lab with linked interns, assets, or visitors.', 'danger')
        return redirect(url_for('admin.labs'))
    db.session.delete(lab)
    db.session.commit()
    flash('Lab deleted successfully.', 'info')
    return redirect(url_for('admin.labs'))


@admin_bp.route('/admin/provinces', methods=['POST'])
@login_required
@admin_only
def add_province():
    name = request.form.get('name')
    if not name:
        flash('Province name is required.', 'danger')
        return redirect(url_for('admin.labs'))

    if Province.query.filter_by(name=name.strip()).first():
        flash('This province already exists.', 'danger')
        return redirect(url_for('admin.labs'))

    province = Province(name=name.strip())
    db.session.add(province)
    db.session.commit()
    flash('Province added successfully.', 'success')
    return redirect(url_for('admin.labs'))


@admin_bp.route('/admin/provinces/<int:province_id>/edit', methods=['POST'])
@login_required
@admin_only
def edit_province(province_id):
    province = Province.query.get_or_404(province_id)
    name = request.form.get('name')
    if not name:
        flash('Province name is required.', 'danger')
        return redirect(url_for('admin.labs'))

    province.name = name.strip()
    db.session.commit()
    flash('Province updated successfully.', 'success')
    return redirect(url_for('admin.labs'))


@admin_bp.route('/admin/provinces/<int:province_id>/delete', methods=['POST'])
@login_required
@admin_only
def delete_province(province_id):
    province = Province.query.get_or_404(province_id)
    if province.labs:
        flash('Cannot delete a province that still has labs.', 'danger')
        return redirect(url_for('admin.labs'))
    db.session.delete(province)
    db.session.commit()
    flash('Province deleted successfully.', 'info')
    return redirect(url_for('admin.labs'))


@admin_bp.route('/admin/api/labs')
@login_required
@admin_only
def labs_json():
    labs = Lab.query.order_by(Lab.name).all()
    return jsonify([{
        'id': lab.id,
        'name': lab.name,
        'province': lab.province.name,
        'latitude': lab.latitude,
        'longitude': lab.longitude,
        'address': lab.address,
        'description': lab.description,
    } for lab in labs])


@admin_bp.route('/admin/api/provinces')
@login_required
@admin_only
def provinces_json():
    provinces = Province.query.order_by(Province.name).all()
    return jsonify([{'id': province.id, 'name': province.name} for province in provinces])
