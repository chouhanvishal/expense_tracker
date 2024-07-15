# Expense Management Project

## Overview

This project is a Django-based application that manages user authentication, invitations, and friendships, along with an expense management module.

## Features

- User Registration
- User Login with JWT Authentication
- Sending and Accepting Friend Invitations
- Managing Friends List
- Expense Management

## Technologies Used

- Django
- Django REST Framework
- Django Simple JWT

## Setup Instructions

### Prerequisites

- Python 3.7+
- Django 3.0+
- Virtualenv (optional but recommended)


## Description

- **expense_tracker/**: Contains Django project settings and configurations.
- **expenses/**: Django app for managing expenses.
- **logs/**: Directory for storing log files (`expenses.log` and `users.log`).
- **user_management/**: Django app for user management and authentication.

## Usage

1. Ensure Python and Django are installed.
2. Set up a virtual environment.
3. Install dependencies listed in `requirement.txt`.
4. Run migrations using `python manage.py migrate`.
5. Start the development server with `python manage.py runserver`.

## Contributing

- Fork the repository.
- Create a new branch (`git checkout -b feature/your-feature`).
- Make your changes.
- Commit your changes (`git commit -am 'Add new feature'`).
- Push to the branch (`git push origin feature/your-feature`).
- Create a new Pull Request.
