# AI Learning Difficulty Predictor
**A Production-Oriented Full-Stack Educational Analytics Platform with Genuine Machine Learning**

---

## 1. Executive Summary

**AI Learning Difficulty Predictor** is a full-stack educational web application engineered to identify subjects and syllabus topics that students may find difficult to understand.Rather than using arbitrary rules or random numbers, the platform employs a trained, cross-validated, and held-out evaluated Machine Learning pipeline that analyzes multidimensional student learning data:

- Formative and summative assessment marks (quizzes, assignments, exams)
- Attempt frequency and re-submission counts
- Systematic repeated mistakes and error patterns
- Weekly study duration and task completion pacing
- Prerequisite topic mastery and learning pace trajectory
- Topic complexity levels (beginner, intermediate, advanced)

The application provides:
- **Interpretable Difficulty Severity Scores (0–100%)** categorized into `Low`, `Moderate`, and `High` risk.
- **Calibrated Outcome Probabilities** with feature sensitivity explanations.
- **Personalized, Actionable Study Recommendations** directly linked to course objectives and resources.
- **Early Support Alert System** allowing instructors to flag declining trends, log interventions, and track outcomes.
- **Admin ML Operations Dashboard** for dataset validation, multi-model benchmarks, confusion matrix visualization, and version activation.

---

## 2. Technology Stack

### Frontend
- **Framework:** React.js 18 + Vite 5
- **Styling:** Tailwind CSS with responsive layout and accessible contrast
- **Routing:** React Router DOM 6 with role-guarded protected routes
- **Visualization:** Recharts (responsive line charts, bar charts, confusion matrices)
- **Icons:** Lucide React
- **HTTP Client:** Axios with JWT request interceptors and 401 session expiration handling
- **State Management:** React Context API (`AuthContext`)

### Backend & API
- **Framework:** Python Flask 3.1
- **Architecture:** Blueprint-based modular RESTful API architecture
- **Database ORM:** Flask-SQLAlchemy 3.1 (SQLite for development / PostgreSQL production-ready)
- **Security & Auth:** PyJWT (HMAC-SHA256, RFC 7519 string subjects, 24h expiration), Werkzeug scrypt password hashing
- **CORS:** Flask-Cors with configurable allowed origins

### Machine Learning Engine
- **Libraries:** Scikit-Learn 1.7, Pandas 2.3, NumPy 2.2, Scipy 1.15
- **Persistence:** Joblib
- **Validation:** 5-Fold Stratified Cross-Validation on training data + 20% held-out test evaluation
- **Algorithms Evaluated:** Logistic Regression (L2 multinomial), Random Forest Classifier, Decision Tree Classifier

---

## 3. Machine Learning Architecture & Evaluation Report

### 3.1 Feature Matrix
The model ingests 10 standardized features:
1. `quiz_score` (float, 0–100): Average score on formative quizzes.
2. `assignment_score` (float, 0–100): Average score on practical coursework.
3. `exam_score` (float, 0–100): Performance on comprehensive exams.
4. `study_time_weekly` (float, 1–28 hours): Dedicated self-study time per week.
5. `attendance_rate` (float, 40–100%): Class attendance and completion percentage.
6. `attempt_count` (int, 1–6): Number of attempts required to complete assignments.
7. `repeated_errors_count` (int, 0–15): Frequency of recurring mistakes on identical concepts.
8. `previous_topic_score` (float, 0–100): Prerequisite topic mastery.
9. `learning_pace_gap` (float, -30 to +30): Relative lag or acceleration vs expected schedule.
10. `topic_difficulty_level` (categorical: `beginner`, `intermediate`, `advanced`): One-hot encoded.

**Target Label:** `difficulty_category` (`Low`, `Moderate`, `High`)

### 3.2 Model Benchmark & Validation Results
Trained on 2,400 samples and evaluated on 600 held-out test samples with 5-fold cross-validation:

| Candidate Algorithm | 5-Fold CV F1-Macro | Test Accuracy | Test F1-Macro | Test Precision (Macro) | Test Recall (Macro) |
|---|---|---|---|---|---|
| **Logistic Regression (Selected)** | **0.9080 ± 0.0111** | **93.83%** | **0.9280** | **0.9256** | **0.9309** |
| Random Forest (120 trees) | 0.8910 ± 0.0095 | 92.17% | 0.9096 | 0.9064 | 0.9143 |
| Decision Tree (depth=6) | 0.8576 ± 0.0156 | 88.83% | 0.8695 | 0.8678 | 0.8718 |

