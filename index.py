"""
=============================================================================
EitaLearn - Personalized Learning Platform (Mock)
=============================================================================
PURPOSE: This Flask application serves as a mock/prototype of a personalized
         learning platform similar to I-Ready. It demonstrates how adaptive
         learning works: Students take diagnostic tests, the system analyzes
         their strengths/weaknesses, and generates personalized learning
         pathways.

THREE USER ROLES:
  - Student: Takes tests, views personalized reports, follows learning paths
  - Teacher: Monitors student progress, assigns pathways, views class data
  - Admin:   Views school-wide statistics, comparisons, feedback analysis

HOW IT WORKS:
  1. User logs in with role-based credentials
  2. Students take a diagnostic assessment
  3. "AI" analyzes results and identifies strengths, weaknesses, mastery areas
  4. System generates personalized curriculum recommendations
  5. Teachers can monitor and adjust student pathways
  6. Admins see aggregated data, before/after comparisons, and AI-driven insights

TODO: Replace mock data with a real database (PostgreSQL/MySQL)
TODO: Replace the simple login dictionary with proper authentication (OAuth, JWT)
TODO: Connect a real AI/ML model for adaptive learning analysis
TODO: Add real-time WebSocket updates for live progress tracking
=============================================================================
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import random
import json
from datetime import datetime, timedelta

# --- Flask App Setup ---
# Creates the Flask application instance.
# secret_key is needed for session management (storing login state).
# TODO: In production, use a secure random key stored in environment variables
app = Flask(__name__)
app.secret_key = 'eitalearn-mock-secret-key-change-in-production'

# ==========================================================================
# MOCK DATA - All fake data used to simulate the platform
# ==========================================================================
# TODO: Replace all of this with real database models and queries

# --- Login Credentials ---
# Simple dictionary-based auth. Username -> {password, role, name, id}
# TODO: Replace with hashed passwords and a real user database
USERS = {
    'student1': {'password': 'pass123', 'role': 'student', 'name': 'Alex Johnson', 'id': 1},
    'student2': {'password': 'pass123', 'role': 'student', 'name': 'Maria Garcia', 'id': 2},
    'student3': {'password': 'pass123', 'role': 'student', 'name': 'James Wilson', 'id': 3},
    'student4': {'password': 'pass123', 'role': 'student', 'name': 'Sophia Lee', 'id': 4},
    'student5': {'password': 'pass123', 'role': 'student', 'name': 'Ethan Brown', 'id': 5},
    'teacher1': {'password': 'teach123', 'role': 'teacher', 'name': 'Ms. Thompson', 'id': 101},
    'teacher2': {'password': 'teach123', 'role': 'teacher', 'name': 'Mr. Davis', 'id': 102},
    'admin1':   {'password': 'admin123', 'role': 'admin', 'name': 'Dr. Williams', 'id': 201},
}

# --- Subject Definitions ---
# Each subject has an icon, color theme, and list of topics/skills
# TODO: Make this configurable by admins
SUBJECTS = {
    'math': {
        'name': 'Mathematics',
        'icon': '📐',
        'color': '#4A90D9',
        'topics': [
            'Number Sense & Operations',
            'Algebraic Thinking',
            'Geometry & Measurement',
            'Data Analysis & Probability',
            'Fractions & Decimals'
        ]
    },
    'reading': {
        'name': 'Reading & Language Arts',
        'icon': '📖',
        'color': '#E8783A',
        'topics': [
            'Reading Comprehension',
            'Vocabulary & Word Study',
            'Grammar & Mechanics',
            'Writing & Composition',
            'Literary Analysis'
        ]
    },
    'science': {
        'name': 'Science',
        'icon': '🔬',
        'color': '#50B86C',
        'topics': [
            'Life Science',
            'Physical Science',
            'Earth & Space Science',
            'Scientific Method',
            'Data Interpretation'
        ]
    }
}

# --- Mock Student Performance Data ---
# Simulates each student's scores across subjects and topics
# Scores are percentages (0-100)
# TODO: This should come from actual assessment results stored in a database
STUDENT_DATA = {
    1: {  # Alex Johnson
        'name': 'Alex Johnson',
        'grade': '7th Grade',
        'class': 'Period 2 - Ms. Thompson',
        'teacher_id': 101,
        'overall_score': 68,
        'subjects': {
            'math': {
                'overall': 55,
                'diagnostic_taken': True,
                'topics': {
                    'Number Sense & Operations': {'score': 72, 'mastery': 'approaching', 'trend': 'up'},
                    'Algebraic Thinking': {'score': 45, 'mastery': 'below', 'trend': 'flat'},
                    'Geometry & Measurement': {'score': 60, 'mastery': 'approaching', 'trend': 'up'},
                    'Data Analysis & Probability': {'score': 50, 'mastery': 'below', 'trend': 'down'},
                    'Fractions & Decimals': {'score': 48, 'mastery': 'below', 'trend': 'flat'},
                }
            },
            'reading': {
                'overall': 78,
                'diagnostic_taken': True,
                'topics': {
                    'Reading Comprehension': {'score': 85, 'mastery': 'proficient', 'trend': 'up'},
                    'Vocabulary & Word Study': {'score': 70, 'mastery': 'approaching', 'trend': 'up'},
                    'Grammar & Mechanics': {'score': 75, 'mastery': 'approaching', 'trend': 'flat'},
                    'Writing & Composition': {'score': 80, 'mastery': 'proficient', 'trend': 'up'},
                    'Literary Analysis': {'score': 78, 'mastery': 'approaching', 'trend': 'up'},
                }
            },
            'science': {
                'overall': 62,
                'diagnostic_taken': True,
                'topics': {
                    'Life Science': {'score': 70, 'mastery': 'approaching', 'trend': 'up'},
                    'Physical Science': {'score': 55, 'mastery': 'below', 'trend': 'flat'},
                    'Earth & Space Science': {'score': 65, 'mastery': 'approaching', 'trend': 'up'},
                    'Scientific Method': {'score': 58, 'mastery': 'below', 'trend': 'down'},
                    'Data Interpretation': {'score': 62, 'mastery': 'approaching', 'trend': 'flat'},
                }
            }
        },
        # Personalized pathway assignments
        'pathways': [
            {'subject': 'math', 'topic': 'Algebraic Thinking', 'progress': 35, 'assigned_by': 'AI', 'status': 'in_progress'},
            {'subject': 'math', 'topic': 'Fractions & Decimals', 'progress': 20, 'assigned_by': 'AI', 'status': 'in_progress'},
            {'subject': 'science', 'topic': 'Physical Science', 'progress': 10, 'assigned_by': 'Ms. Thompson', 'status': 'in_progress'},
        ],
        # Assessment history for progress tracking
        'assessment_history': [
            {'date': '2026-01-15', 'subject': 'math', 'score': 48},
            {'date': '2026-02-01', 'subject': 'math', 'score': 50},
            {'date': '2026-02-15', 'subject': 'math', 'score': 52},
            {'date': '2026-03-01', 'subject': 'math', 'score': 55},
            {'date': '2026-01-15', 'subject': 'reading', 'score': 70},
            {'date': '2026-02-01', 'subject': 'reading', 'score': 73},
            {'date': '2026-02-15', 'subject': 'reading', 'score': 76},
            {'date': '2026-03-01', 'subject': 'reading', 'score': 78},
            {'date': '2026-01-15', 'subject': 'science', 'score': 55},
            {'date': '2026-02-01', 'subject': 'science', 'score': 58},
            {'date': '2026-02-15', 'subject': 'science', 'score': 60},
            {'date': '2026-03-01', 'subject': 'science', 'score': 62},
        ]
    },
    2: {  # Maria Garcia
        'name': 'Maria Garcia',
        'grade': '7th Grade',
        'class': 'Period 2 - Ms. Thompson',
        'teacher_id': 101,
        'overall_score': 82,
        'subjects': {
            'math': {
                'overall': 88,
                'diagnostic_taken': True,
                'topics': {
                    'Number Sense & Operations': {'score': 92, 'mastery': 'advanced', 'trend': 'up'},
                    'Algebraic Thinking': {'score': 85, 'mastery': 'proficient', 'trend': 'up'},
                    'Geometry & Measurement': {'score': 90, 'mastery': 'advanced', 'trend': 'flat'},
                    'Data Analysis & Probability': {'score': 82, 'mastery': 'proficient', 'trend': 'up'},
                    'Fractions & Decimals': {'score': 91, 'mastery': 'advanced', 'trend': 'up'},
                }
            },
            'reading': {
                'overall': 75,
                'diagnostic_taken': True,
                'topics': {
                    'Reading Comprehension': {'score': 72, 'mastery': 'approaching', 'trend': 'flat'},
                    'Vocabulary & Word Study': {'score': 68, 'mastery': 'approaching', 'trend': 'up'},
                    'Grammar & Mechanics': {'score': 80, 'mastery': 'proficient', 'trend': 'up'},
                    'Writing & Composition': {'score': 78, 'mastery': 'approaching', 'trend': 'up'},
                    'Literary Analysis': {'score': 77, 'mastery': 'approaching', 'trend': 'flat'},
                }
            },
            'science': {
                'overall': 80,
                'diagnostic_taken': True,
                'topics': {
                    'Life Science': {'score': 85, 'mastery': 'proficient', 'trend': 'up'},
                    'Physical Science': {'score': 82, 'mastery': 'proficient', 'trend': 'up'},
                    'Earth & Space Science': {'score': 75, 'mastery': 'approaching', 'trend': 'flat'},
                    'Scientific Method': {'score': 78, 'mastery': 'approaching', 'trend': 'up'},
                    'Data Interpretation': {'score': 80, 'mastery': 'proficient', 'trend': 'up'},
                }
            }
        },
        'pathways': [
            {'subject': 'reading', 'topic': 'Reading Comprehension', 'progress': 55, 'assigned_by': 'AI', 'status': 'in_progress'},
            {'subject': 'reading', 'topic': 'Vocabulary & Word Study', 'progress': 40, 'assigned_by': 'AI', 'status': 'in_progress'},
        ],
        'assessment_history': [
            {'date': '2026-01-15', 'subject': 'math', 'score': 82},
            {'date': '2026-02-01', 'subject': 'math', 'score': 84},
            {'date': '2026-02-15', 'subject': 'math', 'score': 86},
            {'date': '2026-03-01', 'subject': 'math', 'score': 88},
            {'date': '2026-01-15', 'subject': 'reading', 'score': 68},
            {'date': '2026-02-01', 'subject': 'reading', 'score': 70},
            {'date': '2026-02-15', 'subject': 'reading', 'score': 73},
            {'date': '2026-03-01', 'subject': 'reading', 'score': 75},
        ]
    },
    3: {  # James Wilson
        'name': 'James Wilson',
        'grade': '7th Grade',
        'class': 'Period 3 - Mr. Davis',
        'teacher_id': 102,
        'overall_score': 45,
        'subjects': {
            'math': {
                'overall': 42,
                'diagnostic_taken': True,
                'topics': {
                    'Number Sense & Operations': {'score': 50, 'mastery': 'below', 'trend': 'flat'},
                    'Algebraic Thinking': {'score': 35, 'mastery': 'well_below', 'trend': 'down'},
                    'Geometry & Measurement': {'score': 48, 'mastery': 'below', 'trend': 'flat'},
                    'Data Analysis & Probability': {'score': 40, 'mastery': 'well_below', 'trend': 'flat'},
                    'Fractions & Decimals': {'score': 37, 'mastery': 'well_below', 'trend': 'down'},
                }
            },
            'reading': {
                'overall': 50,
                'diagnostic_taken': True,
                'topics': {
                    'Reading Comprehension': {'score': 55, 'mastery': 'below', 'trend': 'up'},
                    'Vocabulary & Word Study': {'score': 45, 'mastery': 'below', 'trend': 'flat'},
                    'Grammar & Mechanics': {'score': 50, 'mastery': 'below', 'trend': 'flat'},
                    'Writing & Composition': {'score': 48, 'mastery': 'below', 'trend': 'flat'},
                    'Literary Analysis': {'score': 52, 'mastery': 'below', 'trend': 'up'},
                }
            },
            'science': {
                'overall': 43,
                'diagnostic_taken': True,
                'topics': {
                    'Life Science': {'score': 48, 'mastery': 'below', 'trend': 'flat'},
                    'Physical Science': {'score': 38, 'mastery': 'well_below', 'trend': 'down'},
                    'Earth & Space Science': {'score': 45, 'mastery': 'below', 'trend': 'flat'},
                    'Scientific Method': {'score': 42, 'mastery': 'well_below', 'trend': 'flat'},
                    'Data Interpretation': {'score': 42, 'mastery': 'well_below', 'trend': 'flat'},
                }
            }
        },
        'pathways': [
            {'subject': 'math', 'topic': 'Algebraic Thinking', 'progress': 15, 'assigned_by': 'AI', 'status': 'in_progress'},
            {'subject': 'math', 'topic': 'Fractions & Decimals', 'progress': 10, 'assigned_by': 'AI', 'status': 'in_progress'},
            {'subject': 'math', 'topic': 'Data Analysis & Probability', 'progress': 5, 'assigned_by': 'Mr. Davis', 'status': 'not_started'},
            {'subject': 'science', 'topic': 'Physical Science', 'progress': 5, 'assigned_by': 'AI', 'status': 'in_progress'},
            {'subject': 'reading', 'topic': 'Vocabulary & Word Study', 'progress': 0, 'assigned_by': 'AI', 'status': 'not_started'},
        ],
        'assessment_history': [
            {'date': '2026-01-15', 'subject': 'math', 'score': 40},
            {'date': '2026-02-01', 'subject': 'math', 'score': 38},
            {'date': '2026-02-15', 'subject': 'math', 'score': 41},
            {'date': '2026-03-01', 'subject': 'math', 'score': 42},
            {'date': '2026-01-15', 'subject': 'reading', 'score': 45},
            {'date': '2026-02-01', 'subject': 'reading', 'score': 47},
            {'date': '2026-02-15', 'subject': 'reading', 'score': 48},
            {'date': '2026-03-01', 'subject': 'reading', 'score': 50},
        ]
    },
    4: {  # Sophia Lee
        'name': 'Sophia Lee',
        'grade': '7th Grade',
        'class': 'Period 2 - Ms. Thompson',
        'teacher_id': 101,
        'overall_score': 91,
        'subjects': {
            'math': {
                'overall': 93,
                'diagnostic_taken': True,
                'topics': {
                    'Number Sense & Operations': {'score': 95, 'mastery': 'advanced', 'trend': 'up'},
                    'Algebraic Thinking': {'score': 92, 'mastery': 'advanced', 'trend': 'up'},
                    'Geometry & Measurement': {'score': 94, 'mastery': 'advanced', 'trend': 'flat'},
                    'Data Analysis & Probability': {'score': 90, 'mastery': 'advanced', 'trend': 'up'},
                    'Fractions & Decimals': {'score': 94, 'mastery': 'advanced', 'trend': 'up'},
                }
            },
            'reading': {
                'overall': 90,
                'diagnostic_taken': True,
                'topics': {
                    'Reading Comprehension': {'score': 92, 'mastery': 'advanced', 'trend': 'up'},
                    'Vocabulary & Word Study': {'score': 88, 'mastery': 'proficient', 'trend': 'up'},
                    'Grammar & Mechanics': {'score': 91, 'mastery': 'advanced', 'trend': 'flat'},
                    'Writing & Composition': {'score': 89, 'mastery': 'proficient', 'trend': 'up'},
                    'Literary Analysis': {'score': 90, 'mastery': 'advanced', 'trend': 'up'},
                }
            },
            'science': {
                'overall': 89,
                'diagnostic_taken': True,
                'topics': {
                    'Life Science': {'score': 92, 'mastery': 'advanced', 'trend': 'up'},
                    'Physical Science': {'score': 88, 'mastery': 'proficient', 'trend': 'up'},
                    'Earth & Space Science': {'score': 90, 'mastery': 'advanced', 'trend': 'flat'},
                    'Scientific Method': {'score': 85, 'mastery': 'proficient', 'trend': 'up'},
                    'Data Interpretation': {'score': 90, 'mastery': 'advanced', 'trend': 'up'},
                }
            }
        },
        'pathways': [],
        'assessment_history': [
            {'date': '2026-01-15', 'subject': 'math', 'score': 88},
            {'date': '2026-02-01', 'subject': 'math', 'score': 90},
            {'date': '2026-02-15', 'subject': 'math', 'score': 91},
            {'date': '2026-03-01', 'subject': 'math', 'score': 93},
        ]
    },
    5: {  # Ethan Brown
        'name': 'Ethan Brown',
        'grade': '7th Grade',
        'class': 'Period 3 - Mr. Davis',
        'teacher_id': 102,
        'overall_score': 58,
        'subjects': {
            'math': {
                'overall': 60,
                'diagnostic_taken': True,
                'topics': {
                    'Number Sense & Operations': {'score': 65, 'mastery': 'approaching', 'trend': 'up'},
                    'Algebraic Thinking': {'score': 55, 'mastery': 'below', 'trend': 'flat'},
                    'Geometry & Measurement': {'score': 68, 'mastery': 'approaching', 'trend': 'up'},
                    'Data Analysis & Probability': {'score': 52, 'mastery': 'below', 'trend': 'flat'},
                    'Fractions & Decimals': {'score': 60, 'mastery': 'approaching', 'trend': 'up'},
                }
            },
            'reading': {
                'overall': 55,
                'diagnostic_taken': True,
                'topics': {
                    'Reading Comprehension': {'score': 60, 'mastery': 'approaching', 'trend': 'up'},
                    'Vocabulary & Word Study': {'score': 50, 'mastery': 'below', 'trend': 'flat'},
                    'Grammar & Mechanics': {'score': 55, 'mastery': 'below', 'trend': 'flat'},
                    'Writing & Composition': {'score': 52, 'mastery': 'below', 'trend': 'flat'},
                    'Literary Analysis': {'score': 58, 'mastery': 'below', 'trend': 'up'},
                }
            },
            'science': {
                'overall': 58,
                'diagnostic_taken': True,
                'topics': {
                    'Life Science': {'score': 62, 'mastery': 'approaching', 'trend': 'up'},
                    'Physical Science': {'score': 55, 'mastery': 'below', 'trend': 'flat'},
                    'Earth & Space Science': {'score': 58, 'mastery': 'below', 'trend': 'flat'},
                    'Scientific Method': {'score': 55, 'mastery': 'below', 'trend': 'flat'},
                    'Data Interpretation': {'score': 60, 'mastery': 'approaching', 'trend': 'up'},
                }
            }
        },
        'pathways': [
            {'subject': 'math', 'topic': 'Algebraic Thinking', 'progress': 25, 'assigned_by': 'AI', 'status': 'in_progress'},
            {'subject': 'reading', 'topic': 'Vocabulary & Word Study', 'progress': 30, 'assigned_by': 'AI', 'status': 'in_progress'},
        ],
        'assessment_history': [
            {'date': '2026-01-15', 'subject': 'math', 'score': 52},
            {'date': '2026-02-01', 'subject': 'math', 'score': 55},
            {'date': '2026-02-15', 'subject': 'math', 'score': 57},
            {'date': '2026-03-01', 'subject': 'math', 'score': 60},
        ]
    }
}

# --- Teacher Class Assignments ---
# Maps teacher IDs to their classes and student lists
# TODO: Replace with database relations
TEACHER_CLASSES = {
    101: {  # Ms. Thompson
        'name': 'Ms. Thompson',
        'classes': [
            {
                'name': 'Period 2 - 7th Grade Math/Science',
                'subject': 'math',
                'students': [1, 2, 4]  # Student IDs
            }
        ]
    },
    102: {  # Mr. Davis
        'name': 'Mr. Davis',
        'classes': [
            {
                'name': 'Period 3 - 7th Grade Math/Science',
                'subject': 'math',
                'students': [3, 5]  # Student IDs
            }
        ]
    }
}

# --- Admin Comparison Data (Before/After Implementation) ---
# Simulates school-wide data for admins to see the platform's impact
# TODO: Generate this from real assessment data
ADMIN_COMPARISON_DATA = {
    'before_after': {
        'math': {'before': 58, 'after': 67, 'change': '+15.5%'},
        'reading': {'before': 62, 'after': 71, 'change': '+14.5%'},
        'science': {'before': 55, 'after': 64, 'change': '+16.4%'},
    },
    'school_comparison': [
        {'school': 'Lincoln Middle School (Ours)', 'math': 67, 'reading': 71, 'science': 64, 'uses_platform': True},
        {'school': 'Washington Middle School', 'math': 60, 'reading': 63, 'science': 57, 'uses_platform': False},
        {'school': 'Jefferson Academy', 'math': 72, 'reading': 74, 'science': 69, 'uses_platform': True},
        {'school': 'Roosevelt Middle School', 'math': 55, 'reading': 58, 'science': 52, 'uses_platform': False},
    ],
    'subject_trends': {
        'months': ['Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'],
        'math':    [58, 59, 61, 62, 64, 66, 67],
        'reading': [62, 63, 64, 66, 68, 70, 71],
        'science': [55, 56, 58, 59, 61, 63, 64],
    },
    'engagement': {
        'active_students': 487,
        'total_students': 520,
        'avg_time_per_week': '3.2 hours',
        'pathways_completed': 1247,
        'assessments_taken': 3891,
        'improvement_rate': '78%',
    }
}

# --- Feedback Data ---
# Simulates feedback from students and teachers
# TODO: Collect real feedback through in-app surveys
FEEDBACK_DATA = {
    'student_feedback': [
        {'student': 'Anonymous', 'rating': 4, 'text': 'The practice exercises really helped me understand fractions better!', 'subject': 'math', 'date': '2026-03-15'},
        {'student': 'Anonymous', 'rating': 5, 'text': 'I like that it shows me exactly what I need to work on.', 'subject': 'general', 'date': '2026-03-14'},
        {'student': 'Anonymous', 'rating': 3, 'text': 'Some of the reading passages are too long and boring.', 'subject': 'reading', 'date': '2026-03-13'},
        {'student': 'Anonymous', 'rating': 2, 'text': 'The science questions are way too hard for me.', 'subject': 'science', 'date': '2026-03-12'},
        {'student': 'Anonymous', 'rating': 4, 'text': 'My math scores went up after using the personalized pathway!', 'subject': 'math', 'date': '2026-03-11'},
        {'student': 'Anonymous', 'rating': 5, 'text': 'I love the progress tracking. It keeps me motivated.', 'subject': 'general', 'date': '2026-03-10'},
        {'student': 'Anonymous', 'rating': 3, 'text': 'Wish there were more interactive exercises instead of just questions.', 'subject': 'general', 'date': '2026-03-09'},
        {'student': 'Anonymous', 'rating': 4, 'text': 'The vocabulary builder is really useful.', 'subject': 'reading', 'date': '2026-03-08'},
    ],
    'teacher_feedback': [
        {'teacher': 'Ms. Thompson', 'rating': 5, 'text': 'The dashboard makes it easy to see which students need help immediately.', 'date': '2026-03-14'},
        {'teacher': 'Mr. Davis', 'rating': 4, 'text': 'I appreciate being able to assign specific pathways to struggling students.', 'date': '2026-03-13'},
        {'teacher': 'Ms. Thompson', 'rating': 3, 'text': 'Would like more control over the difficulty of assigned pathways.', 'date': '2026-03-10'},
        {'teacher': 'Mr. Davis', 'rating': 4, 'text': 'The progress reports save me a lot of time in parent meetings.', 'date': '2026-03-08'},
    ],
    # AI-generated themes from feedback
    # TODO: Replace with real NLP/AI analysis
    'ai_themes': [
        {'theme': 'Positive Impact on Scores', 'sentiment': 'positive', 'count': 45, 'summary': 'Students and teachers report measurable improvement in test scores, especially in math.'},
        {'theme': 'Engagement & Motivation', 'sentiment': 'positive', 'count': 38, 'summary': 'Progress tracking and personalized paths keep students motivated and engaged.'},
        {'theme': 'Content Difficulty Mismatch', 'sentiment': 'negative', 'count': 22, 'summary': 'Some students feel exercises are either too hard or too easy. Adaptive difficulty needs refinement.'},
        {'theme': 'Content Variety', 'sentiment': 'negative', 'count': 18, 'summary': 'Students want more interactive and varied exercise types beyond standard questions.'},
        {'theme': 'Teacher Control', 'sentiment': 'neutral', 'count': 12, 'summary': 'Teachers want more granular control over pathway assignments and difficulty settings.'},
    ]
}

# --- Practice Test Questions ---
# These are the diagnostic questions students can take
# Each question has a subject, topic, difficulty, and correct answer
# TODO: Create a much larger question bank with adaptive difficulty
# TODO: Add different question types (multiple choice, drag-and-drop, fill-in)
PRACTICE_QUESTIONS = {
    'math': [
        {
            'id': 'm1', 'topic': 'Number Sense & Operations',
            'difficulty': 'easy',
            'question': 'What is 347 + 256?',
            'options': ['593', '603', '503', '613'],
            'correct': 0,
            'explanation': 'Add the ones (7+6=13, carry 1), tens (4+5+1=10, carry 1), hundreds (3+2+1=6). Answer: 603. The AI would note errors in place value or carrying.'
        },
        {
            'id': 'm2', 'topic': 'Algebraic Thinking',
            'difficulty': 'medium',
            'question': 'Solve for x: 3x + 7 = 22',
            'options': ['x = 3', 'x = 5', 'x = 7', 'x = 4'],
            'correct': 1,
            'explanation': 'Subtract 7 from both sides: 3x = 15. Divide by 3: x = 5. The AI would identify if students struggle with inverse operations.'
        },
        {
            'id': 'm3', 'topic': 'Fractions & Decimals',
            'difficulty': 'medium',
            'question': 'What is 3/4 + 1/6?',
            'options': ['4/10', '11/12', '5/6', '7/12'],
            'correct': 1,
            'explanation': 'Find common denominator (12): 9/12 + 2/12 = 11/12. The AI would check if students understand finding common denominators.'
        },
        {
            'id': 'm4', 'topic': 'Geometry & Measurement',
            'difficulty': 'medium',
            'question': 'A rectangle has a length of 12 cm and a width of 5 cm. What is its area?',
            'options': ['17 cm²', '34 cm²', '60 cm²', '120 cm²'],
            'correct': 2,
            'explanation': 'Area = length × width = 12 × 5 = 60 cm². The AI would check if students confuse area with perimeter.'
        },
        {
            'id': 'm5', 'topic': 'Data Analysis & Probability',
            'difficulty': 'easy',
            'question': 'A bag has 3 red, 5 blue, and 2 green marbles. What is the probability of drawing a blue marble?',
            'options': ['1/2', '3/10', '1/5', '5/10'],
            'correct': 0,
            'explanation': 'P(blue) = 5/10 = 1/2. The AI would assess basic probability understanding.'
        },
        {
            'id': 'm6', 'topic': 'Algebraic Thinking',
            'difficulty': 'hard',
            'question': 'If 2(x - 3) + 4 = 3x - 1, what is x?',
            'options': ['x = -1', 'x = 1', 'x = -3', 'x = 3'],
            'correct': 0,
            'explanation': '2x - 6 + 4 = 3x - 1 → 2x - 2 = 3x - 1 → -1 = x. The AI detects difficulty with distributive property and multi-step equations.'
        },
        {
            'id': 'm7', 'topic': 'Fractions & Decimals',
            'difficulty': 'hard',
            'question': 'Convert 0.375 to a fraction in simplest form.',
            'options': ['3/8', '375/100', '3/75', '37/100'],
            'correct': 0,
            'explanation': '0.375 = 375/1000 = 3/8 after simplifying by dividing by 125. The AI checks decimal-to-fraction conversion skills.'
        },
        {
            'id': 'm8', 'topic': 'Number Sense & Operations',
            'difficulty': 'medium',
            'question': 'What is the greatest common factor (GCF) of 24 and 36?',
            'options': ['6', '8', '12', '4'],
            'correct': 2,
            'explanation': 'Factors of 24: 1,2,3,4,6,8,12,24. Factors of 36: 1,2,3,4,6,9,12,18,36. GCF = 12.'
        },
    ],
    'reading': [
        {
            'id': 'r1', 'topic': 'Reading Comprehension',
            'difficulty': 'medium',
            'question': 'Read the passage: "The ancient Egyptians built the pyramids as tombs for their pharaohs. The largest, the Great Pyramid of Giza, took approximately 20 years to build." What was the primary purpose of the pyramids?',
            'options': ['As temples for worship', 'As tombs for pharaohs', 'As homes for workers', 'As libraries'],
            'correct': 1,
            'explanation': 'The passage directly states pyramids were "tombs for their pharaohs." The AI checks literal comprehension.'
        },
        {
            'id': 'r2', 'topic': 'Vocabulary & Word Study',
            'difficulty': 'easy',
            'question': 'What does the word "benevolent" mean?',
            'options': ['Hostile', 'Kind and generous', 'Intelligent', 'Cautious'],
            'correct': 1,
            'explanation': 'Benevolent means well-meaning and kindly. The AI tracks vocabulary level and suggests targeted word study.'
        },
        {
            'id': 'r3', 'topic': 'Grammar & Mechanics',
            'difficulty': 'easy',
            'question': 'Which sentence uses correct punctuation?',
            'options': [
                'The dog, ran quickly across the yard.',
                'The dog ran quickly across the yard.',
                'The dog ran, quickly across the yard.',
                'The, dog ran quickly across the yard.'
            ],
            'correct': 1,
            'explanation': 'No comma is needed in this simple sentence. The AI identifies comma splice or misuse patterns.'
        },
        {
            'id': 'r4', 'topic': 'Literary Analysis',
            'difficulty': 'hard',
            'question': '"The classroom was a zoo on the last day of school." This is an example of:',
            'options': ['Simile', 'Metaphor', 'Personification', 'Hyperbole'],
            'correct': 1,
            'explanation': 'This is a metaphor because it directly compares the classroom to a zoo without using "like" or "as."'
        },
        {
            'id': 'r5', 'topic': 'Writing & Composition',
            'difficulty': 'medium',
            'question': 'Which is the strongest thesis statement?',
            'options': [
                'Dogs are cool.',
                'This essay is about recycling.',
                'Schools should require community service because it builds character, teaches responsibility, and strengthens communities.',
                'I think homework is bad.'
            ],
            'correct': 2,
            'explanation': 'A strong thesis makes a claim and previews the supporting arguments. The AI evaluates argumentative writing skills.'
        },
        {
            'id': 'r6', 'topic': 'Reading Comprehension',
            'difficulty': 'hard',
            'question': '"Maria slammed the book on the table and stormed out of the room." How is Maria most likely feeling?',
            'options': ['Happy', 'Frustrated or angry', 'Sleepy', 'Confused'],
            'correct': 1,
            'explanation': 'The verbs "slammed" and "stormed" indicate strong negative emotions. The AI checks inference skills.'
        },
        {
            'id': 'r7', 'topic': 'Vocabulary & Word Study',
            'difficulty': 'medium',
            'question': 'The prefix "un-" in "unhappy" means:',
            'options': ['Again', 'Not', 'Before', 'After'],
            'correct': 1,
            'explanation': '"Un-" is a prefix meaning "not." The AI assesses understanding of word structure and morphology.'
        },
    ],
    'science': [
        {
            'id': 's1', 'topic': 'Life Science',
            'difficulty': 'easy',
            'question': 'What is the basic unit of life?',
            'options': ['Atom', 'Cell', 'Organ', 'Tissue'],
            'correct': 1,
            'explanation': 'The cell is the basic structural and functional unit of all living organisms.'
        },
        {
            'id': 's2', 'topic': 'Physical Science',
            'difficulty': 'medium',
            'question': 'Which of Newton\'s Laws states that F = ma?',
            'options': ['First Law', 'Second Law', 'Third Law', 'Law of Gravity'],
            'correct': 1,
            'explanation': 'Newton\'s Second Law: Force equals mass times acceleration. The AI checks physics fundamentals.'
        },
        {
            'id': 's3', 'topic': 'Earth & Space Science',
            'difficulty': 'easy',
            'question': 'What causes the seasons on Earth?',
            'options': [
                'Distance from the Sun',
                'The tilt of Earth\'s axis',
                'The speed of Earth\'s rotation',
                'The Moon\'s gravity'
            ],
            'correct': 1,
            'explanation': 'Earth\'s 23.5° axial tilt causes different parts to receive varying amounts of sunlight throughout the year.'
        },
        {
            'id': 's4', 'topic': 'Scientific Method',
            'difficulty': 'medium',
            'question': 'What comes after forming a hypothesis in the scientific method?',
            'options': ['Ask a question', 'Conduct an experiment', 'Draw conclusions', 'Make observations'],
            'correct': 1,
            'explanation': 'After forming a hypothesis, scientists design and conduct experiments to test it.'
        },
        {
            'id': 's5', 'topic': 'Data Interpretation',
            'difficulty': 'medium',
            'question': 'A graph shows plant growth over 4 weeks: Week 1: 2cm, Week 2: 5cm, Week 3: 9cm, Week 4: 14cm. What is the average growth per week?',
            'options': ['2.5 cm', '3 cm', '3.5 cm', '4 cm'],
            'correct': 2,
            'explanation': 'Total growth = 14 cm over 4 weeks. Average = 14/4 = 3.5 cm per week.'
        },
        {
            'id': 's6', 'topic': 'Life Science',
            'difficulty': 'hard',
            'question': 'Which organelle is responsible for producing energy (ATP) in a cell?',
            'options': ['Nucleus', 'Ribosome', 'Mitochondria', 'Golgi Apparatus'],
            'correct': 2,
            'explanation': 'Mitochondria are the "powerhouses of the cell" — they produce ATP through cellular respiration.'
        },
        {
            'id': 's7', 'topic': 'Physical Science',
            'difficulty': 'hard',
            'question': 'What type of energy transformation occurs in a solar panel?',
            'options': [
                'Chemical to electrical',
                'Light to electrical',
                'Thermal to mechanical',
                'Electrical to light'
            ],
            'correct': 1,
            'explanation': 'Solar panels convert light (solar) energy into electrical energy through photovoltaic cells.'
        },
    ]
}

# --- AI Recommendation Templates ---
# These simulate what a real AI would generate based on student performance
# TODO: Replace with actual AI/ML model outputs
AI_RECOMMENDATIONS = {
    'well_below': {
        'message': '🔴 Needs Immediate Support',
        'detail': 'The AI has identified significant gaps in foundational skills. A structured, step-by-step pathway has been created starting from prerequisite concepts.',
        'actions': [
            'Start with foundational concept review lessons',
            'Complete guided practice exercises with hints enabled',
            'Take mini-assessments after each lesson to track progress',
            'Schedule check-in with teacher for additional support'
        ]
    },
    'below': {
        'message': '🟠 Building Foundations',
        'detail': 'The AI has found areas where core concepts need reinforcement. A focused pathway targets the specific skills that need strengthening.',
        'actions': [
            'Review targeted concept lessons',
            'Practice with scaffolded exercises (gradually reducing hints)',
            'Complete topic-specific quizzes',
            'Revisit challenging problems with step-by-step solutions'
        ]
    },
    'approaching': {
        'message': '🟡 Almost There',
        'detail': 'The AI shows good foundational understanding with some gaps. The pathway focuses on bridging these gaps to reach proficiency.',
        'actions': [
            'Focus on specific weak areas within the topic',
            'Practice mixed-difficulty exercises',
            'Attempt challenge problems to build confidence',
            'Review and correct previous assessment mistakes'
        ]
    },
    'proficient': {
        'message': '🟢 On Track',
        'detail': 'The AI confirms solid understanding of core concepts. The pathway includes enrichment to maintain and extend mastery.',
        'actions': [
            'Continue with grade-level practice',
            'Explore extension activities and real-world applications',
            'Help peers through collaborative learning exercises',
            'Prepare for advanced topic previews'
        ]
    },
    'advanced': {
        'message': '🔵 Exceeding Expectations',
        'detail': 'The AI shows mastery of all assessed concepts. Advanced enrichment and above-grade-level content is recommended.',
        'actions': [
            'Explore above-grade-level concepts',
            'Complete independent research projects',
            'Participate in challenge/competition-style problems',
            'Mentor other students in collaborative activities'
        ]
    }
}


# ==========================================================================
# HELPER FUNCTIONS
# ==========================================================================

def get_mastery_label(mastery):
    """Convert mastery code to human-readable label with color.
    
    TODO: Make mastery thresholds configurable per school/district
    """
    labels = {
        'well_below': ('Well Below Grade Level', '#DC3545'),
        'below': ('Below Grade Level', '#FD7E14'),
        'approaching': ('Approaching Grade Level', '#FFC107'),
        'proficient': ('At Grade Level', '#28A745'),
        'advanced': ('Above Grade Level', '#007BFF'),
    }
    return labels.get(mastery, ('Unknown', '#6C757D'))


def calculate_mastery(score):
    """Determine mastery level from a numeric score.
    
    This is a simplified version — a real AI would use multiple data points,
    not just a single score, to determine mastery level.
    TODO: Implement proper ML-based mastery classification
    """
    if score >= 90:
        return 'advanced'
    elif score >= 75:
        return 'proficient'
    elif score >= 60:
        return 'approaching'
    elif score >= 40:
        return 'below'
    else:
        return 'well_below'


def generate_ai_report(student_id, subject_key=None):
    """Generate a fake AI analysis report for a student.
    
    In a real system, this would:
    1. Pull all assessment data for the student
    2. Run it through an ML model to identify patterns
    3. Compare against learning standards and benchmarks
    4. Generate personalized recommendations
    
    TODO: Replace with actual AI/ML pipeline
    """
    student = STUDENT_DATA.get(student_id)
    if not student:
        return None
    
    report = {
        'student_name': student['name'],
        'generated_at': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
        'overall_score': student['overall_score'],
        'subjects': {}
    }
    
    subjects_to_analyze = {subject_key: student['subjects'][subject_key]} if subject_key else student['subjects']
    
    for subj_key, subj_data in subjects_to_analyze.items():
        subj_info = SUBJECTS[subj_key]
        
        # Find strengths (highest scoring topics)
        topic_scores = [(topic, data['score']) for topic, data in subj_data['topics'].items()]
        topic_scores.sort(key=lambda x: x[1], reverse=True)
        
        strengths = [t for t, s in topic_scores if s >= 75]
        weaknesses = [t for t, s in topic_scores if s < 60]
        growth_areas = [t for t, s in topic_scores if 60 <= s < 75]
        
        # Build recommendations for each weak topic
        topic_recommendations = []
        for topic, data in subj_data['topics'].items():
            rec = AI_RECOMMENDATIONS.get(data['mastery'], AI_RECOMMENDATIONS['approaching'])
            topic_recommendations.append({
                'topic': topic,
                'score': data['score'],
                'mastery': data['mastery'],
                'mastery_label': get_mastery_label(data['mastery']),
                'trend': data['trend'],
                'recommendation': rec
            })
        
        report['subjects'][subj_key] = {
            'name': subj_info['name'],
            'icon': subj_info['icon'],
            'color': subj_info['color'],
            'overall': subj_data['overall'],
            'strengths': strengths,
            'weaknesses': weaknesses,
            'growth_areas': growth_areas,
            'topic_details': topic_recommendations,
            'ai_summary': generate_ai_summary(student['name'], subj_info['name'], strengths, weaknesses, growth_areas, subj_data['overall'])
        }
    
    return report


def generate_ai_summary(name, subject, strengths, weaknesses, growth_areas, score):
    """Generate a human-readable AI summary paragraph.
    
    In production, this would use an LLM (like GPT) to generate natural language.
    TODO: Connect to an actual language model for more dynamic summaries
    """
    first_name = name.split()[0]
    
    if score >= 85:
        opener = f"{first_name} is performing excellently in {subject}."
    elif score >= 70:
        opener = f"{first_name} shows solid understanding in {subject} with room for growth."
    elif score >= 55:
        opener = f"{first_name} is developing skills in {subject} but needs targeted support."
    else:
        opener = f"{first_name} needs significant support in {subject} to reach grade-level expectations."
    
    strength_text = ""
    if strengths:
        strength_text = f" Strong areas include {', '.join(strengths[:2])}."
    
    weakness_text = ""
    if weaknesses:
        weakness_text = f" Priority areas for improvement: {', '.join(weaknesses[:2])}."
    
    growth_text = ""
    if growth_areas:
        growth_text = f" Areas approaching proficiency that need continued practice: {', '.join(growth_areas[:2])}."
    
    recommendation = " The AI recommends focusing on the personalized pathway created below, starting with the lowest-scoring areas."
    
    return opener + strength_text + weakness_text + growth_text + recommendation


# ==========================================================================
# ROUTES — Login & Authentication
# ==========================================================================

@app.route('/')
def home():
    """Redirect to login or dashboard based on session state.
    
    If the user is already logged in (has a session), send them to their
    role-specific dashboard. Otherwise, show the login page.
    """
    if 'user' in session:
        role = session['user']['role']
        return redirect(url_for(f'{role}_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login page display and form submission.
    
    GET: Show the login form with role selection
    POST: Validate credentials against the USERS dictionary
    
    The login form has:
    - Role selector (Student/Teacher/Admin)
    - Username field
    - Password field
    
    TODO: Add rate limiting to prevent brute force
    TODO: Replace with proper authentication (OAuth2, SAML for schools)
    """
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', '')
        
        # Check if user exists and credentials match
        user = USERS.get(username)
        if user and user['password'] == password and user['role'] == role:
            # Store user info in session (cookie-based)
            session['user'] = {
                'username': username,
                'name': user['name'],
                'role': user['role'],
                'id': user['id']
            }
            return redirect(url_for(f'{role}_dashboard'))
        else:
            error = 'Invalid username, password, or role selection.'
    
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    """Clear the session and redirect to login page."""
    session.clear()
    return redirect(url_for('login'))


