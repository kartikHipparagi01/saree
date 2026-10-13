from app import create_app, db
from app.models import User, Worker, Saree, Production, Billing, ActivityLog

app = create_app()
with app.app_context():
    with open("log.txt", "w") as f:
        f.write("=== USERS ===\n")
        for u in User.query.all():
            f.write(f"ID: {u.id}, Username: {u.username}, Role: {u.role}, CreatedAt: {repr(u.created_at)} ({type(u.created_at)})\n")
            
        f.write("\n=== WORKERS ===\n")
        for w in Worker.query.all():
            f.write(f"ID: {w.id}, Name: {w.name}, Phone: {w.phone}, Joining: {repr(w.joining_date)} ({type(w.joining_date)})\n")
            
        f.write("\n=== SAREES ===\n")
        for s in Saree.query.all():
            f.write(f"ID: {s.id}, Name: {s.name}, Category: {s.category}, Payout: {s.worker_payment}\n")
            
        f.write("\n=== PRODUCTION ===\n")
        for p in Production.query.all():
            f.write(f"ID: {p.id}, Date: {repr(p.date)}, Qty: {p.quantity}\n")
            
        f.write("\n=== BILLING ===\n")
        for b in Billing.query.all():
            f.write(f"ID: {b.id}, Start: {repr(b.start_date)}, End: {repr(b.end_date)}\n")
            
        f.write("\n=== ACTIVITY LOGS ===\n")
        for l in ActivityLog.query.all():
            f.write(f"ID: {l.id}, Action: {l.action}, Timestamp: {repr(l.timestamp)} ({type(l.timestamp)})\n")
            f.write(f"  User: {repr(l.user)} (Username: {repr(l.user.username if l.user else None)})\n")
            
        f.write("\n=== END ===\n")
