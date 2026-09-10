# 🗂️ TaskFlow — Enterprise Team Task & Project Management System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5.4-646CFF.svg?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1.svg?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![Uptime Kuma](https://img.shields.io/badge/Monitoring-Uptime_Kuma-3BD671.svg?style=flat-square&logo=uptime-kuma&logoColor=white)](https://uptime.kuma.pet)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)

**TaskFlow** is a modern, full-stack, enterprise-ready project and task management platform engineered for teams that require strict governance, clean role delegation, organization multi-tenancy, and real-time operational visibility.

It pairs a high-performance **FastAPI** REST backend with a lightweight, responsive **React + Vite** single-page application (SPA), fully orchestratable locally via **Docker Compose** or deployable to cloud environments (Railway, AWS App Runner, or any VPS).

---

## 📑 Table of Contents

- [Architectural Overview](#-architectural-overview)
- [✨ What Makes TaskFlow Unique?](#-what-makes-taskflow-unique)
- [🛠️ Technology Stack](#️-technology-stack)
- [🚀 Quick Start: How to Deploy Locally](#-quick-start-how-to-deploy-locally)
  - [Method 1: One-Click Docker Compose (Recommended)](#method-1-one-click-docker-compose-recommended)
  - [Method 2: Standalone Local Development](#method-2-standalone-local-development)
- [👥 Pre-Seeded Demo Credentials](#-pre-seeded-demo-credentials)
- [📡 API & Interactive Documentation](#-api--interactive-documentation)
- [⚙️ Environment Variables Reference](#️-environment-variables-reference)
- [🧪 Testing & Quality Assurance](#-testing--quality-assurance)
- [📁 Project Structure](#-project-structure)
- [🚢 Production Deployment](#-production-deployment)

---

## 🏛️ Architectural Overview

TaskFlow separates presentation, business logic, persistence, and platform monitoring into loosely coupled, highly secure tiers:

```mermaid
graph TD
    Client[Web Browser / Client]
    
    subgraph Frontend Tier
        ViteSPA[React + Vite Single Page Application<br/>:5173 dev / :80 prod]
    end

    subgraph Backend Tier
        FastAPI[FastAPI REST API Service<br/>:8000]
        AuthModule[JWT Auth & RBAC Guard]
        Router[API Router /api/v1]
    end

    subgraph Persistence Tier
        DB[(PostgreSQL 16 / SQLite<br/>:5432)]
    end

    subgraph Observability Tier
        Kuma[Uptime Kuma Dashboard<br/>:3001]
    end

    Client -->|HTTP/REST| ViteSPA
    ViteSPA -->|REST + Bearer JWT| FastAPI
    FastAPI --> AuthModule
    AuthModule --> Router
    Router -->|SQLAlchemy 2.0 ORM| DB
    Kuma -.->|Health Polling /health| FastAPI
```

---

## ✨ What Makes TaskFlow Unique?

### 1. Dual-Tier Role-Based Access Control (RBAC)
Unlike simple task apps with binary permissions, TaskFlow enforces a granular **two-dimensional permission model**:
- **Platform Role (`GlobalRole`)**:
  - `Admin`: Full organizational control, project creation authority, member management, and task allocation rights.
  - `Member`: Collaborative workspace access scoped strictly to assigned projects.
- **Project-Level Role (`ProjectRole`)**:
  - `Owner`: Full project lifecycle control (edit, archive, manage members).
  - `Manager`: Project coordination, task creation, and deadline adjustments.
  - `Member`: Focused execution (status updates on personal work).

### 2. Tailored Dual-Persona Dashboards
Users don't get a one-size-fits-all screen:
- **Manager Dashboard (`/manager-dashboard`)**: Executive view displaying:
  - Total projects active under the manager's oversight.
  - Total tasks allocated by the manager vs. overdue metrics.
  - Interactive visual status breakdown bar (`Todo`, `In Progress`, `In Review`, `Done`, `Cancelled`).
  - Member task load tracker (identifies bottlenecks and overbooked teammates).
  - Live feed of all managed tasks with real-time status and assignee indicators.
- **Member Dashboard (`/member-dashboard`)**: Clean, distraction-free view showing only tasks assigned to the logged-in member, sorted by upcoming deadlines and priorities.

### 3. Organization-Scoped Multi-Tenancy
TaskFlow natively supports multiple organizations (`organization_name`).
- Employees only see and collaborate with teammates belonging to the same company.
- User search, autocomplete, and project invitation endpoints (`/users/organization` and `/users/search`) strictly filter out users from other companies, eliminating cross-tenant data leaks.

### 4. Strict Task Delegation & Integrity Guardrails
- **Assignment Governance**: Only Admins and project managers can assign tasks to employees, preventing team members from shifting tasks away without oversight.
- **Selective Field Updates**: Regular project members can exclusively update the **status** of their own assigned tasks, protecting critical details (deadlines, descriptions, priorities) from inadvertent alteration.

### 5. Multi-Company Enterprise Simulator & Seed Engines
TaskFlow comes equipped with two idempotent database seeding suites:
- **`seed.py`**: Standard seed populating key project roles (Admin, PM, Developer, QA) with realistic cloud migration tasks.
- **`seed_companies_data.py`**: Enterprise scenario generator populating **4 distinct companies** (Acme Corp, NovaTech Solutions, Stellar Dynamics, Apex Digital), **20 active users**, **12 active projects**, and **72+ structured tasks**.

### 6. Built-in Observability & Production Monitoring
- Containerized **Uptime Kuma** monitoring service pre-configured in `docker-compose.yml`.
- Standardized, zero-dependency `/health` endpoint returning version and service readiness.
- Production security headers middleware (`HSTS`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection`).

---

## 🛠️ Technology Stack

| Layer | Technology | Key Capabilities |
|---|---|---|
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12) | Asynchronous, auto-generating OpenAPI / Swagger docs, fast execution |
| **ORM & Database** | [SQLAlchemy 2.0](https://www.sqlalchemy.org/) + PostgreSQL 16 | Typed mappings, connection pooling, SQLite support for rapid local dev |
| **Authentication** | OAuth2 + JWT (Bearer Tokens) | Passlib (Bcrypt) password hashing, access tokens + long-lived refresh tokens |
| **Frontend Framework** | [React 18](https://react.dev/) + [Vite](https://vitejs.dev/) | React Router v6, custom lightweight CSS tokens (no heavy bulky UI libraries) |
| **Containerization** | Docker & Docker Compose | Multi-container stack (App, PostgreSQL 16, Uptime Kuma monitoring) |
| **Monitoring** | [Uptime Kuma](https://uptime.kuma.pet/) | Self-hosted uptime checks, alerting webhooks, response latency graphing |
| **Testing** | [Pytest](https://pytest.org/) + [Playwright](https://playwright.dev/) | Comprehensive API endpoint tests & End-to-End browser UI automation |

---

## 🚀 Quick Start: How to Deploy Locally

You can run TaskFlow locally either via **Docker Compose** (all-in-one stack) or as **individual standalone processes** for development.

### Method 1: One-Click Docker Compose (Recommended)

This launches the **PostgreSQL 16** database, the **FastAPI app**, and the **Uptime Kuma monitoring dashboard** in synchronized containers.

#### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/) installed on your machine.

#### Step 1: Start the services
From the project root directory, run:

```bash
docker compose up -d --build
```

#### Step 2: Access the running applications
Once the containers report healthy status:

| Service | URL | Description |
|---|---|---|
| **TaskFlow App** | `http://localhost:80` (or `http://localhost:8000`) | Full-stack application / API |
| **Interactive API Docs** | `http://localhost:80/docs` | Swagger UI documentation |
| **Monitoring Dashboard** | `http://localhost:3001` | Uptime Kuma monitoring dashboard |

#### Useful Docker commands:
```bash
# View live application logs
docker compose logs -f app

# Run the multi-company seed generator inside the container
docker compose exec app python seed_companies_data.py

# Stop all containers
docker compose down
```

---

### Method 2: Standalone Local Development

If you are developing backend or frontend features and want hot-reloading:

#### Prerequisites
- **Python 3.11+** installed
- **Node.js 18+** and **npm** installed

---

#### Step 1: Backend Setup

1. Open your terminal and navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   # On macOS / Linux:
   python3 -m venv venv
   source venv/bin/activate

   # On Windows (PowerShell):
   python -m venv venv
   venv\Scripts\Activate.ps1
   ```

3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the local environment file:
   ```bash
   # Copy the sample file
   cp .env.example .env
   ```
   *(By default, `.env` is configured to use local SQLite: `sqlite:///./task_manager.db`)*

5. Seed the database with initial demo data:
   ```bash
   # Standard seed (Sarah Connor Admin + Team)
   python seed.py

   # (Optional) Full multi-company enterprise scenario:
   python seed_companies_data.py
   ```

6. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
   - API will be accessible at: `http://127.0.0.1:8000`
   - Interactive Swagger docs: `http://127.0.0.1:8000/docs`
   - Service Health endpoint: `http://127.0.0.1:8000/health`

---

#### Step 2: Frontend Setup

1. In a new terminal window, navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install npm dependencies:
   ```bash
   npm install
   ```

3. Configure the local environment variable:
   ```bash
   # On Linux/macOS:
   echo "VITE_API_URL=http://localhost:8000" > .env.local

   # On Windows (PowerShell):
   Set-Content -Path .env.local -Value "VITE_API_URL=http://localhost:8000"
   ```

4. Start the Vite React development server:
   ```bash
   npm run dev
   ```

5. Open your browser at **`http://localhost:5173`**.

---

## 👥 Pre-Seeded Demo Credentials

The database comes ready with pre-configured accounts across various roles. You can log in immediately:

### Standard Seed Scenario (`seed.py`)
| Role | Email | Password | Organization | Description |
|---|---|---|---|---|
| **Admin / Manager** | `admin@taskflow.dev` | `Admin@123456` | TaskFlow Core | Sarah Connor (Full dashboard, project & member manager) |
| **Product Manager** | `alex.pm@taskflow.dev` | `User@123456` | TaskFlow Core | Alex Mercer (Manages tasks, tracks delivery) |
| **Member (Dev)** | `dev.jordan@taskflow.dev` | `User@123456` | TaskFlow Core | Jordan Lee (Fullstack developer, updates assigned tasks) |
| **Member (QA)** | `qa.elena@taskflow.dev` | `User@123456` | TaskFlow Core | Elena Rostova (QA tester, status updates) |

### Enterprise Multi-Company Scenario (`seed_companies_data.py`)
*All users in this dataset share the password:* `Test@Password123`

| Company | Manager (Admin Role) | Team Members (Member Role) |
|---|---|---|
| **Acme Corp** | `manager@acme.com` | `bob@acme.com`, `charlie@acme.com`, `david@acme.com`, `emma@acme.com` |
| **NovaTech Solutions** | `manager@novatech.com` | `fiona@novatech.com`, `george@novatech.com`, `hannah@novatech.com`, `ian@novatech.com` |
| **Stellar Dynamics** | `manager@stellar.com` | `julia@stellar.com`, `kevin@stellar.com`, `laura@stellar.com`, `mike@stellar.com` |
| **Apex Digital** | `manager@apexdigital.com` | `nora@apexdigital.com`, `oscar@apexdigital.com`, `paul@apexdigital.com`, `quinn@apexdigital.com` |

---

## 📡 API & Interactive Documentation

FastAPI auto-generates interactive API documentation conforming to OpenAPI 3.0:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Primary Endpoints Overview

#### 🔐 Authentication & Profile (`/api/v1/auth`)
- `POST /api/v1/auth/signup` — Register a new account with organization affiliation.
- `POST /api/v1/auth/login` — Exchange credentials for OAuth2 Access & Refresh JWT tokens.
- `POST /api/v1/auth/refresh` — Issue fresh access token using a valid refresh token.
- `GET /api/v1/auth/me` — Retrieve profile details of the authenticated caller.

#### 📁 Project Management (`/api/v1/projects`)
- `GET /api/v1/projects` — List projects associated with the current user.
- `POST /api/v1/projects` — Create a new project container *(Admin only)*.
- `GET /api/v1/projects/{id}` — Fetch detailed project view including tasks and members.
- `PATCH /api/v1/projects/{id}` — Update project properties *(Owner/Manager/Admin)*.
- `DELETE /api/v1/projects/{id}` — Soft delete or archive a project *(Owner/Admin)*.
- `POST /api/v1/projects/{id}/members` — Add an employee from the company to the project.
- `DELETE /api/v1/projects/{id}/members/{user_id}` — Remove a member from the project.

#### 📋 Task Management (`/api/v1/projects/{id}/tasks`)
- `GET /api/v1/projects/{id}/tasks` — Query tasks with filters: `status`, `assignee_id`, `overdue_only`.
- `POST /api/v1/projects/{id}/tasks` — Create a task with priority, status, and deadline *(Admin only)*.
- `PATCH /api/v1/projects/{id}/tasks/{tid}` — Update a task:
  - *Managers/Admins*: Update all fields including title, priority, assignee, due date.
  - *Members*: Update `status` of their own assigned tasks only.
- `DELETE /api/v1/projects/{id}/tasks/{tid}` — Delete a task *(Admin only)*.

#### 📊 Dashboard & Metrics (`/api/v1/dashboard`)
- `GET /api/v1/dashboard` — Aggregated workspace statistics (total projects, active tasks, overdue counts, task status distribution, member task load).

#### 🏢 Organization Directory (`/api/v1/users`)
- `GET /api/v1/users/organization` — List company peers available for assignment.
- `GET /api/v1/users/search` — Autocomplete search across colleagues within the organization.

#### 💓 Health Checks
- `GET /health` — Service readiness probe returning status and version.

---

## ⚙️ Environment Variables Reference

| Variable | Default (Dev) | Production Recommendation | Description |
|---|---|---|---|
| `APP_NAME` | `TaskFlow` | `TaskFlow` | Application title reported in metadata and headers |
| `APP_VERSION` | `1.0.0` | Semantic Version (`1.0.0`) | Running application release version |
| `DATABASE_URL` | `sqlite:///./task_manager.db` | `postgresql://user:pass@host:5432/dbname` | Database connection URI (Postgres required for prod) |
| `SECRET_KEY` | *(dev insecure string)* | `openssl rand -hex 32` | Secret key used to sign and verify HMAC-SHA256 JWT tokens |
| `ALGORITHM` | `HS256` | `HS256` | JWT signing cryptographic algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | `15` to `60` | Lifespan of short-lived access tokens |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | `7` to `30` | Lifespan of long-lived refresh tokens |
| `ALLOWED_ORIGINS` | `http://localhost:5173,...` | `https://your-domain.com` | Allowed CORS origins (comma-separated list) |
| `ENVIRONMENT` | `development` | `production` | Environment switch (controls Swagger exposure & seed guards) |
| `DEBUG` | `false` | `false` | Enables SQLAlchemy SQL echo logging |

---

## 🧪 Testing & Quality Assurance

TaskFlow includes a complete test suite covering backend logic and frontend user journeys:

### 1. Backend Unit & Endpoint Tests (Pytest)
Run the backend API test suite:
```bash
cd backend
pytest
```
*Tests verify authentication, RBAC constraints, organization isolation, and project workflows.*

### 2. End-to-End Automated Browser Tests (Playwright)
Run the automated end-to-end browser tests:
```bash
# Ensure both backend (:8000) and frontend (:5173) are running
python tests/playwright_full_suite.py
```
*Validates the full user journey: Login → Dashboard loading → Project navigation → Task creation → Role-dependent interactions.*

---

## 📁 Project Structure

```
TaskFlow/
├── docker-compose.yml           # Multi-container orchestration (App, PostgreSQL, Uptime Kuma)
├── Dockerfile                   # Production container definition
├── railway.toml                 # Cloud deployment configuration for Railway
├── README.md                    # Project documentation
│
├── backend/                     # FastAPI Backend Application
│   ├── app/
│   │   ├── main.py              # Application factory, lifespan, security headers & CORS
│   │   ├── api/v1/
│   │   │   ├── router.py        # Master API route registry
│   │   │   ├── deps.py          # Fast-injection dependencies (DB, JWT, RBAC guards)
│   │   │   └── endpoints/       # Domain route handlers
│   │   │       ├── auth.py      # Registration, login, token refresh, current user
│   │   │       ├── dashboard.py # Aggregated manager & member analytics
│   │   │       ├── projects.py  # Project CRUD & team member assignment
│   │   │       ├── tasks.py     # Task lifecycle, filters & status update guards
│   │   │       └── user.py      # Company employee directory & search
│   │   ├── core/
│   │   │   ├── config.py        # Pydantic v2 settings & environment parser
│   │   │   └── security.py      # Password hashing (Bcrypt) & JWT encode/decode
│   │   ├── db/
│   │   │   ├── session.py       # SQLAlchemy engine & session factory
│   │   │   └── migrations.py    # Automatic schema migration helpers
│   │   ├── models/
│   │   │   └── models.py        # SQLAlchemy ORM models (User, Project, Task, etc.)
│   │   └── schemas/
│   │       └── schemas.py       # Pydantic validation schemas & API contracts
│   ├── seed.py                  # Default team database seeder
│   ├── seed_companies_data.py   # Multi-company enterprise scenario seeder
│   ├── requirements.txt         # Python dependencies
│   └── tests/                   # Backend endpoint unit tests
│
├── frontend/                    # React + Vite Client Application
│   ├── src/
│   │   ├── api/client.js        # Axios/Fetch API client wrapper with token handling
│   │   ├── context/
│   │   │   └── AuthContext.jsx  # Authentication state, login/logout, session persistence
│   │   ├── components/          # Reusable UI elements (Badges, Modals, Forms, Layout)
│   │   └── pages/
│   │       ├── LoginPage.jsx            # User sign-in
│   │       ├── SignupPage.jsx           # Account creation with organization selection
│   │       ├── DashboardPage.jsx        # Manager analytics & workload overview
│   │       ├── MemberDashboardPage.jsx  # Focused member task view
│   │       ├── ProjectsPage.jsx         # Project catalog & creation modal
│   │       └── ProjectDetailPage.jsx    # Kanban-style task table & member roster
│   ├── index.html               # Web application entry point
│   ├── vite.config.js           # Vite build & proxy configuration
│   └── package.json             # NPM dependencies & scripts
│
└── tests/                       # Playwright End-to-End browser test suite
```

---

## 🚢 Production Deployment

### Option A: Cloud Deployment via Railway
1. Fork or push this repository to your GitHub account.
2. In [Railway](https://railway.app), click **New Project** → **Deploy from GitHub repo**.
3. Add a **PostgreSQL** database service in Railway.
4. Set your environment variables in Railway (`SECRET_KEY`, `ALLOWED_ORIGINS`, `ENVIRONMENT=production`).
5. Railway will automatically build the container and deploy your live app.

### Option B: Cloud VPS (Ubuntu / Debian / AWS EC2)
1. Clone the repository onto your server:
   ```bash
   git clone https://github.com/varshith0810/TaskFlow.git
   cd TaskFlow
   ```
2. Update your `.env` with a secure random `SECRET_KEY` and your domain name in `ALLOWED_ORIGINS`.
3. Start the application with Docker Compose:
   ```bash
   docker compose up -d --build
   ```
4. Configure a reverse proxy like Nginx or Caddy with SSL (Let's Encrypt) pointing to port `80`.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