# ==========================================================================
# ROUTES — Student Dashboard
# ==========================================================================

@app.route('/student')
def student_dashboard():
    """Main student dashboard showing all subjects and performance overview.
    
    This is where students land after login. It shows:
    1. Overall performance summary
    2. Subject cards with scores and mastery levels
    3. Active learning pathways
    4. Quick links to take assessments
    
    The dashboard highlights subjects needing the most improvement (matching
    the Student journey map: "Shows the subjects that need the most improvement on")
    """
    if 'user' not in session or session['user']['role'] != 'student':
        return redirect(url_for('login'))
    
    student_id = session['user']['id']
    student = STUDENT_DATA.get(student_id)
    
    if not student:
        return "Student data not found", 404
    
    return render_template('student.html',
                         student=student,
                         subjects=SUBJECTS,
                         recommendations=AI_RECOMMENDATIONS,
                         get_mastery_label=get_mastery_label)


@app.route('/student/subject/<subject_key>')
def student_subject_detail(subject_key):
    """Detailed view of a single subject with AI feedback and recommendations.
    
    When a student clicks on a struggling subject, they get:
    - Detailed topic-by-topic breakdown
    - AI-generated feedback and actionable recommendations
    - Links to personalized practice pathways
    
    Matches Student journey: "Hopes that the feedback will be clear and tells
    you how to fix it" → We provide clear, actionable AI recommendations.
    """
    if 'user' not in session or session['user']['role'] != 'student':
        return redirect(url_for('login'))
    
    student_id = session['user']['id']
    report = generate_ai_report(student_id, subject_key)
    
    if not report or subject_key not in report['subjects']:
        return "Subject not found", 404
    
    return render_template('student_subject.html',
                         report=report,
                         subject_key=subject_key,
                         subject_data=report['subjects'][subject_key],
                         student=STUDENT_DATA[student_id],
                         subjects=SUBJECTS,
                         get_mastery_label=get_mastery_label)


