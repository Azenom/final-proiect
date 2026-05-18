# Inventory Management System

## Project Description

This project is a web-based Inventory Management System developed with Flask and SQLite. The application allows users to manage company assets, employees, and asset assignments through a clean CRUD interface.

The system supports:

* Employee management
* Asset management
* Asset assignment and return tracking
* CSV import for employees and assets
* Duplicate prevention and validation
* Assignment history tracking
* Asset status management
* Sorting and filtering of records

The application was designed using a layered architecture:


routes -> services -> models
```

This structure improves code organization, maintainability, and scalability.

---

# Technologies Used

## Backend

* Python 3
* Flask
* SQLite3

## Frontend

* HTML5
* CSS3
* Jinja2 Templates

## Other Technologies

* CSV file processing with Python `csv`
* SQLite foreign key relations
* Flash messaging with Flask

---

# Project Structure


final-proiect/
│
├── app.py
├── data/
│   └── inventory.db
├── models/
│   ├── asset.py
│   └── employee.py
├── routes/
│   ├── assets.py
│   ├── employees.py
│   └── assignments.py
├── services/
│   ├── add_assets.py
│   ├── add_employees.py
│   └── assignments.py
├── templates/
├── static/
└── requirements.txt
```

---

# How to Use

## 1. Start the application

Run the following command:

```bash
python app.py
```

After starting the server, open your browser and access:


http://127.0.0.1:5000
```

---

## 2. Asset Management

Users can:

* Add new assets
* Edit existing assets
* Delete assets
* Import assets from CSV
* View asset assignment history
* Sort assets by category, brand, or status

Each asset contains:

* Category
* Brand
* Serial number
* Purchase date
* Status

---

## 3. Employee Management

Users can:

* Add employees
* Edit employee data
* Delete employees
* Import employees from CSV
* Sort employees by name or department

Each employee contains:

* First name
* Last name
* Department

---

## 4. Assignment Management

Users can:

* Assign assets to employees
* Return assigned assets
* View active assignments
* View assignment history

Asset statuses are automatically updated:

* Available
* Assigned
* Service

---

# CSV Import Format

## Employees CSV

Required header:

```csv
first_name,last_name,department
```

Example:

```csv
first_name,last_name,department
John,Doe,IT
Anna,Smith,HR
```

---

## Assets CSV

Required header:

```csv
category,brand,serial_number,purchase_date
```

Example:

```csv
category,brand,serial_number,purchase_date
Laptop,Dell,ABC123,2025-01-10
Monitor,LG,XYZ456,2024-08-15
```

---

# Dependencies

## Required Python Packages

Install dependencies with:

```bash
pip install flask
```

Optional:

```bash
pip install -r requirements.txt
```

---

# Installation Guide

## 1. Clone the repository

```bash
git clone <repository-url>
```

## 2. Navigate into the project folder

```bash
cd final-proiect
```

## 3. Create a virtual environment (recommended)

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

---

## 4. Install dependencies

```bash
pip install flask
```

---

## 5. Run the application

```bash
python app.py
```

---

# Database

The project uses SQLite.

Database file:


data/inventory.db
```

The application uses:

* Foreign keys
* Relational tables
* Assignment history tracking
* Duplicate prevention

---

# Validation Features

The application includes:

* Duplicate employee prevention
* Duplicate serial number prevention
* CSV header validation
* Invalid row detection
* Date validation
* Required field validation

---

# Future Improvements

Possible future improvements:

* Authentication system
* Search functionality
* Pagination
* Export to CSV/PDF
* Logging system
* REST API
* Docker support

---

# Author

Developed as a Flask inventory management project for learning and practice purposes.
