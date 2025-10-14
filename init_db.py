from app import app, db, User, Item 

with app.app_context():
    print("Creating all tables...")
    db.create_all()

    if User.query.first() is None:
        print("Creating demo users...")
        user1 = User(email="user1@example.com", name="User One", role="user")
        user1.set_password("pass123")
        admin1 = User(email="admin@example.com", name="Admin User", role="admin")
        admin1.set_password("admin123")
        db.session.add_all([user1, admin1])
        db.session.commit()
        print("Demo users created successfully.")
    else:
        print("Database already contains users.")

    if Item.query.first() is None:
        print("Creating demo items...")
        item1 = Item(name="Item 1", price=12345)
        item2 = Item(name="Item 2", price=67890)
        db.session.add_all([item1, item2])
        db.session.commit()
        print("Demo items created successfully.")
    else:
        print("Database already contains items.")

    print("Database has been initialized.")