@app.route('/student/test/<subject_key>')
def student_test(subject_key):
    """Show the practice/diagnostic test for a subject.
    
    This presents an interactive assessment that the student takes.
    Questions are pulled from PRACTICE_QUESTIONS and displayed one at a time
    or all at once (depending on the template design).
    
    The test is the first step in the adaptive learning cycle:
    Test → Analyze → Identify → Recommend → Personalize
    
    TODO: Make the test truly adaptive (adjusting difficulty based on responses)
    TODO: Add a timer option for timed assessments
    """
    if 'user' not in session or session['user']['role'] != 'student':
        return redirect(url_for('login'))
    
    questions = PRACTICE_QUESTIONS.get(subject_key, [])
    subject = SUBJECTS.get(subject_key)
    
    if not subject:
        return "Subject not found", 404
    
    return render_template('test.html',
                         questions=questions,
                         subject=subject,
                         subject_key=subject_key)


@app.route('/student/test/<subject_key>/submit', methods=['POST'])
def submit_test(subject_key):
    """Process test submission and generate results.
    
    This is where the "AI analysis" happens (simulated):
    1. Score the test by comparing answers to correct answers
    2. Analyze which topics the student got right/wrong
    3. Determine mastery level per topic
    4. Generate personalized recommendations
    5. Create/update learning pathways
    
    TODO: Store results in database
    TODO: Use real ML model for adaptive analysis
    TODO: Update student's topic scores based on assessment
    """
    if 'user' not in session or session['user']['role'] != 'student':
        return redirect(url_for('login'))
    
    questions = PRACTICE_QUESTIONS.get(subject_key, [])
    subject = SUBJECTS.get(subject_key)
    student_id = session['user']['id']
    
    # Score each question and track per-topic performance
    results = []
    topic_scores = {}  # {topic: {'correct': 0, 'total': 0}}
    total_correct = 0
    
    for q in questions:
        # Get the student's answer from the form
        answer = request.form.get(q['id'])
        is_correct = answer is not None and int(answer) == q['correct']
        
        if is_correct:
            total_correct += 1
        
        # Track per-topic accuracy
        topic = q['topic']
        if topic not in topic_scores:
            topic_scores[topic] = {'correct': 0, 'total': 0}
        topic_scores[topic]['total'] += 1
        if is_correct:
            topic_scores[topic]['correct'] += 1
        
        results.append({
            'question': q['question'],
            'topic': topic,
            'difficulty': q['difficulty'],
            'student_answer': int(answer) if answer else -1,
            'correct_answer': q['correct'],
            'options': q['options'],
            'is_correct': is_correct,
            'explanation': q['explanation']
        })
    
    # Calculate overall and per-topic scores
    overall_score = round((total_correct / len(questions)) * 100) if questions else 0
    
    topic_analysis = []
    for topic, data in topic_scores.items():
        score = round((data['correct'] / data['total']) * 100)
        mastery = calculate_mastery(score)
        mastery_label, mastery_color = get_mastery_label(mastery)
        rec = AI_RECOMMENDATIONS.get(mastery, AI_RECOMMENDATIONS['approaching'])
        
        topic_analysis.append({
            'topic': topic,
            'score': score,
            'correct': data['correct'],
            'total': data['total'],
            'mastery': mastery,
            'mastery_label': mastery_label,
            'mastery_color': mastery_color,
            'recommendation': rec
        })
    
    # Sort topics: worst performing first (these need the most attention)
    topic_analysis.sort(key=lambda x: x['score'])
    
    # Generate AI pathway recommendations based on results
    # In a real system, this would update the student's learning path
    new_pathways = []
    for ta in topic_analysis:
        if ta['score'] < 75:  # Below proficient
            new_pathways.append({
                'topic': ta['topic'],
                'mastery': ta['mastery_label'],
                'recommendation': ta['recommendation'],
                'priority': 'high' if ta['score'] < 50 else 'medium'
            })
    
    return render_template('results.html',
                         results=results,
                         topic_analysis=topic_analysis,
                         overall_score=overall_score,
                         total_correct=total_correct,
                         total_questions=len(questions),
                         subject=subject,
                         subject_key=subject_key,
                         new_pathways=new_pathways,
                         student=STUDENT_DATA.get(student_id))


