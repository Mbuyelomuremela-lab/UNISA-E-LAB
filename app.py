import os

from flask import Flask, redirect, url_for, flash, request
from flask_login import current_user
from sqlalchemy import text
from config import Config
from extensions import db, login_manager, csrf, mail
from services.security import session_timeout


def ensure_lab_address_column(app):
    if db.engine.url.get_backend_name() != 'sqlite':
        return

    with app.app_context():
        result = db.session.execute(text("PRAGMA table_info('lab')"))
        existing = result.fetchall()
        columns = [row[1] for row in existing]
        if 'address' not in columns:
            db.session.execute(text("ALTER TABLE lab ADD COLUMN address VARCHAR(255)"))
            db.session.commit()


def ensure_visitor_contact_columns(app):
    if db.engine.url.get_backend_name() != 'sqlite':
        return

    with app.app_context():
        result = db.session.execute(text("PRAGMA table_info('visitor')"))
        existing = result.fetchall()
        columns = [row[1] for row in existing]
        if 'email' not in columns:
            db.session.execute(text("ALTER TABLE visitor ADD COLUMN email VARCHAR(120)"))
        if 'phone' not in columns:
            db.session.execute(text("ALTER TABLE visitor ADD COLUMN phone VARCHAR(50)"))
        db.session.commit()


def ensure_user_role_column(app):
    if db.engine.url.get_backend_name() != 'sqlite':
        return

    with app.app_context():
        result = db.session.execute(text("PRAGMA table_info('user')"))
        existing = result.fetchall()
        columns = [row[1] for row in existing]
        if 'role' not in columns:
            db.session.execute(text("ALTER TABLE user ADD COLUMN role VARCHAR(20) DEFAULT 'intern'"))
            db.session.commit()


def ensure_user_status_column(app):
    if db.engine.url.get_backend_name() != 'sqlite':
        return

    with app.app_context():
        result = db.session.execute(text("PRAGMA table_info('user')"))
        existing = result.fetchall()
        columns = [row[1] for row in existing]
        if 'status' not in columns:
            db.session.execute(text("ALTER TABLE user ADD COLUMN status VARCHAR(20) DEFAULT 'working'"))
            db.session.commit()


def ensure_asset_identifiers_columns(app):
    if db.engine.url.get_backend_name() != 'sqlite':
        return

    with app.app_context():
        result = db.session.execute(text("PRAGMA table_info('asset')"))
        existing = result.fetchall()
        columns = [row[1] for row in existing]
        if 'serial_number' not in columns:
            db.session.execute(text("ALTER TABLE asset ADD COLUMN serial_number VARCHAR(120)"))
        if 'unisa_number' not in columns:
            db.session.execute(text("ALTER TABLE asset ADD COLUMN unisa_number VARCHAR(120)"))
        db.session.commit()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    from models import User, Lab, Province, Asset, Visitor, LoginActivity
    from routes.auth import auth_bp
    from routes.intern import intern_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(intern_bp)
    app.register_blueprint(admin_bp)

    @app.before_request
    def before_request():
        session_timeout()
        if current_user.is_authenticated:
            current_user.last_seen = db.func.now()
            db.session.commit()

    @app.route('/')
    def home():
        if current_user.is_authenticated:
            return redirect(url_for('intern.dashboard') if current_user.role == 'intern' else url_for('admin.overview'))
        return redirect(url_for('auth.login'))

    with app.app_context():
        db.create_all()
        ensure_lab_address_column(app)
        ensure_visitor_contact_columns(app)
        ensure_user_role_column(app)
        ensure_user_status_column(app)
        ensure_asset_identifiers_columns(app)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
