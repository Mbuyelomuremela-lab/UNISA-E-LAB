from extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='intern')
    status = db.Column(db.String(20), default='working')
    lab_id = db.Column(db.Integer, db.ForeignKey('lab.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    lab = db.relationship('Lab', back_populates='interns')
    login_activities = db.relationship(
        'LoginActivity',
        back_populates='user',
        lazy='dynamic',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    @property
    def is_working(self):
        return self.status == 'working'

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_system_admin(self):
        return self.role == 'system_admin'

    @property
    def is_admin_or_system_admin(self):
        return self.role in ('admin', 'system_admin')


class Province(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    labs = db.relationship('Lab', back_populates='province')


class Lab(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    province_id = db.Column(db.Integer, db.ForeignKey('province.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(255), nullable=True)
    description = db.Column(db.String(255), nullable=True)

    province = db.relationship('Province', back_populates='labs')
    interns = db.relationship('User', back_populates='lab')
    assets = db.relationship('Asset', back_populates='lab')
    visitors = db.relationship('Visitor', back_populates='lab')


class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    serial_number = db.Column(db.String(120), nullable=True)
    unisa_number = db.Column(db.String(120), nullable=True)
    asset_type = db.Column(db.String(80), nullable=False)
    condition = db.Column(db.String(50), nullable=False)
    availability = db.Column(db.String(50), nullable=False)
    comments = db.Column(db.Text, nullable=True)
    lab_id = db.Column(db.Integer, db.ForeignKey('lab.id'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lab = db.relationship('Lab', back_populates='assets')


class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(140), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    student_number = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    reason = db.Column(db.String(140), nullable=False)
    check_in = db.Column(db.DateTime, default=datetime.utcnow)
    lab_id = db.Column(db.Integer, db.ForeignKey('lab.id'), nullable=False)

    lab = db.relationship('Lab', back_populates='visitors')


class LoginActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    lab_id = db.Column(db.Integer, db.ForeignKey('lab.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    geo_passed = db.Column(db.Boolean, default=False)
    ip_address = db.Column(db.String(50), nullable=True)

    user = db.relationship('User', back_populates='login_activities')
    lab = db.relationship('Lab')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
