import sqlite3
import pandas as pd
import os

DB_FILENAME = 'dementia_screening.db'

def get_db_connection():
    """
    Establish a connection to the SQLite database.
    """
    try:
        conn = sqlite3.connect(DB_FILENAME)
        return conn
    except Exception as e:
        print(f"Error while connecting to SQLite: {e}")
        return None

def init_db():
    """
    Initializes the database schema if it doesn't already exist.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create patients table — uniqueness is on (name, age, gender) combined,
        # so the same name with different age or gender creates a separate patient.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, age, gender)
            )
        """)

        # Migration: if the old patients table has a UNIQUE constraint on name
        # alone (legacy schema), recreate it with the composite unique key.
        try:
            cursor.execute("PRAGMA index_list(patients)")
            indexes = cursor.fetchall()
            for idx_row in indexes:
                idx_name = idx_row[1]
                cursor.execute(f"PRAGMA index_info({idx_name})")
                idx_cols = [col[2] for col in cursor.fetchall()]
                # Detect the old single-column UNIQUE on 'name' only
                if idx_cols == ['name'] and idx_row[2] == 1:  # unique=1
                    cursor.execute("ALTER TABLE patients RENAME TO patients_old")
                    cursor.execute("""
                        CREATE TABLE patients (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            age INTEGER,
                            gender TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(name, age, gender)
                        )
                    """)
                    cursor.execute("""
                        INSERT INTO patients (id, name, age, gender, created_at)
                        SELECT id, name, age, gender, created_at FROM patients_old
                    """)
                    cursor.execute("DROP TABLE patients_old")
                    break
        except Exception:
            pass  # migration not needed or already done
        
        # Create users table (For Healthcare Workers)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT,
                username TEXT,
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Migration: Add columns to users if missing
        user_cols = [
            ("full_name", "TEXT"),
            ("email", "TEXT"),
            ("is_admin", "INTEGER DEFAULT 0")
        ]
        for col_name, col_type in user_cols:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            except sqlite3.OperationalError:
                pass
        
        # Create ratings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                rating INTEGER NOT NULL,
                feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Drop legacy assessments if it has wrong structure (e.g. participant_id instead of patient_id)
        cursor.execute("PRAGMA table_info(assessments)")
        cols = [row[1] for row in cursor.fetchall()]
        if cols and 'participant_id' in cols:
            cursor.execute("DROP TABLE assessments")
            
        # Create clean assessments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clinician_id INTEGER,
                patient_id INTEGER NOT NULL,
                assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                overall_score REAL,
                confidence_score REAL,
                risk_level TEXT,
                working_memory_score REAL,
                attention_score REAL,
                recall_score REAL,
                speech_rate REAL,
                recommendation TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
                FOREIGN KEY (clinician_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)

        # Create interactive_assessments table (retaining for login history or migration fallback if needed)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactive_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clinician_id INTEGER,
                patient_id TEXT NOT NULL,
                patient_name TEXT,
                patient_age INTEGER,
                patient_gender TEXT,
                cognitive_score REAL NOT NULL,
                speech_score REAL NOT NULL,
                overall_score REAL NOT NULL,
                risk_level TEXT NOT NULL,
                voice_features TEXT,
                assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
    except Exception as e:
        print(f"Error initializing the database: {e}")
    finally:
        if conn:
            conn.close()

def register_user(email, password, full_name=None, is_admin=0):
    conn = get_db_connection()
    if not conn: return False, "Database connection failed"
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            return False, "Email already exists."
        cursor.execute("""
            INSERT INTO users (email, password, full_name, username, is_admin) 
            VALUES (?, ?, ?, ?, ?)
        """, (email, password, full_name, email, is_admin))
        user_id = cursor.lastrowid
        conn.commit()
        return True, user_id
    except sqlite3.Error as e:
        return False, str(e)
    finally:
        if conn: conn.close()

