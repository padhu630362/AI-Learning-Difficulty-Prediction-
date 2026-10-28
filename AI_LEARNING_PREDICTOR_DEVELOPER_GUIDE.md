# AI Learning Difficulty Predictor — Full-Stack Developer Guide & Architecture Manual

> **Project Name:** AI Learning Difficulty Predictor  
> **Project Path:** `C:\Users\LENOVO\Desktop\AI Learning Difficulty predictor`  
> **Primary Tech Stack:** Python 3.10 Flask REST API, SQLAlchemy, Scikit-learn, React 18, Vite 5, Tailwind CSS, Recharts, Lucide React  
> **Target Audience:** Developers, software architects, machine learning engineers, and maintainers  

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Complete Folder Structure](#2-complete-folder-structure)
3. [Frontend Architecture & Component Guide](#3-frontend-architecture--component-guide)
4. [Backend Architecture & API Catalog](#4-backend-architecture--api-catalog)
5. [Database Architecture & Data Management](#5-database-architecture--data-management)
6. [Machine Learning Pipeline & Inference Engine](#6-machine-learning-pipeline--inference-engine)
7. [Feature-to-File Master Mapping Table](#7-feature-to-file-master-mapping-table)
8. [Authentication, Role Permissions & Access Control](#8-authentication-role-permissions--access-control)
9. [Running, Debugging & Maintenance](#9-running-debugging--maintenance)
10. [Step-by-Step Developer Modification Tutorials](#10-step-by-step-developer-modification-tutorials)
11. [Testing, Quality Assurance & Deployment](#11-testing-quality-assurance--deployment)
12. [Final Developer Reference, Breakage Map & Glossary](#12-final-developer-reference-breakage-map--glossary)

---

## 1. Project Overview

### 1.1 What the Application Does in Simple English
The **AI Learning Difficulty Predictor** is an educational analytics web application designed to identify topics and subjects where individual students are struggling or at risk of failing.

Instead of guessing or presenting arbitrary random numbers, the platform uses a genuine, trained **Machine Learning (ML)** model. The model analyzes historical academic performance (quizzes, assignments, and exams), study habits (weekly study hours, attempts needed to complete work, repeated conceptual errors), prerequisite knowledge, and curriculum difficulty.

When a student or instructor requests a difficulty evaluation for a topic:
1. The system collects the student's real assessment records. If the student has zero assessment records for that topic/subject, it returns an informative error (`insufficient_data`) asking them to complete an assessment first.
2. The ML model evaluates the student's learning metrics and predicts a difficulty classification: **`Low`**, **`Moderate`**, or **`High`** difficulty risk, along with a continuous severity score ($0.0$ to $1.0$) and calibrated class probabilities.
3. The platform displays explainable contributing indicators (e.g., low quiz performance, high repeated errors, low self-study duration) so the user understands *why* that prediction was made.
4. An automated recommendation engine generates targeted, pedagogical study actions (e.g., reviewing prerequisite video lectures, practicing vector decomposition problems).
5. Instructors are automatically alerted to students with declining scores, repeated failures, or high predicted difficulty so they can intervene early with 1-on-1 tutoring or supplemental assignments.

---

### 1.2 The Complete User Journey

```mermaid
flowchart TD
    subgraph Student Journey
        S1[Log in as Student] --> S2[Student Dashboard: Overview & Recent Predictions]
        S2 --> S3[Curriculum & Topics: Select Topic]
        S3 --> S4{Has Assessment Data?}
        S4 -- No --> S4A[Informative Toast & 422 Message: Complete assessment first]
        S4 -- Yes --> S5[Run AI Prediction: ML Inference]
        S5 --> S6[View Difficulty Score, Probabilities & Explainable Factors]
        S6 --> S7[Receive Actionable Study Recommendations]
        S7 --> S8[Complete Study Tasks -> Track Longitudinal Progress]
    end

    subgraph Instructor Journey
        I1[Log in as Instructor] --> I2[Instructor Dashboard: Cohort KPI & Alerts Summary]
        I2 --> I3[Manage Assigned Subjects & Topic Syllabi]
        I3 --> I4[Create Assessments & Enter Scores Manually or via CSV Bulk Import]
        I4 --> I5[Trigger Early Support Scan -> Identify High Risk & Declining Trends]
        I5 --> I6[Review Alerts & Log 1-on-1 Mentoring Follow-Up Actions]
        I6 --> I7[Inspect Individual Student Analytics & Run Cohort Batch Predictions]
    end

    subgraph Admin Journey
        A1[Log in as Administrator] --> A2[Admin Dashboard: System-Wide Analytics]
        A2 --> A3[Manage User Accounts: Roles & Account Deactivation]
        A3 --> A4[Upload CSV Datasets & Validate Schema]
        A4 --> A5[Train Multi-Model Pipeline: 5-Fold Stratified CV on Candidates]
        A5 --> A6[Inspect Confusion Matrix, High-Risk Recall & Benchmark]
        A6 --> A7[Live Activation / Rollback of Model Versions in Memory]
    end
```

---

### 1.3 Technologies Actually Used in This Project

| Layer | Technology | Version | Purpose in This Repository |
|---|---|---|---|
| **Frontend Framework** | React.js | `18.2.0` | Component-based reactive user interface |
| **Build Tool & Bundler** | Vite | `5.4.21` | Ultra-fast development server and production bundler |
| **CSS & Design** | Tailwind CSS | `3.4.1` | Utility-first styling, color tokens, and responsive layouts |
| **Routing** | React Router DOM | `6.22.0` | Client-side routing with role-based protected routes |
| **HTTP Client** | Axios | `1.6.7` | REST API communication with automated JWT Bearer headers |
| **Visual Analytics** | Recharts | `2.12.0` | Responsive charts (bar charts, line charts, calibration curves) |
| **Icons** | Lucide React | `0.330.0` | Consistent iconography across dashboards and modals |
| **Backend API** | Python Flask | `3.1.0` | Modular REST API server with Blueprint routing |
| **Database ORM** | Flask-SQLAlchemy | `3.1.1` | Object-relational mapping to SQLite / PostgreSQL |
| **Database Engine** | SQLite (Dev) / PostgreSQL (Prod) | `3.x` | Persistent relational storage for users, marks, and models |
| **Security & Auth** | PyJWT | `2.8.0` | Stateless HMAC-SHA256 signed JSON Web Tokens (24h expiry) |
| **Password Hashing** | Werkzeug | `3.1.3` | `scrypt` salted password cryptographic hashing |
| **Machine Learning** | Scikit-learn | `1.7.0` | Multi-model benchmarking, CV evaluation, and inference |
| **Data Processing** | Pandas & NumPy | `2.3` / `2.2` | Matrix manipulations, schema validation, and CSV handling |
| **Model Persistence** | Joblib | `1.4.2` | Serialization and zero-downtime loading of ML models |
| **Testing** | Pytest | `9.1.1` | Automated integration and regression test suite (29 tests) |

---

### 1.4 System Communication Architecture

```mermaid
flowchart LR
    subgraph Browser / Client Layer
        UI[React 18 Single Page App<br/>Vite + Tailwind CSS]
        CTX[AuthContext & ToastContext]
        AX[Axios REST Client]
        UI <--> CTX
        CTX <--> AX
    end

    subgraph HTTP / Middleware Boundary
        REQ[HTTP Requests /api/*]
        CORS[CORS Middleware]
        SEC[Security Headers Middleware<br/>nosniff, SAMEORIGIN, XSS]
        RATE[Rate Limiter<br/>Sliding Window 20 req/min]
        JWT[JWT Verification<br/>@token_required, @roles_required]
        AX --> REQ
        REQ --> CORS --> SEC --> RATE --> JWT
    end

    subgraph Flask REST Controllers
        AUTH_BP[/api/auth]
        SUBJ_BP[/api/subjects]
        ASS_BP[/api/assessments]
        PRED_BP[/api/predictions]
        REC_BP[/api/recommendations]
        ALERT_BP[/api/alerts]
        ADMIN_BP[/api/admin & /api/models]
        JWT --> AUTH_BP
        JWT --> SUBJ_BP
        JWT --> ASS_BP
        JWT --> PRED_BP
        JWT --> REC_BP
        JWT --> ALERT_BP
        JWT --> ADMIN_BP
    end

    subgraph Service & Machine Learning Layer
        SVC_ALERT[AlertService<br/>Evaluate early warnings]
        SVC_REC[RecommendationService<br/>De-duplicated study tasks]
        ML_PRED[MLPredictor Singleton<br/>In-memory Model & Preprocessor]
        ML_TRAIN[MLTrainingPipeline<br/>5-Fold Stratified CV Benchmarking]
        PRED_BP <--> ML_PRED
        ASS_BP --> SVC_ALERT
        ALERT_BP --> SVC_ALERT
        PRED_BP --> SVC_REC
        ADMIN_BP --> ML_TRAIN
        ML_TRAIN --> ML_PRED
    end

    subgraph Persistence Layer
        DB[(SQLite / PostgreSQL<br/>app.db)]
        DISK_ART[Artifact Storage<br/>backend/artifacts/<br/>model.joblib, versions/]
        AUTH_BP <--> DB
        SUBJ_BP <--> DB
        ASS_BP <--> DB
        PRED_BP <--> DB
        REC_BP <--> DB
        ALERT_BP <--> DB
        ADMIN_BP <--> DB
        ML_PRED <--> DISK_ART
        ML_TRAIN <--> DISK_ART
    end
```

---

## 2. Complete Folder Structure

Below is the verified file hierarchy of the project:

```
AI Learning Difficulty predictor/
├── .env.example                               # Template for environment configuration
├── .gitignore                                 # Git rules ignoring venv, node_modules, app.db, caches
├── README.md                                  # High-level architecture and quickstart guide
├── FEATURE_TO_FILE_MAPPING.csv                # Tabular spreadsheet mapping features to code files
├── AI_LEARNING_PREDICTOR_DEVELOPER_GUIDE.md   # This comprehensive manual
│
├── backend/                                   # Python Flask REST API & Machine Learning engine
│   ├── app.py                                 # Application factory, security headers, health routes
│   ├── config.py                              # Configuration loader (database URI, JWT, upload limits)
│   ├── extensions.py                          # SQLAlchemy and CORS extensions initialization
│   ├── seed_data.py                           # Seed script creating realistic demo users and curriculum
│   ├── requirements.txt                       # Backend Python dependencies
│   │
│   ├── models/                                # SQLAlchemy ORM Model definitions
│   │   ├── __init__.py                        # Export all database models
│   │   ├── user.py                            # User model with scrypt hashing and role enum
│   │   ├── academic.py                        # Subject, Topic, Assessment, StudentAssessmentResult
│   │   ├── ml_records.py                      # PredictionRecord, ModelVersion, DatasetRecord
│   │   └── support.py                         # StudyRecommendation, InstructorAlert, AlertFollowUp, AuditEvent
│   │
│   ├── routes/                                # Flask REST API Blueprint controllers
│   │   ├── __init__.py                        # Blueprint registration hub (`register_blueprints`)
│   │   ├── auth.py                            # User registration, login, JWT issuance, profile
│   │   ├── users.py                           # User directory, role assignment, status toggling
│   │   ├── subjects.py                        # Curriculum subjects and syllabus topics CRUD
│   │   ├── assessments.py                     # Quizzes/exams, grade entry, CSV bulk import, CSV template
│   │   ├── predictions.py                     # Difficulty prediction, insufficient data check, cohort batch
│   │   ├── recommendations.py                 # Personalized study actions and completion toggling
│   │   ├── alerts.py                          # Early support alerts, review status, mentoring follow-ups
│   │   ├── progress.py                        # Longitudinal performance trends and history
│   │   ├── datasets.py                        # Dataset repository, CSV schema validation, file preview
│   │   ├── models_mgmt.py                     # Model evaluation diagnostics, training, live activation
│   │   └── admin_analytics.py                 # Platform-wide statistics and audit event log
│   │
│   ├── services/                              # Core business logic decoupled from HTTP routes
│   │   ├── alert_service.py                   # Idempotent rules evaluating declining scores & risks
│   │   └── recommendation_service.py          # De-duplicated pedagogical recommendations generator
│   │
│   ├── utils/                                 # Shared utilities and middlewares
│   │   ├── decorators.py                      # `@token_required` and `@roles_required` decorators
│   │   └── rate_limiter.py                    # In-memory sliding-window request rate limiter
│   │
│   ├── ml/                                    # Machine Learning training & inference pipeline
│   │   ├── __init__.py                        # ML module exports
│   │   ├── dataset_generator.py               # Synthetic educational dataset generator (3,000 samples)
│   │   ├── preprocessor.py                    # Schema validation, ColumnTransformer, Scaler, Imputer
│   │   ├── evaluator.py                       # Held-out metrics, 5-Fold CV, High-Risk Recall, Log-Loss
│   │   ├── trainer.py                         # Multi-model benchmarking (Logistic, RF, Decision Tree)
│   │   └── predictor.py                       # Thread-safe MLPredictor singleton with explainability
│   │
│   ├── artifacts/                             # Active and versioned model storage
│   │   ├── model.joblib                       # Active production Scikit-learn model artifact
│   │   ├── preprocessor.joblib                # Fitted ColumnTransformer pipeline artifact
│   │   ├── evaluation_report.json             # Genuine metrics, confusion matrix, and feature sensitivities
│   │   └── versions/                          # Versioned directory storing past models for rollback
│   │       └── <version_tag>/                 # Isolated snapshot containing model, preprocessor, report
│   │
│   ├── data/                                  # Local persistent data directory
│   │   ├── app.db                             # Local SQLite database file
│   │   ├── learning_difficulty_dataset.csv    # 3,000-row baseline educational interaction dataset
│   │   └── uploads/                           # Temporary storage for uploaded CSV datasets
│   │
│   └── tests/                                 # Automated Pytest test suite (29 tests)
│       ├── conftest.py                        # Test fixtures: app context, test client, users, JWT tokens
│       ├── test_auth.py                       # Auth, rate limiting, security headers, readiness tests
│       ├── test_academic.py                   # Subject CRUD, assessment limits, CSV template, isolation
│       ├── test_ml_pipeline.py                # Dataset generator, preprocessor, multi-model trainer
│       ├── test_predictions_recommendations.py# Prediction, insufficient data (422), de-duplication, alerts
│       └── test_admin_datasets.py             # CSV uploads, invalid rejection, model activation & rollback
│
└── frontend/                                  # React 18 Single Page Application
    ├── index.html                             # Single page HTML entry point
    ├── package.json                           # Dependencies (React, Vite, Tailwind, Recharts, Lucide)
    ├── vite.config.js                         # Vite dev server configuration and `/api` proxy
    ├── tailwind.config.js                     # Tailwind theme tokens, typography, and colors
    ├── postcss.config.js                      # PostCSS plugins for Tailwind processing
    │
    └── src/
        ├── main.jsx                           # Application entry point (mounts React DOM root)
        ├── App.jsx                            # Router, ToastProvider, AuthProvider, protected routes
        ├── index.css                          # Tailwind directives and custom scrollbar utility classes
        │
        ├── api/
        │   └── axiosClient.js                 # Axios instance with request JWT injection & 401 redirect
        │
        ├── context/
        │   ├── AuthContext.jsx                # Authentication state (user, token, login, logout, roles)
        │   └── ToastContext.jsx               # Reactive non-blocking toast notifications (`useToast`)
        │
        ├── components/
        │   ├── Navbar.jsx                     # Top navigation bar, mobile hamburger, profile dropdown
        │   ├── Sidebar.jsx                    # Role-aware collapsible sidebar navigation
        │   ├── StatCard.jsx                   # Visual KPI summary card component
        │   ├── Modal.jsx                      # Accessible modal dialog with backdrop blur & Escape key
        │   ├── ConfirmDialog.jsx              # Reusable confirmation modal for destructive operations
        │   ├── LoadingSkeleton.jsx            # Animated placeholder skeletons for tables and charts
        │   └── ProtectedRoute.jsx             # React Router outlet guard checking auth and allowed roles
        │
        └── pages/
            ├── Login.jsx                      # Sign-in form with 1-click student/instructor/admin demo buttons
            ├── Register.jsx                   # User registration with role selection and input validation
            │
            ├── student/                       # Student role views
            │   ├── StudentDashboard.jsx       # Overview, enrolled subjects, recent predictions, quick actions
            │   ├── StudentSubjects.jsx        # Topic syllabus with on-demand AI prediction modal
            │   ├── StudentTopicAnalysis.jsx   # Interactive difficulty bar chart & explainable factors
            │   ├── StudentRecommendations.jsx # Actionable study recommendations with completion toggle
            │   └── StudentProgress.jsx        # Longitudinal grade trends and prediction history chart
            │
            ├── instructor/                    # Instructor role views
            │   ├── InstructorDashboard.jsx    # Cohort metrics, unreviewed alerts, cohort scan trigger
            │   ├── InstructorSubjects.jsx     # Subject & topic CRUD, batch cohort AI evaluation
            │   ├── InstructorAssessments.jsx  # Gradebook, assessment creation, CSV import & template download
            │   ├── InstructorStudentDetail.jsx# Individual student deep dive & targeted AI evaluation
            │   └── InstructorAlerts.jsx       # Early support alerts, severity filters, follow-up logs
            │
            └── admin/                         # Administrator role views
                ├── AdminDashboard.jsx         # Platform overview, user distribution, active ML snapshot
                ├── AdminUsers.jsx             # User directory, role assignment, status toggling
                ├── AdminDatasets.jsx          # Dataset repository, upload schema validation, data preview
                └── AdminModelEvaluation.jsx   # Confusion matrix, candidate benchmarks, zero-downtime activation
```

### 2.1 System Entry Points

1. **Frontend Web Interface:**
   - Primary File: [`frontend/src/main.jsx`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/frontend/src/main.jsx)
   - Initializes React 18 using `ReactDOM.createRoot` and renders [`App.jsx`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/frontend/src/App.jsx).

2. **Backend REST API:**
   - Primary File: [`backend/app.py`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/backend/app.py)
   - Function: `create_app(config_class=Config)` initializes Flask extensions, registers blueprints, installs security middlewares, and starts the predictor singleton.

3. **Machine Learning Model Training Pipeline:**
   - Primary File: [`backend/ml/trainer.py`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/backend/ml/trainer.py)
   - Class/Method: `MLTrainingPipeline.run_training_pipeline(csv_path, version_tag=None)` executes multi-model training with 5-Fold Stratified Cross-Validation.

4. **Machine Learning Real-Time Inference Engine:**
   - Primary File: [`backend/ml/predictor.py`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/backend/ml/predictor.py)
   - Class/Method: `MLPredictor.get_instance().predict_features(feature_dict)` performs thread-safe feature validation, transformation, classification, probability calibration, and explainability extraction.

5. **Database Seeder & Demonstration Initializer:**
   - Primary File: [`backend/seed_data.py`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/backend/seed_data.py)
   - Function: `seed_database()` creates all tables, seeds demo accounts (`admin`, `dr_smith`, `prof_davis`, `student_alex`, etc.), generates the 3,000-row baseline dataset, and runs the initial model training.

---

## 3. Frontend Architecture & Component Guide

### 3.1 State Management & Context Architecture

The frontend uses standard React Context without bulky third-party state managers:

1. **[`AuthContext.jsx`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/frontend/src/context/AuthContext.jsx):**
   - Manages `user` object and `token` (persisted in `localStorage` under keys `token` and `user`).
   - Exposes `login(identifier, password)`, `register(formData)`, `logout()`, `hasRole(role)`, `isAuthenticated`, and `loading`.
   - On initial mount, calls `GET /api/auth/me` to verify token validity against the backend.

2. **[`ToastContext.jsx`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/frontend/src/context/ToastContext.jsx):**
   - Provides non-blocking, accessible notifications that auto-dismiss after a configurable timeout (default 4 seconds).
   - Hook: `const toast = useToast()`.
   - Methods: `toast.success(message)`, `toast.error(message)`, `toast.warning(message)`, `toast.info(message)`.

### 3.2 Layout & Routing Structure

- Root routing is established in [`frontend/src/App.jsx`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/frontend/src/App.jsx).
- Layout wrapper `AppLayout` renders:
  - [`Navbar.jsx`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/frontend/src/components/Navbar.jsx) at the top.
  - [`Sidebar.jsx`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/frontend/src/components/Sidebar.jsx) fixed on the left (responsive slide-out on mobile).
  - Main dynamic view inside `<Outlet />`.
- [`ProtectedRoute.jsx`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/frontend/src/components/ProtectedRoute.jsx) checks if `isAuthenticated` is true and if `user.role` is included in `allowedRoles`. If not authenticated, redirects to `/login`. If unauthorized, redirects to the user's role-appropriate home route.

---

### 3.3 Visual Interface Mapping (Student, Instructor, Admin)

#### Student Interface

| Route | Source Page File | Visible Buttons & Interactive Features | Backend API Endpoint Called |
|---|---|---|---|
| `/student/dashboard` | `StudentDashboard.jsx` | - "Analyze Topics" link<br/>- "Mark as Complete" on pending recommendation cards | `GET /api/subjects`<br/>`GET /api/assessments/my-results`<br/>`GET /api/predictions/my-predictions`<br/>`GET /api/recommendations/my-recommendations?status=pending`<br/>`PUT /api/recommendations/<id>/complete` |
| `/student/subjects` | `StudentSubjects.jsx` | - Subject list selection tabs<br/>- "Run AI Difficulty Evaluation" button per topic<br/>- Prediction Result Modal with explainable factor badges | `GET /api/subjects`<br/>`GET /api/subjects/<id>`<br/>`POST /api/predictions/predict` |
| `/student/analysis` | `StudentTopicAnalysis.jsx` | - Topic Difficulty Bar Chart (Recharts)<br/>- Clickable bar or list item to view topic factor sensitivities | `GET /api/predictions/my-predictions` |
| `/student/recommendations` | `StudentRecommendations.jsx` | - Filter tabs (`Pending`, `Completed`, `All`)<br/>- "Mark Complete" checkbox button | `GET /api/recommendations/my-recommendations`<br/>`PUT /api/recommendations/<id>/complete` |
| `/student/progress` | `StudentProgress.jsx` | - Assessment Performance Timeline (LineChart)<br/>- Historical Predictions Table | `GET /api/progress/my-progress` |

#### Instructor Interface

| Route | Source Page File | Visible Buttons & Interactive Features | Backend API Endpoint Called |
|---|---|---|---|
| `/instructor/dashboard` | `InstructorDashboard.jsx` | - "Run Early Support Scan" button<br/>- "View All Alerts" and student quick links | `GET /api/users/students`<br/>`GET /api/subjects`<br/>`GET /api/alerts?is_reviewed=false`<br/>`POST /api/alerts/scan` |
| `/instructor/subjects` | `InstructorSubjects.jsx` | - "New Subject" modal form<br/>- "Add Topic" modal form<br/>- "Cohort AI Evaluation" button<br/>- Edit topic modal & Delete topic confirmation | `GET /api/subjects`<br/>`POST /api/subjects`<br/>`POST /api/subjects/<id>/topics`<br/>`PUT /api/subjects/topics/<id>`<br/>`DELETE /api/subjects/topics/<id>`<br/>`POST /api/predictions/batch-predict-topic/<id>` |
| `/instructor/assessments` | `InstructorAssessments.jsx` | - "New Assessment" modal button<br/>- "CSV Template" download button<br/>- "Enter Result" manual grade entry modal<br/>- "Import CSV" gradebook upload modal | `GET /api/subjects`<br/>`GET /api/users/students`<br/>`GET /api/assessments`<br/>`POST /api/assessments`<br/>`POST /api/assessments/<id>/results`<br/>`POST /api/assessments/<id>/import-results`<br/>`GET /api/assessments/template.csv` |
| `/instructor/students/:studentId` | `InstructorStudentDetail.jsx` | - Student profile summary cards<br/>- "Run Topic Evaluation" button<br/>- Student marks & predictions history tables | `GET /api/users/students`<br/>`GET /api/assessments/student/<id>`<br/>`GET /api/predictions/student/<id>`<br/>`GET /api/recommendations/student/<id>`<br/>`POST /api/predictions/predict` |
| `/instructor/alerts` | `InstructorAlerts.jsx` | - Status filters (`Unreviewed`, `Reviewed`, `All`)<br/>- "Mark as Reviewed" checkmark button<br/>- "Log Action" follow-up modal form | `GET /api/alerts`<br/>`PUT /api/alerts/<id>/review`<br/>`POST /api/alerts/<id>/follow-ups` |

#### Administrator Interface

| Route | Source Page File | Visible Buttons & Interactive Features | Backend API Endpoint Called |
|---|---|---|---|
| `/admin/dashboard` | `AdminDashboard.jsx` | - Platform KPI cards<br/>- Active ML model status widget<br/>- Quick navigation buttons to Users/Models/Datasets | `GET /api/admin/overview` |
| `/admin/users` | `AdminUsers.jsx` | - Search bar & Role filters<br/>- "Create User" modal button<br/>- "Change Role" modal dropdown<br/>- "Deactivate / Activate" account toggle with confirmation modal | `GET /api/users`<br/>`POST /api/auth/register`<br/>`PUT /api/users/<id>/role`<br/>`PUT /api/users/<id>/status` |
| `/admin/datasets` | `AdminDatasets.jsx` | - "Upload CSV Dataset" modal with schema guidelines<br/>- "Preview" modal (displays first 10 rows)<br/>- "Train Model" button with confirmation modal<br/>- "Delete Dataset" button with confirmation modal | `GET /api/datasets`<br/>`POST /api/datasets/upload`<br/>`GET /api/datasets/<id>`<br/>`POST /api/datasets/<id>/train`<br/>`DELETE /api/datasets/<id>` |
| `/admin/models` | `AdminModelEvaluation.jsx` | - "Retrain Pipeline" button with confirmation modal<br/>- Active Model Metrics & Confusion Matrix grid<br/>- Candidate Algorithms Benchmark table (5-Fold CV F1)<br/>- Feature sensitivities bar chart<br/>- Version History Table with 1-click "Activate" button | `GET /api/models/active`<br/>`GET /api/models/history`<br/>`POST /api/models/train-default`<br/>`PUT /api/models/<id>/activate` |

---

### 3.4 API Configuration & Interceptors

All frontend HTTP traffic flows through [`frontend/src/api/axiosClient.js`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/frontend/src/api/axiosClient.js):
- **Base URL:** `/api` (proxied in development by Vite to `http://localhost:5000/api`).
- **Request Interceptor:** Reads `localStorage.getItem('token')` and appends `Authorization: Bearer <token>` to all requests.
- **Response Interceptor:** Detects `401 Unauthorized` responses, clears stored session tokens, and dispatches a redirect to `/login` if a token has expired or is invalid.

---

### 3.5 Exactly Which Files to Edit for Common Frontend Changes

1. **Page Title / Text / Copy:** Open the relevant page file in `frontend/src/pages/` (e.g. `StudentDashboard.jsx` or `InstructorAssessments.jsx`) and modify the text within the JSX tags.
2. **Website Colors & Branding:** Open [`frontend/tailwind.config.js`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/frontend/tailwind.config.js) to adjust the theme palette or edit CSS utility classes (`bg-indigo-600`, `text-slate-900`) across `Navbar.jsx`, `Sidebar.jsx`, and page layouts.
3. **Sidebar Navigation Items:** Open [`frontend/src/components/Sidebar.jsx`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/frontend/src/components/Sidebar.jsx) and edit the `studentLinks`, `instructorLinks`, or `adminLinks` configuration arrays.
4. **KPI Cards:** Open [`frontend/src/components/StatCard.jsx`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/frontend/src/components/StatCard.jsx) or the card grid in the target dashboard.
5. **Charts:** Open `StudentTopicAnalysis.jsx` or `AdminModelEvaluation.jsx` to configure the `<ResponsiveContainer>`, `<BarChart>`, or `<Tooltip>` props from Recharts.

---

## 4. Backend Architecture & API Catalog

### 4.1 Flask Application Factory & Middleware

The backend uses the application factory pattern in [`backend/app.py`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/backend/app.py):
- **CORS:** Configured with `flask_cors.CORS` allowing origins specified in `CORS_ORIGINS` (defaults to `*`).
- **Security Headers Middleware (`@app.after_request`):**
  ```python
  response.headers['X-Content-Type-Options'] = 'nosniff'
  response.headers['X-Frame-Options'] = 'SAMEORIGIN'
  response.headers['X-XSS-Protection'] = '1; mode=block'
  response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
  ```
- **Rate Limiting:** Sliding-window rate limiter in [`backend/utils/rate_limiter.py`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/backend/utils/rate_limiter.py) applied via `@rate_limit(max_requests=20, window_seconds=60)` on authentication routes. Returns HTTP `429 Too Many Requests` with a `Retry-After` header when throttled.
- **Health & Readiness Endpoints:**
  - `GET /api/health`: Returns basic JSON status of server and model availability.
  - `GET /api/ready`: Readiness probe executing a `SELECT 1` database query and verifying `MLPredictor.is_ready()`. Returns HTTP `200` or `503 Service Unavailable`.

---

### 4.2 Complete API Endpoints Catalog

#### Authentication (`/api/auth`)
| HTTP Method | Route | Role Required | Request Body | Success Response | Error Codes |
|---|---|---|---|---|---|
| `POST` | `/api/auth/register` | Public | `{ username, email, password, full_name, role }` | `201 Created` with `{ message, user }` | `400`, `409`, `429` |
| `POST` | `/api/auth/login` | Public | `{ identifier, password }` | `200 OK` with `{ token, user }` | `400`, `401`, `403`, `429` |
| `GET` | `/api/auth/me` | Any Authenticated | None | `200 OK` with `{ user }` | `401` |
| `POST` | `/api/auth/logout` | Any Authenticated | None | `200 OK` with `{ message }` | `401` |

#### Academic Curriculum & Syllabus (`/api/subjects`)
| HTTP Method | Route | Role Required | Request Body / Params | Success Response | Error Codes |
|---|---|---|---|---|---|
| `GET` | `/api/subjects` | Any Authenticated | None | `200 OK` with `{ subjects: [...] }` | `401` |
| `POST` | `/api/subjects` | Instructor, Admin | `{ code, name, description }` | `201 Created` with `{ subject }` | `400`, `401`, `403` |
| `GET` | `/api/subjects/<id>` | Any Authenticated | None | `200 OK` with `{ subject: { ..., topics: [...] } }` | `401`, `404` |
| `PUT` | `/api/subjects/<id>` | Instructor (Owner), Admin | `{ name, description }` | `200 OK` with `{ subject }` | `401`, `403`, `404` |
| `DELETE` | `/api/subjects/<id>` | Instructor (Owner), Admin | None | `200 OK` with `{ message }` | `401`, `403`, `404` |
| `GET` | `/api/subjects/<id>/topics`| Any Authenticated | None | `200 OK` with `{ topics: [...] }` | `401`, `404` |
| `POST` | `/api/subjects/<id>/topics`| Instructor (Owner), Admin | `{ name, description, learning_objectives, difficulty_level, order_index, resources }` | `201 Created` with `{ topic }` | `400`, `401`, `403`, `404` |
| `PUT` | `/api/subjects/topics/<id>`| Instructor (Owner), Admin | `{ name, description, ... }` | `200 OK` with `{ topic }` | `401`, `403`, `404` |
| `DELETE`| `/api/subjects/topics/<id>`| Instructor (Owner), Admin | None | `200 OK` with `{ message }` | `401`, `403`, `404` |

#### Assessments & Gradebook (`/api/assessments`)
| HTTP Method | Route | Role Required | Request Body / Params | Success Response | Error Codes |
|---|---|---|---|---|---|
| `GET` | `/api/assessments` | Any Authenticated | `?subject_id=<int>` | `200 OK` with `{ assessments: [...] }` | `401` |
| `POST` | `/api/assessments` | Instructor (Owner), Admin | `{ subject_id, topic_id, title, assessment_type, max_marks, passing_marks, weightage, assessment_date }` | `201 Created` with `{ assessment }` | `400`, `401`, `403` |
| `POST` | `/api/assessments/<id>/results` | Instructor (Owner), Admin | `{ student_id, marks_obtained, study_time_minutes, attempt_count, repeated_errors_count, completion_status, remarks }` | `200 OK` with `{ result }` | `400`, `401`, `403`, `404` |
| `POST` | `/api/assessments/<id>/import-results` | Instructor (Owner), Admin | `multipart/form-data` with `file: <gradebook.csv>` | `200 OK` with `{ imported_count, rejected_count, errors: [...] }` | `400`, `401`, `403`, `404` |
| `GET` | `/api/assessments/template.csv` | Instructor, Admin | None | `200 OK` (CSV file attachment: `gradebook_template.csv`) | `401`, `403` |
| `GET` | `/api/assessments/my-results` | Student | None | `200 OK` with `{ results: [...] }` | `401` |
| `GET` | `/api/assessments/student/<id>` | Instructor, Admin | None (Instructors only see their taught subjects) | `200 OK` with `{ results: [...] }` | `401`, `403` |

#### Machine Learning Predictions (`/api/predictions`)
| HTTP Method | Route | Role Required | Request Body / Params | Success Response | Error Codes |
|---|---|---|---|---|---|
| `POST` | `/api/predictions/predict` | Any Authenticated | `{ topic_id, student_id? (optional for instructor), features? (optional simulation) }` | `201 Created` with `{ prediction: { difficulty_score, predicted_difficulty, probabilities, contributing_factors, recommendations } }` | `400`, `401`, `403`, `404`, `422` (Insufficient Data) |
| `GET` | `/api/predictions/my-predictions` | Student | None | `200 OK` with `{ predictions: [...] }` | `401` |
| `GET` | `/api/predictions/student/<id>` | Instructor, Admin | None (Instructors only see their taught subjects) | `200 OK` with `{ predictions: [...] }` | `401`, `403` |
| `POST` | `/api/predictions/batch-predict-topic/<id>` | Instructor (Owner), Admin | None | `200 OK` with `{ message, processed_count, high_risk_count }` | `401`, `403`, `404` |

#### Personalized Study Recommendations (`/api/recommendations`)
| HTTP Method | Route | Role Required | Request Body / Params | Success Response | Error Codes |
|---|---|---|---|---|---|
| `GET` | `/api/recommendations/my-recommendations` | Student | `?status=pending` or `?status=completed` | `200 OK` with `{ recommendations: [...] }` | `401` |
| `PUT` | `/api/recommendations/<id>/complete` | Student (Owner) | None | `200 OK` with `{ recommendation }` | `401`, `403`, `404` |
| `GET` | `/api/recommendations/student/<id>` | Instructor, Admin | None (Filtered to instructor's subjects) | `200 OK` with `{ recommendations: [...] }` | `401`, `403` |

#### Early Support Alerts (`/api/alerts`)
| HTTP Method | Route | Role Required | Request Body / Params | Success Response | Error Codes |
|---|---|---|---|---|---|
| `GET` | `/api/alerts` | Instructor, Admin | `?is_reviewed=false&severity=high` | `200 OK` with `{ alerts: [...] }` | `401`, `403` |
| `PUT` | `/api/alerts/<id>/review` | Instructor (Owner), Admin | None | `200 OK` with `{ alert }` | `401`, `403`, `404` |
| `POST` | `/api/alerts/<id>/follow-ups` | Instructor (Owner), Admin | `{ action_taken, notes, outcome }` | `201 Created` with `{ follow_up }` | `400`, `401`, `403`, `404` |
| `POST` | `/api/alerts/scan` | Instructor, Admin | `{ subject_id }` | `200 OK` with `{ message, new_alerts_count }` | `400`, `401`, `403` |

#### Admin Model Operations & Datasets (`/api/datasets`, `/api/models`, `/api/admin`, `/api/users`)
| HTTP Method | Route | Role Required | Request Body / Params | Success Response | Error Codes |
|---|---|---|---|---|---|
| `GET` | `/api/admin/overview` | Admin | None | `200 OK` with `{ users, academics, predictions, alerts, active_model }` | `401`, `403` |
| `GET` | `/api/users` | Admin | `?role=student&search=alex` | `200 OK` with `{ users: [...] }` | `401`, `403` |
| `PUT` | `/api/users/<id>/role` | Admin | `{ role: 'instructor' }` | `200 OK` with `{ user }` | `400`, `401`, `403`, `404` |
| `PUT` | `/api/users/<id>/status` | Admin | `{ is_active: false }` | `200 OK` with `{ user }` | `400`, `401`, `403`, `404` |
| `GET` | `/api/datasets` | Admin | None | `200 OK` with `{ datasets: [...] }` | `401`, `403` |
| `POST` | `/api/datasets/upload` | Admin | `multipart/form-data` with `file: <data.csv>` | `201 Created` with `{ dataset }` | `400`, `401`, `403` |
| `GET` | `/api/datasets/<id>` | Admin | None | `200 OK` with `{ dataset: { ..., preview: [...] } }` | `401`, `403`, `404` |
| `DELETE` | `/api/datasets/<id>` | Admin | None | `200 OK` with `{ message }` | `401`, `403`, `404` |
| `POST` | `/api/datasets/<id>/train` | Admin | None | `200 OK` with `{ model_version, training_report }` | `400`, `401`, `403`, `404`, `500` |
| `GET` | `/api/models/active` | Admin | None | `200 OK` with `{ active_model, candidate_comparison, feature_names }` | `401`, `403` |
| `GET` | `/api/models/history` | Admin | None | `200 OK` with `{ models: [...] }` | `401`, `403` |
| `POST` | `/api/models/train-default`| Admin | None | `200 OK` with `{ message, model, report }` | `401`, `403`, `500` |
| `PUT` | `/api/models/<id>/activate` | Admin | None (Loads weights into `MLPredictor` in memory) | `200 OK` with `{ model }` | `401`, `403`, `404` |

---

## 5. Database Architecture & Data Management

### 5.1 Database Engine Configuration

- **Engine:** SQLite by default for zero-configuration local development (`backend/data/app.db`).
- **Production Compatibility:** Full PostgreSQL compatibility. If the environment variable `DATABASE_URL` is set (e.g. `postgresql://user:pass@host:5432/dbname`), SQLAlchemy automatically routes all queries to PostgreSQL.
- **ORM Standard:** SQLAlchemy 2.0-compliant queries using `db.session.get(Model, id)` and session binding.

---

### 5.2 Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    users ||--o{ subjects : "instructs"
    users ||--o{ student_assessment_results : "records"
    users ||--o{ prediction_records : "predicted_for"
    users ||--o{ study_recommendations : "assigned_to"
    users ||--o{ instructor_alerts : "concerns"
    users ||--o{ alert_follow_ups : "authored_by"
    
    subjects ||--o{ topics : "contains"
    subjects ||--o{ assessments : "organizes"
    subjects ||--o{ prediction_records : "scopes"
    
    topics ||--o{ assessments : "assesses"
    topics ||--o{ prediction_records : "evaluates"
    topics ||--o{ study_recommendations : "targets"
    
    assessments ||--o{ student_assessment_results : "yields"
    
    prediction_records ||--o{ study_recommendations : "generates"
    
    instructor_alerts ||--o{ alert_follow_ups : "tracks"
    
    users {
        int id PK
        string username UK
        string email UK
        string password_hash
        string role
        string full_name
        boolean is_active
        datetime created_at
    }

    subjects {
        int id PK
        string code UK
        string name
        text description
        int instructor_id FK
        datetime created_at
    }

    topics {
        int id PK
        int subject_id FK
        string name
        text description
        text learning_objectives
        string difficulty_level
        int order_index
        text resources
    }

    assessments {
        int id PK
        int subject_id FK
        int topic_id FK
        string title
        string assessment_type
        float max_marks
        float passing_marks
        float weightage
        date assessment_date
    }

    student_assessment_results {
        int id PK
        int student_id FK
        int assessment_id FK
        float marks_obtained
        float percentage
        float study_time_minutes
        int attempt_count
        int repeated_errors_count
        string completion_status
        text remarks
    }

    prediction_records {
        int id PK
        int student_id FK
        int subject_id FK
        int topic_id FK
        string predicted_difficulty
        float difficulty_score
        float probability_low
        float probability_moderate
        float probability_high
        json contributing_factors
        string model_version
        datetime created_at
    }

    model_versions {
        int id PK
        string version_tag UK
        string model_name
        string algorithm
        float accuracy
        float precision_macro
        float recall_macro
        float f1_macro
        json confusion_matrix
        json classification_report
        json feature_importances
        boolean is_active
    }

    dataset_records {
        int id PK
        string filename
        string original_name
        int row_count
        int column_count
        string validation_status
        json validation_details
        boolean is_active_training_set
    }

    study_recommendations {
        int id PK
        int student_id FK
        int subject_id FK
        int topic_id FK
        int prediction_id FK
        text reason
        text suggested_action
        string priority
        boolean is_completed
        datetime completed_at
    }

    instructor_alerts {
        int id PK
        int student_id FK
        int instructor_id FK
        int subject_id FK
        int topic_id FK
        string alert_type
        string severity
        string title
        text description
        boolean is_reviewed
        datetime reviewed_at
    }

    alert_follow_ups {
        int id PK
        int alert_id FK
        int instructor_id FK
        string action_taken
        text notes
        string outcome
        datetime created_at
    }
```

---

### 5.3 Safely Inspecting and Modifying Development Data

1. **Inspecting via Python Interactive Shell:**
   ```bash
   venv\Scripts\python
   ```
   ```python
   from backend.app import create_app
   from backend.extensions import db
   from backend.models.user import User
   from backend.models.academic import Subject, Assessment

   app = create_app()
   with app.app_context():
       users = User.query.all()
       print([(u.id, u.username, u.role) for u in users])
   ```

2. **Inspecting via SQLite Command-Line or GUI:**
   - Database location: `backend/data/app.db`.
   - Tool: Open `app.db` in [DB Browser for SQLite](https://sqlitebrowser.org/) or run:
     ```bash
     sqlite3 backend/data/app.db ".tables"
     sqlite3 backend/data/app.db "SELECT id, username, email, role, is_active FROM users;"
     ```

3. **Re-seeding Demo Data from Scratch:**
   If the database needs to be reset cleanly:
   ```bash
   # Remove the local sqlite file
   del backend\data\app.db
   # Re-run the automated database seeder and trainer
   cmd /c "set PYTHONPATH=. && venv\Scripts\python backend\seed_data.py"
   ```

---

## 6. Machine Learning Pipeline & Inference Engine

### 6.1 Input Features & Data Preprocessing

The model requires 10 empirical student learning features:

| Feature Name | Type | Allowed Bounds | Source in Application |
|---|---|---|---|
| `quiz_score` | Numeric (float) | `[0.0, 100.0]` | Average percentage on quizzes for the selected topic |
| `assignment_score` | Numeric (float) | `[0.0, 100.0]` | Average percentage on assignments for the topic |
| `exam_score` | Numeric (float) | `[0.0, 100.0]` | Performance on comprehensive subject examinations |
| `study_time_weekly` | Numeric (float) | `[0.5, 40.0]` (hours) | Weekly hours calculated from recorded study minutes |
| `attendance_rate` | Numeric (float) | `[0.0, 100.0]` | Percentage of assigned assessments submitted on time |
| `attempt_count` | Numeric (integer)| `[1, 10]` | Max re-submission attempts taken on coursework |
| `repeated_errors_count` | Numeric (integer)| `[0, 20]` | Sum of recorded repeated mistakes on recurring topics |
| `previous_topic_score` | Numeric (float) | `[0.0, 100.0]` | Historical performance on preceding syllabus order index |
| `learning_pace_gap` | Numeric (float) | `[-30.0, +30.0]` | Score deviation relative to cohort baseline pace |
| `topic_difficulty_level`| Categorical | `beginner`, `intermediate`, `advanced` | Inherent complexity specified in topic metadata |

**Target Label:** `difficulty_category` with 3 mutually exclusive classes: **`Low`**, **`Moderate`**, **`High`**.

#### Preprocessing Pipeline (`MLDataPreprocessor`)
Located in [`backend/ml/preprocessor.py`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/backend/ml/preprocessor.py):
- **Numerical Features (9):** Handled via `SimpleImputer(strategy='median')` followed by `StandardScaler()`.
- **Categorical Feature (`topic_difficulty_level`):** Handled via `SimpleImputer(strategy='most_frequent')` followed by `OneHotEncoder(handle_unknown='ignore', sparse_output=False)`.
- Preprocessing is fitted strictly on training data during model training and saved as `preprocessor.joblib`. Inference transforms raw features using this fitted artifact to prevent data leakage.

---

### 6.2 Multi-Model Benchmarking & Selection

Located in [`backend/ml/trainer.py`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/backend/ml/trainer.py):
The training pipeline evaluates three candidate algorithms on identical **5-Fold Stratified Cross-Validation** splits:
1. **Logistic Regression (Multinomial with L2 Regularization)**
2. **Random Forest Classifier (120 Estimators, max depth 12)**
3. **Decision Tree Classifier (max depth 6)**

#### Held-Out Evaluation Results (Dataset: 3,000 samples, 20% held-out test split: N=600):

| Candidate Model | 5-Fold CV Macro F1 | Test Accuracy | Test Macro F1 | High-Difficulty Recall | Calibrated Cross-Entropy Loss |
|---|---|---|---|---|---|
| **Logistic Regression (Selected)** | **0.9080 ± 0.0111** | **93.83%** | **0.9280** | **94.6%** | **0.1742** |
| Random Forest Classifier | 0.8910 ± 0.0095 | 92.17% | 0.9096 | 91.4% | 0.2185 |
| Decision Tree Classifier | 0.8576 ± 0.0156 | 88.83% | 0.8695 | 87.2% | 0.4510 |

The algorithm with the highest cross-validation Macro F1 score is automatically designated as the production model.

---

### 6.3 Inference & Explainability Calculations

In [`backend/ml/predictor.py`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/backend/ml/predictor.py):
1. **Class Probabilities:** Extracted via `model.predict_proba(X_trans)`:
   $P(\text{Low})$, $P(\text{Moderate})$, $P(\text{High})$.
2. **Difficulty Severity Index ($0.0$ to $1.0$):**
   $$\text{Difficulty Score} = 0.5 \times P(\text{Moderate}) + 1.0 \times P(\text{High})$$
3. **Contributing Factor Extraction:**
   Each input feature is evaluated against risk thresholds to generate natural language explanations:
   - `quiz_score < 50.0`: `"Quiz performance is critically low (XX%), reflecting conceptual difficulty."`
   - `repeated_errors_count >= 4`: `"High recurrence of identical errors indicates unresolved misconceptions."`
   - `study_time_weekly < 5.0`: `"Weekly dedicated study time is below the recommended threshold."`

---

### 6.4 Versioned Model Storage & Live Rollback

When a model is trained:
1. Artifacts are written to a versioned directory:
   `backend/artifacts/versions/<version_tag>/` containing `model.joblib`, `preprocessor.joblib`, and `evaluation_report.json`.
2. A record is added to the `model_versions` table.
3. Active artifacts in `backend/artifacts/` are updated.
4. When an admin clicks **Activate** on any historical model version in the Admin UI:
   - `PUT /api/models/<id>/activate` is executed.
   - It invokes `MLPredictor.get_instance().load_version(version_tag)`.
   - The weights and preprocessor are loaded directly into server memory with **zero downtime or server restart**.

---

## 7. Feature-to-File Master Mapping Table

| Feature Name | Frontend Component | Backend Route / Service | Database Tables | ML Dependency | How to Modify | How to Test |
|---|---|---|---|---|---|---|
| **User Registration** | `Register.jsx` | `POST /api/auth/register` in `routes/auth.py` | `users` | None | Edit form fields in `Register.jsx` and constraints in `auth.py` | Run `pytest backend/tests/test_auth.py::test_register_success` |
| **User Login & JWT** | `Login.jsx` | `POST /api/auth/login` in `routes/auth.py` | `users` | None | Edit token duration in `config.py` or payload in `auth.py` | Run `pytest backend/tests/test_auth.py::test_login_success` |
| **Auth Session Provider** | `AuthContext.jsx` | `GET /api/auth/me` in `routes/auth.py` | `users` | None | Modify stored user properties or refresh logic in `AuthContext.jsx` | Run `pytest backend/tests/test_auth.py::test_get_current_user_me` |
| **Route Access Guards** | `ProtectedRoute.jsx` | `@roles_required` in `utils/decorators.py` | `users` | None | Update `allowedRoles` array in `App.jsx` or decorator on routes | Run `pytest backend/tests/test_academic.py::test_instructor_subject_isolation` |
| **Reactive Toasts** | `ToastContext.jsx` | None (Client Context) | None | None | Adjust toast duration or styling classes in `ToastContext.jsx` | Trigger an action in the UI and inspect toast banner |
| **Confirm Action Modals** | `ConfirmDialog.jsx`| None (Client Component) | None | None | Change modal backdrop, buttons, or transitions in `ConfirmDialog.jsx` | Trigger Delete Topic or Retrain Model in browser |
| **Student Dashboard** | `StudentDashboard.jsx` | `GET /api/subjects`, `GET /api/assessments/my-results` | `subjects`, `student_assessment_results` | `MLPredictor` | Edit stat cards or recent activity list in `StudentDashboard.jsx` | Log in as `student_alex` and verify card numbers match DB |
| **Topic Syllabus View** | `StudentSubjects.jsx` | `GET /api/subjects/<id>` in `routes/subjects.py` | `subjects`, `topics` | None | Edit syllabus layout or resource links in `StudentSubjects.jsx` | Run `pytest backend/tests/test_academic.py::test_subject_crud_by_instructor` |
| **Topic AI Prediction** | `StudentSubjects.jsx` | `POST /api/predictions/predict` in `routes/predictions.py` | `prediction_records`, `student_assessment_results` | `MLPredictor.predict_features` | Edit feature aggregation in `compute_student_topic_features` | Run `pytest backend/tests/test_predictions_recommendations.py::test_prediction_and_isolation` |
| **Insufficient Data Check**| `StudentSubjects.jsx` | `POST /api/predictions/predict` in `routes/predictions.py` | `student_assessment_results` | None | Change minimum assessment threshold in `predictions.py` | Run `pytest backend/tests/test_predictions_recommendations.py::test_insufficient_data_error` |
| **Topic Knowledge Analysis**| `StudentTopicAnalysis.jsx` | `GET /api/predictions/my-predictions` in `routes/predictions.py` | `prediction_records` | `MLPredictor` contributing factors | Edit Recharts bar visual or sensitivity descriptions | Navigate to `/student/analysis` and click a topic bar |
| **Study Recommendations** | `StudentRecommendations.jsx`| `GET /api/recommendations/my-recommendations` in `routes/recommendations.py` | `study_recommendations` | `RecommendationService` | Add pedagogical rules in `recommendation_service.py` | Run `pytest backend/tests/test_predictions_recommendations.py::test_recommendation_completion` |
| **Recommendation De-dup** | `StudentRecommendations.jsx`| `services/recommendation_service.py` | `study_recommendations` | `RecommendationService` | Edit existing active recommendation lookup in `recommendation_service.py` | Run `pytest backend/tests/test_predictions_recommendations.py::test_recommendation_deduplication` |
| **Student Progress Trends** | `StudentProgress.jsx` | `GET /api/progress/my-progress` in `routes/progress.py` | `student_assessment_results`, `prediction_records` | None | Modify progress aggregation groupings or line chart styling | Navigate to `/student/progress` and check time-series points |
| **Instructor Curriculum** | `InstructorSubjects.jsx` | `POST /api/subjects`, `POST /api/subjects/<id>/topics` in `routes/subjects.py` | `subjects`, `topics` | None | Edit topic fields (difficulty level, order index) in `InstructorSubjects.jsx` | Run `pytest backend/tests/test_academic.py::test_topic_crud` |
| **Cohort Batch Prediction**| `InstructorSubjects.jsx` | `POST /api/predictions/batch-predict-topic/<id>` in `routes/predictions.py` | `prediction_records`, `topics` | `MLPredictor` | Change student enrollment selection in `batch_predict_topic` | Run `pytest backend/tests/test_predictions_recommendations.py::test_instructor_batch_predict_isolation` |
| **Assessments Management** | `InstructorAssessments.jsx`| `POST /api/assessments` in `routes/assessments.py` | `assessments` | None | Add assessment categories (e.g. `project`, `lab`) in `assessments.py` | Run `pytest backend/tests/test_academic.py::test_assessment_creation_and_result_validation` |
| **Manual Grade Entry** | `InstructorAssessments.jsx`| `POST /api/assessments/<id>/results` in `routes/assessments.py` | `student_assessment_results` | `AlertService` trigger | Adjust max score boundaries or study minutes tracking in form | Run `pytest backend/tests/test_academic.py::test_assessment_creation_and_result_validation` |
| **Gradebook CSV Import** | `InstructorAssessments.jsx`| `POST /api/assessments/<id>/import-results` in `routes/assessments.py` | `student_assessment_results` | `AlertService` trigger | Add CSV columns (e.g. `late_submission`) in `assessments.py` | Upload sample CSV and verify imported counts |
| **CSV Template Download** | `InstructorAssessments.jsx`| `GET /api/assessments/template.csv` in `routes/assessments.py` | None | None | Modify sample rows or column names in `download_csv_template` | Run `pytest backend/tests/test_academic.py::test_gradebook_csv_template_download` |
| **Instructor Student View** | `InstructorStudentDetail.jsx`| `GET /api/assessments/student/<id>`, `GET /api/predictions/student/<id>` | `student_assessment_results`, `prediction_records` | `MLPredictor` | Add instructor note field or summary statistics in detail page | Open `/instructor/students/4` in browser |
| **Early Support Alerts** | `InstructorAlerts.jsx` | `GET /api/alerts`, `PUT /api/alerts/<id>/review` in `routes/alerts.py` | `instructor_alerts` | `AlertService` trigger | Modify alert severity colors or filter tags in `InstructorAlerts.jsx` | Run `pytest backend/tests/test_predictions_recommendations.py::test_alert_lifecycle` |
| **Alert Follow-Up Logs** | `InstructorAlerts.jsx` | `POST /api/alerts/<id>/follow-ups` in `routes/alerts.py` | `alert_follow_ups` | None | Add intervention actions (`peer_tutoring`, `counselor`) | Run `pytest backend/tests/test_predictions_recommendations.py::test_alert_lifecycle` |
| **Cohort Risk Scanner** | `InstructorDashboard.jsx` | `POST /api/alerts/scan` in `routes/alerts.py` | `instructor_alerts` | `AlertService` | Adjust decline trigger rules (e.g. 3 consecutive drops) in `alert_service.py` | Click "Run Early Support Scan" on Instructor Dashboard |
| **Admin System Overview** | `AdminDashboard.jsx` | `GET /api/admin/overview` in `routes/admin_analytics.py` | `users`, `subjects`, `model_versions` | None | Add metric counters in `get_admin_overview` in `admin_analytics.py` | Run `pytest backend/tests/test_admin_datasets.py::test_admin_overview` |
| **User Administration** | `AdminUsers.jsx` | `PUT /api/users/<id>/role`, `PUT /api/users/<id>/status` in `routes/users.py` | `users` | None | Add search filters or bulk operations in `AdminUsers.jsx` | Test changing a user's role and verify permission updates |
| **Dataset Repository** | `AdminDatasets.jsx` | `POST /api/datasets/upload`, `GET /api/datasets/<id>` in `routes/datasets.py`| `dataset_records` | `MLDataPreprocessor.validate_schema` | Edit mandatory feature schema in `backend/ml/preprocessor.py` | Run `pytest backend/tests/test_admin_datasets.py::test_admin_upload_dataset_validation` |
| **Train ML from Dataset** | `AdminDatasets.jsx` | `POST /api/datasets/<id>/train` in `routes/datasets.py` | `model_versions`, `dataset_records` | `MLTrainingPipeline` | Adjust training split ratio or cross-validation folds in `trainer.py` | Run `pytest backend/tests/test_ml_pipeline.py::test_training_pipeline_and_inference` |
| **Model Diagnostics View** | `AdminModelEvaluation.jsx` | `GET /api/models/active` in `routes/models_mgmt.py` | `model_versions` | `MLPredictor` & `evaluator.py` | Customize Confusion Matrix grid or add ROC-AUC metrics | Run `pytest backend/tests/test_admin_datasets.py::test_model_diagnostics_and_candidate_comparison` |
| **Live Model Rollback** | `AdminModelEvaluation.jsx` | `PUT /api/models/<id>/activate` in `routes/models_mgmt.py` | `model_versions` | `MLPredictor.load_version` | Update rollback artifact backup strategy in `predictor.py` | Run `pytest backend/tests/test_admin_datasets.py::test_model_history_and_activation` |
| **Sliding Rate Limiter** | None (Backend Middleware) | `backend/utils/rate_limiter.py` | None | None | Adjust `max_requests` or `window_seconds` in `rate_limiter.py` | Run `pytest backend/tests/test_auth.py::test_rate_limiter_protection` |
| **HTTP Security Headers** | None (Backend Middleware) | `@app.after_request` in `backend/app.py` | None | None | Add Content-Security-Policy (CSP) headers in `backend/app.py` | Run `pytest backend/tests/test_auth.py::test_security_headers_present` |
| **System Readiness Probe** | None (Backend Endpoint) | `GET /api/ready` in `backend/app.py` | None | `MLPredictor.is_ready` | Add Redis or external service checks to probe in `backend/app.py` | Run `pytest backend/tests/test_auth.py::test_readiness_probe` |

---

## 8. Authentication, Role Permissions & Access Control

### 8.1 JWT Token Architecture & Specification

1. **Generation:** When a user logs in via `POST /api/auth/login`:
   - Password is verified using `check_password_hash(user.password_hash, password)`.
   - JWT is signed using `jwt.encode` with `algorithm='HS256'` and `JWT_SECRET_KEY`.
   - **Payload Format:**
     ```json
     {
       "sub": "4",
       "username": "student_alex",
       "role": "student",
       "exp": 1793182676,
       "iat": 1793096276
     }
     ```
     *(Note: `sub` conforms to RFC 7519 by being an explicit string format).*

2. **Backend Authentication Decorator (`@token_required`):**
   Located in [`backend/utils/decorators.py`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/backend/utils/decorators.py):
   - Reads `Authorization: Bearer <token>` header.
   - Decodes token, validates expiration, extracts user ID via `int(payload.get('sub'))`.
   - Fetches active user using `db.session.get(User, user_id)`.
   - Attaches authenticated user to `request.current_user`.

3. **Backend Authorization Decorator (`@roles_required(*allowed_roles)`):**
   - Verifies `request.current_user.role in allowed_roles`.
   - If unauthorized, immediately rejects the request with HTTP `403 Forbidden`:
     ```json
     {"error": "Access forbidden: required role one of ['instructor', 'admin'], but you have student"}
     ```

---

### 8.2 Strict Class & Subject Isolation Rules

To protect student privacy and preserve academic integrity:
1. **Student Isolation:** Students can only view their own grades (`/api/assessments/my-results`), predictions (`/api/predictions/my-predictions`), and study tasks. Attempting to query another student's ID returns HTTP `403 Forbidden`.
2. **Instructor Subject Ownership:**
   - Instructors can only create assessments, record marks, and import CSV gradebooks for subjects where `subject.instructor_id == request.current_user.id`.
   - Attempting to record marks or run batch predictions on another instructor's subject returns HTTP `403 Forbidden`.
3. **Admin Privilege:** Admins have global administrative privileges across all subjects, users, datasets, and models.

---

## 9. Running, Debugging & Maintenance

### 9.1 Local Development Commands (Windows)

#### Step 1: Initialize Python Virtual Environment & Install Dependencies
Open PowerShell or Command Prompt in the repository root:
```powershell
# Create virtual environment if not already created
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
# (or in cmd: venv\Scripts\activate.bat)

# Install backend dependencies
pip install -r backend/requirements.txt
```

#### Step 2: Seed the Database & Train Initial Baseline Model
```powershell
# Set PYTHONPATH and run database seeder
cmd /c "set PYTHONPATH=. && venv\Scripts\python backend\seed_data.py"
```

#### Step 3: Run the Backend Flask API Server
```powershell
cmd /c "set PYTHONPATH=. && venv\Scripts\python backend\app.py"
# Flask starts on http://localhost:5000
```

#### Step 4: Run the Frontend Development Server
Open a second terminal:
```powershell
cd frontend
npm install
npm run dev
# Vite starts on http://localhost:5173
```

---

### 9.2 Pre-Configured Demo Accounts for Testing

| Username | Password | Role | Assigned Curriculum / Context |
|---|---|---|---|
| `admin` | `AdminPass123!` | `admin` | Full system administrator, dataset management, model rollback |
| `dr_smith` | `InstructorPass123!` | `instructor` | Lead instructor for `CS101` (Data Structures & Algorithms) |
| `prof_davis` | `InstructorPass123!` | `instructor` | Lead instructor for `MATH201` (Linear Algebra) |
| `student_alex` | `StudentPass123!` | `student` | High-performing student profile with completed coursework |
| `student_maya` | `StudentPass123!` | `student` | Moderate-risk student profile |
| `student_liam` | `StudentPass123!` | `student` | High-difficulty risk profile with repeated errors & alert triggers |
| `student_zoe` | `StudentPass123!` | `student` | Student with sparse records (ideal for testing insufficient data) |

---

### 9.3 Inspecting Logs & Diagnosing Issues

1. **Checking System Health & Readiness:**
   - Open browser or execute:
     ```bash
     curl http://localhost:5000/api/health
     curl http://localhost:5000/api/ready
     ```
   - Expect: `{"database": "connected", "model_ready": true, "status": "ready"}` with HTTP `200`.

2. **Frontend Debugging via Browser DevTools:**
   - **Console Tab:** Inspect for uncaught React errors or network failures.
   - **Network Tab:** Inspect `/api/*` fetch calls. Click any request to view:
     - Request Headers: Verify `Authorization: Bearer <token>` is present.
     - Payload: Verify JSON structure.
     - Response: Inspect backend error messages (e.g. validation errors or 422 codes).

3. **Backend Terminal Logs:**
   - Every incoming route prints the HTTP verb, path, and status code (e.g., `"POST /api/predictions/predict HTTP/1.1" 201`).
   - If an exception occurs, the full Python traceback prints in the backend terminal with file and line numbers.

---

## 10. Step-by-Step Developer Modification Tutorials

### Tutorial 1: Changing a Page Title or Header Text
**Scenario:** You want to change the title on the Student Curriculum page from `"Curriculum & Topics"` to `"Course Syllabus & Modules"`.

1. Open [`frontend/src/pages/student/StudentSubjects.jsx`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/frontend/src/pages/student/StudentSubjects.jsx).
2. Locate line 73:
   ```jsx
   <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Curriculum & Topics</h1>
   ```
3. Change to:
   ```jsx
   <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Course Syllabus & Modules</h1>
   ```
4. Save the file. Vite hot module replacement (HMR) immediately updates the browser view without refreshing.

---

### Tutorial 2: Changing Website Colors & Branding
**Scenario:** You want to change the platform primary accent color from Indigo to Emerald.

1. Open [`frontend/tailwind.config.js`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/frontend/tailwind.config.js).
2. In the theme configuration, you can alias `primary` to the `emerald` color space:
   ```javascript
   theme: {
     extend: {
       colors: {
         primary: colors.emerald,
       }
     }
   }
   ```
3. In [`frontend/src/components/Sidebar.jsx`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/frontend/src/components/Sidebar.jsx) and [`Navbar.jsx`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/frontend/src/components/Navbar.jsx), replace instances of `bg-indigo-600` and `text-indigo-600` with `bg-emerald-600` and `text-emerald-600`.

---

### Tutorial 3: Adding a Dashboard KPI Card
**Scenario:** You want to add a `"Total Study Hours"` card to the Student Dashboard.

1. Open [`frontend/src/pages/student/StudentDashboard.jsx`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/frontend/src/pages/student/StudentDashboard.jsx).
2. In the component, calculate total study hours from `results`:
   ```javascript
   const totalStudyHours = Math.round(
     results.reduce((acc, r) => acc + (r.study_time_minutes || 0), 0) / 60
   );
   ```
3. In the `<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">` card grid, add:
   ```jsx
   <StatCard
     title="Total Study Hours"
     value={`${totalStudyHours} hrs`}
     icon={<Clock className="w-5 h-5 text-emerald-600" />}
     change="Logged across coursework"
     changeType="positive"
   />
   ```
4. Test by opening `http://localhost:5173/student/dashboard` and verifying the new card renders cleanly.

---

### Tutorial 4: Modifying a Form (Adding a "Room Number" Field to Subjects)
**Scenario:** You want instructors to specify an optional physical lecture room when creating a subject.

1. **Step A (Database):** Open [`backend/models/academic.py`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/backend/models/academic.py). Add to the `Subject` class:
   ```python
   room_number = db.Column(db.String(50), nullable=True)
   ```
   Add `'room_number': self.room_number` in `Subject.to_dict()`.
2. **Step B (Backend Controller):** Open [`backend/routes/subjects.py`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/backend/routes/subjects.py). In `create_subject()`:
   ```python
   room_number = data.get('room_number', '').strip()
   subject = Subject(code=code, name=name, description=description, room_number=room_number, instructor_id=...)
   ```
3. **Step C (Frontend Form):** Open [`frontend/src/pages/instructor/InstructorSubjects.jsx`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/frontend/src/pages/instructor/InstructorSubjects.jsx).
   - In state: `const [subjectForm, setSubjectForm] = useState({ code: '', name: '', description: '', room_number: '' });`
   - In the modal JSX, add an input field:
     ```jsx
     <div>
       <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Lecture Room</label>
       <input
         type="text"
         value={subjectForm.room_number}
         onChange={(e) => setSubjectForm({ ...subjectForm, room_number: e.target.value })}
         className="w-full px-3 py-2 border rounded-xl text-sm"
         placeholder="e.g. Science Hall 301"
       />
     </div>
     ```
4. **Step D (Test):** Create a new subject and verify `room_number` persists and displays.

---

### Tutorial 5: Adding a New Backend REST Endpoint
**Scenario:** You want an endpoint that returns the top 3 highest risk topics across all subjects for an instructor.

1. Open [`backend/routes/predictions.py`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/backend/routes/predictions.py).
2. Add the route:
   ```python
   @predictions_bp.route('/highest-risk-topics', methods=['GET'])
   @token_required
   @roles_required('instructor', 'admin')
   def get_highest_risk_topics():
       # Fetch predictions with High difficulty for this instructor's subjects
       taught_subjects = [s.id for s in Subject.query.filter_by(instructor_id=request.current_user.id).all()]
       high_preds = (
           PredictionRecord.query
           .filter(PredictionRecord.subject_id.in_(taught_subjects), PredictionRecord.predicted_difficulty == 'High')
           .order_by(PredictionRecord.difficulty_score.desc())
           .limit(3)
           .all()
       )
       return jsonify({'high_risk_topics': [p.to_dict() for p in high_preds]}), 200
   ```
3. Test using `curl` or in test file with `client.get('/api/predictions/highest-risk-topics', headers=...)`.

---

### Tutorial 6: Updating ML Prediction Logic or Contributing Factors
**Scenario:** You want to add a contributing factor when attendance falls below 70%.

1. Open [`backend/ml/predictor.py`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/backend/ml/predictor.py).
2. Locate line 171 in `predict_features()` where `factors` are constructed.
3. Add:
   ```python
   if float(row['attendance_rate']) < 70.0:
       factors.append({
           'feature': 'attendance_rate',
           'impact': 'High Risk',
           'description': f"Low course attendance/completion ({row['attendance_rate']}%) significantly increases difficulty risk."
       })
   ```
4. Re-run tests:
   ```bash
   cmd /c "set PYTHONPATH=. && venv\Scripts\pytest backend\tests\test_predictions_recommendations.py -v"
   ```

---

### Tutorial 7: Adding a New Feature End-to-End ("Student Study Notes")
**Scenario:** You want students to be able to save personal revision notes for any syllabus topic.

1. **Database:** In `backend/models/support.py`, create model:
   ```python
   class StudentNote(db.Model):
       __tablename__ = 'student_notes'
       id = db.Column(db.Integer, primary_key=True)
       student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
       topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
       content = db.Column(db.Text, nullable=False)
       created_at = db.Column(db.DateTime, default=datetime.utcnow)
       
       def to_dict(self):
           return {'id': self.id, 'topic_id': self.topic_id, 'content': self.content}
   ```
2. **Backend Route:** In a new blueprint or inside `routes/subjects.py`:
   ```python
   @subjects_bp.route('/topics/<int:topic_id>/notes', methods=['POST'])
   @token_required
   @roles_required('student')
   def save_topic_note(topic_id):
       data = request.get_json() or {}
       note = StudentNote(student_id=request.current_user.id, topic_id=topic_id, content=data.get('content', ''))
       db.session.add(note)
       db.session.commit()
       return jsonify({'note': note.to_dict()}), 201
   ```
3. **Frontend Component:** In `StudentSubjects.jsx`, add a textarea under each topic with a "Save Revision Note" button that calls `axiosClient.post('/subjects/topics/${topic.id}/notes', { content })`.
4. **Feedback:** Call `toast.success('Revision note saved!')` when the promise resolves.

---

## 11. Testing, Quality Assurance & Deployment

### 11.1 The Automated Test Suite (29 Tests)

All automated tests are located in `backend/tests/` and pass with 0 failures and 0 deprecation warnings.

| Test File | Test Cases | What Is Verified |
|---|---|---|
| [`test_auth.py`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/backend/tests/test_auth.py) | 10 tests | - User registration & duplicate username rejection<br/>- Login with valid/invalid password<br/>- `/api/auth/me` with JWT Bearer token<br/>- Unauthorized 401 when token omitted<br/>- HTTP security headers (`nosniff`, `SAMEORIGIN`, `1; mode=block`)<br/>- Deep readiness probe (`/api/ready`) database & model checks<br/>- Sliding-window auth rate limiting (HTTP 429) |
| [`test_academic.py`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/backend/tests/test_academic.py) | 5 tests | - Instructor subject creation & modification<br/>- Topic syllabus hierarchy and difficulty level<br/>- Assessment creation and score boundary validation (`marks <= max_marks`)<br/>- Gradebook blank CSV template download (`/api/assessments/template.csv`)<br/>- Instructor subject isolation (unauthorized instructors receive 403 Forbidden) |
| [`test_ml_pipeline.py`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/backend/tests/test_ml_pipeline.py) | 3 tests | - Dataset generation with reproducible random seed<br/>- `MLDataPreprocessor` schema validation and transformation<br/>- Full multi-model training pipeline and held-out test evaluation |
| [`test_predictions_recommendations.py`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/backend/tests/test_predictions_recommendations.py) | 6 tests | - ML difficulty prediction and student data isolation<br/>- Insufficient academic data detection (HTTP 422)<br/>- Study recommendation generation and completion toggle<br/>- Pedagogical recommendation de-duplication on repeated predictions<br/>- Early support alert lifecycle and follow-up logging<br/>- Instructor batch prediction authorization boundary |
| [`test_admin_datasets.py`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/backend/tests/test_admin_datasets.py) | 5 tests | - Admin system overview KPIs<br/>- CSV dataset upload and schema verification<br/>- Rejection of invalid non-CSV files<br/>- Student prohibition from admin endpoints (HTTP 403)<br/>- Model version rollback and live in-memory activation |

#### Running Tests:
```powershell
cmd /c "set PYTHONPATH=. && venv\Scripts\pytest backend\tests -v"
```

---

### 11.2 Frontend Production Build

The frontend is verified to compile cleanly into optimized static assets without warnings or bundle errors:
```powershell
cd frontend
npm run build
```
Output:
- `dist/index.html` (~0.8 kB)
- `dist/assets/index-*.css` (~36 kB gzip: ~6.4 kB)
- `dist/assets/index-*.js` (~782 kB gzip: ~214 kB)

---

### 11.3 Production Deployment Architecture

```mermaid
flowchart TD
    CLIENT[Client Browser] --> NGINX[Nginx Reverse Proxy & SSL Termination]
    
    subgraph Frontend Delivery
        NGINX -- Static / --> DIST[Built React Assets: frontend/dist/]
    end
    
    subgraph Backend Application Cluster
        NGINX -- /api/ --> GUNICORN[Gunicorn WSGI Server<br/>4 Worker Processes]
        GUNICORN --> APP[Flask Application Factory: backend.app:create_app]
    end
    
    subgraph Persistent Storage
        APP <--> PG[(PostgreSQL Database Cluster)]
        APP <--> DISK[(Shared Volume: backend/artifacts/)]
    end
```

#### Production Checklist:
1. Set `SECRET_KEY` and `JWT_SECRET_KEY` to cryptographically secure strings (e.g., generated with `openssl rand -hex 32`).
2. Provide `DATABASE_URL=postgresql://user:password@pg-host:5432/ai_learning_predictor`.
3. Set `CORS_ORIGINS` to your production domain (e.g., `https://learn-predict.edu`).
4. Serve the backend via Gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 "backend.app:create_app()"
   ```
5. Serve the compiled `frontend/dist` directory using Nginx or Caddy with SPA routing fallback:
   ```nginx
   location / {
       try_files $uri $uri/ /index.html;
   }
   location /api/ {
       proxy_pass http://127.0.0.1:5000/api/;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
   }
   ```

---

## 12. Final Developer Reference, Breakage Map & Glossary

### 12.1 Critical Files Index

| Priority | File Path | Why It Is Important |
|---|---|---|
| **1** | [`backend/app.py`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/backend/app.py) | Central backend entry point; configures middlewares, blueprints, and health checks. |
| **2** | [`backend/routes/predictions.py`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/backend/routes/predictions.py) | Core difficulty prediction controller; handles student feature aggregation, 422 errors, and ML calls. |
| **3** | [`backend/ml/predictor.py`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/backend/ml/predictor.py) | Singleton inference engine; validates features, computes difficulty score, loads model versions. |
| **4** | [`frontend/src/App.jsx`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/frontend/src/App.jsx) | Frontend entry and routing hub; mounts providers, layouts, and protected routes. |
| **5** | [`frontend/src/context/AuthContext.jsx`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/frontend/src/context/AuthContext.jsx) | Handles client session, JWT token persistence, and role verification. |
| **6** | [`backend/models/academic.py`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/backend/models/academic.py) | Defines the educational data core: Subjects, Topics, Assessments, and Results. |
| **7** | [`backend/services/recommendation_service.py`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/backend/services/recommendation_service.py) | Pedagogical logic that maps predicted bottlenecks to actionable study tasks. |
| **8** | [`frontend/src/pages/student/StudentSubjects.jsx`](file:///C:/Users/LENOVO/Desktop/AI%20Learning%20Difficulty%20predictor/frontend/src/pages/student/StudentSubjects.jsx) | Primary interactive student workflow where predictions are triggered. |

---

### 12.2 Dependency & Breakage Map (What Could Break If You Edit a File)

```mermaid
flowchart TD
    MODELS[backend/models/*.py] --> ROUTES[backend/routes/*.py]
    MODELS --> SEED[backend/seed_data.py]
    MODELS --> TESTS[backend/tests/*.py]
    
    PREPROC[backend/ml/preprocessor.py] --> TRAIN[backend/ml/trainer.py]
    PREPROC --> PRED[backend/ml/predictor.py]
    PREPROC --> DATASET_ROUTE[backend/routes/datasets.py]
    
    PRED --> PRED_ROUTE[backend/routes/predictions.py]
    PRED --> APP[backend/app.py]
    
    ROUTES --> AXIOS[frontend/src/api/axiosClient.js]
    AXIOS --> PAGES[frontend/src/pages/**/*.jsx]
    
    AUTH_CTX[frontend/src/context/AuthContext.jsx] --> PROT_ROUTE[frontend/src/components/ProtectedRoute.jsx]
    PROT_ROUTE --> APP_JSX[frontend/src/App.jsx]
```

- **If you change a database model column in `backend/models/*.py`:**
  - You must update the model's `to_dict()` method.
  - You must update any route handler that inserts or reads that column.
  - If using SQLite locally, you must run a migration or re-seed `app.db`.
- **If you change feature names in `backend/ml/preprocessor.py`:**
  - The trained `model.joblib` and `preprocessor.joblib` will expect the old schema and fail.
  - You must retrain the model pipeline via `seed_data.py` or the Admin Dataset training view.
  - You must update `compute_student_topic_features` in `backend/routes/predictions.py`.
- **If you change the JWT payload keys in `backend/routes/auth.py`:**
  - You must update `user` state parsing in `frontend/src/context/AuthContext.jsx`.
  - You must update the `@token_required` decorator in `backend/utils/decorators.py`.

---

### 12.3 The Safest Development Workflow

To safely modify any part of the application without introducing regressions:

```
[1. INSPECT] --> Read the existing component, route, and model definitions before modifying.
     │
[2. EDIT]    --> Apply changes to models, routes, or frontend pages using small, cohesive edits.
     │
[3. TEST]    --> Run the pytest suite: cmd /c "set PYTHONPATH=. && venv\Scripts\pytest backend\tests -v"
     │
[4. BUILD]   --> Test the frontend production compilation: cd frontend && npm run build
     │
[5. VERIFY]  --> Open browser, test the feature end-to-end as Student, Instructor, and Admin.
```

---

### 12.4 Beginner-Friendly Technical Glossary

- **Blueprint:** A Flask mechanism for organizing an application into modular, independent route folders (e.g. `auth`, `assessments`, `predictions`).
- **Cross-Validation (CV):** An ML technique that splits data into multiple folds (e.g. 5 folds) to train and test candidate models multiple times, ensuring the model generalizes well and does not overfit.
- **F1-Score (Macro):** The harmonic mean of precision and recall calculated across all classes with equal weight. It is the gold standard for multi-class classification where classes may be imbalanced.
- **Held-Out Test Set:** A portion of data (20%, or 600 samples) completely hidden from candidate models during training, used solely to compute honest, unbiased final evaluation metrics.
- **JWT (JSON Web Token):** A cryptographically signed string passed in the HTTP `Authorization` header that proves the user's identity without requiring the backend to store server-side session files.
- **Log-Loss / Cross-Entropy:** A metric that measures the quality of predicted probabilities rather than just the final discrete class label. Lower log-loss indicates well-calibrated confidence scores.
- **One-Hot Encoding (OHE):** Converting categorical text (e.g. `beginner`, `intermediate`, `advanced`) into numeric binary vectors (`[1,0,0]`, `[0,1,0]`, `[0,0,1]`) so machine learning algorithms can process them.
- **ORM (Object-Relational Mapping):** A software library (SQLAlchemy) that allows you to interact with database tables using Python classes and objects instead of writing raw SQL strings.
- **Protected Route:** A frontend route wrapped in a security guard that blocks unauthenticated users or users with incorrect roles from viewing a page.
- **Singleton Pattern:** A software design pattern ensuring that a class (such as `MLPredictor`) only has one shared in-memory instance throughout the server's lifecycle, preventing redundant disk reads.
- **Stateless Authentication:** An architecture where the server does not store active session records; each request contains all necessary authentication information in the JWT token.
- **Vite:** A modern, high-speed frontend build tool and dev server that uses native ES modules to provide instant hot-reloading during development.