@app.route('/student/pathway/<subject_key>/<topic>')
def student_pathway(subject_key, topic):
    """Show a personalized learning pathway for a specific topic.
    
    This is the "personalized curriculum" — a step-by-step learning plan
    tailored to the student's current level and needs.
    
    The pathway includes:
    - Concept review lessons
    - Practice exercises (interactive)
    - Mini-assessments to check understanding
    - Real-world application activities
    
    Matches Student journey: "To make it the right difficulty level, the
    right topic, and make it engaging"
    
    TODO: Generate pathway content dynamically based on AI analysis
    TODO: Add adaptive difficulty that adjusts as student progresses
    """
    if 'user' not in session or session['user']['role'] != 'student':
        return redirect(url_for('login'))
    
    student_id = session['user']['id']
    student = STUDENT_DATA.get(student_id)
    subject = SUBJECTS.get(subject_key)
    
    if not subject:
        return "Subject not found", 404
    
    # Find the student's current score for this topic
    topic_data = student['subjects'].get(subject_key, {}).get('topics', {}).get(topic, {})
    current_score = topic_data.get('score', 50)
    mastery = topic_data.get('mastery', calculate_mastery(current_score))
    
    # Generate fake pathway steps based on mastery level
    # TODO: Replace with real curriculum content from a content management system
    pathway_steps = generate_pathway_steps(topic, mastery, subject_key)
    
    return render_template('pathway.html',
                         student=student,
                         subject=subject,
                         subject_key=subject_key,
                         topic=topic,
                         topic_data=topic_data,
                         mastery=mastery,
                         mastery_label=get_mastery_label(mastery),
                         pathway_steps=pathway_steps,
                         recommendation=AI_RECOMMENDATIONS.get(mastery))