### 3.3 Confusion Matrix (Held-Out Test Set: N = 600)
```
                  Predicted Low    Predicted Moderate    Predicted High
True Low               252                 11                   0
True Moderate            6                120                   9
True High                0                 11                 191
```

### 3.4 Per-Class Classification Report
- **Low Difficulty:** Precision: `97.7%`, Recall: `95.8%`, F1-Score: `96.7%` (Support: 263)
- **Moderate Difficulty:** Precision: `84.5%`, Recall: `88.9%`, F1-Score: `86.6%` (Support: 135)
- **High Difficulty:** Precision: `95.5%`, Recall: `94.6%`, F1-Score: `95.0%` (Support: 202)
- **Macro Average:** Precision: `92.6%`, Recall: `93.1%`, F1-Score: `92.8%`
- **Weighted Average:** Precision: `94.0%`, Recall: `93.8%`, F1-Score: `93.9%`

### 3.5 Feature Importance Sensitivity
1. `quiz_score` (Weight: 2.261)
2. `exam_score` (Weight: 1.624)
3. `assignment_score` (Weight: 1.448)
4. `repeated_errors_count` (Weight: 1.230)
5. `study_time_weekly` (Weight: 0.975)
6. `attempt_count` (Weight: 0.932)
7. `previous_topic_score` (Weight: 0.616)
8. `learning_pace_gap` (Weight: 0.235)

---

## 4. Role-Based Permissions

| Capability | Student | Instructor | Admin |
|---|:---:|:---:|:---:|
| Personal Dashboard & Progress Tracking | Yes | Own | System |
| View Own Grades & Predictions | Yes | Cohort | All |
| On-Demand Topic Difficulty Prediction | Yes (Self) | Cohort Students | All |
| Complete Study Recommendations | Yes | Monitor | Monitor |
| Manage Subjects & Topics (CRUD) | - | Yes (Assigned) | Yes (All) |
| Create Quizzes, Assignments, Exams | - | Yes | Yes |
| Record Marks & CSV Gradebook Bulk Import | - | Yes | Yes |
| Trigger Early Support Alerts & Follow-Ups | - | Yes | Yes |
| Manage Platform Users & Assign Roles | - | - | Yes |
| Upload & Validate CSV Datasets | - | - | Yes |
| Trigger ML Training & Model Activation | - | - | Yes |
| Inspect Confusion Matrix & System Audit | - | - | Yes |

---

## 5. Seed Demo Accounts

The application includes realistic sample data seeded into the database:

| Role | Username | Email | Password |
|---|---|---|---|
| **Administrator** | `admin` | `admin@university.edu` | `AdminPass123!` |
| **Instructor** | `dr_smith` | `sarah.smith@university.edu` | `InstructorPass123!` |
| **Instructor** | `prof_davis` | `alan.davis@university.edu` | `InstructorPass123!` |
| **Student (Excelling)** | `student_alex` | `alex.miller@student.edu` | `StudentPass123!` |
| **Student (Moderate)** | `student_maya` | `maya.patel@student.edu` | `StudentPass123!` |
| **Student (Needs Support)** | `student_liam` | `liam.chen@student.edu` | `StudentPass123!` |
| **Student** | `student_zoe` | `zoe.taylor@student.edu` | `StudentPass123!` |

*(One-click demo login buttons are also available on the Login screen for instant access).*

---

## 6. Installation & Quick Start

### 6.1 Prerequisites
- Python 3.10+
- Node.js 18+ and npm 9+

### 6.2 Setup Backend Environment
```bash
# Clone the repository and navigate to the project directory
cd "AI Learning Difficulty predictor"

# Create and activate virtual environment
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# Install Python backend dependencies
pip install -r backend/requirements.txt
```

### 6.3 Initialize Database and Train Baseline ML Model
```bash
# Windows PowerShell:
$env:PYTHONPATH="."
python backend/seed_data.py

# Linux/macOS:
PYTHONPATH=. python backend/seed_data.py
```
*This command creates the database tables, seeds demo users, curriculum subjects, student submissions, generates 3,000 synthetic training samples, benchmarks candidate algorithms, and exports the production model artifact.*

