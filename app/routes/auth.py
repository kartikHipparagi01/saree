from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def role_required(*roles):
    """
    Custom decorator to restrict endpoints based on user role.
    Usage: @role_required('admin') or @role_required('admin', 'worker')
    """
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles:
                flash("Access denied. You do not have permissions to view this resource.", "danger")
                if current_user.role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif current_user.role == 'worker':
                    return redirect(url_for('worker.dashboard'))
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/captcha')
def get_captcha():
    import random
    import string
    from flask import jsonify, session
    captcha_code = ''.join(random.choices(string.digits, k=6))
    session['captcha'] = captcha_code
    return jsonify({'captcha': captcha_code})

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    from flask import session
    import random
    import string

    # If user is already logged in, redirect to respective dashboard
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'worker':
            return redirect(url_for('worker.dashboard'))
            
    if request.method == 'POST':
        username = request.form.get('username').strip().lower()
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        entered_captcha = request.form.get('captcha', '').strip()
        stored_captcha = session.get('captcha', '')
        
        # Verify Captcha
        if not entered_captcha or entered_captcha != stored_captcha:
            flash("Incorrect 6-digit captcha. Please try again.", "danger")
            # Refresh captcha for next attempt
            session['captcha'] = ''.join(random.choices(string.digits, k=6))
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            
            # Audit log login action
            from app.models import ActivityLog, db
            log = ActivityLog(user_id=user.id, action='LOGIN', details=f"User {user.username} logged in successfully.")
            db.session.add(log)
            db.session.commit()
            
            flash(f"Welcome back, {user.username.capitalize()}!", "success")
            
            # Check for redirect parameter
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
                
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'worker':
                return redirect(url_for('worker.dashboard'))
        else:
            flash("Invalid username or password. Please try again.", "danger")
            # Refresh captcha for next attempt
            session['captcha'] = ''.join(random.choices(string.digits, k=6))
            
    if request.method == 'GET' or not session.get('captcha'):
        # Generate initial captcha
        session['captcha'] = ''.join(random.choices(string.digits, k=6))
        
        # Diagnostic print of admins in DB
        try:
            admins = User.query.filter_by(role='admin').all()
            print("DIAGNOSTIC - Admins in Database:")
            for adm in admins:
                print(f"  - ID: {adm.id}, Username: '{adm.username}'")
        except Exception as e:
            print("DIAGNOSTIC - Failed to query admins:", e)
            
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    # Audit log logout action
    from app.models import ActivityLog, db
    log = ActivityLog(user_id=current_user.id, action='LOGOUT', details=f"User {current_user.username} logged out.")
    db.session.add(log)
    db.session.commit()
    
    logout_user()
    flash("You have been successfully logged out.", "success")
    return redirect(url_for('auth.login'))

@auth_bp.route('/update-profile-photo', methods=['POST'])
@login_required
def update_profile_photo():
    import os
    from datetime import datetime
    from werkzeug.utils import secure_filename
    from flask import current_app
    from app import db
    
    if 'profile_image' not in request.files:
        flash("No file selected.", "danger")
        return redirect(request.referrer or url_for('auth.login'))
        
    file = request.files['profile_image']
    if file.filename == '':
        flash("No file selected.", "danger")
        return redirect(request.referrer or url_for('auth.login'))
        
    # Define upload directory
    role_dir = 'admins' if current_user.role == 'admin' else 'workers'
    uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads', role_dir)
    os.makedirs(uploads_dir, exist_ok=True)
    
    # Generate a secure filename
    ext = os.path.splitext(file.filename)[1]
    filename = f"user_{current_user.id}_{int(datetime.utcnow().timestamp())}{ext}"
    file_path = os.path.join(uploads_dir, filename)
    
    try:
        file.save(file_path)
        
        if current_user.role == 'admin':
            # Delete old admin avatar if any
            if current_user.profile_image:
                try:
                    old_path = os.path.join(uploads_dir, current_user.profile_image)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                except Exception:
                    pass
            current_user.profile_image = filename
        else:
            # For workers, update the worker profile record
            if current_user.worker_profile:
                if current_user.worker_profile.profile_image:
                    try:
                        old_path = os.path.join(uploads_dir, current_user.worker_profile.profile_image)
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    except Exception:
                        pass
                current_user.worker_profile.profile_image = filename
                
        db.session.commit()
        flash("Profile photo updated successfully!", "success")
    except Exception as e:
        flash(f"Failed to upload photo: {e}", "danger")
        
    return redirect(request.referrer or url_for('auth.login'))
