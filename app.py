from flask import Flask, render_template, request, redirect, url_for, session, flash
from markupsafe import Markup, escape
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_here_change_in_production')

# Hardcoded login credentials
LOGIN_EMAIL = "nakshinterior2020@gmail.com"
LOGIN_PASSWORD = "ivgenerator@3101"

# Company information
COMPANY_INFO = {
    'company_name': 'Naksh Interior',
    'gst_number': '27ASXPC6135D1ZN',
    'address': '407, 4th Floor, Shivneri A-21 Bldg, Swarajya City, Sec. 12, Near Spine City Mall, Spine Road, PCMC, Pune',
    'phone': '+91 9762764662',
    'email_contact': 'nakshinterior2020@gmail.com'
}

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.template_filter('nl2br')
def nl2br(value):
    escaped_value = escape(value)
    return Markup(escaped_value.replace('\n', Markup('<br>\n')))

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == LOGIN_EMAIL and password == LOGIN_PASSWORD:
            session['logged_in'] = True
            # Set company info in session
            for key, value in COMPANY_INFO.items():
                session[key] = value
            flash('Login successful!', 'success')
            return redirect(url_for('invoice_form'))
        else:
            flash('Login failed. Check your username and password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/invoice', methods=['GET', 'POST'])
@login_required
def invoice_form():
    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        customer_address = request.form.get('customer_address')
        invoice_number = request.form.get('invoice_number')
        invoice_date = request.form.get('invoice_date')
        terms_conditions = request.form.get('terms_conditions', '')

        # Separate collections for Civil and Furniture items
        civil_items = []
        furniture_items = []
        
        # Extract Civil Work Items
        for key in request.form:
            if key.startswith('civil_description'):
                index = key.replace('civil_description', '')
                description = request.form.get(f'civil_description{index}')
                size = request.form.get(f'civil_size{index}')
                amount = float(request.form.get(f'civil_amount{index}', 0))
                
                if description and size and amount > 0:
                    civil_items.append({
                        'description': description,
                        'quantity_unit': size,
                        'total': amount
                    })

        # Extract Furniture Work Items
        for key in request.form:
            if key.startswith('furniture_description'):
                index = key.replace('furniture_description', '')
                description = request.form.get(f'furniture_description{index}')
                size = request.form.get(f'furniture_size{index}')
                amount = float(request.form.get(f'furniture_amount{index}', 0))
                
                if description and size and amount > 0:
                    furniture_items.append({
                        'description': description,
                        'quantity_unit': size,
                        'total': amount
                    })

        # Extract Specification Items
        specification_items = []
        for key in request.form:
            if key.startswith('spec_description'):
                index = key.replace('spec_description', '')
                description = request.form.get(f'spec_description{index}')
                materials = request.form.get(f'spec_materials{index}')
                
                if description and materials:
                    specification_items.append({
                        'description': description,
                        'materials': materials
                    })

        # Calculate totals
        civil_total = sum(item['total'] for item in civil_items)
        furniture_total = sum(item['total'] for item in furniture_items)
        subtotal = civil_total + furniture_total
        
        # For now, we'll set GST to 0. You can modify this based on your requirements
        gst_tax = 0
        igst_tax = 0
        shipping_charges = 0
        
        total_amount = subtotal + gst_tax + igst_tax + shipping_charges

        return render_template('invoice_template.html',
            company_name='Naksh Interior',
            customer_name=customer_name,
            customer_address=customer_address,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            civil_items=civil_items,
            furniture_items=furniture_items,
            specification_items=specification_items,
            civil_total=civil_total,
            furniture_total=furniture_total,
            subtotal=subtotal,
            gst_tax=gst_tax,
            igst_tax=igst_tax,
            shipping_charges=shipping_charges,
            total_amount=total_amount,
            terms_conditions=terms_conditions,
            currency='INR',
            currency_symbol='₹',
            include_gst=False,  # Set to True if you want to show GST
            include_igst=False  # Set to True if you want to show IGST
        )

    return render_template('invoice_form.html')


# Health check endpoint for Render
@app.route('/health')
def health_check():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)