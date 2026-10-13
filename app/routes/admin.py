from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Saree, Worker, Production, Billing, User, ActivityLog, Customer, CustomerInvoice, CustomerInvoiceItem, WorkerAdvance
from app.routes.auth import role_required
from app.services.analytics_service import (
    get_dashboard_stats, get_production_trends, 
    get_saree_distribution, get_worker_rankings
)
from app.services.pdf_service import generate_billing_pdf, generate_sales_invoice_pdf
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

def log_activity(action, details):
    """Utility helper to write an entry into the admin audit log."""
    log = ActivityLog(user_id=current_user.id, action=action, details=details)
    db.session.add(log)
    db.session.commit()

# --- 1. DASHBOARD ---
@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    stats = get_dashboard_stats()
    trends = get_production_trends(days=15)
    sarees_dist = get_saree_distribution()
    rankings = get_worker_rankings()
    
    # Fetch recent logs and recent productions
    recent_productions = Production.query.order_by(Production.date.desc()).limit(5).all()
    recent_logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(5).all()
    
    return render_template(
        'admin/dashboard.html',
        stats=stats,
        trends=trends,
        sarees_dist=sarees_dist,
        rankings=rankings,
        recent_productions=recent_productions,
        recent_logs=recent_logs
    )

# --- 2. SAREE MANAGEMENT ---
@admin_bp.route('/sarees', methods=['GET'])
@login_required
@role_required('admin')
def list_sarees():
    sarees = Saree.query.order_by(Saree.created_at.desc()).all()
    return render_template('admin/sarees.html', sarees=sarees)

@admin_bp.route('/sarees/add', methods=['POST'])
@login_required
@role_required('admin')
def add_saree():
    name = request.form.get('name').strip()
    color = request.form.get('color', '').strip()
    category = request.form.get('category').strip()
    cost_price = float(request.form.get('cost_price'))
    selling_price = float(request.form.get('selling_price'))
    worker_payment = float(request.form.get('worker_payment'))
    
    # Validation
    if not color:
        flash("Please enter a color for the saree.", "danger")
        return redirect(url_for('admin.list_sarees'))
    if Saree.query.filter_by(name=name, color=color).first():
        flash(f"Saree '{name}' in color '{color}' already exists in catalog.", "danger")
        return redirect(url_for('admin.list_sarees'))
        
    # Handle Saree Image Upload
    saree_image_filename = None
    if 'saree_image' in request.files:
        from werkzeug.utils import secure_filename
        import os
        import time
        file = request.files['saree_image']
        if file and file.filename != '':
            uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'sarees')
            os.makedirs(uploads_dir, exist_ok=True)
            filename = f"saree_{int(time.time())}_{secure_filename(file.filename)}"
            file.save(os.path.join(uploads_dir, filename))
            saree_image_filename = filename
            
    saree = Saree(
        name=name,
        color=color,
        category=category,
        cost_price=cost_price,
        selling_price=selling_price,
        worker_payment=worker_payment,
        saree_image=saree_image_filename
    )
    db.session.add(saree)
    db.session.commit()
    
    log_activity('ADD_SAREE', f"Added saree product '{name}' in {color} (Category: {category}, Rate: {worker_payment})")
    flash(f"Saree '{name}' ({color}) successfully added to database.", "success")
    return redirect(url_for('admin.list_sarees'))

