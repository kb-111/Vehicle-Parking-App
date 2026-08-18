# 🚗 Vehicle Parking App (V1)

A multi-user web application built using **Flask** that manages parking lots, parking spots, and vehicle reservations for 4-wheelers.

## 📌 Project Overview

This application allows:

* **Admin (Superuser)** to manage parking lots and monitor usage
* **Users** to register, login, and reserve parking spots

The system automatically assigns available parking spots and tracks parking duration and cost.

## 🛠️ Tech Stack

* **Backend:** Flask (Python)
* **Frontend:** HTML, CSS, Bootstrap, Jinja2
* **Database:** SQLite (created programmatically)
* **Libraries (optional):**

  * Flask-Login (authentication)
  * Chart.js (visualizations)

## 👥 Roles & Features

### 🔑 Admin (Superuser)

* Pre-created (no registration required)
* Create, update, delete parking lots
* Define number of parking spots per lot
* View all parking spots (Available / Occupied)
* View registered users
* View analytics (charts)

### 👤 User

* Register & login
* View available parking lots
* Book parking spot (auto-allocation)
* Release/vacate parking spot
* View parking history & cost

## 🗂️ Database Design

### Tables:

#### 1. User

* id (PK)
* username
* password
* role (admin/user)

#### 2. ParkingLot

* id (PK)
* prime_location_name
* price
* address
* pin_code
* max_spots

#### 3. ParkingSpot

* id (PK)
* lot_id (FK)
* status (Available / Occupied)

#### 4. Reservation

* id (PK)
* spot_id (FK)
* user_id (FK)
* parking_timestamp
* leaving_timestamp
* cost


## ⚙️ Installation & Setup

```bash
# Clone the repository
git clone https://github.com/your-username/vehicle-parking-app.git

# Navigate to project folder
cd vehicle-parking-app

# Create virtual environment
python -m venv venv

# Activate environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

## ▶️ Usage

* Open browser and go to:

  ```
  http://127.0.0.1:5000
  ```

### Admin Login

```
Username: admin
Password: admin123
```

### User

* Register a new account and start booking parking

---

## 📊 Features Implemented

✔ Admin dashboard
✔ User authentication
✔ Parking lot management
✔ Auto parking spot allocation
✔ Parking history tracking
✔ Cost calculation
✔ Responsive UI (Bootstrap)

---

## 🌟 Optional Enhancements

* Search parking spots 🔍
* REST APIs (Flask-RESTful)
* Charts using Chart.js 📈
* Form validation

---

## 📁 Project Structure

```
vehicle-parking-app/
│
├── app.py
├── models.py
├── routes/
├── templates/
├── static/
├── instance/
├── requirements.txt
└── README.md
```

## 🤖 AI Usage

This project used AI tools (like ChatGPT) for:

* Code structuring guidance
* Debugging help
* README and documentation drafting

---

## 👨‍💻 Author

* **Basabdutta Konar**


