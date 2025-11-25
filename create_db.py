
from project import create_app, db

from project.models import User, Department


app = create_app()

def setup_database():
    print("Creating database and tables...")
    db.create_all()
    print("Database and tables created.")

def create_default_admin():
    print("Checking for existing admin...")
    admin = User.query.filter_by(role='admin').first()
    
    if not admin:
        print("Admin user not found. Creating default admin...")
        default_admin = User(
            username='admin',
            role='admin'
        )
        default_admin.set_password('admin123')
        
        db.session.add(default_admin)
        db.session.commit()
        print("Default admin user 'admin' with password 'admin123' created.")
    else:
        print("Admin user already exists.")

def create_default_departments():
    print("Checking for default departments...")
    depts = ['Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'General Medicine']
    
    for dept_name in depts:
        dept = Department.query.filter_by(name=dept_name).first()
        if not dept:
            new_dept = Department(name=dept_name)
            db.session.add(new_dept)
            print(f"Created department: {dept_name}")
            
    db.session.commit()
    print("Default departments check complete.")


if __name__ == '__main__':

    with app.app_context():
        setup_database()
        create_default_admin()
        create_default_departments()