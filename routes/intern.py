from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from models import Asset, Visitor, Lab, db
from datetime import datetime

intern_bp = Blueprint('intern', __name__, template_folder='../templates')


def intern_only(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'intern':
            return redirect(url_for('auth.login'))
        return fn(*args, **kwargs)
    return wrapper


@intern_bp.route('/intern/dashboard')
@login_required
@intern_only
def dashboard():
    lab = Lab.query.get(current_user.lab_id)
    assets = Asset.query.filter_by(lab_id=current_user.lab_id).all()
    visitors = Visitor.query.filter_by(lab_id=current_user.lab_id).order_by(Visitor.check_in.desc()).limit(10).all()
    return render_template('intern/dashboard.html', lab=lab, assets=assets, visitors=visitors)


@intern_bp.route('/intern/assets', methods=['GET', 'POST'])
@login_required
@intern_only
def assets():
    lab = Lab.query.get(current_user.lab_id)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        asset_type = request.form.get('asset_type', '').strip()
        condition = request.form.get('condition')
        availability = request.form.get('availability')
        comments = request.form.get('comments')

        if not name or not asset_type:
            flash('Asset name and type are required.', 'danger')
            return redirect(url_for('intern.assets'))

        duplicate_asset = Asset.query.filter(
            Asset.lab_id == current_user.lab_id,
            func.lower(Asset.name) == name.lower(),
            func.lower(Asset.asset_type) == asset_type.lower()
        ).first()

        if duplicate_asset:
            flash('This asset already exists for your lab.', 'danger')
            return redirect(url_for('intern.assets'))

        asset = Asset(
            name=name,
            asset_type=asset_type,
            condition=condition,
            availability=availability,
            comments=comments,
            lab_id=current_user.lab_id
        )
        db.session.add(asset)
        db.session.commit()
        flash('Asset added successfully.', 'success')
        return redirect(url_for('intern.assets'))
    assets = Asset.query.filter_by(lab_id=current_user.lab_id).order_by(Asset.updated_at.desc()).all()
    return render_template('intern/assets.html', lab=lab, assets=assets)


@intern_bp.route('/intern/assets/<int:asset_id>/edit', methods=['POST'])
@login_required
@intern_only
def edit_asset(asset_id):
    asset = Asset.query.filter_by(id=asset_id, lab_id=current_user.lab_id).first_or_404()
    name = request.form.get('name', '').strip()
    asset_type = request.form.get('asset_type', '').strip()
    condition = request.form.get('condition')
    availability = request.form.get('availability')
    comments = request.form.get('comments')

    if not name or not asset_type:
        flash('Asset name and type are required.', 'danger')
        return redirect(url_for('intern.assets'))

    duplicate_asset = Asset.query.filter(
        Asset.lab_id == current_user.lab_id,
        func.lower(Asset.name) == name.lower(),
        func.lower(Asset.asset_type) == asset_type.lower(),
        Asset.id != asset.id
    ).first()

    if duplicate_asset:
        flash('This asset already exists for your lab.', 'danger')
        return redirect(url_for('intern.assets'))

    asset.name = name
    asset.asset_type = asset_type
    asset.condition = condition
    asset.availability = availability
    asset.comments = comments
    asset.updated_at = datetime.utcnow()
    db.session.commit()
    flash('Asset updated successfully.', 'success')
    return redirect(url_for('intern.assets'))


@intern_bp.route('/intern/visitors', methods=['GET', 'POST'])
@login_required
@intern_only
def visitors():
    lab = Lab.query.get(current_user.lab_id)
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        category = request.form.get('category')
        student_number = request.form.get('student_number', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        reason = request.form.get('reason')

        if not full_name:
            flash('Visitor name is required.', 'danger')
            return redirect(url_for('intern.visitors'))

        if category == 'UNISA student' and not student_number:
            flash('Student number is required for UNISA student visitors.', 'danger')
            return redirect(url_for('intern.visitors'))

        if not email and not phone:
            flash('Email or phone number is required to identify the visitor.', 'danger')
            return redirect(url_for('intern.visitors'))

        today = datetime.utcnow().date()
        duplicate_filters = [
            Visitor.lab_id == current_user.lab_id,
            db.func.date(Visitor.check_in) == today,
        ]

        if email and phone:
            duplicate_filters.append(
                (Visitor.email == email) | (Visitor.phone == phone)
            )
        elif email:
            duplicate_filters.append(Visitor.email == email)
        else:
            duplicate_filters.append(Visitor.phone == phone)

        duplicate = Visitor.query.filter(*duplicate_filters).first()

        if duplicate:
            flash('This visitor has already been registered today.', 'danger')
            return redirect(url_for('intern.visitors'))

        visitor = Visitor(
            full_name=full_name,
            category=category,
            student_number=student_number if student_number else None,
            email=email if email else None,
            phone=phone if phone else None,
            reason=reason,
            lab_id=current_user.lab_id,
            check_in=datetime.utcnow()
        )
        db.session.add(visitor)
        db.session.commit()
        flash('Visitor registered successfully.', 'success')
        return redirect(url_for('intern.visitors'))

    visitors = Visitor.query.filter_by(lab_id=current_user.lab_id).order_by(Visitor.check_in.desc()).all()
    return render_template('intern/visitors.html', lab=lab, visitors=visitors)


@intern_bp.route('/intern/visitors/<int:visitor_id>/edit', methods=['POST'])
@login_required
@intern_only
def edit_visitor(visitor_id):
    visitor = Visitor.query.filter_by(id=visitor_id, lab_id=current_user.lab_id).first_or_404()
    full_name = request.form.get('full_name', '').strip()
    category = request.form.get('category')
    student_number = request.form.get('student_number', '').strip()
    email = request.form.get('email', '').strip().lower()
    phone = request.form.get('phone', '').strip()
    reason = request.form.get('reason')

    if not full_name:
        flash('Visitor name is required.', 'danger')
        return redirect(url_for('intern.visitors'))

    if category == 'UNISA student' and not student_number:
        flash('Student number is required for UNISA student visitors.', 'danger')
        return redirect(url_for('intern.visitors'))

    if not email and not phone:
        flash('Email or phone number is required to identify the visitor.', 'danger')
        return redirect(url_for('intern.visitors'))

    visitor.full_name = full_name
    visitor.category = category
    visitor.student_number = student_number if student_number else None
    visitor.email = email if email else None
    visitor.phone = phone if phone else None
    visitor.reason = reason
    db.session.commit()
    flash('Visitor record updated successfully.', 'success')
    return redirect(url_for('intern.visitors'))


@intern_bp.route('/intern/visitors/<int:visitor_id>/delete', methods=['POST'])
@login_required
@intern_only
def delete_visitor(visitor_id):
    visitor = Visitor.query.filter_by(id=visitor_id, lab_id=current_user.lab_id).first_or_404()
    db.session.delete(visitor)
    db.session.commit()
    flash('Visitor record deleted.', 'success')
    return redirect(url_for('intern.visitors'))
