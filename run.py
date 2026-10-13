from app import create_app, db

app = create_app()

def seed_database():
    """Create missing tables; admin credentials come from environment settings."""
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    seed_database()
    app.run(host='0.0.0.0', port=5000, debug=app.config['APP_ENV'] != 'production')