### 6.4 Setup Frontend
```bash
cd frontend
npm install
npm run build
cd ..
```

---

## 7. Running the Application

### Start the Backend Server (Port 5000)
```bash
# In your project root with venv activated:
# Windows PowerShell:
$env:PYTHONPATH="."
python backend/app.py

# Linux/macOS:
PYTHONPATH=. python backend/app.py
```
*Backend runs on `http://127.0.0.1:5000` with API health check at `http://127.0.0.1:5000/api/health`.*

### Start the Frontend Dev Server (Port 5173)
```bash
# In a new terminal window:
cd frontend
npm run dev
```
*Access the web application in your browser at `http://localhost:5173`.*

---

## 8. Automated Testing

A full automated test suite using `pytest` is included in `backend/tests/`:

```bash
# Windows PowerShell:
$env:PYTHONPATH="."
pytest backend/tests -v

# Linux/macOS:
PYTHONPATH=. pytest backend/tests -v
```

### Test Coverage Summary:
```
backend/tests/test_academic.py::test_subject_crud_by_instructor PASSED
backend/tests/test_academic.py::test_topic_crud PASSED
backend/tests/test_academic.py::test_assessment_creation_and_result_validation PASSED
backend/tests/test_admin_datasets.py::test_admin_overview PASSED
backend/tests/test_admin_datasets.py::test_admin_upload_dataset_validation PASSED
backend/tests/test_admin_datasets.py::test_reject_invalid_file_type PASSED
backend/tests/test_admin_datasets.py::test_student_forbidden_from_admin_datasets PASSED
backend/tests/test_auth.py::test_register_success PASSED
backend/tests/test_auth.py::test_register_duplicate_username PASSED
backend/tests/test_auth.py::test_login_success PASSED
backend/tests/test_auth.py::test_login_invalid_password PASSED
backend/tests/test_auth.py::test_get_current_user_me PASSED
backend/tests/test_auth.py::test_unauthorized_without_token PASSED
backend/tests/test_ml_pipeline.py::test_dataset_generation PASSED
backend/tests/test_ml_pipeline.py::test_preprocessor_validation PASSED
backend/tests/test_ml_pipeline.py::test_training_pipeline_and_inference PASSED
backend/tests/test_predictions_recommendations.py::test_prediction_and_isolation PASSED
backend/tests/test_predictions_recommendations.py::test_recommendation_completion PASSED
backend/tests/test_predictions_recommendations.py::test_alert_lifecycle PASSED
====================== 19 passed in 20.26s =======================
```

---

## 9. REST API Reference

### System Health & Readiness
- `GET /api/health` — Basic ping returning database and ML model readiness status.
- `GET /api/ready` — Deep readiness probe verifying database query execution and loaded predictor artifacts.

### Authentication
- `POST /api/auth/register` — Register a new account (`username`, `email`, `password`, `full_name`, `role`). Protected by sliding-window rate limiting.
- `POST /api/auth/login` — Authenticate and receive signed JWT. Protected by sliding-window rate limiting.
- `GET /api/auth/me` — Retrieve active authenticated user profile.
- `POST /api/auth/logout` — Invalidate user session.

### Academic Curriculum & Assessments
- `GET /api/subjects` — List curriculum subjects.
- `POST /api/subjects` — Create a new subject (Instructor/Admin).
- `GET /api/subjects/<id>` — Get subject details with topic syllabus.
- `POST /api/subjects/<id>/topics` — Create topic under subject.
- `PUT /api/subjects/topics/<id>` — Modify topic parameters.
- `DELETE /api/subjects/topics/<id>` — Remove topic.
- `GET /api/assessments` — List quizzes, assignments, and exams.
- `POST /api/assessments` — Create assessment with max marks, weightage, passing marks.
- `POST /api/assessments/<id>/results` — Record student grade with study time and attempts.
- `POST /api/assessments/<id>/import-results` — Batch import grades from CSV with duplicate detection.
- `GET /api/assessments/template.csv` — Download blank CSV gradebook template.
- `GET /api/assessments/my-results` — Student's personal gradebook records.