def generate_pathway_steps(topic, mastery, subject_key):
    """Create mock pathway steps based on mastery level.
    
    In a real system, these would be actual lessons, videos, and exercises
    pulled from a curriculum database, adapted to the student's level.
    
    TODO: Connect to real content/curriculum database
    TODO: Use AI to select and order content based on learning gaps
    """
    base_steps = [
        {
            'step': 1,
            'type': 'lesson',
            'title': f'Review: Core Concepts of {topic}',
            'description': f'[AI would generate] A review lesson covering the fundamental concepts of {topic}, tailored to your current understanding level.',
            'duration': '15 min',
            'status': 'available',
            'icon': '📚'
        },
        {
            'step': 2,
            'type': 'video',
            'title': f'Video: Understanding {topic}',
            'description': f'[AI would select] An instructional video matched to your learning style, explaining {topic} with visual examples.',
            'duration': '10 min',
            'status': 'available',
            'icon': '🎥'
        },
        {
            'step': 3,
            'type': 'practice',
            'title': f'Guided Practice: {topic}',
            'description': f'[AI would generate] Practice problems at YOUR level with step-by-step hints available. Difficulty adjusts based on your responses.',
            'duration': '20 min',
            'status': 'locked',
            'icon': '✏️'
        },
        {
            'step': 4,
            'type': 'interactive',
            'title': f'Interactive Activity: {topic} in Real Life',
            'description': f'[AI would create] A hands-on activity showing how {topic} applies to real-world situations, making the learning more engaging.',
            'duration': '15 min',
            'status': 'locked',
            'icon': '🎮'
        },
        {
            'step': 5,
            'type': 'quiz',
            'title': f'Check Understanding: {topic} Mini-Quiz',
            'description': f'[AI would generate] A short quiz to check your understanding before moving on. Questions are adapted based on what you\'ve practiced.',
            'duration': '10 min',
            'status': 'locked',
            'icon': '📝'
        },
        {
            'step': 6,
            'type': 'challenge',
            'title': f'Challenge: Apply {topic} Skills',
            'description': f'[AI would create] A challenge problem set that combines {topic} with previously mastered skills to deepen understanding.',
            'duration': '15 min',
            'status': 'locked',
            'icon': '🏆'
        },
    ]
    
    # If mastery is very low, add prerequisite steps at the beginning
    if mastery in ('well_below', 'below'):
        prerequisite = {
            'step': 0,
            'type': 'prerequisite',
            'title': f'Prerequisites: Building Blocks for {topic}',
            'description': f'[AI detected gaps] Before diving into {topic}, let\'s review the foundational skills you\'ll need. This lesson covers the prerequisite concepts.',
            'duration': '20 min',
            'status': 'available',
            'icon': '🔧'
        }
        base_steps.insert(0, prerequisite)
        # Renumber steps
        for i, step in enumerate(base_steps):
            step['step'] = i + 1
    
    return base_steps


