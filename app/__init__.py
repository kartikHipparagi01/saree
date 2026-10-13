from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config

# Initialize extensions globally
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

# Setup login configurations
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'

def migrate_saree_color_schema():
    """Add saree colors and replace name-only uniqueness with variant uniqueness."""
    from sqlalchemy import inspect

    inspector = inspect(db.engine)
    columns = [column['name'] for column in inspector.get_columns('sarees')]
    if 'color' not in columns:
        db.session.execute(db.text(
            "ALTER TABLE sarees ADD COLUMN color VARCHAR(50) NOT NULL DEFAULT 'Not specified'"
        ))
        db.session.commit()

    inspector = inspect(db.engine)
    if db.engine.dialect.name == 'sqlite':
        with db.engine.connect() as connection:
            unique_indexes = connection.exec_driver_sql("PRAGMA index_list('sarees')").fetchall()
            name_only_unique = any(
                index[2] and [
                    column[2] for column in connection.exec_driver_sql(
                        f"PRAGMA index_info('{index[1].replace(chr(39), chr(39) * 2)}')"
                    ).fetchall()
                ] == ['name']
                for index in unique_indexes
            )
    else:
        name_only_unique = any(
            constraint.get('column_names') == ['name']
            for constraint in inspector.get_unique_constraints('sarees')
        )
    if not name_only_unique:
        return

    if db.engine.dialect.name == 'sqlite':
        raw_connection = db.engine.raw_connection()
        try:
            cursor = raw_connection.cursor()
            cursor.execute('PRAGMA foreign_keys=OFF')
            cursor.execute('''
                CREATE TABLE sarees_color_migration (
                    id INTEGER NOT NULL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    color VARCHAR(50) NOT NULL DEFAULT 'Not specified',
                    category VARCHAR(50) NOT NULL,
                    cost_price FLOAT NOT NULL,
                    selling_price FLOAT NOT NULL,
                    worker_payment FLOAT NOT NULL,
                    saree_image VARCHAR(255),
                    created_at DATETIME,
                    CONSTRAINT uq_sarees_name_color UNIQUE (name, color)
                )
            ''')
            cursor.execute('''
                INSERT INTO sarees_color_migration
                    (id, name, color, category, cost_price, selling_price,
                     worker_payment, saree_image, created_at)
                SELECT id, name, color, category, cost_price, selling_price,
                       worker_payment, saree_image, created_at
                FROM sarees
            ''')
            cursor.execute('DROP TABLE sarees')
            cursor.execute('ALTER TABLE sarees_color_migration RENAME TO sarees')
            raw_connection.commit()
            cursor.execute('PRAGMA foreign_keys=ON')
            cursor.close()
        except Exception:
            raw_connection.rollback()
            cursor.execute('PRAGMA foreign_keys=ON')
            raise
        finally:
            raw_connection.close()
        print('Database auto-migrated: sarees can now have multiple color variants.')
    elif db.engine.dialect.name == 'mysql':
        unique_indexes = [
            index for index in inspector.get_indexes('sarees')
            if index.get('unique') and index.get('column_names') == ['name']
        ]
        with db.engine.begin() as connection:
            for index in unique_indexes:
                index_name = index['name'].replace('`', '``')
                connection.exec_driver_sql(f'ALTER TABLE sarees DROP INDEX `{index_name}`')
            connection.exec_driver_sql(
                'ALTER TABLE sarees ADD CONSTRAINT uq_sarees_name_color UNIQUE (name, color)'
            )
        print('Database auto-migrated: sarees can now have multiple color variants.')

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app context
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Register all model tables before create_all and startup migrations run.
    from app.models import User
    
    # Auto-migration of columns/tables if missing in SQLite database
    with app.app_context():
        try:
            # Ensure tables exist
            db.create_all()

            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            
            # Check profile_image column in workers
            columns = [c['name'] for c in inspector.get_columns('workers')]
            if 'profile_image' not in columns:
                db.session.execute(db.text("ALTER TABLE workers ADD COLUMN profile_image VARCHAR(255);"))
                db.session.commit()
                print("Database auto-migrated: added profile_image column to workers table.")
                
            # Check profile_image column in users
            user_columns = [c['name'] for c in inspector.get_columns('users')]
            if 'profile_image' not in user_columns:
                db.session.execute(db.text("ALTER TABLE users ADD COLUMN profile_image VARCHAR(255);"))
                db.session.commit()
                print("Database auto-migrated: added profile_image column to users table.")
                
            # Check saree_image column in sarees
            saree_columns = [c['name'] for c in inspector.get_columns('sarees')]
            if 'saree_image' not in saree_columns:
                db.session.execute(db.text("ALTER TABLE sarees ADD COLUMN saree_image VARCHAR(255);"))
                db.session.commit()
                print("Database auto-migrated: added saree_image column to sarees table.")

            migrate_saree_color_schema()
                
            # Check worker_advances table
            if 'worker_advances' not in inspector.get_table_names():
                db.session.execute(db.text("""
                    CREATE TABLE worker_advances (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        worker_id INTEGER NOT NULL,
                        amount REAL NOT NULL,
                        reason VARCHAR(255),
                        date DATETIME DEFAULT CURRENT_TIMESTAMP,
                        status VARCHAR(20) DEFAULT 'pending',
                        billing_id INTEGER,
                        FOREIGN KEY (worker_id) REFERENCES workers (id) ON DELETE CASCADE,
                        FOREIGN KEY (billing_id) REFERENCES billings (id) ON DELETE SET NULL
                    );
                """))
                db.session.commit()
                print("Database auto-migrated: created worker_advances table.")
                
            # Check billing columns
            billing_cols = [c['name'] for c in inspector.get_columns('billings')]
            if 'advance_deducted' not in billing_cols:
                db.session.execute(db.text("ALTER TABLE billings ADD COLUMN advance_deducted REAL DEFAULT 0.0;"))
                db.session.commit()
                print("Database auto-migrated: added advance_deducted column to billings.")
            if 'net_payout' not in billing_cols:
                db.session.execute(db.text("ALTER TABLE billings ADD COLUMN net_payout REAL DEFAULT 0.0;"))
                db.session.commit()
                print("Database auto-migrated: added net_payout column to billings.")

        except Exception as e:
            print(f"Database auto-migration skipped/failed: {e}")

        # Bootstrap/rotate the administrator only from private environment settings.
        if app.config['ADMIN_USERNAME'] and app.config['ADMIN_PASSWORD']:
            admin_user = User.query.filter_by(role='admin').first()
            if admin_user is None:
                admin_user = User(username=app.config['ADMIN_USERNAME'], role='admin')
                admin_user.set_password(app.config['ADMIN_PASSWORD'])
                db.session.add(admin_user)
                db.session.commit()
            elif (admin_user.username != app.config['ADMIN_USERNAME'] or
                    not admin_user.check_password(app.config['ADMIN_PASSWORD'])):
                admin_user.username = app.config['ADMIN_USERNAME']
                admin_user.set_password(app.config['ADMIN_PASSWORD'])
                db.session.commit()
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Custom Jinja filters
    @app.template_filter('currency')
    def currency_filter(value):
        """Formats currency value into Indian Rupee style (₹) with commas."""
        if value is None:
            return "₹0.00"
        try:
            return f"₹{value:,.2f}"
        except (ValueError, TypeError):
            return f"₹{value}"

    @app.template_filter('format_date')
    def date_filter(value, format='%d-%b-%Y'):
        """Formats date or datetime objects into structured readable format."""
        if value is None:
            return ""
        return value.strftime(format)
        
    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.worker import worker_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(worker_bp, url_prefix='/worker')
    
    # Default route redirects to auth.login
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
        
    # Global headers hook to disable page caching for complete logout security
    @app.after_request
    def add_header(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    return app
