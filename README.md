🚀 iReport - Intelligent Crime Reporting System

A comprehensive, AI-powered crime reporting and management system with multi-role access, real-time tracking, and advanced analytics.

📋 Project Overview

iReport is a full-stack web application that enables citizens to report crimes, track case progress, and interact with law enforcement through an intuitive interface. The system features AI-powered case classification, automated officer assignment, and comprehensive analytics for law enforcement agencies.

🎯 Features

🔐 Authentication & Security

❖Multi-role User System (Admin, Police, Volunteer, Public)

❖OTP-based Registration & Verification

❖JWT Token Authentication

❖Role-based Access Control

❖Secure Password Reset

📝 Complaint Management

❖User & Anonymous Complaint Filing

❖AI-Powered Case Classification

❖Automated Officer Assignment

❖Real-time Case Tracking

❖File Upload Support

👮‍♂️ Law Enforcement Features

❖Police Dashboard & Case Management

❖Officer Performance Analytics

❖Team Performance Tracking

❖Availability Management

❖Case Assignment & Reassignment

📊 Advanced Analytics

❖Trend Analysis & Predictive Insights

❖Geospatial Heatmaps

❖High-Risk Area Identification

❖Patrol Route Recommendations

❖Performance Metrics

🤖 AI & Automation

❖Smart Chatbot Assistant

❖AI Case Classification

❖Automated Officer Assignment

❖Priority-based Routing

❖Volunteer Matching

📱 Notifications & Communication

❖Real-time Notifications

❖SMS Integration (Fast2SMS)

❖Email Notifications

❖Chat System

📄 Reporting

❖Analytics Reports

❖Case Reports (PDF)

❖System Status Reports

❖Automated Report Generation

🏗️ System Architecture

Backend Structure

backend/

├── auth/                                  # Authentication & Authorization

├── complaints/                            # Complaint Management

├── police/                                # Police Features

├── admin/                                 # Admin Dashboard & Analytics

├── chatbot/                               # AI Chatbot

├── notifications/                         # Notification System

├── sms/                                   # SMS Services

├── reports/                               # Report Generation

└── utils/                                 # Utility Functions

Frontend Structure

frontend/

├── assets/

│   ├── css/                                # Stylesheets

│   └── js/                                 # JavaScript Modules

├── pages/                                  # Application Pages

└── chatbot/                                # Chatbot Interface

🚀 Installation & Setup

Prerequisites

➤Python 3.8+

➤Node.js 14+

➤SQLite Database

Backend Setup

bash

cd backend

# Create virtual environment

python -m venv venv

source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies

pip install -r requirements.txt

# Initialize database

python init_db.py

python seed_roles.py

python seed_data.py

# Start backend server

python app.py

Frontend Setup

bash

cd frontend

# Install dependencies

npm install

# Start development server

npm start

🔧 Configuration

Environment Variables

Create a .env file in the backend directory:

env

SECRET_KEY=your-secret-key

DATABASE_URL=sqlite:///ireport.db

SMS_API_KEY=your-fast2sms-api-key

EMAIL_HOST=smtp.gmail.com

EMAIL_PORT=587

EMAIL_USER=your-email@gmail.com

EMAIL_PASS=your-app-password

API Configuration

Update frontend/assets/js/config.js with your backend URL:

javascript

const API_BASE_URL = 'http://localhost:5000/api';

📊 API Endpoints

Authentication

➤POST /api/auth/register - User registration

➤POST /api/auth/login - User login

➤GET /api/auth/me - Get current user

➤POST /api/auth/verify-otp - OTP verification

Complaints

➤POST /api/complaints/file - File complaint

➤POST /api/complaints/file-anonymous - File anonymous complaint

➤GET /api/complaints/my-complaints - Get user complaints

Tracking

➤GET /api/track/status/{case_id} - Track case status

➤GET /api/track/details/{case_id} - Get case details

Admin

➤GET /api/admin/dashboard - Admin dashboard

➤GET /api/admin/cases - All cases

➤GET /api/admin/users - All users

➤POST /api/admin/assign-case - Assign case to officer

Police

➤GET /api/police/dashboard - Police dashboard

➤GET /api/police/cases - Police cases

➤PUT /api/police/availability - Update availability

Analytics

➤GET /api/analytics/trends - Trend analysis

➤GET /api/analytics/heatmap - Geospatial heatmap

➤GET /api/analytics/predictive-insights - Predictive analytics

👥 User Roles

🎯 Public User

✦Register and file complaints

✦Track case progress

✦Use chatbot assistance

✦File anonymous reports

🛡️ Police Officer

✦Manage assigned cases

✦Update case status

✦View performance metrics

✦Set availability status

🤝 Volunteer

✦Handle low-priority cases

✦Community engagement

✦Support law enforcement

👑 Administrator

✦System management

✦User management

✦Analytics and reporting

✦Case assignment oversight

🤖 AI Features

Case Classification

✦Rule-based classification for crime type detection

✦Priority assignment based on severity

✦Automated routing to appropriate personnel

Smart Assignment

✦Officer matching based on location, workload, and expertise

✦Volunteer assignment for low-priority cases

✦Fallback mechanisms for unassignable cases

Chatbot Assistant

✦Natural language processing

✦Session management

✦Context-aware responses

📱 Frontend Pages

Core Pages

◆index.html - Landing page

◆login.html - User authentication

◆register.html - User registration

◆dashboard.html - User dashboard

Complaint Management

◆file-complaint.html - File new complaint

◆my-complaints.html - View user complaints

◆track.html - Case tracking

◆view.html - Case details

Role-specific Pages

◆admin-dashboard.html - Admin interface

◆police.html - Police dashboard

◆volunteer.html - Volunteer interface

Additional Features

◆awareness.html - Crime awareness

◆learning.html - Educational content

◆puzzle.html - Interactive elements

🧪 Testing

Run comprehensive backend tests:

bash

cd backend/tests

python test_backend.py

Test Coverage
✅ Health Endpoints

✅ Authentication

✅ Complaint Management

✅ Case Tracking

✅ Admin Features

✅ Police Features

✅ Analytics

✅ Notifications

✅ Chatbot

✅ SMS Services

✅ Reports

✅ Security

✅ Performance


🔒 Security Features

▼Input validation and sanitization

▼SQL injection prevention

▼XSS protection

▼CSRF protection

▼Secure file upload

▼Session management

▼Role-based access control

📈 Performance

▼Response Time: ~2.02s per request (average)

▼Concurrent Users: Support for multiple roles

▼Database Optimization: Efficient queries and indexing

▼File Handling: Secure upload and storage

🚨 Emergency Features

▼Anonymous reporting for sensitive cases

▼Priority escalation for urgent matters

▼Real-time notifications for law enforcement

▼SMS alerts for critical updates

🔮 Future Enhancements

✱Mobile application

✱Voice-based reporting

✱Advanced ML models

✱Multi-language support

✱Integration with government databases

✱Blockchain for evidence tracking

✱IoT device integration

🤝 Contributing

➲Fork the repository

➲Create a feature branch

➲Commit your changes

➲Push to the branch

➲Create a Pull Request

📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

🆘 Support

➲For technical support or questions:

➲Check the documentation

➲Open an issue on GitHub

➲Contact the development team

🚀 Built with modern web technologies to make communities safer through technology.

DOI number : 10.5281/zenodo.17500893

Journal name : IJSRET
https://ijsret.com/2025/11/01/ireport-a-cybercrime-assistant/