def verify_user(email, password, is_admin=0):
    conn = get_db_connection()
    if not conn: return False, None, None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, full_name, is_admin 
            FROM users 
            WHERE email = ? AND password = ? AND is_admin = ?
        """, (email, password, is_admin))
        user = cursor.fetchone()
        if user:
            return True, user[0], user[1] # Success, UserID, FullName
        return False, None, None
    except sqlite3.Error:
        return False, None, None
    finally:
        if conn: conn.close()

def fetch_admin_metrics():
    conn = get_db_connection()
    if not conn: return {}
    try:
        cursor = conn.cursor()
        metrics = {}
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 0")
        metrics['total_users'] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM interactive_assessments")
        metrics['total_assessments'] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM interactive_assessments WHERE risk_level = 'High Risk'")
        metrics['high_risk_detections'] = cursor.fetchone()[0]
        cursor.execute("SELECT AVG(overall_score) FROM interactive_assessments")
        metrics['avg_cognitive_score'] = cursor.fetchone()[0] or 0
        return metrics
    except sqlite3.Error:
        return {}
    finally:
        if conn: conn.close()

def fetch_all_interactive_assessments():
    conn = get_db_connection()
    if not conn: return pd.DataFrame()
    try:
        query = "SELECT * FROM interactive_assessments ORDER BY assessment_date DESC"
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"Error fetching all interactive data: {e}")
        return pd.DataFrame()
    finally:
        if conn: conn.close()

def save_assessment_record(clinician_id, age, gender, cognitive_scores, speech_features, risk_result):
    """
    Saves a complete assessment record to the database.
    """
    conn = get_db_connection()
    if not conn:
        print("Could not connect to database, unable to save record.")
        return False
        
    try:
        cursor = conn.cursor()
        # 1. Insert/Create a participant record
        cursor.execute(
            "INSERT INTO participants (age, gender) VALUES (?, ?)",
            (age, gender)
        )
        participant_id = cursor.lastrowid
        
        # 2. Insert assessment data
        query = """
            INSERT INTO assessments (
                clinician_id, participant_id, memory_recall_score, object_naming_score, 
                sentence_repetition_score, verbal_fluency_score,
                speech_rate, pause_frequency, hesitation_duration, fluency_score,
                risk_level, risk_explanation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        values = (
            clinician_id,
            participant_id,
            cognitive_scores['memory_recall'],
            cognitive_scores['object_naming'],
            cognitive_scores['sentence_repetition'],
            cognitive_scores['verbal_fluency'],
            speech_features['speech_rate'],
            speech_features['pause_frequency'],
            speech_features['hesitation_duration'],
            speech_features['fluency_score'],
            risk_result['risk_level'],
            risk_result['explanation']
        )
        
        cursor.execute(query, values)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Failed to insert record: {e}")
        return False
    finally:
        if conn: conn.close()
        
def save_rating(user_id, rating, feedback=""):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ratings (user_id, rating, feedback) VALUES (?, ?, ?)", (user_id, rating, feedback))
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        if conn: conn.close()

def fetch_all_assessments(clinician_id):
    """
    Retrieves all assessments joined with participant data for analysis, filtered by clinician.
    """
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
        
    query = """
        SELECT a.*, p.age, p.gender
        FROM assessments a
        JOIN participants p ON a.participant_id = p.id
        WHERE a.clinician_id = ?
    """
    try:
        df = pd.read_sql_query(query, conn, params=(clinician_id,))
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()
    finally:
        if conn: conn.close()

def save_interactive_assessment(clinician_id, patient_id, patient_name, patient_age, patient_gender, cognitive_score, speech_score, overall_score, risk_level, voice_features=None):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO interactive_assessments (
                clinician_id, patient_id, patient_name, patient_age, patient_gender, 
                cognitive_score, speech_score, overall_score, risk_level, voice_features
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
            clinician_id, patient_id, patient_name, patient_age, patient_gender, 
            cognitive_score, speech_score, overall_score, risk_level, voice_features
        ))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Failed to insert interactive record: {e}")
        return False
    finally:
        if conn: conn.close()

def fetch_interactive_assessments(clinician_id, patient_id=None):
    """
    Fetches interactive assessments, strictly isolated by clinician_id.
    """
    conn = get_db_connection()
    if not conn: return pd.DataFrame()
    
    query = "SELECT * FROM interactive_assessments WHERE clinician_id = ?"
    params = [clinician_id]
    
    if patient_id:
        query += " AND patient_id = ?"
        params.append(patient_id)
        
    query += " ORDER BY assessment_date ASC"
    
    try:
        df = pd.read_sql_query(query, conn, params=tuple(params))
        return df
    except Exception as e:
        print(f"Error fetching interactive data: {e}")
        return pd.DataFrame()
    finally:
        if conn: conn.close()