### Machine Learning Predictions & Recommendations
- `POST /api/predictions/predict` — Execute difficulty inference for student/topic.
- `GET /api/predictions/my-predictions` — Current student's historical predictions.
- `GET /api/predictions/student/<id>` — Instructor view of student predictions.
- `POST /api/predictions/batch-predict-topic/<id>` — Cohort-wide prediction for all enrolled students.
- `GET /api/recommendations/my-recommendations` — Fetch study recommendations (filter by `status=pending|completed`).
- `PUT /api/recommendations/<id>/complete` — Mark study task completed.

### Early Support Alerts
- `GET /api/alerts` — List support alerts (filter by `severity`, `is_reviewed`).
- `PUT /api/alerts/<id>/review` — Mark alert reviewed.
- `POST /api/alerts/<id>/follow-ups` — Record follow-up mentoring action and outcome.
- `POST /api/alerts/scan` — Cohort scan for declining performance and consecutive failures.

### Admin & ML Diagnostics
- `GET /api/admin/overview` — Platform KPI statistics and active model state.
- `GET /api/datasets` — List dataset inventory.
- `POST /api/datasets/upload` — Upload CSV dataset with schema validation.
- `GET /api/datasets/<id>` — Dataset schema summary and first 10 rows preview.
- `POST /api/datasets/<id>/train` — Train candidate models and activate best model.
- `GET /api/models/active` — Real evaluation report, confusion matrix, feature importances.
- `GET /api/models/history` — All model versions and comparison.
- `PUT /api/models/<id>/activate` — Switch active production model version.

---

## 10. Repository File Structure

