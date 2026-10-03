Digital Wallet Management System

A web-based Digital Wallet Management System developed as an MCA mini project. The system allows users to securely manage their wallet, add money, transfer money to other registered users, and manage their profile.

Technologies Used

* Python
* Flask
* HTML
* CSS
* JavaScript
* MySQL

Features

* User registration
* User login and logout
* Digital wallet creation
* Add money to wallet
* Transfer money to another user
* Balance management
* Transaction history
* User profile management
* Input validation and error handling
* Secure session-based authentication

System Modules

1. User Registration

New users can create an account by providing the required details. A wallet is automatically created for the registered user.

2. User Login

Registered users can log in using their credentials and access their wallet dashboard.

3. Wallet Management

Users can view their current wallet balance and add money to their wallet.

4. Money Transfer

Users can transfer money to another registered user using the recipient's email address.

5. Transaction Management

The system records wallet transactions such as adding money and transferring money.

6. Profile Management

Users can view and update their profile information.

Database

The project uses MySQL as the database.

Main tables:

* users — stores user information
* wallet — stores wallet and balance information
* transactions — stores transaction details

 Project Structure


Digital-Wallet-Management-System/
│
├── app.py
├── db.py
├── requirements.txt
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── add_money.html
│   ├── transfer.html
│   └── profile.html
│
└── static/
    └── style.css


Installation

1. Clone the repository

git clone <repository-url>

2. Open the project folder

Open the project in PyCharm or another Python IDE.

3. Install required packages

pip install -r requirements.txt

4. Configure MySQL

Create the required MySQL database and tables before running the application.

Update the database connection settings in `database.py` according to your local MySQL configuration.

5. Run the application

python app.py

Open the application in your browser using the local Flask address shown in the terminal.

Project Purpose

The main purpose of this project is to demonstrate the development of a database-driven web application using Flask and MySQL, while implementing basic digital wallet operations such as balance management and money transfer.

Academic Project

Project: Digital Wallet Management System
Course: Master of Computer Applications (MCA)
Academic Year: 2025–2027