@admin_bp.route('/sarees/edit/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def edit_saree(id):
    saree = Saree.query.get_or_404(id)
    name = request.form.get('name').strip()
    color = request.form.get('color', '').strip()
    if not color:
        flash("Please enter a color for the saree.", "danger")
        return redirect(url_for('admin.list_sarees'))
    duplicate = Saree.query.filter_by(name=name, color=color).filter(Saree.id != saree.id).first()
    if duplicate:
        flash(f"Saree '{name}' in color '{color}' already exists in catalog.", "danger")
        return redirect(url_for('admin.list_sarees'))
    saree.name = name
    saree.color = color
    saree.category = request.form.get('category').strip()
    saree.cost_price = float(request.form.get('cost_price'))
    saree.selling_price = float(request.form.get('selling_price'))
    saree.worker_payment = float(request.form.get('worker_payment'))
    
    # Handle Saree Image Update
    if 'saree_image' in request.files:
        from werkzeug.utils import secure_filename
        import os
        import time
        file = request.files['saree_image']
        if file and file.filename != '':
            uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'sarees')
            os.makedirs(uploads_dir, exist_ok=True)
            # Remove old saree image if exists
            if saree.saree_image:
                try:
                    old_path = os.path.join(uploads_dir, saree.saree_image)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                except Exception:
                    pass
            filename = f"saree_{int(time.time())}_{secure_filename(file.filename)}"
            file.save(os.path.join(uploads_dir, filename))
            saree.saree_image = filename
            
    db.session.commit()
    log_activity('EDIT_SAREE', f"Edited saree product '{saree.name}' ({saree.color}, ID: {saree.id})")
    flash(f"Saree '{saree.name}' ({saree.color}) details successfully updated.", "success")
    return redirect(url_for('admin.list_sarees'))

@admin_bp.route('/sarees/delete/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def delete_saree(id):
    saree = Saree.query.get_or_404(id)
    
    # Cascade delete all associated productions and invoice items to prevent foreign key issues
    Production.query.filter_by(saree_id=saree.id).delete()
    CustomerInvoiceItem.query.filter_by(saree_id=saree.id).delete()
    
    db.session.delete(saree)
    db.session.commit()
    
    log_activity('DELETE_SAREE', f"Deleted saree product '{saree.name}' ({saree.color}) and associated history logs (ID: {saree.id})")
    flash(f"Saree '{saree.name}' ({saree.color}) and associated historic production/invoicing records successfully deleted.", "success")
    return redirect(url_for('admin.list_sarees'))


# --- 3. WORKER MANAGEMENT ---
@admin_bp.route('/workers', methods=['GET'])
@login_required
@role_required('admin')
def list_workers():
    workers = Worker.query.order_by(Worker.joining_date.desc()).all()
    return render_template('admin/workers.html', workers=workers)

@admin_bp.route('/workers/add', methods=['POST'])
@login_required
@role_required('admin')
def add_worker():
    name = request.form.get('name').strip()
    phone = request.form.get('phone').strip()
    address = request.form.get('address').strip()
    joining_date_str = request.form.get('joining_date')
    create_account = True if request.form.get('create_account') else False
    
    joining_date = datetime.strptime(joining_date_str, '%Y-%m-%d') if joining_date_str else datetime.utcnow()
    
    # Handle Profile Image Upload
    profile_image_filename = None
    if 'profile_image' in request.files:
        from werkzeug.utils import secure_filename
        import os
        import time
        file = request.files['profile_image']
        if file and file.filename != '':
            uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'workers')
            os.makedirs(uploads_dir, exist_ok=True)
            filename = f"worker_{int(time.time())}_{secure_filename(file.filename)}"
            file.save(os.path.join(uploads_dir, filename))
            profile_image_filename = filename
            
    user_id = None
    if create_account:
        username = request.form.get('username').strip().lower()
        password = request.form.get('password')
        
        # Verify username uniqueness
        if User.query.filter_by(username=username).first():
            flash(f"Username '{username}' is already taken. Please choose another one.", "danger")
            return redirect(url_for('admin.list_workers'))
            
        u = User(username=username, role='worker')
        u.set_password(password)
        db.session.add(u)
        db.session.flush() # Populate u.id
        user_id = u.id
        
    worker = Worker(
        user_id=user_id,
        name=name,
        phone=phone,
        address=address,
        joining_date=joining_date,
        status='active',
        profile_image=profile_image_filename
    )
    db.session.add(worker)
    db.session.commit()
    
    log_activity('ADD_WORKER', f"Added worker '{name}' (Phone: {phone}, Portal Account: {create_account})")
    flash(f"Worker '{name}' successfully registered.", "success")
    return redirect(url_for('admin.list_workers'))

