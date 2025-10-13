from app import app, db, User

with app.app_context():
    print("Creating all tables...")

    db.create_all()

    if User.query.first() is None:
        print("Creating demo users...")
        
        user1 = User(email='user1@example.com', name='User One', role='user')
        user1.set_password('pass123')

        admin1 = User(email='admin@example.com', name='Admin User', role='admin')
        admin1.set_password('admin123')

        db.session.add(user1)
        db.session.add(admin1)
        db.session.commit()
        print("Demo users created successfully.")
    else:
        print("Database already contains users.")

    print("Database has been initialized.")