def save_patient_assessment(clinician_id, name, age, gender, overall_score, confidence_score, risk_level, working_memory_score, attention_score, recall_score, speech_rate, recommendation):
    try:
        age_int = int(age)
        if age_int < 16 or age_int > 120:
            return False
    except (ValueError, TypeError):
        return False
        
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        # Find or create patient record by unique identity (name + age + gender).
        # Two patients with the same name but different age or gender are
        # treated as separate patients.
        cursor.execute(
            "SELECT id FROM patients WHERE LOWER(TRIM(name)) = LOWER(TRIM(?)) AND age = ? AND gender = ?",
            (name, age, gender)
        )
        row = cursor.fetchone()
        if row:
            patient_id = row[0]
        else:
            try:
                cursor.execute("INSERT INTO patients (name, age, gender) VALUES (?, ?, ?)", (name, age, gender))
                patient_id = cursor.lastrowid
            except sqlite3.IntegrityError:
                # Composite UNIQUE (name, age, gender) conflict — re-fetch
                cursor.execute(
                    "SELECT id FROM patients WHERE LOWER(TRIM(name)) = LOWER(TRIM(?)) AND age = ? AND gender = ?",
                    (name, age, gender)
                )
                fallback_row = cursor.fetchone()
                if fallback_row:
                    patient_id = fallback_row[0]
                else:
                    return False
        
        # Insert assessment record
        cursor.execute("""
            INSERT INTO assessments (
                clinician_id, patient_id, overall_score, confidence_score, risk_level,
                working_memory_score, attention_score, recall_score, speech_rate, recommendation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (clinician_id, patient_id, overall_score, confidence_score, risk_level,
              working_memory_score, attention_score, recall_score, speech_rate, recommendation))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error saving patient assessment: {e}")
        return False
    finally:
        conn.close()

def fetch_patient_assessments(patient_name):
    conn = get_db_connection()
    if not conn: return pd.DataFrame()
    try:
        query = """
            SELECT a.*, p.name AS patient_name, p.age AS patient_age, p.gender AS patient_gender
            FROM assessments a
            JOIN patients p ON a.patient_id = p.id
            WHERE p.name = ?
            ORDER BY a.assessment_date ASC
        """
        df = pd.read_sql_query(query, conn, params=(patient_name,))
        return df
    except Exception as e:
        print(f"Error fetching patient assessments: {e}")
        return pd.DataFrame()
    finally:
        if conn: conn.close()

def search_patients(query):
    conn = get_db_connection()
    matching_names = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT name FROM patients WHERE name LIKE ?", (f"%{query}%",))
            matching_names = [row[0] for row in cursor.fetchall() if row[0]]
        except Exception as e:
            print(f"Error searching patients: {e}")
        finally:
            conn.close()
    return matching_names

def get_patients_directory():
    """Returns a dataframe of all patients with their age, gender, and total assessment count."""
    conn = get_db_connection()
    if not conn: return pd.DataFrame()
    query = """
        SELECT p.id, p.name, p.age, p.gender, COUNT(a.id) as assessment_count, MAX(a.assessment_date) as last_assessment
        FROM patients p
        LEFT JOIN assessments a ON p.id = a.patient_id
        GROUP BY p.id
        ORDER BY p.name ASC
    """
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"Error fetching patients directory: {e}")
        return pd.DataFrame()
    finally:
        if conn: conn.close()

def get_full_reports():
    """Returns a comprehensive dataframe of all assessments for the reports page."""
    conn = get_db_connection()
    if not conn: return pd.DataFrame()
    query = """
        SELECT a.id, p.id as patient_id, p.name as patient_name, p.age, p.gender, a.assessment_date, 
               a.overall_score, a.risk_level, a.speech_rate as voice_score, 
               a.working_memory_score as memory_score, a.attention_score as sequencing_score,
               a.recall_score as language_score
        FROM assessments a
        JOIN patients p ON a.patient_id = p.id
        ORDER BY a.assessment_date DESC
    """
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"Error fetching reports: {e}")
        return pd.DataFrame()
    finally:
        if conn: conn.close()
