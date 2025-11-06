from app import app,db,User,Department

def setup():
    print('creating Database')
    db.create_all()
    print('database created')

def default_admin():
    print('checking for exsisting admin')

    admin=User.query.filter_by(role='admin').first()

    if not admin:
        default_admin=User(
            username='admin',
            role='admin'
        )
        default_admin.set_password('password123')
        db.session.add(default_admin)
        db.session.commit()
        print('admin created')
    else:
        print('admin user already created')

def default_department():
    department = ['Cardiology', 'Neurology', 'Orthopedics', 'Gastroenterologist' ,'General Medicine','General Surgery']
    for dept_name in department:
        dept=Department.query.filter_by(name=dept_name).first()
        if not dept:
            new_dept=Department(name=dept_name)
            db.session.add(new_dept)
            print(f"Created department: {dept_name}")
    db.session.commit()

if __name__=='__main__':
    with app.app_context():
        setup()
        default_admin()
        default_department()
        


