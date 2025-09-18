# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, join_room, emit
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

# --- APP & DATABASE CONFIGURATION ---
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'a_very_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- SOCKET.IO EVENTS FOR CHAT (FIX #1: MOVED TO THE CORRECT POSITION) ---
@socketio.on('join')
def on_join(data):
    """User joins a room specific to a prescription request."""
    room = str(data['room'])
    join_room(room)

@socketio.on('send_message')
def handle_send_message(data):
    """Handles sending a message, saving it, and broadcasting it."""
    request_id = int(data['request_id'])
    message_text = data['msg']
    room = str(request_id)

    new_message = ChatMessage(
        request_id=request_id,
        sender_id=current_user.id,
        message_text=message_text
    )
    db.session.add(new_message)

    
    prescription_req = PrescriptionRequest.query.get(request_id)
    if prescription_req and prescription_req.status == 'Pending':
        prescription_req.status = 'Awaiting Reply'
    db.session.commit()

    # Now that the message is saved, new_message.timestamp is available
    message_data = {
        'username': current_user.username,
        'msg': message_text,
        'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M')
    }
    emit('receive_message', message_data, room=room)

@socketio.on('change_status')
def handle_change_status(data):
    """Handles a pharmacist changing the status of a request."""
    request_id = int(data['request_id'])
    new_status = data['status']
    room = str(request_id)

    # Find the request and update its status in the database
    prescription_req = PrescriptionRequest.query.get(request_id)
    if prescription_req and current_user.role == 'pharmacist':
        prescription_req.status = new_status
        db.session.commit()

        # Broadcast the status change to everyone in the room
        emit('status_updated', {'status': new_status}, room=room)
# --- DATABASE MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(50), nullable=False)
    requests = db.relationship('PrescriptionRequest', backref='customer', lazy=True)
    # (CLEANUP: Removed redundant 'messages' relationship)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class PrescriptionRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    medicines_text = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('prescription_request.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    # This 'sender' relationship allows us to use 'message.sender.username' in templates
    sender = db.relationship('User', backref='sent_messages')

# --- FLASK-LOGIN SETUP ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROUTES ---
@app.route('/')
def index():
    """Renders the new home page."""
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists.')
            return redirect(url_for('signup'))

        new_user = User(username=username, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            flash('Please check your login details and try again.')
            return redirect(url_for('login'))

        login_user(user)
        if user.role == 'pharmacist':
            return redirect(url_for('pharmacist_dashboard'))
        else:
            return redirect(url_for('customer_dashboard'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- CUSTOMER ROUTES ---
@app.route('/customer/dashboard')
@login_required
def customer_dashboard():
    if current_user.role != 'customer':
        flash("Access denied.", "danger")
        return redirect(url_for('login'))
    
    requests = PrescriptionRequest.query.filter_by(customer_id=current_user.id).order_by(PrescriptionRequest.timestamp.desc()).all()
    return render_template('customer_dashboard.html', requests=requests)

@app.route('/customer/new_prescription', methods=['GET', 'POST'])
@login_required
def new_prescription():
    if current_user.role != 'customer':
        flash("Access denied.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        medicines_text = request.form.get('medicines')
        if not medicines_text:
            flash("Medicine list cannot be empty.", "warning")
            return redirect(url_for('new_prescription'))
        
        new_req = PrescriptionRequest(customer_id=current_user.id, medicines_text=medicines_text)
        db.session.add(new_req)
        db.session.commit()
        
        flash("Your prescription has been submitted successfully!", "success")
        return redirect(url_for('customer_dashboard'))

    return render_template('new_prescription.html')

# --- PHARMACIST ROUTES ---
@app.route('/pharmacist/dashboard')
@login_required
def pharmacist_dashboard():
    if current_user.role != 'pharmacist':
        flash("Access denied.", "danger")
        return redirect(url_for('login'))
    
    pending_requests = PrescriptionRequest.query.join(User).filter(PrescriptionRequest.status == 'Pending').order_by(PrescriptionRequest.timestamp.asc()).all()
    return render_template('pharmacist_dashboard.html', requests=pending_requests)

# --- SHARED ROUTES ---
@app.route('/request/<int:request_id>')
@login_required
def request_details(request_id):
    req = PrescriptionRequest.query.get_or_404(request_id)
    
    if current_user.role == 'customer' and req.customer_id != current_user.id:
        flash("You are not authorized to view this request.", "danger")
        return redirect(url_for('customer_dashboard'))
    
    customer = User.query.get(req.customer_id)
    chat_history = ChatMessage.query.filter_by(request_id=request_id).order_by(ChatMessage.timestamp.asc()).all()

    return render_template('request_details.html', req=req, customer=customer, chat_history=chat_history)

@app.route('/request/<int:request_id>',methods=['POST'])
@login_required
def delete_request(request_id):
    # Find the request to be deleted
    req_to_delete = PrescriptionRequest.query.get_or_404(request_id)

    # CRITICAL SECURITY CHECK: Ensure the current user is the owner of the request
    if req_to_delete.customer_id != current_user.id:
        flash("You are not authorized to delete this request.", "danger")
        return redirect(url_for('customer_dashboard'))

    try:
        # First, delete any chat messages associated with the request
        ChatMessage.query.filter_by(request_id=request_id).delete()
        
        # Now, delete the request itself
        db.session.delete(req_to_delete)
        
        # Commit the changes to the database
        db.session.commit()
        flash("Request has been successfully deleted.", "success")
    except:
        db.session.rollback()
        flash("An error occurred while deleting the request.", "danger")

    return redirect(url_for('customer_dashboard'))

# medicore/app.py -> before the __main__ block

# --- DEBUG ROUTE (Temporary) ---
@app.route('/debug/user')
@login_required
def debug_user():
    role = current_user.role
    # This page will show us the exact role stored in the database
    return f"""
        <h1>User Debug Information</h1>
        <p><b>Username:</b> {current_user.username}</p>
        <p><b>Role from database:</b> '{role}'</p>
        <hr>
        <p><b>Is role exactly 'customer'?</b> {role == 'customer'}</p>
        <p>If the above is 'False', the 'Access Denied' error will occur.</p>
    """
# --- MAIN EXECUTION ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)