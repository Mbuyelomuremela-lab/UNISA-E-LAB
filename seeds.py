from app import create_app
from extensions import db
from models import Province, Lab, User

app = create_app()

with app.app_context():
    if Province.query.count() == 0:
        provinces = ['Gauteng', 'Limpopo', 'Mpumalanga', 'KwaZulu-Natal', 'Western Cape']
        for name in provinces:
            db.session.add(Province(name=name))
        db.session.commit()

    if Lab.query.count() == 0:
        gauteng = Province.query.filter_by(name='Gauteng').first()
        db.session.add_all([
            Lab(name='Sunnyside Lab A', province_id=gauteng.id, latitude=-25.7479, longitude=28.2293, address='123 Sunnyside Ave, Pretoria', description='Main intern training lab.'),
            Lab(name='Sunnyside Lab B', province_id=gauteng.id, latitude=-25.7465, longitude=28.2321, address='45 Campus Road, Pretoria', description='Second lab for equipment testing.')
        ])
        db.session.commit()

    def create_user_if_missing(full_name, email, role, password, lab_id=None):
        existing = User.query.filter_by(email=email).first()
        if existing:
            return existing
        user = User(full_name=full_name, email=email, role=role, lab_id=lab_id)
        user.set_password(password)
        db.session.add(user)
        return user

    create_user_if_missing('System Administrator', 'sysadmin@sunnyside.edu', 'system_admin', 'SysAdmin@123')
    create_user_if_missing('Campus Administrator', 'admin@sunnyside.edu', 'admin', 'Admin@123')
    create_user_if_missing('Intern User', 'intern@sunnyside.edu', 'intern', 'Intern@123', lab_id=Lab.query.first().id)
    db.session.commit()

    print('Database seeded successfully.')
