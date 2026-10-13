from app import create_app, db
from app.models import Customer, CustomerInvoice, CustomerInvoiceItem, Saree
from app.services.pdf_service import generate_sales_invoice_pdf
from datetime import datetime

app = create_app()
with app.app_context():
    # 1. Ensure tables exist
    db.create_all()
    
    # 2. Get or create Customer
    customer = Customer.query.filter_by(name="Shri Neelakanteshwar Sarees").first()
    if not customer:
        customer = Customer(
            name="Shri Neelakanteshwar Sarees",
            gstin="29AIRPH3656G1ZU",
            phone="9632371493",
            address="Sadashiv Nagar, Near Old Water Tank, BANHATTI-587311",
            state="Karnataka",
            state_code="29"
        )
        db.session.add(customer)
        db.session.flush()
        print("Created sample customer profile.")
    
    # 3. Get first Saree or create one
    saree = Saree.query.first()
    if not saree:
        saree = Saree(
            name="Banarasi Katan Silk",
            category="Silk",
            cost_price=4500.0,
            selling_price=7500.0,
            worker_payment=800.0
        )
        db.session.add(saree)
        db.session.flush()
        print("Created sample Saree product.")
        
    # 4. Generate sequential invoice number
    invoice_count = CustomerInvoice.query.count()
    invoice_number = f"SN-{invoice_count + 242}"
    
    # 5. Create CustomerInvoice
    invoice = CustomerInvoice(
        invoice_number=invoice_number,
        customer_id=customer.id,
        date=datetime.now(),
        lorry_no="KA-23-M-8899",
        eway_bill_no="123456789012",
        place_of_supply="Banhatti",
        sgst_rate=2.5,
        cgst_rate=2.5,
        igst_rate=0.0
    )
    db.session.add(invoice)
    db.session.flush()
    
    # 6. Add Line Item
    item1 = CustomerInvoiceItem(
        invoice_id=invoice.id,
        saree_id=saree.id,
        hsn_code="5007",
        meters=5.5,
        quantity=24,
        rate=saree.selling_price,
        amount=24 * saree.selling_price
    )
    db.session.add(item1)
    
    # If there is another saree, add it too!
    saree2 = Saree.query.offset(1).first()
    if saree2:
        item2 = CustomerInvoiceItem(
            invoice_id=invoice.id,
            saree_id=saree2.id,
            hsn_code="5007",
            meters=6.3,
            quantity=15,
            rate=saree2.selling_price,
            amount=15 * saree2.selling_price
        )
        db.session.add(item2)
    
    db.session.flush()
    
    # Calculate tax & totals
    taxable_val = sum(item.amount for item in invoice.items)
    sgst_amt = taxable_val * 0.025
    cgst_amt = taxable_val * 0.025
    
    raw_total = taxable_val + sgst_amt + cgst_amt
    grand_total = float(round(raw_total))
    round_off = grand_total - raw_total
    
    invoice.taxable_value = taxable_val
    invoice.sgst_amount = sgst_amt
    invoice.cgst_amount = cgst_amt
    invoice.round_off = round_off
    invoice.grand_total = grand_total
    
    db.session.flush()
    
    # Generate matching PDF
    pdf_path = generate_sales_invoice_pdf(invoice)
    invoice.pdf_path = pdf_path
    db.session.commit()
    
    print(f"\nSUCCESS! Sample Invoice {invoice_number} created.")
    print(f"PDF statement saved to: {pdf_path}")
