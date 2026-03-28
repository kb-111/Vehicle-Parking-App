from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    reservations = db.relationship('Reservation', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Admin(db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<Admin {self.username}>'

class ParkingLot(db.Model):
    __tablename__ = 'parking_lots'
    
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    maximum_number_of_spots = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    parking_spots = db.relationship('ParkingSpot', backref='parking_lot', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ParkingLot {self.prime_location_name}>'
    
    def available_spots_count(self):
        return len([spot for spot in self.parking_spots if spot.status == 'A'])
    
    def occupied_spots_count(self):
        return len([spot for spot in self.parking_spots if spot.status == 'O'])


class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'
    
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False)
    spot_number = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(1), default='A', nullable=False)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    
    reservations = db.relationship('Reservation', backref='parking_spot', lazy=True)
    
    def __repr__(self):
        return f'<ParkingSpot {self.spot_number} - {self.status}>'
    
    def current_reservation(self):
    
        return Reservation.query.filter_by(
            spot_id=self.id, 
            leaving_timestamp=None
        ).first()


class Reservation(db.Model):
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=False)
    parking_timestamp = db.Column(db.DateTime, default=datetime.now)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    parking_cost = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'<Reservation {self.vehicle_number} - Spot {self.spot_id}>'

    @property
    def parking_lot(self):
        
        return self.parking_spot.parking_lot if self.parking_spot else None

    @property
    def duration_hours(self):
        """Total hours parked (rounded up to 1 hour minimum)"""
        end_time = self.leaving_timestamp or datetime.now()
        duration = end_time - self.parking_timestamp
        hours = duration.total_seconds() / 3600
        return max(1, round(hours, 2))

    @property
    def total_cost(self):
        
        if self.parking_lot:
            return round(self.duration_hours * self.parking_lot.price_per_hour, 2)
        return 0

    def duration_parked(self):
        
        end_time = self.leaving_timestamp or datetime.now()
        duration = end_time - self.parking_timestamp
        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)
        return f"{hours}h {minutes}m" if hours else f"{minutes}m"
