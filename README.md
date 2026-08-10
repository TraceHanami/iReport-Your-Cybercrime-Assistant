<div align="center">

<img src="https://img.shields.io/badge/iReport-Cybercrime%20Assistant-1565c0?style=for-the-badge&logo=shield&logoColor=white" alt="iReport"/>

# 🛡️ iReport — Cybercrime Reporting System

**An AI-powered, full-stack web application for reporting, tracking, and managing cybercrime cases.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Vercel](https://img.shields.io/badge/Deploy-Vercel-000000?style=flat-square&logo=vercel&logoColor=white)](https://vercel.com)
[![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=flat-square&logo=jsonwebtokens&logoColor=white)](https://jwt.io)
[![License](https://img.shields.io/badge/License-MIT-00c853?style=flat-square)](LICENSE)

<br/>

> Published in **IJSRET Journal** · DOI: [10.5281/zenodo.17500893](https://doi.org/10.5281/zenodo.17500893)
>
> 📰 [Read the Paper](https://ijsret.com/2025/11/01/ireport-a-cybercrime-assistant/)

<br/>

[🚀 Quick Start](#-quick-start) · [🌐 Deploy to Vercel](#-deploy-to-vercel) · [✨ Features](#-features) · [📡 API Reference](#-api-reference) · [🏗️ Architecture](#-architecture) · [🧪 Testing](#-testing)

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

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.8+ |
| pip | Latest |

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/TraceHanami/iReport-Your-Cybercrime-Assistant.git
cd iReport-Your-Cybercrime-Assistant

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
python backend/app.py
```

Open your browser at → `http://localhost:5000`

---

## 🌐 Deploy to Vercel

iReport comes pre-configured with `vercel.json` and a serverless Flask entry point (`api/index.py`) for seamless deployment on [Vercel](https://vercel.com).

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

### Option 1: Deploy via Vercel CLI (Quickest)

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Deploy directly:
   ```bash
   vercel --prod
   ```

### Option 2: Deploy via Vercel Dashboard

1. Push your repository to GitHub / GitLab / Bitbucket.
2. Go to [Vercel Dashboard](https://vercel.com/dashboard) and click **Add New Project**.
3. Import your repository.
4. Set Environment Variables under Project Settings:
   - `SECRET_KEY`: `your-production-secret-key`
   - `JWT_SECRET_KEY`: `your-jwt-secret-key`
   - `DATABASE_URL`: *(Optional)* PostgreSQL connection string (e.g. Neon, Supabase). If omitted, fallback SQLite storage is managed in `/tmp`.
5. Click **Deploy**. Vercel will automatically build and publish your application.

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
│  │  (HTML/JS)   │      │    (10 Blueprints)        │  │
│  └──────────────┘      └──────────┬───────────────┘  │
│                                   │                  │
│         ┌─────────────────────────┼──────────────┐   │
│         │                         │              │   │
│    ┌────▼────┐            ┌───────▼──────┐ ┌────▼──┐ │
│    │ SQLite /│            │ AI Classifier │ │  PDF  │ │
│    │Postgres │            │  (NLP Rules) │ │Engine │ │
│    └─────────┘            └──────────────┘ └───────┘ │
└──────────────────────────────────────────────────────┘
```

---

## 📄 License

Released under the **MIT License** — see [LICENSE](LICENSE) for details.

<div align="center">

**Built to make digital India safer. 🇮🇳**

</div>