```
AI Learning Difficulty predictor/
├── backend/
│   ├── app.py                     # Flask application factory, error handling & health route
│   ├── config.py                  # Configuration loader (SQLite/Postgres, JWT, upload limits)
│   ├── extensions.py              # SQLAlchemy & CORS extensions
│   ├── seed_data.py               # Database seeder with realistic demo data & ML baseline training
│   ├── requirements.txt           # Python dependency specification
│   ├── models/
│   │   ├── __init__.py            # Model registry
│   │   ├── user.py                # User entity with scrypt hashing & role authorization
│   │   ├── academic.py            # Subject, Topic, Assessment, StudentAssessmentResult
│   │   ├── ml_records.py          # PredictionRecord, ModelVersion, DatasetRecord
│   │   └── support.py             # StudyRecommendation, InstructorAlert, AlertFollowUp, AuditEvent
│   ├── routes/
│   │   ├── __init__.py            # Blueprint registration helper
│   │   ├── auth.py                # Registration, login, profile endpoints
│   │   ├── users.py               # User directory, role assignment, status toggling
│   │   ├── subjects.py            # Subjects and syllabus topics CRUD
│   │   ├── assessments.py         # Assessments management, grade entry, CSV bulk import
│   │   ├── predictions.py         # On-demand and batch ML difficulty inference
│   │   ├── recommendations.py     # Actionable study recommendations & completion tracking
│   │   ├── alerts.py              # Early support alerts, follow-up logs, cohort scan
│   │   ├── progress.py            # Longitudinal progress trends & timeline aggregation
│   │   ├── datasets.py            # Admin dataset uploads, schema checks, preview
│   │   ├── models_mgmt.py         # ML diagnostics, multi-model evaluation, activation
│   │   └── admin_analytics.py     # Platform-wide statistics & audit logs
│   ├── ml/
│   │   ├── __init__.py            # ML package interface
│   │   ├── dataset_generator.py   # Reproducible synthetic educational dataset generator
│   │   ├── preprocessor.py        # Schema validation, missing value imputation, scaling, OHE
│   │   ├── evaluator.py           # Metrics computation (accuracy, macro F1, confusion matrix)
│   │   ├── trainer.py             # Stratified K-Fold CV pipeline benchmarking candidate algorithms
│   │   └── predictor.py           # Thread-safe singleton inference engine with explainability
│   ├── artifacts/                 # Active models, preprocessors, evaluation reports
│   │   ├── model.joblib           # Active scikit-learn model artifact
│   │   ├── preprocessor.joblib    # Fitted ColumnTransformer pipeline
│   │   ├── evaluation_report.json # Genuine metrics, confusion matrix & feature importances
│   │   └── versions/              # Versioned model artifacts for zero-downtime rollback
│   ├── data/                      # Persistent SQLite database & training datasets
│   └── tests/                     # Automated pytest suite (29 test cases)
│       ├── conftest.py            # Test database fixture, mock users & JWT tokens
│       ├── test_auth.py           # Registration, login, rate limiting, security headers, readiness
│       ├── test_academic.py       # Subject, topic, assessment validation & instructor isolation
│       ├── test_ml_pipeline.py    # Preprocessing, training, inference tests
│       ├── test_predictions_recommendations.py # Prediction, insufficient data, deduplication, alerts
│       └── test_admin_datasets.py # CSV upload, validation, rejection, model activation tests
├── frontend/
│   ├── package.json               # Node.js dependencies (React, Vite, Tailwind, Recharts, Lucide)
│   ├── vite.config.js             # Vite configuration with API proxy to port 5000
│   ├── tailwind.config.js         # Tailwind styling tokens & theme colors
│   ├── postcss.config.js          # PostCSS configuration
│   ├── index.html                 # HTML5 document template
│   └── src/
│       ├── main.jsx               # React entry point
│       ├── App.jsx                # Router & role-based protected route definitions
│       ├── index.css              # Tailwind base layer & custom scrollbar styles
│       ├── api/
│       │   └── axiosClient.js     # Axios instance with JWT interceptor & 401 redirect
│       ├── context/
│       │   ├── AuthContext.jsx    # Session provider (login, register, logout, role check)
│       │   └── ToastContext.jsx   # Non-blocking reactive toast provider
│       ├── components/
│       │   ├── Navbar.jsx         # Responsive navigation bar with role badges & profile menu
│       │   ├── Sidebar.jsx        # Role-aware collapsible sidebar navigation
│       │   ├── StatCard.jsx       # Metric KPI card component
│       │   ├── Modal.jsx          # Accessible modal dialog
│       │   ├── ConfirmDialog.jsx  # Accessible confirmation modal for destructive operations
│       │   ├── LoadingSkeleton.jsx# Animated loading skeletons for cards, tables, charts
│       │   └── ProtectedRoute.jsx # Route guard enforcing authentication and role permissions
│       └── pages/
│           ├── Login.jsx          # Login view with 1-click student/instructor/admin demo profiles
│           ├── Register.jsx       # User registration with role selection
│           ├── student/
│           │   ├── StudentDashboard.jsx     # Overview, enrolled subjects, recent predictions
│           │   ├── StudentSubjects.jsx      # Topic syllabus with on-demand AI prediction modal
│           │   ├── StudentTopicAnalysis.jsx # Topic difficulty bar chart & explainable factors
│           │   ├── StudentRecommendations.jsx # Actionable study tasks with completion toggles
│           │   └── StudentProgress.jsx      # Longitudinal performance trends & prediction history
│           ├── instructor/
│           │   ├── InstructorDashboard.jsx     # Cohort overview, alert summaries, scan trigger
│           │   ├── InstructorSubjects.jsx      # Curriculum & topic CRUD, batch prediction
│           │   ├── InstructorAssessments.jsx   # Gradebook, assessment creation, CSV import
│           │   ├── InstructorStudentDetail.jsx # Individual student deep dive & custom prediction
│           │   └── InstructorAlerts.jsx        # Early support dashboard & follow-up action logs
│           └── admin/
│               ├── AdminDashboard.jsx          # System overview, active ML model snapshot
│               ├── AdminUsers.jsx              # User directory, role assignment, status toggling
│               ├── AdminDatasets.jsx           # Dataset repository, upload schema check, preview
│               └── AdminModelEvaluation.jsx    # Confusion matrix, classification report, retrain
├── .env.example                   # Environment configuration template
├── .gitignore                     # Git exclusion rules
└── README.md                      # Comprehensive project documentation
```

---

## 11. Security & Privacy Safeguards

1. **Authentication & Password Protection:** Passwords are never stored in plaintext; salted and hashed using the modern `scrypt` algorithm via Werkzeug.
2. **Stateless JWT Authorization:** Tokens carry string subjects, signed using HMAC-SHA256 with 24-hour expiration. Every protected endpoint enforces server-side role checks.
3. **Data Isolation:** Students are strictly prohibited from querying or modifying other students' grades, predictions, or recommendations.
4. **Input & Upload Validation:** Maximum upload size is enforced (16 MB). Dataset uploads are strictly validated against a required CSV schema before storage and cannot execute arbitrary server-side code.
5. **No Fake AI:** Predictions stem strictly from the trained and cross-validated machine learning pipeline, returning explainable statistical associations to support learning without making arbitrary claims.

