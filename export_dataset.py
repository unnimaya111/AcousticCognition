import sqlite3
import pandas as pd
import json
import os

def export_data():
    db_name = None
    if os.path.exists('acoustic_cognition.db'):
        db_name = 'acoustic_cognition.db'
    elif os.path.exists('dementia_screening.db'):
        db_name = 'dementia_screening.db'
        
    if not db_name:
        print("Database not found. Make sure dementia_screening.db or acoustic_cognition.db exists.")
        return

    print(f"Database used: {db_name}")

    try:
        # Read-only connection
        db_uri = f"file:{db_name}?mode=ro"
        conn = sqlite3.connect(db_uri, uri=True)
        
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables found: {tables}")

        df_patients = pd.DataFrame()
        df_assessments = pd.DataFrame()
        df_interactive = pd.DataFrame()

        # Identify tables
        patient_tables = ['patients', 'patient_records']
        assessment_tables = ['assessments', 'assessment_results']
        
        found_pt_table = next((t for t in patient_tables if t in tables), None)
        found_ass_table = next((t for t in assessment_tables if t in tables), None)

        if found_pt_table:
            df_patients = pd.read_sql_query(f"SELECT * FROM {found_pt_table}", conn)
        
        if found_ass_table:
            df_assessments = pd.read_sql_query(f"SELECT * FROM {found_ass_table}", conn)
            
        if 'interactive_assessments' in tables:
            df_interactive = pd.read_sql_query("SELECT * FROM interactive_assessments", conn)

        records = []

        # Process standard assessments joined with patients
        if not df_assessments.empty and not df_patients.empty:
            # Join on patient_id if available
            df_joined = pd.merge(
                df_assessments, 
                df_patients, 
                left_on='patient_id', 
                right_on='id', 
                how='left',
                suffixes=('_ass', '_pat')
            )
            
            for _, row in df_joined.iterrows():
                record = {
                    'age': row.get('age', 0),
                    'gender': row.get('gender', 'Unknown'),
                    'memory_score': row.get('working_memory_score', 0),
                    'object_score': row.get('recall_score', 0),
                    'sequencing_score': row.get('attention_score', 0),
                    'clock_score': 0,
                    'voice_score': row.get('speech_rate', 0),
                    'wpm': row.get('speech_rate', 0),
                    'pause_count': 0,
                    'long_pause_count': 0,
                    'silence_ratio': 0,
                    'hesitation_count': 0,
                    'fluency_score': row.get('speech_rate', 0),
                    'risk_label': row.get('risk_level', 'Unknown')
                }
                records.append(record)

        # Process interactive_assessments (richer voice features)
        if not df_interactive.empty:
            for _, row in df_interactive.iterrows():
                vf = {}
                if pd.notna(row.get('voice_features')):
                    try:
                        vf = json.loads(row['voice_features'])
                    except Exception:
                        pass
                        
                record = {
                    'age': row.get('patient_age', 0),
                    'gender': row.get('patient_gender', 'Unknown'),
                    'memory_score': row.get('cognitive_score', 0),
                    'object_score': 0,
                    'sequencing_score': 0,
                    'clock_score': 0,
                    'voice_score': row.get('speech_score', 0),
                    'wpm': vf.get('speech_rate_wpm', 0) if isinstance(vf, dict) else 0,
                    'pause_count': vf.get('pause_count', 0) if isinstance(vf, dict) else 0,
                    'long_pause_count': vf.get('long_pauses', 0) if isinstance(vf, dict) else 0,
                    'silence_ratio': vf.get('silence_ratio', 0) if isinstance(vf, dict) else 0,
                    'hesitation_count': vf.get('hesitation_count', 0) if isinstance(vf, dict) else 0,
                    'fluency_score': vf.get('fluency_score', 0) if isinstance(vf, dict) else 0,
                    'risk_label': row.get('risk_level', 'Unknown')
                }
                records.append(record)

        if not records:
            print("No assessment records found. Complete some assessments first.")
            return

        df_out = pd.DataFrame(records)
        
        # Safety rules for null values
        df_out.fillna({'gender': 'Unknown', 'risk_label': 'Unknown'}, inplace=True)
        df_out.fillna(0, inplace=True)
        
        # Ensure all requested columns exist precisely
        expected_cols = [
            'age', 'gender', 'memory_score', 'object_score', 'sequencing_score',
            'clock_score', 'voice_score', 'wpm', 'pause_count', 'long_pause_count',
            'silence_ratio', 'hesitation_count', 'fluency_score', 'risk_label'
        ]
        
        for col in expected_cols:
            if col not in df_out.columns:
                df_out[col] = 'Unknown' if col in ['gender', 'risk_label'] else 0
                
        df_out = df_out[expected_cols]
        csv_path = "dementia_dataset.csv"
        df_out.to_csv(csv_path, index=False)
        
        print(f"Number of records exported: {len(df_out)}")
        print(f"CSV saved path: {os.path.abspath(csv_path)}")

    except Exception as e:
        print(f"Error reading database: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    export_data()
