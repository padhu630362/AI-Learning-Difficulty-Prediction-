import os
import datetime
from backend.app import create_app
from backend.extensions import db
from backend.models.user import User
from backend.models.academic import Subject, Topic, Assessment, StudentAssessmentResult
from backend.models.ml_records import DatasetRecord, ModelVersion, PredictionRecord
from backend.models.support import InstructorAlert, StudyRecommendation, AlertFollowUp
from backend.ml.dataset_generator import generate_educational_dataset
from backend.ml.trainer import MLTrainingPipeline
from backend.ml.predictor import MLPredictor
from backend.services.recommendation_service import RecommendationService
from backend.services.alert_service import AlertService

def seed_database():
    app = create_app()
    with app.app_context():
        print("Initializing database tables...")
        db.create_all()

        # Check if users already exist
        if User.query.filter_by(username='admin').first():
            print("Database already seeded. Skipping initial user creation.")
            return

        print("Creating users...")
        admin = User(
            username='admin',
            email='admin@university.edu',
            full_name='System Administrator',
            role='admin'
        )
        admin.set_password('AdminPass123!')

        instructor1 = User(
            username='dr_smith',
            email='sarah.smith@university.edu',
            full_name='Dr. Sarah Smith',
            role='instructor'
        )
        instructor1.set_password('InstructorPass123!')

        instructor2 = User(
            username='prof_davis',
            email='alan.davis@university.edu',
            full_name='Prof. Alan Davis',
            role='instructor'
        )
        instructor2.set_password('InstructorPass123!')

        student1 = User(
            username='student_alex',
            email='alex.miller@student.edu',
            full_name='Alex Miller',
            role='student'
        )
        student1.set_password('StudentPass123!')

        student2 = User(
            username='student_maya',
            email='maya.patel@student.edu',
            full_name='Maya Patel',
            role='student'
        )
        student2.set_password('StudentPass123!')

        student3 = User(
            username='student_liam',
            email='liam.chen@student.edu',
            full_name='Liam Chen',
            role='student'
        )
        student3.set_password('StudentPass123!')

        student4 = User(
            username='student_zoe',
            email='zoe.taylor@student.edu',
            full_name='Zoe Taylor',
            role='student'
        )
        student4.set_password('StudentPass123!')

        db.session.add_all([admin, instructor1, instructor2, student1, student2, student3, student4])
        db.session.commit()

        print("Creating subjects and topics...")
        cs_subject = Subject(
            code='CS101',
            name='Data Structures & Algorithms',
            description='Fundamental computing concepts including linked structures, trees, algorithm design, and algorithmic complexity.',
            instructor_id=instructor1.id
        )

        math_subject = Subject(
            code='MATH201',
            name='Linear Algebra & Vector Spaces',
            description='Matrices, Gaussian elimination, eigenvalues, eigenvectors, and linear transformations.',
            instructor_id=instructor2.id
        )

        db.session.add_all([cs_subject, math_subject])
        db.session.commit()

        # Topics for CS101
        cs_topics = [
            Topic(
                subject_id=cs_subject.id,
                name='Arrays & Dynamic Lists',
                description='Memory layout of arrays, bounds checking, dynamic resizing amortized analysis.',
                learning_objectives='Understand contiguous memory, time complexity of index access vs insertion.',
                difficulty_level='beginner',
                order_index=1,
                resources='https://en.wikipedia.org/wiki/Dynamic_array'
            ),
            Topic(
                subject_id=cs_subject.id,
                name='Linked Lists & Pointer Manipulation',
                description='Singly and doubly linked lists, pointer mutations, edge cases with null references.',
                learning_objectives='Master pointer referencing, node insertion, cycle detection.',
                difficulty_level='intermediate',
                order_index=2,
                resources='https://en.wikipedia.org/wiki/Linked_list'
            ),
            Topic(
                subject_id=cs_subject.id,
                name='Binary Search Trees & Balancing',
                description='Binary search tree invariant, traversal orders, AVL and Red-Black tree rebalancing.',
                learning_objectives='Implement in-order traversal, rotation operations, search efficiency bounds.',
                difficulty_level='intermediate',
                order_index=3,
                resources='https://en.wikipedia.org/wiki/Binary_search_tree'
            ),
            Topic(
                subject_id=cs_subject.id,
                name='Graph Algorithms & Shortest Path',
                description='Adjacency list/matrix representation, Breadth-First Search, Depth-First Search, and Dijkstra shortest path.',
                learning_objectives='Construct graph graphs, identify connected components, calculate shortest paths with priority queues.',
                difficulty_level='advanced',
                order_index=4,
                resources='https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm'
            ),
        ]

        # Topics for MATH201
        math_topics = [
            Topic(
                subject_id=math_subject.id,
                name='Systems of Linear Equations & Row Reduction',
                description='Row echelon forms, Gaussian elimination, pivot positions, and solution sets.',
                learning_objectives='Solve linear systems using matrix operations and identify free variables.',
                difficulty_level='beginner',
                order_index=1,
                resources='https://en.wikipedia.org/wiki/Gaussian_elimination'
            ),
            Topic(
                subject_id=math_subject.id,
                name='Vector Spaces & Subspaces',
                description='Span, linear independence, basis of a vector space, dimension theorem.',
                learning_objectives='Prove vector space axioms, compute null space and column space bases.',
                difficulty_level='intermediate',
                order_index=2,
                resources='https://en.wikipedia.org/wiki/Vector_space'
            ),
            Topic(
                subject_id=math_subject.id,
                name='Eigenvalues & Diagonalization',
                description='Characteristic polynomial, eigenspaces, geometric and algebraic multiplicity, matrix diagonalization.',
                learning_objectives='Compute eigenvalues of nxn matrices and evaluate matrix powers.',
                difficulty_level='advanced',
                order_index=3,
                resources='https://en.wikipedia.org/wiki/Eigenvalues_and_eigenvectors'
            )
        ]

        db.session.add_all(cs_topics + math_topics)
        db.session.commit()

        print("Creating assessments...")
        today = datetime.date.today()
        cs_assessments = [
            Assessment(
                subject_id=cs_subject.id,
                topic_id=cs_topics[0].id,
                title='Quiz 1: Dynamic Arrays & Big-O',
                assessment_type='quiz',
                max_marks=20.0,
                passing_marks=10.0,
                weightage=0.1,
                assessment_date=today - datetime.timedelta(days=35),
                created_by=instructor1.id
            ),
            Assessment(
                subject_id=cs_subject.id,
                topic_id=cs_topics[1].id,
                title='Assignment 1: Linked List Implementation',
                assessment_type='assignment',
                max_marks=100.0,
                passing_marks=50.0,
                weightage=0.2,
                assessment_date=today - datetime.timedelta(days=25),
                created_by=instructor1.id
            ),
            Assessment(
                subject_id=cs_subject.id,
                topic_id=cs_topics[2].id,
                title='Quiz 2: BST Insertion & Traversals',
                assessment_type='quiz',
                max_marks=25.0,
                passing_marks=12.5,
                weightage=0.1,
                assessment_date=today - datetime.timedelta(days=15),
                created_by=instructor1.id
            ),
            Assessment(
                subject_id=cs_subject.id,
                topic_id=cs_topics[3].id,
                title='Midterm Exam: Data Structures & Graphs',
                assessment_type='exam',
                max_marks=100.0,
                passing_marks=45.0,
                weightage=0.35,
                assessment_date=today - datetime.timedelta(days=5),
                created_by=instructor1.id
            )
        ]

        math_assessments = [
            Assessment(
                subject_id=math_subject.id,
                topic_id=math_topics[0].id,
                title='Quiz 1: Row Reduction Practice',
                assessment_type='quiz',
                max_marks=30.0,
                passing_marks=15.0,
                weightage=0.15,
                assessment_date=today - datetime.timedelta(days=20),
                created_by=instructor2.id
            ),
            Assessment(
                subject_id=math_subject.id,
                topic_id=math_topics[1].id,
                title='Assignment: Subspaces and Basis',
                assessment_type='assignment',
                max_marks=50.0,
                passing_marks=25.0,
                weightage=0.25,
                assessment_date=today - datetime.timedelta(days=8),
                created_by=instructor2.id
            )
        ]

        db.session.add_all(cs_assessments + math_assessments)
        db.session.commit()

        print("Recording student assessment results...")
        # Alex is excelling
        # Maya is intermediate
        # Liam is struggling with Graph Algorithms & BSTs
        # Zoe is doing well in Math, struggling in CS

        results = [
            # Student 1: Alex Miller (Strong student)
            StudentAssessmentResult(student_id=student1.id, assessment_id=cs_assessments[0].id, marks_obtained=19.0, percentage=95.0, study_time_minutes=120, attempt_count=1, repeated_errors_count=0),
            StudentAssessmentResult(student_id=student1.id, assessment_id=cs_assessments[1].id, marks_obtained=92.0, percentage=92.0, study_time_minutes=300, attempt_count=1, repeated_errors_count=1),
            StudentAssessmentResult(student_id=student1.id, assessment_id=cs_assessments[2].id, marks_obtained=24.0, percentage=96.0, study_time_minutes=140, attempt_count=1, repeated_errors_count=0),
            StudentAssessmentResult(student_id=student1.id, assessment_id=cs_assessments[3].id, marks_obtained=88.0, percentage=88.0, study_time_minutes=420, attempt_count=1, repeated_errors_count=1),
            StudentAssessmentResult(student_id=student1.id, assessment_id=math_assessments[0].id, marks_obtained=28.0, percentage=93.3, study_time_minutes=90, attempt_count=1, repeated_errors_count=0),

            # Student 2: Maya Patel (Moderate / steady)
            StudentAssessmentResult(student_id=student2.id, assessment_id=cs_assessments[0].id, marks_obtained=15.0, percentage=75.0, study_time_minutes=90, attempt_count=1, repeated_errors_count=2),
            StudentAssessmentResult(student_id=student2.id, assessment_id=cs_assessments[1].id, marks_obtained=70.0, percentage=70.0, study_time_minutes=180, attempt_count=2, repeated_errors_count=3),
            StudentAssessmentResult(student_id=student2.id, assessment_id=cs_assessments[2].id, marks_obtained=16.0, percentage=64.0, study_time_minutes=110, attempt_count=2, repeated_errors_count=2),
            StudentAssessmentResult(student_id=student2.id, assessment_id=cs_assessments[3].id, marks_obtained=68.0, percentage=68.0, study_time_minutes=250, attempt_count=1, repeated_errors_count=3),

            # Student 3: Liam Chen (Struggling - High Difficulty Risk in Graphs & Trees)
            StudentAssessmentResult(student_id=student3.id, assessment_id=cs_assessments[0].id, marks_obtained=13.0, percentage=65.0, study_time_minutes=70, attempt_count=2, repeated_errors_count=3),
            StudentAssessmentResult(student_id=student3.id, assessment_id=cs_assessments[1].id, marks_obtained=52.0, percentage=52.0, study_time_minutes=120, attempt_count=3, repeated_errors_count=5),
            StudentAssessmentResult(student_id=student3.id, assessment_id=cs_assessments[2].id, marks_obtained=10.0, percentage=40.0, study_time_minutes=60, attempt_count=3, repeated_errors_count=6),
            StudentAssessmentResult(student_id=student3.id, assessment_id=cs_assessments[3].id, marks_obtained=38.0, percentage=38.0, study_time_minutes=150, attempt_count=2, repeated_errors_count=7),

            # Student 4: Zoe Taylor
            StudentAssessmentResult(student_id=student4.id, assessment_id=cs_assessments[0].id, marks_obtained=14.0, percentage=70.0, study_time_minutes=80, attempt_count=1, repeated_errors_count=1),
            StudentAssessmentResult(student_id=student4.id, assessment_id=cs_assessments[1].id, marks_obtained=62.0, percentage=62.0, study_time_minutes=140, attempt_count=2, repeated_errors_count=3),
            StudentAssessmentResult(student_id=student4.id, assessment_id=math_assessments[0].id, marks_obtained=27.0, percentage=90.0, study_time_minutes=160, attempt_count=1, repeated_errors_count=1),
            StudentAssessmentResult(student_id=student4.id, assessment_id=math_assessments[1].id, marks_obtained=44.0, percentage=88.0, study_time_minutes=200, attempt_count=1, repeated_errors_count=1)
        ]
        db.session.add_all(results)
        db.session.commit()

        print("Generating reproducible synthetic dataset and training ML model...")
        dataset_path = os.path.join(app.config['DATA_FOLDER'], 'learning_difficulty_dataset.csv')
        generate_educational_dataset(3000, 42, dataset_path)

        # Register dataset in DatasetRecord
        dataset_record = DatasetRecord(
            filename='learning_difficulty_dataset.csv',
            original_name='learning_difficulty_dataset.csv',
            row_count=3000,
            column_count=11,
            columns_list=[
                'quiz_score', 'assignment_score', 'exam_score', 'study_time_weekly',
                'attendance_rate', 'attempt_count', 'repeated_errors_count',
                'previous_topic_score', 'learning_pace_gap', 'topic_difficulty_level',
                'difficulty_category'
            ],
            validation_status='valid',
            is_active_training_set=True,
            uploaded_by=admin.id
        )
        db.session.add(dataset_record)
        db.session.commit()

        print("Executing ML Training Pipeline on dataset...")
        pipeline = MLTrainingPipeline(artifacts_dir=app.config['ARTIFACTS_FOLDER'])
        version_tag = 'v1.0.0-production-baseline'
        report = pipeline.run_training_pipeline(dataset_path, version_tag=version_tag)

        best_m = report['best_metrics']
        model_version = ModelVersion(
            version_tag=version_tag,
            model_name=report['best_model'],
            algorithm=report['best_model'],
            accuracy=best_m['accuracy'],
            precision_macro=best_m['precision_macro'],
            recall_macro=best_m['recall_macro'],
            f1_macro=best_m['f1_macro'],
            f1_weighted=best_m.get('f1_weighted'),
            confusion_matrix=best_m.get('confusion_matrix'),
            classification_report=best_m.get('classification_report'),
            feature_importances=best_m.get('feature_importances'),
            parameters=best_m.get('hyperparameters'),
            training_sample_count=report['training_sample_count'],
            is_active=True,
            trained_by=admin.id
        )
        db.session.add(model_version)
        db.session.commit()

        # Reload predictor singleton
        predictor = MLPredictor.get_instance(artifacts_dir=app.config['ARTIFACTS_FOLDER'])
        predictor.load_artifacts()

        print("Generating initial predictions and recommendations for students...")
        # Predict for Liam on Binary Search Trees and Graph Algorithms
        from backend.routes.predictions import compute_student_topic_features
        for topic in cs_topics:
            features = compute_student_topic_features(student3.id, topic.id)
            pred_out = predictor.predict_features(features)
            pred_rec = PredictionRecord(
                student_id=student3.id,
                subject_id=cs_subject.id,
                topic_id=topic.id,
                predicted_difficulty=pred_out['predicted_difficulty'],
                difficulty_score=pred_out['difficulty_score'],
                probability_low=pred_out['probability_low'],
                probability_moderate=pred_out['probability_moderate'],
                probability_high=pred_out['probability_high'],
                contributing_factors=pred_out['contributing_factors'],
                model_version=pred_out['model_version']
            )
            db.session.add(pred_rec)
            db.session.commit()
            RecommendationService.generate_recommendations_for_prediction(student3.id, cs_subject.id, topic.id, pred_rec)

        # Predict for Alex on CS topics
        for topic in cs_topics:
            features = compute_student_topic_features(student1.id, topic.id)
            pred_out = predictor.predict_features(features)
            pred_rec = PredictionRecord(
                student_id=student1.id,
                subject_id=cs_subject.id,
                topic_id=topic.id,
                predicted_difficulty=pred_out['predicted_difficulty'],
                difficulty_score=pred_out['difficulty_score'],
                probability_low=pred_out['probability_low'],
                probability_moderate=pred_out['probability_moderate'],
                probability_high=pred_out['probability_high'],
                contributing_factors=pred_out['contributing_factors'],
                model_version=pred_out['model_version']
            )
            db.session.add(pred_rec)
            db.session.commit()
            RecommendationService.generate_recommendations_for_prediction(student1.id, cs_subject.id, topic.id, pred_rec)

        # Predict for Maya
        for topic in cs_topics[:2]:
            features = compute_student_topic_features(student2.id, topic.id)
            pred_out = predictor.predict_features(features)
            pred_rec = PredictionRecord(
                student_id=student2.id,
                subject_id=cs_subject.id,
                topic_id=topic.id,
                predicted_difficulty=pred_out['predicted_difficulty'],
                difficulty_score=pred_out['difficulty_score'],
                probability_low=pred_out['probability_low'],
                probability_moderate=pred_out['probability_moderate'],
                probability_high=pred_out['probability_high'],
                contributing_factors=pred_out['contributing_factors'],
                model_version=pred_out['model_version']
            )
            db.session.add(pred_rec)
            db.session.commit()
            RecommendationService.generate_recommendations_for_prediction(student2.id, cs_subject.id, topic.id, pred_rec)

        print("Evaluating early support alerts...")
        # Trigger alert scans for students
        for s in [student1, student2, student3, student4]:
            AlertService.evaluate_and_generate_alerts(s.id, cs_subject.id, instructor1.id)
            AlertService.evaluate_and_generate_alerts(s.id, math_subject.id, instructor2.id)

        # Add sample follow-up to demonstrate alert lifecycle
        sample_alert = InstructorAlert.query.filter_by(student_id=student3.id, alert_type='repeated_low_score').first()
        if sample_alert:
            AlertFollowUp(
                alert_id=sample_alert.id,
                instructor_id=instructor1.id,
                action_taken="Scheduled 30-minute 1-on-1 tutoring session and assigned guided BST practice worksheet.",
                notes="Student demonstrated good motivation; primary hurdle was pointer mutations in tree recursion.",
                outcome="improved"
            )
            sample_alert.is_reviewed = True
            sample_alert.reviewed_at = datetime.datetime.utcnow()
            db.session.commit()

        print("Database seeded successfully with realistic demo data and trained ML baseline!")

if __name__ == '__main__':
    seed_database()

