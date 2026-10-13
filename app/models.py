from datetime import datetime
from sqlalchemy import UniqueConstraint
from flask_login import UserMixin
from app import db, bcrypt

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='worker') # 'admin' or 'worker'
    profile_image = db.Column(db.String(255), nullable=True) # Profile picture filename for admins
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    logs = db.relationship('ActivityLog', backref='user', lazy=True, cascade="all, delete-orphan")
    worker_profile = db.relationship('Worker', backref='user', uselist=False, lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Worker(db.Model):
    __tablename__ = 'workers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.Text, nullable=True)
    joining_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active') # 'active' or 'inactive'
    profile_image = db.Column(db.String(255), nullable=True) # Profile picture filename
    
    # Relationships
    productions = db.relationship('Production', backref='worker', lazy=True, cascade="all, delete-orphan")
    bills = db.relationship('Billing', backref='worker', lazy=True, cascade="all, delete-orphan")

class Saree(db.Model):
    __tablename__ = 'sarees'
    __table_args__ = (UniqueConstraint('name', 'color', name='uq_sarees_name_color'),)
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(50), nullable=False, default='Not specified', server_default='Not specified')
    category = db.Column(db.String(50), nullable=False) # e.g. Silk, Cotton, Crepe, Georgette
    cost_price = db.Column(db.Float, nullable=False) # Company cost to weave/raw materials
    selling_price = db.Column(db.Float, nullable=False) # Wholesale selling price
    worker_payment = db.Column(db.Float, nullable=False) # Labor rate paid to weaver per saree
    saree_image = db.Column(db.String(255), nullable=True) # Saree image filename
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    productions = db.relationship('Production', backref='saree', lazy=True)

class Production(db.Model):
    __tablename__ = 'productions'
    
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id', ondelete='CASCADE'), nullable=False)
    saree_id = db.Column(db.Integer, db.ForeignKey('sarees.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Financial metrics (automatically computed upon insertion)
    worker_earnings = db.Column(db.Float, nullable=False) # quantity * Saree.worker_payment
    company_revenue = db.Column(db.Float, nullable=False) # quantity * Saree.selling_price
    company_profit = db.Column(db.Float, nullable=False) # company_revenue - worker_earnings - (quantity * Saree.cost_price)
    
    recorded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    recorded_by = db.relationship('User', foreign_keys=[recorded_by_id])

class Billing(db.Model):
    __tablename__ = 'billings'
    
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id', ondelete='CASCADE'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    total_production = db.Column(db.Integer, nullable=False)
    total_earnings = db.Column(db.Float, nullable=False) # Gross Earnings
    advance_deducted = db.Column(db.Float, nullable=False, default=0.0) # Subtracted advances
    net_payout = db.Column(db.Float, nullable=False, default=0.0) # total_earnings - advance_deducted
    company_profit = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending') # 'pending' or 'paid'
    pdf_path = db.Column(db.String(255), nullable=True) # Relative path to download invoice pdf
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WorkerAdvance(db.Model):
    __tablename__ = 'worker_advances'
    
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(255), nullable=True) # e.g. "Hospital", "Festival", "Emergency"
    date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending') # 'pending' or 'deducted'
    billing_id = db.Column(db.Integer, db.ForeignKey('billings.id', ondelete='SET NULL'), nullable=True)
    
    # Relationships
    worker = db.relationship('Worker', backref=db.backref('advances', lazy=True, cascade="all, delete-orphan"))
    billing = db.relationship('Billing', backref=db.backref('advances', lazy=True))

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    action = db.Column(db.String(100), nullable=False) # e.g., 'ADD_PRODUCTION', 'CREATE_WORKER'
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # Sold To
    gstin = db.Column(db.String(20), nullable=True) # Party GSTIN
    phone = db.Column(db.String(15), nullable=True)
    address = db.Column(db.Text, nullable=True) # Place of Supply
    state = db.Column(db.String(50), nullable=True, default='Karnataka')
    state_code = db.Column(db.String(10), nullable=True, default='29')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    invoices = db.relationship('CustomerInvoice', backref='customer', lazy=True, cascade="all, delete-orphan")


class CustomerInvoice(db.Model):
    __tablename__ = 'customer_invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False) # Serial number (e.g. SN-242)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    lorry_no = db.Column(db.String(50), nullable=True)
    eway_bill_no = db.Column(db.String(50), nullable=True)
    place_of_supply = db.Column(db.String(100), nullable=True)
    
    # Financial details
    taxable_value = db.Column(db.Float, nullable=False, default=0.0) # Subtotal of items
    sgst_rate = db.Column(db.Float, nullable=False, default=2.5) # SGST percentage
    cgst_rate = db.Column(db.Float, nullable=False, default=2.5) # CGST percentage
    igst_rate = db.Column(db.Float, nullable=False, default=0.0) # IGST percentage
    
    sgst_amount = db.Column(db.Float, nullable=False, default=0.0)
    cgst_amount = db.Column(db.Float, nullable=False, default=0.0)
    igst_amount = db.Column(db.Float, nullable=False, default=0.0)
    
    round_off = db.Column(db.Float, nullable=False, default=0.0)
    grand_total = db.Column(db.Float, nullable=False, default=0.0)
    
    pdf_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    items = db.relationship('CustomerInvoiceItem', backref='invoice', lazy=True, cascade="all, delete-orphan")


class CustomerInvoiceItem(db.Model):
    __tablename__ = 'customer_invoice_items'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('customer_invoices.id', ondelete='CASCADE'), nullable=False)
    saree_id = db.Column(db.Integer, db.ForeignKey('sarees.id'), nullable=False)
    hsn_code = db.Column(db.String(20), nullable=True, default='5007') # HSN Code
    meters = db.Column(db.Float, nullable=True, default=5.5) # Length in meters
    quantity = db.Column(db.Integer, nullable=False, default=1)
    rate = db.Column(db.Float, nullable=False) # Unit price
    amount = db.Column(db.Float, nullable=False) # quantity * rate
    
    # Relationships
    saree = db.relationship('Saree')
