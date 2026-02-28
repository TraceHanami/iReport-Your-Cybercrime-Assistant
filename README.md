<div align="center">

<img src="https://img.shields.io/badge/iReport-Cybercrime%20Assistant-1565c0?style=for-the-badge&logo=shield&logoColor=white" alt="iReport"/>

# 🛡️ iReport — Cybercrime Reporting System

**An AI-powered, full-stack web application for reporting, tracking, and managing cybercrime cases.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://sqlite.org)
[![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=flat-square&logo=jsonwebtokens&logoColor=white)](https://jwt.io)
[![License](https://img.shields.io/badge/License-MIT-00c853?style=flat-square)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-35%2F36%20passing-00c853?style=flat-square)](#-testing)

<br/>

> Published in **IJSRET Journal** · DOI: [10.5281/zenodo.17500893](https://doi.org/10.5281/zenodo.17500893)
>
> 📰 [Read the Paper](https://ijsret.com/2025/11/01/ireport-a-cybercrime-assistant/)

<br/>

[🚀 Quick Start](#-quick-start) · [✨ Features](#-features) · [📡 API Reference](#-api-reference) · [🏗️ Architecture](#-architecture) · [🧪 Testing](#-testing)

</div>

---

## 📋 Overview

iReport is a comprehensive cybercrime reporting and case management platform built to bridge the gap between citizens and law enforcement agencies. The system leverages AI for intelligent case classification and routing, while providing role-based dashboards for every stakeholder — from the victim filing a complaint to the administrator overseeing the entire operation.

### Why iReport?

| Challenge | iReport Solution |
|-----------|-----------------|
| Citizens don't know where to report cybercrime | Single unified portal with guided filing |
| Cases are misrouted or delayed | AI auto-classifies and assigns to the best-fit officer |
| Victims have no visibility into case progress | Real-time case tracking by Case ID (no login required) |
| Law enforcement lacks pattern insights | Analytics dashboards with heatmaps and trend analysis |
| Anonymous victims fear retaliation | Full anonymous complaint filing with no identity stored |

---

## ✨ Features

### 🔐 Authentication & Security
- Multi-role user system (Admin · Police · Volunteer · Public)
- OTP-based email verification on registration
- JWT token authentication with configurable expiry
- Role-based access control on every endpoint
- Secure password hashing

### 📝 Complaint Management
- Registered and anonymous complaint filing
- AI-powered crime type detection from natural language
- Priority auto-assignment (Critical / High / Medium / Low)
- Automated officer routing based on workload and availability
- Complete case timeline with full audit trail

### 👮 Law Enforcement Tools
- Officer dashboard with prioritized case queue
- Real-time case status updates with investigation notes
- Availability management (Available / Busy / Off Duty)
- Personal performance metrics and monthly reports

### 📊 Analytics & Intelligence
- Monthly case trend bar charts
- Crime type distribution with resolution rates
- Geographic hotspot heatmaps by city
- AI predictive insights and officer workload analysis

### 🤖 AI & Automation
- Rule-based NLP classifier covering 10+ cybercrime categories
- Smart officer assignment (lowest workload, available first)
- Conversational chatbot with crime-specific guidance
- Live case lookup within the chatbot interface

### 📄 Reporting
- Downloadable PDF case reports (ReportLab)
- PDF analytics reports for administrators
- In-browser case timeline visualization

### 🔔 Notifications
- Per-user notification system with type tagging
- Automatic alerts on case assignment and status changes
- Unread badge counts and mark-all-read support

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.8+ |
| pip | Latest |

> **No Node.js required.** The frontend is pure HTML/CSS/JS served directly by Flask.

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/TraceHanami/iReport-Your-Cybercrime-Assistant.git
cd iReport-Your-Cybercrime-Assistant

# 2. Install Python dependencies
pip install flask PyJWT reportlab python-dotenv

# 3. Initialize the database and seed demo data
cd backend
python init_db.py
python seed_data.py

# 4. Start the server
python app.py
```

Open your browser at → **[http://localhost:5000](http://localhost:5000)**

### One-Line Start (after first setup)

```bash
./start.sh            # Auto-initializes DB on first run
./start.sh --test     # Run the test suite before starting
```

---

## 🔑 Demo Credentials

| Role | Email | Password | Goes to |
|------|-------|----------|---------|
| 👑 Admin | `admin@ireport.gov` | `Admin@123` | Admin Dashboard |
| 👮 Officer | `officer@ireport.gov` | `Police@123` | Police Dashboard |
| 🤝 Volunteer | `volunteer@ireport.gov` | `Volunteer@123` | Volunteer Dashboard |
| 👤 Public | `user@ireport.gov` | `User@123` | User Dashboard |

---

## 🏗️ Architecture

### System Design

```
┌──────────────────────────────────────────────────────┐
│                      iReport                         │
│                                                      │
│  ┌──────────────┐      ┌──────────────────────────┐  │
│  │   Frontend   │ ←──→ │     Flask REST API        │  │
│  │  (HTML/JS)   │      │    (9 Blueprints)         │  │
│  └──────────────┘      └──────────┬───────────────┘  │
│                                   │                  │
│         ┌─────────────────────────┼──────────────┐   │
│         │                         │              │   │
│    ┌────▼────┐            ┌───────▼──────┐ ┌────▼──┐ │
│    │ SQLite  │            │ AI Classifier │ │  PDF  │ │
│    │   DB    │            │  (NLP Rules) │ │Engine │ │
│    └─────────┘            └──────────────┘ └───────┘ │
└──────────────────────────────────────────────────────┘
```

### Backend Structure

```
backend/
├── app.py                      ← Flask app, CORS, blueprint registration
├── init_db.py                  ← Schema definition & DB initialization
├── seed_data.py                ← Demo users, roles, and sample cases
│
├── auth/
│   └── routes.py               ← Register, login, OTP, JWT, profile
│
├── complaints/
│   ├── routes.py               ← File complaint, anonymous filing, list
│   └── track.py                ← Public case status & timeline lookup
│
├── police/
│   ├── routes.py               ← Officer dashboard, case updates, availability
│   └── volunteer_routes.py     ← Volunteer-specific endpoints
│
├── admin/
│   └── routes.py               ← Admin dashboard, case assignment, analytics
│
├── chatbot/
│   └── routes.py               ← Session management, NLP response engine
│
├── notifications/
│   └── routes.py               ← Per-user notification CRUD
│
├── reports/
│   └── routes.py               ← PDF generation (case + analytics)
│
├── utils/
│   ├── auth_utils.py           ← JWT encode/decode, decorators, OTP
│   ├── classifier.py           ← AI crime classifier & auto-assignment
│   └── db.py                   ← SQLite connection helper
│
└── tests/
    └── test_backend.py         ← 36-test integration suite
```

### Frontend Structure

```
frontend/
├── index.html                  ← Public landing page
├── assets/
│   └── js/app.js               ← Shared: API client, Auth, UI helpers, Nav
│
└── pages/
    ├── login.html              ← Authentication
    ├── register.html           ← OTP-based registration
    ├── dashboard.html          ← Public user home
    ├── file-complaint.html     ← Filing form (registered + anonymous)
    ├── my-complaints.html      ← Paginated complaint history
    ├── track.html              ← Public case tracker (no login)
    ├── admin-dashboard.html    ← Admin overview + charts
    ├── admin-cases.html        ← Case management + assignment modal
    ├── police-dashboard.html   ← Officer case queue + update modal
    ├── volunteer-dashboard.html← Volunteer interface
    ├── analytics.html          ← Trends, heatmap, AI insights
    ├── awareness.html          ← Cyber safety guide (10 crime types)
    └── chatbot.html            ← AI chatbot interface
```

### Database Schema

```sql
roles            → id, name, description
users            → id, full_name, email, phone, password_hash, role_id,
                   is_verified, otp, otp_expires_at, availability,
                   badge_number, department, is_active, created_at
cases            → id, case_id, title, description, crime_type, priority,
                   status, reporter_id, assigned_officer_id,
                   assigned_volunteer_id, location, is_anonymous,
                   contact_info, created_at, updated_at, resolved_at
case_updates     → id, case_id, updated_by, status, note, created_at
notifications    → id, user_id, title, message, type, is_read, case_id
chatbot_sessions → id, session_id, user_id, context, created_at
chatbot_messages → id, session_id, role, content, created_at
```

---

## 📡 API Reference

> All authenticated endpoints require: `Authorization: Bearer <token>`

### Auth

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `POST` | `/api/auth/register` | ❌ | Register new user (returns OTP in demo mode) |
| `POST` | `/api/auth/login` | ❌ | Login → returns JWT token + user object |
| `GET` | `/api/auth/me` | ✅ | Get current user profile |
| `POST` | `/api/auth/verify-otp` | ❌ | Verify email OTP |
| `POST` | `/api/auth/resend-otp` | ❌ | Resend OTP to email |
| `POST` | `/api/auth/change-password` | ✅ | Change account password |

### Complaints

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `POST` | `/api/complaints/file` | ✅ | File authenticated complaint |
| `POST` | `/api/complaints/file-anonymous` | ❌ | File anonymous complaint |
| `GET` | `/api/complaints/my-complaints` | ✅ | Paginated complaint list (`?page=1&per_page=10`) |
| `GET` | `/api/complaints/<case_id>` | ✅ | Full complaint details + timeline |

### Tracking (Public — No Login Required)

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `GET` | `/api/track/status/<case_id>` | ❌ | Quick status + priority lookup |
| `GET` | `/api/track/details/<case_id>` | ❌ | Full case details + timeline |

### Police

| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| `GET` | `/api/police/dashboard` | Police | Stats, recent cases, and profile |
| `GET` | `/api/police/cases` | Police/Admin | Case queue with status filter |
| `PUT` | `/api/police/cases/<case_id>/update` | Police/Admin | Update status + add note |
| `PUT` | `/api/police/availability` | Police/Volunteer | Set availability status |
| `GET` | `/api/police/performance` | Police/Admin | Monthly performance metrics |

### Admin

| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| `GET` | `/api/admin/dashboard` | Admin | System-wide stats + officer performance |
| `GET` | `/api/admin/cases` | Admin | All cases (search, filter, paginate) |
| `GET` | `/api/admin/users` | Admin | All users with case counts |
| `POST` | `/api/admin/assign-case` | Admin | Assign case to officer |
| `PUT` | `/api/admin/users/<id>/toggle` | Admin | Activate / deactivate user |

### Analytics

| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| `GET` | `/api/admin/analytics/trends` | Admin/Police | Monthly trends + crime distribution |
| `GET` | `/api/admin/analytics/heatmap` | Admin/Police | Top locations by case count |
| `GET` | `/api/admin/analytics/predictive-insights` | Admin/Police | AI insights + workload |

### Chatbot

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `POST` | `/api/chatbot/start` | ❌ | Start a new chat session |
| `POST` | `/api/chatbot/message` | ❌ | Send message, receive NLP-guided response |
| `GET` | `/api/chatbot/history/<session_id>` | ❌ | Full chat history |

### Reports

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| `GET` | `/api/reports/case/<case_id>` | ✅ | Download case PDF report |
| `GET` | `/api/reports/analytics` | Admin | Download system analytics PDF |

---

## 👥 User Roles

### 👤 Public Citizen
- Register an account or file anonymously
- Describe cybercrime incidents with evidence details
- Track any case by Case ID — no login required
- Receive real-time notifications on case updates
- Chat with the AI assistant 24/7
- Download official PDF case reports

### 👮 Police Officer
- View assigned case queue sorted by priority
- Update case status and record investigation notes
- Toggle availability (Available / Busy / Off Duty)
- Review monthly personal performance statistics
- Access system analytics and geographic heatmaps

### 🤝 Volunteer
- Handle low-priority community cases
- Update case notes and progress
- Manage personal availability

### 👑 Administrator
- Full system oversight and user management
- Manually assign or reassign cases to officers
- Activate or deactivate any user account
- Export PDF analytics reports
- View AI-generated predictive insights

---

## 🤖 AI System

### Crime Type Classifier

The NLP classifier matches complaint text against a curated keyword lexicon:

| Crime Type | Trigger Keywords |
|------------|-----------------|
| `phishing` | fake email, fake link, credential, spoofed, impersonat |
| `ransomware` | encrypt, files locked, ransom, bitcoin demand, decrypt |
| `fraud` | UPI, bank fraud, cheated, money lost, scam |
| `hacking` | unauthorized access, brute force, account breached |
| `identity_theft` | stolen ID, Aadhaar misuse, fake profile, PAN card |
| `cyberbullying` | harass, threaten, troll, stalk, abuse online |
| `data_breach` | data leak, exposed database, personal data |
| `online_scam` | fake website, lottery, advance fee, Nigerian |
| `cyberstalking` | track location, surveillance, monitoring |
| `child_exploitation` | minor, grooming, CSAM |

### Priority Assignment

| Priority | Triggers |
|----------|----------|
| 🔴 **Critical** | Ransomware, child exploitation, immediate threats |
| 🟠 **High** | Large financial loss (lakh/crore), corporate breach, hacking |
| 🟡 **Medium** | Phishing, general fraud, online scam |
| 🟢 **Low** | Minor incidents, awareness queries |

### Smart Assignment Logic

```
if priority in (critical, high) OR crime_type in (ransomware, hacking, data_breach):
    → Assign to police officer with fewest active cases
elif priority == low:
    → Assign to available volunteer with fewest active cases
else:
    → Assign to any available police officer
fallback:
    → Assign to any active police/volunteer user
```

---

## 🧪 Testing

```bash
cd backend
python tests/test_backend.py
```

### Coverage

| Category | Tests | Status |
|----------|:-----:|:------:|
| Health & Info endpoints | 2 | ✅ |
| Authentication (login, register, OTP, JWT) | 6 | ✅ |
| Complaint filing (auth + anonymous) | 3 | ✅ |
| Case tracking (public endpoints) | 3 | ✅ |
| Police features (dashboard, cases, availability) | 3 | ✅ |
| Admin features (dashboard, cases, users, assign) | 5 | ✅ |
| Analytics (trends, heatmap, predictive) | 3 | ✅ |
| Chatbot (session, message, crime topics, track) | 4 | ✅ |
| Notifications | 1 | ✅ |
| PDF report generation (case + analytics) | 2 | ✅ |
| Security & RBAC | 3 | ✅ |
| **Total** | **35 / 36** | ✅ |

---

## 🔒 Security

| Measure | Implementation |
|---------|---------------|
| Authentication | JWT tokens, configurable expiry |
| Authorization | Role decorator on every protected endpoint |
| Password Storage | SHA-256 hashing (upgrade to bcrypt for production) |
| OTP Expiry | 10-minute time limit on verification codes |
| SQL Injection | Parameterized queries throughout |
| CORS | Manual middleware (no third-party dependency) |
| Anonymous Cases | Reporter identity never stored or linked |
| Input Validation | Server-side validation on all form endpoints |

---

## ⚙️ Configuration

Create a `.env` file in the `backend/` directory:

```env
# Required
SECRET_KEY=your-long-random-secret-key-change-this

# Optional: Email OTP delivery
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password

# Optional: SMS OTP delivery (Fast2SMS)
SMS_API_KEY=your-fast2sms-api-key
```

> In demo mode, OTPs are returned directly in the API response. Connect an SMTP or SMS provider to enable real delivery in production.

---

## 🚨 Emergency Contacts (India)

| Service | Number |
|---------|--------|
| 🔵 National Cyber Helpline | **1930** (24/7) |
| 🔴 Police | **100** |
| 🟣 Women Helpline | **1091** |
| 🌐 Online Portal | **cybercrime.gov.in** |

---

## 🔮 Roadmap

- [ ] Mobile application (React Native)
- [ ] Voice-based complaint filing
- [ ] Transformer-based ML classifier
- [ ] Multi-language support (Hindi, Tamil, Bengali…)
- [ ] Integration with government CCTNS database
- [ ] Blockchain-based evidence integrity
- [ ] Real-time WebSocket notifications
- [ ] Production email/SMS OTP delivery
- [ ] TOTP two-factor authentication
- [ ] Docker + docker-compose deployment

---

## 🤝 Contributing

```bash
# 1. Fork the repository and clone locally
git checkout -b feature/your-feature-name

# 2. Make your changes, then run tests
cd backend && python tests/test_backend.py

# 3. Commit with a descriptive message
git commit -m "feat: add voice-based reporting module"

# 4. Push and open a Pull Request
git push origin feature/your-feature-name
```

---

## 📄 License

Released under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## 📚 Citation

If you use iReport in academic work, please cite:

```bibtex
@article{ireport2025,
  title   = {iReport: A Cybercrime Assistant},
  journal = {IJSRET},
  year    = {2025},
  doi     = {10.5281/zenodo.17500893},
  url     = {https://ijsret.com/2025/11/01/ireport-a-cybercrime-assistant/}
}
```

---

<div align="center">

**Built to make digital India safer. 🇮🇳**

<br/>

⭐ Star this repo if you found it useful!

</div>
