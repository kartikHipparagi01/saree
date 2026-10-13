from app.models import Production, Worker, Saree, db
from sqlalchemy import func
from datetime import datetime, timedelta

def get_dashboard_stats():
    """
    Returns standard high-level business stats for the admin dashboard.
    """
    # 1. Total Sarees Produced
    total_production = db.session.query(func.sum(Production.quantity)).scalar() or 0
    
    # 2. Total Labor Cost (Paid to Workers)
    total_labor = db.session.query(func.sum(Production.worker_earnings)).scalar() or 0
    
    # 3. Total Company Revenue
    total_revenue = db.session.query(func.sum(Production.company_revenue)).scalar() or 0
    
    # 4. Total Company Profit
    total_profit = db.session.query(func.sum(Production.company_profit)).scalar() or 0
    
    # 5. Count active/total workers
    total_workers = Worker.query.filter_by(status='active').count()
    
    # 6. Count total Saree catalog count
    catalog_count = Saree.query.count()
    
    return {
        "total_production": int(total_production),
        "total_labor": float(total_labor),
        "total_revenue": float(total_revenue),
        "total_profit": float(total_profit),
        "active_workers": total_workers,
        "catalog_count": catalog_count
    }

def get_production_trends(days=15):
    """
    Returns daily production metrics (date, quantity, profit) for the last N days
    to construct dynamic area/line trends on dashboards.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days-1)
    
    # Base query grouped by date
    results = db.session.query(
        func.date(Production.date).label('day'),
        func.sum(Production.quantity).label('qty'),
        func.sum(Production.company_profit).label('profit')
    ).filter(
        Production.date >= start_date
    ).group_by(
        func.date(Production.date)
    ).order_by(
        'day'
    ).all()
    
    # Create dictionary mapping from existing dates
    data_map = {r.day: {"qty": r.qty, "profit": r.profit} for r in results}
    
    # Fill in potential gaps (missing days) with 0s to maintain smooth line chart
    labels = []
    quantities = []
    profits = []
    
    for i in range(days):
        current_day = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        labels.append((start_date + timedelta(days=i)).strftime('%d %b'))
        
        if current_day in data_map:
            quantities.append(int(data_map[current_day]["qty"]))
            profits.append(float(data_map[current_day]["profit"]))
        else:
            quantities.append(0)
            profits.append(0.0)
            
    return {
        "labels": labels,
        "quantities": quantities,
        "profits": profits
    }

def get_saree_distribution():
    """
    Returns data mapping categories of sarees produced to show item-type distributions.
    """
    results = db.session.query(
        Saree.category,
        func.sum(Production.quantity).label('qty')
    ).join(Production, Saree.id == Production.saree_id).group_by(
        Saree.category
    ).all()
    
    labels = [r.category for r in results]
    values = [int(r.qty) for r in results]
    
    # If empty, add a placeholder
    if not labels:
        labels = ["No Data"]
        values = [0]
        
    return {
        "labels": labels,
        "values": values
    }

def get_worker_rankings(limit=5):
    """
    Returns worker list ranked by production output (quantity) and earnings.
    """
    results = db.session.query(
        Worker.name,
        func.sum(Production.quantity).label('qty'),
        func.sum(Production.worker_earnings).label('earnings')
    ).join(Production, Worker.id == Production.worker_id).group_by(
        Worker.id
    ).order_by(
        func.sum(Production.quantity).desc()
    ).limit(limit).all()
    
    labels = [r.name for r in results]
    quantities = [int(r.qty) for r in results]
    earnings = [float(r.earnings) for r in results]
    
    # If empty
    if not labels:
        labels = ["No Data"]
        quantities = [0]
        earnings = [0.0]
        
    return {
        "labels": labels,
        "quantities": quantities,
        "earnings": earnings
    }
