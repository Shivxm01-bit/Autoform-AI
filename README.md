# Google Form Autofill & Link Generator Service (CRC Edition with Supabase Auth & PostgreSQL)

A modern, high-performance web application featuring a **React 19 + Tailwind CSS** frontend and **FastAPI** backend, upgraded with **Corporate Resource Center (CRC)** student profile support, **Supabase Authentication** (Email/Password & Google OAuth), and a persistent **PostgreSQL `profiles` database** protected by **Row Level Security (RLS)** and **Supabase JWT verification**.

---

## 📁 Project Structure

```
google-form-filler/
├── main.py                      # FastAPI application entry point & route definitions
├── models/
│   ├── __init__.py
│   └── schemas.py               # Pydantic data schemas (CRC StudentProfile)
├── services/
│   ├── __init__.py
│   ├── auth_service.py          # Supabase JWT token verification dependency
│   ├── google_form_service.py   # Async Google Forms parser, CRC matcher & URL builder
│   └── gemini_mapper.py         # AI semantic mapping service
├── supabase/
│   └── schema.sql               # PostgreSQL CRC profiles table schema, RLS & triggers
├── supabase_schema.sql          # Root copy of Supabase schema
├── tests/
│   └── test_api.py              # Pytest test suite (auth, CRC matching, mocked scraper)
├── frontend/                    # React 19 + Vite + Tailwind CSS frontend
│   ├── src/
│   │   ├── components/
│   │   │   └── ProtectedRoute.jsx # Route protection guard
│   │   ├── constants/
│   │   │   └── crcOptions.js     # Standardized categorical dropdown options
│   │   ├── context/
│   │   │   ├── AuthContext.jsx   # Supabase Auth Provider
│   │   │   └── useAuth.js        # useAuth Hook
│   │   ├── lib/
│   │   │   └── supabaseClient.js # Supabase JS Client configuration
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx     # Login/Register UI (Email + Google OAuth)
│   │   │   └── DashboardPage.jsx # Protected CRC Dashboard with 3 collapsible sections
│   │   ├── App.jsx               # React Router configuration
│   │   ├── main.jsx
│   │   └── index.css
│   ├── .env                      # Frontend environment variables
│   └── package.json
├── .env                         # Backend environment variables
├── requirements.txt             # Python dependencies
└── README.md
```

---

## 📋 Corporate Resource Center (CRC) Profile Schema

The Master Profile is organized into three collapsible sections:

### 1. 👤 Personal Information & Contact
- `enrollment_no` (e.g. `2021BCSE042`)
- `full_name` (e.g. `Alex Mercer`)
- `dob` (Date of Birth)
- `gender` (`<select>`: `Male`, `Female`, `Other`, `Prefer not to say`)
- `home_location` (e.g. `Noida, Uttar Pradesh`)
- `permanent_address` (Full Residential Address)
- `contact_no` (Primary Mobile)
- `alt_contact_no` (Alternate Mobile / Guardian)
- `personal_email` (Personal Gmail/Email)
- `institutional_email` (College Email)
- `driving_license_yes_no` (`<select>`: `Yes`, `No`)

### 2. 🎓 Academic Record
- `school_name` (`<select>`: e.g. `School of Computer Science & Engineering`, `School of Engineering & Technology`, etc.)
- `category_ug_pg` (`<select>`: `UG`, `PG`, `Integrated`, `Diploma`, `PhD`)
- `course` (e.g. `B.Tech`)
- `ug_specialization` (e.g. `Computer Science & Engineering`)
- `ug_cgpa` (e.g. `8.92`)
- `ug_passing_year` (e.g. `2026`)
- `pg_specialization`, `pg_cgpa`, `pg_passing_year` (Optional for PG candidates)
- `tenth_percentage`, `tenth_board`, `tenth_passing_year`
- `twelfth_percentage`, `twelfth_board`, `twelfth_passing_year`

### 3. 💼 Professional Experience & Preferences
- `internship_organization` (e.g. `Amazon Web Services (AWS)`)
- `internship_topic` (e.g. `Distributed Cloud Microservices & Scalable Telemetry`)
- `extra_certifications` (Technical Certifications & Courses)
- `applying_for_role` (`<select>`: `Software Development Engineer (SDE)`, `Frontend Developer`, `Backend Developer`, `Data Analyst`, `Data Scientist`, etc.)

---

## 🛠️ Step-by-Step Setup Instructions

### Step 1: Database Setup in Supabase

1. Open your [Supabase Dashboard](https://app.supabase.com).
2. Go to the **SQL Editor** tab.
3. Run [`supabase/schema.sql`](file:///Users/shivampandey/.gemini/antigravity-ide/scratch/google-form-filler/supabase/schema.sql).

### Step 2: Environment Configuration

#### Backend `.env`:
```ini
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
LOG_LEVEL=info
GEMINI_API_KEY=your_gemini_api_key

# Supabase Settings (Project Settings -> API)
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_JWT_SECRET=your-supabase-jwt-secret
```

#### Frontend `frontend/.env`:
```ini
VITE_SUPABASE_URL=https://your-project-ref.supabase.co
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
VITE_API_BASE_URL=http://localhost:8000
```

---

## 🚀 Running the Application

### 1. Start the FastAPI Backend
```bash
cd /Users/shivampandey/.gemini/antigravity-ide/scratch/google-form-filler
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Start the React Frontend
```bash
cd /Users/shivampandey/.gemini/antigravity-ide/scratch/google-form-filler/frontend
npm run dev
```
- Login Page: [http://localhost:3000/login](http://localhost:3000/login)
- Dashboard: [http://localhost:3000/dashboard](http://localhost:3000/dashboard)

---

## 🧪 Running Backend Tests

```bash
.venv/bin/pytest tests/ -v
```