@admin_bp.route('/workers/edit/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def edit_worker(id):
    worker = Worker.query.get_or_404(id)
    worker.name = request.form.get('name').strip()
    worker.phone = request.form.get('phone').strip()
    worker.address = request.form.get('address').strip()
    worker.status = request.form.get('status')
    
    joining_date_str = request.form.get('joining_date')
    if joining_date_str:
        worker.joining_date = datetime.strptime(joining_date_str, '%Y-%m-%d')
        
    # Handle Profile Image Update
    if 'profile_image' in request.files:
        from werkzeug.utils import secure_filename
        import os
        import time
        file = request.files['profile_image']
        if file and file.filename != '':
            uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'workers')
            os.makedirs(uploads_dir, exist_ok=True)
            # Remove old profile picture if exists
            if worker.profile_image:
                try:
                    old_path = os.path.join(uploads_dir, worker.profile_image)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                except Exception:
                    pass
            filename = f"worker_{int(time.time())}_{secure_filename(file.filename)}"
            file.save(os.path.join(uploads_dir, filename))
            worker.profile_image = filename
            
    # Check if worker needs portal account password reset or creation
    reset_password = True if request.form.get('reset_password') else False
    if reset_password and worker.user:
        new_password = request.form.get('new_password')
        worker.user.set_password(new_password)
        
    db.session.commit()
    log_activity('EDIT_WORKER', f"Edited worker details for '{worker.name}' (ID: {worker.id}, Status: {worker.status})")
    flash(f"Worker '{worker.name}' details successfully updated.", "success")
    return redirect(url_for('admin.list_workers'))

