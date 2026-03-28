from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User, Admin, ParkingLot, ParkingSpot, Reservation
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hjfyf-ioingy-shiva'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)


def init_database():
    with app.app_context():
        db.create_all()
        
        
        if not Admin.query.filter_by(username='admin').first():
            admin = Admin(username='admin', password='admin123')
            db.session.add(admin)
            db.session.commit()
            print("Default admin created - Username: admin, Password: admin123")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin = Admin.query.filter_by(username=username, password=password).first()
        if admin:
            session['admin_id'] = admin.id
            session['user_type'] = 'admin'
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials!', 'error')
    
    return render_template('admin_login.html')

@app.route('/register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone = request.form.get('phone', '')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return render_template('user_register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return render_template('user_register.html')
        
        
        user = User(username=username, email=email, password=password, phone=phone)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('user_login'))
    
    return render_template('user_register.html')

@app.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['user_type'] = 'user'
            flash('Login successful!', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('user_login.html')


@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('user_type') != 'admin':
        flash('Admin access required!', 'error')
        return redirect(url_for('admin_login'))
    
    
    total_lots = ParkingLot.query.count()
    total_spots = ParkingSpot.query.count()
    occupied_spots = ParkingSpot.query.filter_by(status='O').count()
    available_spots = ParkingSpot.query.filter_by(status='A').count()
    total_users = User.query.count()
    
    parking_lots = ParkingLot.query.all()
    
    return render_template('admin_dashboard.html', 
                         total_lots=total_lots,
                         total_spots=total_spots,
                         occupied_spots=occupied_spots,
                         available_spots=available_spots,
                         total_users=total_users,
                         parking_lots=parking_lots)


@app.route('/admin/create_lot', methods=['GET', 'POST'])
def create_parking_lot():
    if session.get('user_type') != 'admin':
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        location_name = request.form['location_name']
        address = request.form['address']
        pin_code = request.form['pin_code']
        price_per_hour = float(request.form['price_per_hour'])
        max_spots = int(request.form['max_spots'])
        
        lot = ParkingLot(
            prime_location_name=location_name,
            address=address,
            pin_code=pin_code,
            price_per_hour=price_per_hour,
            maximum_number_of_spots=max_spots
        )
        db.session.add(lot)
        db.session.commit()
        
        
        for i in range(1, max_spots + 1):
            spot = ParkingSpot(
                lot_id=lot.id,
                spot_number=f"S{i:03d}",
                status='A'
            )
            db.session.add(spot)
        
        db.session.commit()
        flash(f'Parking lot "{location_name}" created with {max_spots} spots!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('create_parking_lot.html')


@app.route('/admin/users')
def admin_users():
    users = User.query.all()  
    return render_template('admin_users.html', users=users)

@app.route('/lot_details/<int:lot_id>')
def lot_details(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    
    spot_details = []
    for spot in spots:
        current_reservation = Reservation.query.filter_by(spot_id=spot.id, leaving_timestamp=None).first()
        if current_reservation:
            user = User.query.get(current_reservation.user_id)
        else:
            user = None

        spot_details.append({
            'spot': spot,
            'user': user,
            'reservation': current_reservation
        })

    return render_template('lot_details.html', lot=lot, spot_details=spot_details)

@app.route('/booked_users')
def booked():
    users=db.session.query(User).join(Reservation).distinct().all()
    return render_template('park.html',users=users)

@app.route('/user/dashboard')
def user_dashboard():
    if session.get('user_type') != 'user':
        flash('User login required!', 'error')
        return redirect(url_for('user_login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    current_reservations = Reservation.query.filter_by(
        user_id=user_id, 
        leaving_timestamp=None
    ).all()
    
    past_reservations = Reservation.query.filter(
        Reservation.user_id == user_id,
        Reservation.leaving_timestamp.isnot(None)
    ).order_by(Reservation.parking_timestamp.desc()).all()
    

    parking_lots = ParkingLot.query.all()
    available_lots = [lot for lot in parking_lots if lot.available_spots_count() > 0]
    
    active_reservations = len(current_reservations)
    total_reservations = len(current_reservations) + len(past_reservations)
    total_spent = round(sum(res.total_cost for res in past_reservations), 2)
    recent_reservations = past_reservations[:5]
    available_spots = sum(lot.available_spots_count() for lot in parking_lots)
    
    return render_template(
        'user_dashboard.html',
        user=user,
        active_reservations=active_reservations,
        total_reservations=total_reservations,
        total_spent=total_spent,
        available_spots=available_spots,
        recent_reservations=recent_reservations,
        active_reservations_list=current_reservations,
        parking_lots=parking_lots
    )

def available_spots_count(self):
    current_reservations = Reservation.query.filter_by(
        parking_lot_id=self.id, leaving_timestamp=None
    ).count()
    return self.maximum_number_of_spots - current_reservations


@app.route('/book_spot/<int:lot_id>', methods=['GET', 'POST'])
def book_spot(lot_id):
    if session.get('user_type') != 'user':
        return redirect(url_for('user_login'))

    lot = ParkingLot.query.get_or_404(lot_id)
    available_spots = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').all()

    if request.method == 'POST':
        vehicle_number = request.form['vehicle_number']

        if not available_spots:
            flash('No available spots in this parking lot!', 'error')
            return redirect(url_for('view_spots', lot_id=lot_id))

        spot = available_spots[0]
        reservation = Reservation(
            spot_id=spot.id,
            user_id=session['user_id'],
            vehicle_number=vehicle_number
        )
        spot.status = 'O'

        db.session.add(reservation)
        db.session.commit()

        flash(f'Spot {spot.spot_number} booked successfully!', 'success')
        return redirect(url_for('user_dashboard'))

    return render_template('parking_lots.html', lot=lot, available_spots=available_spots)


@app.route('/parking-lots')
def parking_lots():
    lots = ParkingLot.query.all()
    return render_template('parking_lots.html', parking_lots=lots)

@app.route('/lot/<int:lot_id>/spots')
def view_spots(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    return render_template('view_spots.html', lot=lot, spots=spots)


@app.route('/update_profile', methods=['POST'])
def update_profile():
    if session.get('user_type') != 'user':
        flash('User login required!', 'error')
        return redirect(url_for('user_login'))

    user_id = session['user_id']
    user = User.query.get(user_id)

    username = request.form.get('username')
    email = request.form.get('email')
    phone = request.form.get('phone')

    user.username = username
    user.email = email
    user.phone = phone

    db.session.commit()

    flash('Profile updated successfully!', 'success')
    return redirect(url_for('user_dashboard'))


@app.route('/release_spot/<int:reservation_id>',methods=['POST'])
def release_spot(reservation_id):
    if session.get('user_type') != 'user':
        return redirect(url_for('user_login'))
    
    user_id = session['user_id']
    reservation = Reservation.query.filter_by(
        id=reservation_id, 
        user_id=user_id,
        leaving_timestamp=None
    ).first()
    
    if not reservation:
        flash('Reservation not found!', 'error')
        return redirect(url_for('user_dashboard'))
    

    reservation.leaving_timestamp = datetime.utcnow()
    reservation.parking_cost = reservation.total_cost
    
    spot = ParkingSpot.query.get(reservation.spot_id)
    spot.status = 'A'
    
    db.session.commit()
    
    return redirect(url_for('user_dashboard'))

@app.route('/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    occupied_spots = lot.occupied_spots_count() 

    if request.method == 'POST':
        print(request.form)  

        lot.prime_location_name = request.form['location_name']
        lot.pin_code = request.form['pin_code']
        lot.address = request.form['address']
        lot.price_per_hour = float(request.form['price_per_hour'])

        new_max = int(request.form['max_spots'])
        current_total = len(lot.parking_spots)

        if new_max < lot.occupied_spots_count():
            flash("Cannot reduce spots below the number of occupied spots.", "danger")
            return redirect(request.url)

        elif new_max > current_total:
            for i in range(current_total + 1, new_max + 1):
                new_spot = ParkingSpot(
                    lot_id=lot.id,
                    spot_number=f"S{i:03}",
                    status='A'
                )
                db.session.add(new_spot)

        elif new_max < current_total:
            
            to_remove = current_total - new_max
            removable_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A')\
                                               .order_by(ParkingSpot.spot_number.desc())\
                                               .limit(to_remove).all()
            if len(removable_spots) < to_remove:
                flash("Not enough available spots to delete.", "danger")
                return redirect(request.url)
            for spot in removable_spots:
                db.session.delete(spot)

        lot.prime_location_name = request.form['location_name']
        lot.pin_code = request.form['pin_code']
        lot.address = request.form['address']
        lot.price_per_hour = float(request.form['price_per_hour'])
        lot.maximum_number_of_spots = new_max

        db.session.commit()
        flash("Parking lot updated successfully!", "success")
        return redirect(url_for('admin_dashboard'))


    return render_template('edit_lot.html', lot=lot, occupied_spots=occupied_spots)


@app.route('/delete_lot/<int:lot_id>', methods=['POST'])
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    occupied_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()

    if occupied_spots > 0:
        flash("Cannot delete parking lot: Some spots are still occupied.", "danger")
        return redirect(url_for('admin_dashboard'))

    try:
        db.session.delete(lot)
        db.session.commit()
        flash("Parking lot deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        print("Error deleting lot:", e)
        flash("Failed to delete the parking lot.", "danger")

    return redirect(url_for('admin_dashboard'))


@app.route('/api/parking_stats')
def parking_stats():
    if session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    lots = ParkingLot.query.all()
    stats = []
    
    for lot in lots:
        stats.append({
            'name': lot.prime_location_name,
            'total_spots': lot.maximum_number_of_spots,
            'available': lot.available_spots_count(),
            'occupied': lot.occupied_spots_count()
        })
    
    return jsonify(stats)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_database()
    app.run(debug=True)