# ==========================================================================
# ROUTES — Teacher Dashboard
# ==========================================================================

@app.route('/teacher')
def teacher_dashboard():
    """Main teacher dashboard showing classes and student overview.
    
    Teachers see:
    1. Their classes with at-a-glance student counts
    2. Flagged students who need intervention (falling grades)
    3. Class-wide performance metrics
    4. Quick actions to assign pathways
    
    Matches Teacher journey: "Flags students/classes with falling grades"
    and "Teachers choose which data want to see, shows important stats"
    """
    if 'user' not in session or session['user']['role'] != 'teacher':
        return redirect(url_for('login'))
    
    teacher_id = session['user']['id']
    teacher_data = TEACHER_CLASSES.get(teacher_id)
    
    if not teacher_data:
        return "Teacher data not found", 404
    
    # Build a comprehensive view of all students in this teacher's classes
    all_students = []
    flagged_students = []  # Students needing intervention
    
    for cls in teacher_data['classes']:
        for sid in cls['students']:
            student = STUDENT_DATA.get(sid)
            if student:
                student_info = {
                    'id': sid,
                    'name': student['name'],
                    'grade': student['grade'],
                    'overall_score': student['overall_score'],
                    'subjects': student['subjects'],
                    'pathways': student['pathways'],
                    'class_name': cls['name'],
                }
                all_students.append(student_info)
                
                # Flag students scoring below 60% overall (need intervention)
                # TODO: Make this threshold configurable by teacher
                if student['overall_score'] < 60:
                    flagged_students.append(student_info)
    
    # Sort flagged students by score (lowest first — most urgent)
    flagged_students.sort(key=lambda x: x['overall_score'])
    
    # Calculate class averages for the summary
    class_avg = round(sum(s['overall_score'] for s in all_students) / len(all_students)) if all_students else 0
    
    # Pre-compute dicts for JavaScript (Jinja2 doesn't support Python dict comprehensions)
    subject_labels = {k: v['name'] for k, v in SUBJECTS.items()}
    subject_colors = {k: v['color'] for k, v in SUBJECTS.items()}
    subject_topics = {k: v['topics'] for k, v in SUBJECTS.items()}
    
    return render_template('teacher.html',
                         teacher=teacher_data,
                         all_students=all_students,
                         flagged_students=flagged_students,
                         class_avg=class_avg,
                         subjects=SUBJECTS,
                         subject_labels=subject_labels,
                         subject_colors=subject_colors,
                         subject_topics=subject_topics,
                         student_data=STUDENT_DATA,
                         get_mastery_label=get_mastery_label)


