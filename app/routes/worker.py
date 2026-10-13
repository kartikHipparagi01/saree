from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Saree, Worker, Production, Billing, ActivityLog
from app.routes.auth import role_required
from datetime import datetime, timedelta
from sqlalchemy import func

worker_bp = Blueprint('worker', __name__)

def get_worker_profile_or_404():
    """Helper to verify worker profile belongs to the logged-in User."""
    profile = current_user.worker_profile
    if not profile:
        flash("You do not have an associated Worker profile. Contact your Administrator.", "danger")
        return None
    return profile

@worker_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
@role_required('worker')
def dashboard():
    worker = get_worker_profile_or_404()
    if not worker:
        return redirect(url_for('auth.login'))
        
    # Handle Daily Work Submission inside GET/POST dashboard wrapper (for sleek UX)
    if request.method == 'POST':
        date_str = request.form.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.utcnow()
        
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
            return redirect(url_for('worker.dashboard'))
            
        logged_count = 0
        total_earnings = 0
        logged_names = []
        
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
            logged_names.append(f"{qty} x '{saree.name}' ({saree.color})")
            
        if logged_count > 0:
            # Log action
            log = ActivityLog(
                user_id=current_user.id,
                action='WORKER_SUBMIT_PRODUCTION',
                details=f"Worker {worker.name} logged self-production batch: {', '.join(logged_names)} (Total Earnings: {total_earnings})"
            )
            db.session.add(log)
            db.session.commit()
            flash(f"Successfully logged self-production of {logged_count} sarees!", "success")
        else:
            flash("No valid production items were logged.", "warning")
            
        return redirect(url_for('worker.dashboard'))

    # Calculate dashboard metrics
    today = datetime.utcnow().date()
    start_of_today = datetime.combine(today, datetime.min.time())
    
    # Start of current week (Monday)
    start_of_week = start_of_today - timedelta(days=start_of_today.weekday())
    
    # Start of current month
    start_of_month = start_of_today.replace(day=1)
    
    # 1. Today's production quantity
    qty_today = db.session.query(func.sum(Production.quantity)).filter(
        Production.worker_id == worker.id,
        Production.date >= start_of_today
    ).scalar() or 0
    
    # 2. Week's earnings
    earnings_week = db.session.query(func.sum(Production.worker_earnings)).filter(
        Production.worker_id == worker.id,
        Production.date >= start_of_week
    ).scalar() or 0
    
    # 3. Month's earnings
    earnings_month = db.session.query(func.sum(Production.worker_earnings)).filter(
        Production.worker_id == worker.id,
        Production.date >= start_of_month
    ).scalar() or 0
    
    # 4. Unpaid Earnings Balance
    last_bill = Billing.query.filter_by(worker_id=worker.id).order_by(Billing.end_date.desc()).first()
    unpaid_query = Production.query.filter_by(worker_id=worker.id)
    if last_bill:
        unpaid_query = unpaid_query.filter(Production.date > last_bill.end_date)
    unpaid_prods = unpaid_query.all()
    unpaid_balance = sum(p.worker_earnings for p in unpaid_prods)
    
    # Fetch lists
    sarees = Saree.query.order_by(Saree.name, Saree.color).all()
    recent_productions = Production.query.filter_by(worker_id=worker.id).order_by(Production.date.desc()).limit(10).all()
    personal_bills = Billing.query.filter_by(worker_id=worker.id).order_by(Billing.created_at.desc()).all()
    
    return render_template(
        'worker/dashboard.html',
        worker=worker,
        sarees=sarees,
        recent_productions=recent_productions,
        personal_bills=personal_bills,
        qty_today=int(qty_today),
        earnings_week=float(earnings_week),
        earnings_month=float(earnings_month),
        unpaid_balance=float(unpaid_balance),
        last_billed_date=last_bill.end_date if last_bill else None
    )