@admin_bp.route('/workers/delete/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def delete_worker(id):
    worker = Worker.query.get_or_404(id)
    worker_name = worker.name
    worker_id = worker.id
    
    # Cache user account to delete it as well
    user = worker.user
    
    db.session.delete(worker)
    if user:
        db.session.delete(user)
        
    db.session.commit()
    
    log_activity('DELETE_WORKER', f"Deleted worker profile '{worker_name}' and user portal account (ID: {worker_id})")
    flash(f"Worker '{worker_name}' profile successfully deleted.", "success")
    return redirect(url_for('admin.list_workers'))


# --- 4. PRODUCTION LOGS ---
@admin_bp.route('/production', methods=['GET'])
@login_required
@role_required('admin')
def list_production():
    productions = Production.query.order_by(Production.date.desc()).all()
    workers = Worker.query.filter_by(status='active').order_by(Worker.name).all()
    sarees = Saree.query.order_by(Saree.name, Saree.color).all()
    
    return render_template(
        'admin/production.html',
        productions=productions,
        workers=workers,
        sarees=sarees
    )

@admin_bp.route('/production/add', methods=['POST'])
@login_required
@role_required('admin')
def add_production():
    worker_id_val = request.form.get('worker_id')
    if not worker_id_val:
        flash("You must select a weaver.", "danger")
        return redirect(url_for('admin.list_production'))
        
    worker_id = int(worker_id_val)
    date_str = request.form.get('date')
    date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.utcnow()
    
    worker = Worker.query.get_or_404(worker_id)
    
    # Parse list arrays from dynamic rows
    saree_ids = request.form.getlist('saree_id[]')
    quantities = request.form.getlist('quantity[]')
    
    # Fallback to single saree fields if lists are empty
    if not saree_ids:
        single_saree = request.form.get('saree_id')
        single_qty = request.form.get('quantity')
        if single_saree and single_qty:
            saree_ids = [single_saree]
            quantities = [single_qty]
            
    if not saree_ids:
        flash("You must specify at least one saree entry to record production.", "danger")
        return redirect(url_for('admin.list_production'))
        
    logged_count = 0
    total_earnings = 0
    
    for i in range(len(saree_ids)):
        if not saree_ids[i] or not quantities[i]:
            continue
        try:
            sid = int(saree_ids[i])
            qty = int(quantities[i])
        except (ValueError, TypeError):
            continue
            
        if qty <= 0:
            continue
            
        saree = Saree.query.get_or_404(sid)
        
        # Financial metrics calculations
        worker_earnings = qty * saree.worker_payment
        company_revenue = qty * saree.selling_price
        company_profit = company_revenue - worker_earnings - (qty * saree.cost_price)
        
        prod = Production(
            worker_id=worker.id,
            saree_id=saree.id,
            quantity=qty,
            date=date,
            worker_earnings=worker_earnings,
            company_revenue=company_revenue,
            company_profit=company_profit,
            recorded_by_id=current_user.id
        )
        db.session.add(prod)
        logged_count += qty
        total_earnings += worker_earnings
        
    db.session.commit()
    
    if logged_count > 0:
        log_activity('ADD_PRODUCTION', f"Logged batch of {logged_count} sarees for weaver '{worker.name}' (Total Payout: {total_earnings})")
        flash(f"Production successfully recorded for {worker.name} ({logged_count} sarees logged).", "success")
    else:
        flash("No valid production items were logged.", "warning")
        
    return redirect(url_for('admin.list_production'))

@admin_bp.route('/production/delete/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def delete_production(id):
    prod = Production.query.get_or_404(id)
    worker_name = prod.worker.name
    saree_name = f"{prod.saree.name} ({prod.saree.color})"
    qty = prod.quantity
    
    db.session.delete(prod)
    db.session.commit()
    
    log_activity('DELETE_PRODUCTION', f"Removed production entry of {qty} x '{saree_name}' for weaver '{worker_name}'")
    flash("Production entry deleted successfully.", "success")
    return redirect(url_for('admin.list_production'))


# --- 5. BILLING & INVOICES ---
@admin_bp.route('/billing', methods=['GET'])
@login_required
@role_required('admin')
def list_billing():
    workers = Worker.query.filter_by(status='active').order_by(Worker.name).all()
    billings = Billing.query.order_by(Billing.created_at.desc()).all()
    
    # Query all worker advances to display on the ledger
    advances = WorkerAdvance.query.order_by(WorkerAdvance.date.desc()).all()
    
    # For each active worker, calculate current pending/unsettled production quantities, earnings, and advances
    unsettled_summaries = {}
    for w in workers:
        # Find latest billing date for this worker if exists
        last_bill = Billing.query.filter_by(worker_id=w.id).order_by(Billing.end_date.desc()).first()
        
        # Query productions after last billing date, or all if never billed
        query = Production.query.filter_by(worker_id=w.id)
        if last_bill:
            query = query.filter(Production.date > last_bill.end_date)
            
        unsettled_prods = query.all()
        
        total_qty = sum(p.quantity for p in unsettled_prods)
        total_earn = sum(p.worker_earnings for p in unsettled_prods)
        total_profit = sum(p.company_profit for p in unsettled_prods)
        
        # Query pending advances
        pending_advs = WorkerAdvance.query.filter_by(worker_id=w.id, status='pending').all()
        total_adv = sum(adv.amount for adv in pending_advs)
        
        unsettled_summaries[w.id] = {
            "qty": total_qty,
            "earnings": total_earn,
            "profit": total_profit,
            "advance": total_adv,
            "last_billed_date": last_bill.end_date if last_bill else None
        }
        
    return render_template(
        'admin/billing.html',
        workers=workers,
        billings=billings,
        advances=advances,
        unsettled_summaries=unsettled_summaries
    )

@admin_bp.route('/billing/generate', methods=['POST'])
@login_required
@role_required('admin')
def generate_bill():
    worker_id = int(request.form.get('worker_id'))
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    status = request.form.get('status', 'pending') # 'pending' or 'paid'
    
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    # Make end_date include full day up to 23:59:59
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
    
    worker = Worker.query.get_or_404(worker_id)
    
    # Query productions inside range
    productions = Production.query.filter_by(worker_id=worker.id).filter(
        Production.date >= start_date,
        Production.date <= end_date
    ).order_by(Production.date.asc()).all()
    
    if not productions:
        flash(f"No production logs found for {worker.name} within selected date range.", "warning")
        return redirect(url_for('admin.list_billing'))
        
    total_production = sum(p.quantity for p in productions)
    total_earnings = sum(p.worker_earnings for p in productions)
    company_profit = sum(p.company_profit for p in productions)
    
    # Query and calculate pending advances to deduct
    deduct_amount_req = request.form.get('deduct_amount')
    requested_deduct = float(deduct_amount_req) if deduct_amount_req else 0.0
    
    pending_advs = WorkerAdvance.query.filter_by(worker_id=worker.id, status='pending').order_by(WorkerAdvance.date.asc()).all()
    total_pending = sum(adv.amount for adv in pending_advs)
    
    # Cap the requested deduction at total pending advances
    advance_deducted = min(requested_deduct, total_pending)
    
    # Cap the deduction at total earnings to prevent negative payout
    if advance_deducted > total_earnings:
        advance_deducted = total_earnings
        
    net_payout = max(0.0, total_earnings - advance_deducted)
    
    # Call service to write ReportLab PDF (passing advance and net payout values)
    pdf_path = generate_billing_pdf(
        worker=worker,
        start_date=start_date,
        end_date=end_date,
        productions=productions,
        total_earnings=total_earnings,
        company_profit=company_profit,
        advance_deducted=advance_deducted,
        net_payout=net_payout
    )
    
    # Create Billing record
    bill = Billing(
        worker_id=worker.id,
        start_date=start_date,
        end_date=end_date,
        total_production=total_production,
        total_earnings=total_earnings,
        advance_deducted=advance_deducted,
        net_payout=net_payout,
        company_profit=company_profit,
        status=status,
        pdf_path=pdf_path
    )
    db.session.add(bill)
    db.session.flush() # Populate bill.id
    
    # Link and mark advances as deducted chronologically (supporting partial splitting)
    remaining_to_deduct = advance_deducted
    for adv in pending_advs:
        if remaining_to_deduct <= 0:
            break
            
        if adv.amount <= remaining_to_deduct:
            # Fully deduct this entry
            remaining_to_deduct -= adv.amount
            adv.status = 'deducted'
            adv.billing_id = bill.id
        else:
            # Partially deduct this entry by splitting it
            deduct_part = remaining_to_deduct
            remaining_to_deduct = 0.0
            
            # Reduce original advance entry amount
            adv.amount -= deduct_part
            
            # Create a split advance entry that is fully deducted and linked
            split_adv = WorkerAdvance(
                worker_id=worker.id,
                amount=deduct_part,
                reason=f"Deduction partial from SPM-{bill.id} (Split of {adv.reason or 'Advance'})",
                date=adv.date,
                status='deducted',
                billing_id=bill.id
            )
            db.session.add(split_adv)
            
    db.session.commit()
    
    log_activity('GENERATE_BILL', f"Generated statement SPM-{worker.id} for weaver '{worker.name}' ({total_production} sarees, Gross: {total_earnings}, Advances Deducted: {advance_deducted}, Net Payout: {net_payout})")
    flash(f"Statement successfully generated with ₹{advance_deducted:,.2f} advance deductions for {worker.name}.", "success")
    return redirect(url_for('admin.list_billing'))


# --- 5A. WORKER ADVANCES ---
@admin_bp.route('/advances/add', methods=['POST'])
@login_required
@role_required('admin')
def add_advance():
    worker_id = int(request.form.get('worker_id'))
    amount = float(request.form.get('amount'))
    reason = request.form.get('reason', '').strip()
    date_str = request.form.get('date')
    
    date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.utcnow()
    worker = Worker.query.get_or_404(worker_id)
    
    adv = WorkerAdvance(
        worker_id=worker_id,
        amount=amount,
        reason=reason,
        date=date,
        status='pending'
    )
    db.session.add(adv)
    db.session.commit()
    
    log_activity('ADD_ADVANCE', f"Issued advance payout of {amount} to weaver '{worker.name}' (Reason: {reason})")
    flash(f"Advance of ₹{amount:,.2f} successfully registered for {worker.name}.", "success")
    return redirect(url_for('admin.list_billing'))

@admin_bp.route('/advances/delete/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def delete_advance(id):
    adv = WorkerAdvance.query.get_or_404(id)
    worker_name = adv.worker.name
    amount = adv.amount
    
    db.session.delete(adv)
    db.session.commit()
    
    log_activity('DELETE_ADVANCE', f"Deleted advance payout of {amount} for weaver '{worker_name}'")
    flash("Advance record successfully deleted.", "success")
    return redirect(url_for('admin.list_billing'))

@admin_bp.route('/billing/settle/<int:id>', methods=['POST', 'GET'])
@login_required
@role_required('admin')
def settle_bill(id):
    bill = Billing.query.get_or_404(id)
    bill.status = 'paid'
    db.session.commit()
    
    log_activity('SETTLE_BILL', f"Settled payments (Marked Paid) for statement ID {bill.id} for weaver '{bill.worker.name}'")
    flash("Statement marked as Paid successfully.", "success")
    return redirect(url_for('admin.list_billing'))

@admin_bp.route('/billing/delete/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def delete_bill(id):
    bill = Billing.query.get_or_404(id)
    worker_name = bill.worker.name
    
    # Attempt to delete PDF invoice file if exists
    try:
        pdf_full_path = os.path.join(current_app.root_path, bill.pdf_path)
        if os.path.exists(pdf_full_path):
            os.remove(pdf_full_path)
    except Exception:
        pass # Handle silently
        
    db.session.delete(bill)
    db.session.commit()
    
    log_activity('DELETE_BILL', f"Deleted billing statement ID {bill.id} for weaver '{worker_name}'")
    flash("Statement report deleted successfully.", "success")
    return redirect(url_for('admin.list_billing'))


# --- 6. ACTIVITY LOGS ---
@admin_bp.route('/logs')
@login_required
@role_required('admin')
def list_logs():
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).all()
    return render_template('admin/logs.html', logs=logs)


# --- 7. WHOLESALE CUSTOMERS (OUTSIDE PARTIES) ---
@admin_bp.route('/customers', methods=['GET'])
@login_required
@role_required('admin')
def list_customers():
    customers = Customer.query.order_by(Customer.name.asc()).all()
    return render_template('admin/customers.html', customers=customers)


@admin_bp.route('/customers/add', methods=['POST'])
@login_required
@role_required('admin')
def add_customer():
    name = request.form.get('name').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    gstin = request.form.get('gstin', '').strip()
    state = request.form.get('state', 'Karnataka').strip()
    state_code = request.form.get('state_code', '29').strip()
    
    if not name:
        flash("Customer name is required.", "danger")
        return redirect(url_for('admin.list_customers'))
        
    customer = Customer(
        name=name,
        phone=phone,
        address=address,
        gstin=gstin,
        state=state,
        state_code=state_code
    )
    db.session.add(customer)
    db.session.commit()
    
    log_activity('ADD_CUSTOMER', f"Registered wholesale customer/outside party '{name}'")
    flash(f"Customer '{name}' registered successfully.", "success")
    return redirect(url_for('admin.list_customers'))


@admin_bp.route('/customers/edit/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    customer.name = request.form.get('name').strip()
    customer.phone = request.form.get('phone', '').strip()
    customer.address = request.form.get('address', '').strip()
    customer.gstin = request.form.get('gstin', '').strip()
    customer.state = request.form.get('state', 'Karnataka').strip()
    customer.state_code = request.form.get('state_code', '29').strip()
    
    if not customer.name:
        flash("Customer name is required.", "danger")
        return redirect(url_for('admin.list_customers'))
        
    db.session.commit()
    log_activity('EDIT_CUSTOMER', f"Updated wholesale customer details for '{customer.name}'")
    flash("Customer profile updated successfully.", "success")
    return redirect(url_for('admin.list_customers'))


@admin_bp.route('/customers/delete/<int:id>', methods=['GET'])
@login_required
@role_required('admin')
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    name = customer.name
    db.session.delete(customer)
    db.session.commit()
    
    log_activity('DELETE_CUSTOMER', f"Deleted customer '{name}' and all associated invoices")
    flash(f"Customer '{name}' removed successfully.", "success")
    return redirect(url_for('admin.list_customers'))


# --- 8. CUSTOMER SALES INVOICES (OUTSIDE PARTY BILLING) ---
@admin_bp.route('/sales-invoices', methods=['GET'])
@login_required
@role_required('admin')
def list_sales_invoices():
    invoices = CustomerInvoice.query.order_by(CustomerInvoice.date.desc()).all()
    return render_template('admin/customer_invoices.html', invoices=invoices)


@admin_bp.route('/sales-invoices/create', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def create_sales_invoice():
    if request.method == 'GET':
        customers = Customer.query.order_by(Customer.name.asc()).all()
        sarees = Saree.query.order_by(Saree.name.asc(), Saree.color.asc()).all()
        return render_template('admin/create_customer_invoice.html', customers=customers, sarees=sarees)
        
    # POST - Create Sales Bill
    customer_id_raw = request.form.get('customer_id')
    date_str = request.form.get('invoice_date')
    lorry_no = request.form.get('lorry_no', '').strip()
    eway_bill_no = request.form.get('eway_bill_no', '').strip()
    place_of_supply = request.form.get('place_of_supply', '').strip()
    
    sgst_rate = float(request.form.get('sgst_rate', 2.5))
    cgst_rate = float(request.form.get('cgst_rate', 2.5))
    igst_rate = float(request.form.get('igst_rate', 0.0))
    
    invoice_date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.utcnow()
    
    # Check if we should register a new customer dynamically
    if customer_id_raw == 'new_customer':
        new_name = request.form.get('new_customer_name', '').strip()
        new_gstin = request.form.get('new_customer_gstin', '').strip()
        new_phone = request.form.get('new_customer_phone', '').strip()
        new_state = request.form.get('new_customer_state', 'Karnataka').strip()
        new_state_code = request.form.get('new_customer_state_code', '29').strip()
        new_address = request.form.get('new_customer_address', '').strip()
        
        if not new_name:
            flash("New customer name is required.", "danger")
            return redirect(url_for('admin.create_sales_invoice'))
            
        customer = Customer.query.filter_by(name=new_name).first()
        if not customer:
            customer = Customer(
                name=new_name,
                gstin=new_gstin,
                phone=new_phone,
                state=new_state,
                state_code=new_state_code,
                address=new_address
            )
            db.session.add(customer)
            db.session.flush() # Populate newly generated customer.id
            log_activity('ADD_CUSTOMER', f"Dynamically registered wholesale customer '{new_name}' during sales billing")
    else:
        customer_id = int(customer_id_raw)
        customer = Customer.query.get_or_404(customer_id)
        
    # Line items parsed
    saree_ids = request.form.getlist('saree_id[]')
    hsn_codes = request.form.getlist('hsn_code[]')
    meters_list = request.form.getlist('meters[]')
    quantities = request.form.getlist('quantity[]')
    rates = request.form.getlist('rate[]')
    
    if not saree_ids:
        flash("Invoice must contain at least one saree product line item.", "danger")
        return redirect(url_for('admin.create_sales_invoice'))
        
    # Allocate sequential invoice number e.g. SN-242 safely preventing UNIQUE constraint conflicts
    max_invoice = CustomerInvoice.query.order_by(CustomerInvoice.id.desc()).first()
    if max_invoice:
        try:
            last_num_str = max_invoice.invoice_number.split('-')[-1]
            next_num = int(last_num_str) + 1
        except (ValueError, IndexError):
            next_num = CustomerInvoice.query.count() + 242
    else:
        next_num = 242
        
    invoice_number = f"SN-{next_num}"
    
    # Create Invoice shell
    invoice = CustomerInvoice(
        invoice_number=invoice_number,
        customer_id=customer.id,
        date=invoice_date,
        lorry_no=lorry_no,
        eway_bill_no=eway_bill_no,
        place_of_supply=place_of_supply,
        sgst_rate=sgst_rate,
        cgst_rate=cgst_rate,
        igst_rate=igst_rate
    )
    db.session.add(invoice)
    db.session.flush() # Grab ID before creating line items
    
    taxable_value = 0.0
    for i in range(len(saree_ids)):
        sid = int(saree_ids[i])
        hsn = hsn_codes[i].strip() or "5007"
        meters = float(meters_list[i]) if meters_list[i] else 5.5
        qty = int(quantities[i])
        rate = float(rates[i])
        amount = qty * rate
        taxable_value += amount
        
        item = CustomerInvoiceItem(
            invoice_id=invoice.id,
            saree_id=sid,
            hsn_code=hsn,
            meters=meters,
            quantity=qty,
            rate=rate,
            amount=amount
        )
        db.session.add(item)
        
    # Financial tax logic
    sgst_amount = taxable_value * (sgst_rate / 100.0)
    cgst_amount = taxable_value * (cgst_rate / 100.0)
    igst_amount = taxable_value * (igst_rate / 100.0)
    
    raw_total = taxable_value + sgst_amount + cgst_amount + igst_amount
    grand_total = float(round(raw_total))
    round_off = grand_total - raw_total
    
    invoice.taxable_value = taxable_value
    invoice.sgst_amount = sgst_amount
    invoice.cgst_amount = cgst_amount
    invoice.igst_amount = igst_amount
    invoice.round_off = round_off
    invoice.grand_total = grand_total
    
    # Save, generate matching PDF invoice, and save relative static URL
    db.session.flush()
    pdf_rel_path = generate_sales_invoice_pdf(invoice)
    invoice.pdf_path = pdf_rel_path
    
    db.session.commit()
    
    log_activity('CREATE_SALES_INVOICE', f"Generated Customer Tax Invoice {invoice_number} for customer '{invoice.customer.name}' totaling ₹{grand_total:,.2f}")
    flash(f"Invoice {invoice_number} created successfully.", "success")
    return redirect(url_for('admin.list_sales_invoices'))


@admin_bp.route('/sales-invoices/delete/<int:id>', methods=['GET'])
@login_required
@role_required('admin')
def delete_sales_invoice(id):
    invoice = CustomerInvoice.query.get_or_404(id)
    inv_num = invoice.invoice_number
    cust_name = invoice.customer.name
    
    # Clear physical file
    try:
        pdf_full_path = os.path.join(current_app.root_path, invoice.pdf_path)
        if os.path.exists(pdf_full_path):
            os.remove(pdf_full_path)
    except Exception:
        pass
        
    db.session.delete(invoice)
    db.session.commit()
    
    log_activity('DELETE_SALES_INVOICE', f"Deleted Sales Tax Invoice {inv_num} for customer '{cust_name}'")
    flash(f"Sales invoice {inv_num} deleted successfully.", "success")
    return redirect(url_for('admin.list_sales_invoices'))


@admin_bp.route('/sales-invoices/print/<int:id>', methods=['GET'])
@login_required
@role_required('admin')
def print_sales_invoice_html(id):
    invoice = CustomerInvoice.query.get_or_404(id)
    from app.services.pdf_service import num_to_words
    words = num_to_words(invoice.grand_total)
    return render_template('admin/print_sales_invoice.html', invoice=invoice, words=words)

@admin_bp.route('/settings/bill-setup', methods=['POST'])
@login_required
@role_required('admin')
def update_bill_setup():
    import os
    from flask import current_app
    
    img_dir = os.path.join(current_app.root_path, 'static', 'images')
    os.makedirs(img_dir, exist_ok=True)
    
    if 'left_logo' in request.files:
        file = request.files['left_logo']
        if file and file.filename != '':
            file.save(os.path.join(img_dir, 'left_logo.png'))
            flash("Left Deity Arch Logo updated successfully!", "success")
            
    if 'right_logo' in request.files:
        file = request.files['right_logo']
        if file and file.filename != '':
            file.save(os.path.join(img_dir, 'right_logo.png'))
            flash("Right Deity Portrait Logo updated successfully!", "success")
            
    return redirect(request.referrer or url_for('admin.dashboard'))