@app.route('/teacher/student/<int:student_id>')
def teacher_student_detail(student_id):
    """Detailed view of a single student's performance (teacher view).
    
    Shows the teacher:
    - Complete performance profile across all subjects
    - Active and completed learning pathways with progress
    - AI-generated recommendations
    - Assessment history and score trends
    - Option to assign additional pathways
    
    Matches Teacher journey: "Teachers able to view all steps of pathways,
    track as student completes" and "Shows important stats"
    """
    if 'user' not in session or session['user']['role'] != 'teacher':
        return redirect(url_for('login'))
    
    student = STUDENT_DATA.get(student_id)
    if not student:
        return "Student not found", 404
    
    report = generate_ai_report(student_id)
    
    # Pre-compute dicts for JavaScript (Jinja2 doesn't support Python dict comprehensions)
    subject_colors = {k: v['color'] for k, v in SUBJECTS.items()}
    subject_names = {k: v['name'] for k, v in SUBJECTS.items()}
    subject_topics = {k: v['topics'] for k, v in SUBJECTS.items()}
    
    return render_template('teacher_student.html',
                         student=student,
                         student_id=student_id,
                         report=report,
                         subjects=SUBJECTS,
                         subject_colors=subject_colors,
                         subject_names=subject_names,
                         subject_topics=subject_topics,
                         recommendations=AI_RECOMMENDATIONS,
                         get_mastery_label=get_mastery_label)


