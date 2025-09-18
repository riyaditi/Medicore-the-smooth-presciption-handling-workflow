Medicore: The Smooth Prescription Handling Workflow

## About The Project ✨
Medicore is a web-based platform designed to bridge the communication gap between customers needing prescriptions and their local pharmacists. Traditionally, customers have to physically visit a pharmacy to check for medicine availability, which can be time-consuming. This project provides a simple and efficient workflow where customers can submit their prescription list online, and pharmacists can provide real-time feedback on the availability of the medicines.
The core of the application is a dedicated chat and status update system for each prescription request, ensuring a clear and direct line of communication.

## Key Features
Dual User Roles: Separate, tailored dashboards and functionalities for Customers and Pharmacists.

Secure Authentication: A complete user registration, login, and session management system.

Prescription Submission: A simple interface for customers to submit their list of required medicines.

Real-Time Chat: A dedicated, live chat for each prescription request, allowing pharmacists to communicate directly with customers.

Pharmacist Queue: A dashboard for pharmacists that organizes all incoming "Pending" requests.

Live Status Updates: Pharmacists can update the request status to "Available" or "Unavailable," which is reflected in real-time for the customer.

Request Management: Customers have the option to delete their submitted requests.

## Built With 🧪
This project was built using a beginner-friendly yet powerful set of technologies.

Backend:
Python 3
Flask
Flask-SocketIO
Flask-SQLAlchemy
Flask-Login

Frontend:
HTML5
CSS3
JavaScript
Bootstrap 5

Database:
SQLite

## Project Structure 📂
Here is the final structure of the project files and folders:

medicore/
│
├── app.py              # Main Flask application file (backend logic)
├── requirements.txt    # List of Python packages to install
├── database.db         # SQLite database file (created automatically)
├── README.md           # This file
│
├── static/
│   ├── css/
│   │   └── style.css   # Custom CSS for styling
│   ├── js/
│   │   └── chat.js     # Frontend JavaScript for real-time chat
│   └── images/
│       ├── logo.png
│       └── background.jpg
│
└── templates/
    ├── layout.html             # Base template for all pages
    ├── home.html               # The project home page
    ├── login.html              # Login page
    ├── signup.html             # Signup page
    ├── customer_dashboard.html   # Customer's main page
    ├── pharmacist_dashboard.html # Pharmacist's main page
    ├── new_prescription.html   # Form for new prescriptions
    └── request_details.html    # Page for viewing a request and chatting
## Getting Started 🚀
To get a local copy up and running, follow these simple steps.

### Prerequisites
Make sure you have Python 3.8+ and pip installed on your system.

### Installation & Setup
Clone the repository
Bash
```
git clone https://github.com/your_username/medicore.git
```
Navigate to the project directory
Bash
```
cd medicore
Create and activate a virtual environment
```
On Windows:
Bash
```
python -m venv venv
.\venv\Scripts\activate
```
On macOS/Linux:
Bash
```
python3 -m venv venv
source venv/bin/activate
```
Install the required packages
Bash
```
pip install -r requirements.txt
```
## Usage
Run the application
Bash
```
python app.py
Open your web browser and go to http://127.0.0.1:5000.
```
To test the full workflow:
1. Register a 'Customer' account.
2. Register a 'Pharmacist' account.
3. Log in as the customer and submit a new prescription.
4. Log in as the pharmacist (preferably in a different browser or an incognito window) to see the pending request on your dashboard.
5. Click on the request to view details, update the status, and chat with the customer in real-time.
