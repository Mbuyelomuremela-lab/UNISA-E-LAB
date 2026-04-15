import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, session
from flask_login import login_user, logout_user, current_user, login_required
from extensions import csrf
from models import User, Lab, LoginActivity, db
from services.qr_service import generate_qr_code
from services.geolocation_service import is_within_radius
from services.security import validate_password_strength

auth_bp = Blueprint('auth', __name__, template_folder='../templates')

pending_tokens = {}


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('intern.dashboard') if current_user.role == 'intern' else url_for('admin.overview'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'danger')
            return render_template('login.html')

        if user.role in ('admin', 'system_admin'):
            login_user(user)
            return redirect(url_for('admin.overview'))

        token = str(uuid.uuid4())
        pending_tokens[token] = user.id
        qr_link = url_for('auth.verify_qr', token=token, _external=True)
        qr_image = generate_qr_code(qr_link)
        return render_template('login_qr.html', qr_image=qr_image, qr_link=qr_link)

    return render_template('login.html')


@auth_bp.route('/verify_qr')
def verify_qr():
    token = request.args.get('token')
    if not token or token not in pending_tokens:
        flash('QR token expired or invalid. Please login again.', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('qr_verify.html', token=token)


@auth_bp.route('/validate_location', methods=['POST'])
@csrf.exempt
def validate_location():
    token = request.json.get('token')
    lat = request.json.get('latitude')
    lon = request.json.get('longitude')
    user_id = pending_tokens.get(token)

    if not token or not user_id:
        return jsonify({'success': False, 'message': 'Invalid QR session.'}), 400

    user = User.query.get(user_id)
    if not user or user.role != 'intern':
        return jsonify({'success': False, 'message': 'User not found.'}), 404

    lab = Lab.query.get(user.lab_id)
    if not lab:
        return jsonify({'success': False, 'message': 'Assigned lab not found.'}), 400

    passed, distance = is_within_radius(float(lat), float(lon), lab.latitude, lab.longitude, current_app.config['INTERN_RADIUS_METERS'])
    activity = LoginActivity(user_id=user.id, lab_id=lab.id, geo_passed=passed, ip_address=request.remote_addr)
    db.session.add(activity)
    db.session.commit()

    if not passed:
        return jsonify({'success': False, 'message': 'You are outside the lab radius. Access denied.'}), 403

    login_user(user)
    pending_tokens.pop(token, None)
    return jsonify({'success': True, 'redirect': url_for('intern.dashboard')})


@auth_bp.route('/logout')
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
            return render_template('change_password.html')

        if new_password != confirm_password:
            flash('New password and confirmation do not match.', 'danger')
            return render_template('change_password.html')

        if not validate_password_strength(new_password):
            flash('Password must be 6-7 characters and use letters, numbers, period, @, or #.', 'danger')
            return render_template('change_password.html')

        current_user.set_password(new_password)
        db.session.commit()

        flash('Password updated successfully.', 'success')
        return redirect(url_for('admin.overview') if current_user.role in ('admin', 'system_admin') else url_for('intern.dashboard'))

    return render_template('change_password.html')