@app.route('/teacher/assign-pathway', methods=['POST'])
def assign_pathway():
    """Allow teacher to assign a new pathway to a student.
    
    Teachers can manually assign pathways based on their professional judgment,
    overriding or supplementing the AI's automatic recommendations.
    
    Matches Teacher journey: "Sees recommended student pathways and assigns"
    
    TODO: Store pathway assignments in database
    TODO: Notify students of new pathway assignments
    """
    if 'user' not in session or session['user']['role'] != 'teacher':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    student_id = data.get('student_id')
    subject = data.get('subject')
    topic = data.get('topic')
    
    # In a real app, this would save to a database
    # For the mock, we'll just return a success response
    return jsonify({
        'success': True,
        'message': f'Pathway for {topic} ({subject}) has been assigned.',
        'ai_note': 'The AI will adapt this pathway based on the student\'s performance as they progress.'
    })


# ==========================================================================
# ROUTES — Admin Dashboard
# ==========================================================================

@app.route('/admin')
def admin_dashboard():
    """Main admin dashboard with school-wide statistics and comparisons.
    
    Admins see three main sections:
    1. Overall View — School-wide performance metrics, trends, engagement
    2. Areas for Improvement — AI-identified areas that need attention
    3. Feedback — Student and teacher feedback with AI-analyzed themes
    
    This is designed to convince admins of the platform's value:
    - Before/after comparisons show improvement
    - School-to-school comparisons show competitive advantage
    - Engagement metrics show adoption
    - AI recommendations show actionable next steps
    
    Matches Admin journey: "App recommends what the admin can do to make
    the scores better" and "comparisons"
    """
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect(url_for('login'))
    
    # Calculate aggregate stats from all student data
    all_students = list(STUDENT_DATA.values())
    total_students = len(all_students)
    avg_overall = round(sum(s['overall_score'] for s in all_students) / total_students) if total_students else 0
    
    # Count students by performance tier
    performance_tiers = {'advanced': 0, 'proficient': 0, 'approaching': 0, 'below': 0, 'well_below': 0}
    for s in all_students:
        tier = calculate_mastery(s['overall_score'])
        performance_tiers[tier] += 1
    
    # Subject averages
    subject_avgs = {}
    for subj_key in SUBJECTS:
        scores = [s['subjects'][subj_key]['overall'] for s in all_students if subj_key in s['subjects']]
        subject_avgs[subj_key] = round(sum(scores) / len(scores)) if scores else 0
    
    # Pre-compute dicts for JavaScript (Jinja2 doesn't support Python dict comprehensions)
    subject_colors = {k: v['color'] for k, v in SUBJECTS.items()}
    subject_names = {k: v['name'] for k, v in SUBJECTS.items()}
    
    return render_template('admin.html',
                         comparison=ADMIN_COMPARISON_DATA,
                         feedback=FEEDBACK_DATA,
                         subjects=SUBJECTS,
                         subject_colors=subject_colors,
                         subject_names=subject_names,
                         total_students=total_students,
                         avg_overall=avg_overall,
                         performance_tiers=performance_tiers,
                         subject_avgs=subject_avgs,
                         get_mastery_label=get_mastery_label)


# ==========================================================================
# API ROUTES — For AJAX calls from JavaScript
# ==========================================================================

@app.route('/api/student/<int:student_id>/report')
def api_student_report(student_id):
    """API endpoint to get a student's AI report as JSON.
    
    Used by the teacher dashboard to dynamically load student details
    without a full page reload.
    
    TODO: Add proper API authentication (API keys, JWT tokens)
    """
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    report = generate_ai_report(student_id)
    if not report:
        return jsonify({'error': 'Student not found'}), 404
    
    return jsonify(report)


@app.route('/api/admin/stats')
def api_admin_stats():
    """API endpoint for admin dashboard statistics.
    
    Returns aggregate data for chart rendering on the admin dashboard.
    TODO: Add caching for expensive aggregate queries
    """
    if 'user' not in session or session['user']['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    return jsonify({
        'comparison': ADMIN_COMPARISON_DATA,
        'subjects': {k: v['name'] for k, v in SUBJECTS.items()},
    })


# ==========================================================================
# MAIN — Start the Flask server
# ==========================================================================

if __name__ == '__main__':
    # TODO: In production, use a proper WSGI server (gunicorn, waitress)
    # TODO: Set debug=False in production
    # TODO: Configure proper logging
    print("\n" + "="*60)
    print("  EitaLearn - Personalized Learning Platform (Mock)")
    print("="*60)
    print("\n  Login Credentials:")
    print("  ------------------")
    print("  Students: student1/pass123, student2/pass123, etc.")
    print("  Teachers: teacher1/teach123, teacher2/teach123")
    print("  Admin:    admin1/admin123")
    print(f"\n  Server running at: http://127.0.0.1:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000)
