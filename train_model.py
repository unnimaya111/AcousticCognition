import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

def train():
    csv_file = "dementia_dataset.csv"
    if not os.path.exists(csv_file):
        print(f"Dataset {csv_file} not found. Please run export_dataset.py first.")
        return

    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"Error reading dataset: {e}")
        return

    print("Dataset loaded successfully.")

    if len(df) < 10:
        print("Not enough data to train a reliable model. Add more assessment records.")
        return

    # Clean numeric columns
    numeric_cols = [
        'age', 'memory_score', 'object_score', 'sequencing_score',
        'clock_score', 'voice_score', 'wpm', 'pause_count', 'long_pause_count',
        'silence_ratio', 'hesitation_count', 'fluency_score'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        else:
            df[col] = 0

    # Clean gender column
    if 'gender' not in df.columns:
        df['gender'] = 'Unknown'
    df['gender'] = df['gender'].fillna('Unknown')
    
    # Clean target column
    if 'risk_label' not in df.columns:
        print("Target column 'risk_label' not found.")
        return
        
    df['risk_label'] = df['risk_label'].fillna('Unknown')
    df = df[df['risk_label'] != 'Unknown']

    # Standardize risk labels
    label_map = {
        "Moderate Risk (Suggest Follow-up)": "Moderate Risk",
        "High Risk (Significant Delay Detected)": "High Risk",
        "Mild Risk": "Low Risk"
    }
    df['risk_label'] = df['risk_label'].replace(label_map)
    print("Risk labels standardized.")
    
    if len(df) < 10:
        print("Not enough data to train a reliable model.")
        return

    # Print class distribution after standardization
    print("Class distribution:")
    print(df['risk_label'].value_counts())

    # Encode categorical variables
    gender_enc = LabelEncoder()
    df['gender_encoded'] = gender_enc.fit_transform(df['gender'].astype(str))
    
    label_enc = LabelEncoder()
    df['risk_encoded'] = label_enc.fit_transform(df['risk_label'].astype(str))

    # Prepare features and target
    features = numeric_cols + ['gender_encoded']
    X = df[features]
    y = df['risk_encoded']

    unique_classes = df['risk_encoded'].nunique()
    
    if unique_classes <= 1:
        print("Only one risk class found. Model training skipped.")
        return

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train Random Forest Classifier
    print("Training Random Forest...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    clf.fit(X_train, y_train)

    # Evaluate
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    print(f"Model accuracy: {acc:.4f}")

    # Fix classification_report safely
    present_labels = np.unique(np.concatenate([y_test, y_pred]))
    
    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            y_pred,
            labels=present_labels,
            target_names=label_enc.inverse_transform(present_labels),
            zero_division=0
        )
    )

    # Save outputs only when training succeeds
    if clf is not None and gender_enc is not None and label_enc is not None:
        try:
            joblib.dump(clf, "dementia_risk_model.pkl")
            joblib.dump(gender_enc, "gender_encoder.pkl")
            joblib.dump(label_enc, "risk_label_encoder.pkl")
            
            print("Model training completed successfully.")
            print("Saved: dementia_risk_model.pkl")
            print("Saved: gender_encoder.pkl")
            print("Saved: risk_label_encoder.pkl")
            
            # Verify files exist after saving
            print(f"{os.path.exists('dementia_risk_model.pkl')}")
            print(f"{os.path.exists('gender_encoder.pkl')}")
            print(f"{os.path.exists('risk_label_encoder.pkl')}")
            
        except Exception as e:
            print(f"Error saving model files: {str(e)}")
    else:
        print("Error: Model or encoders are invalid. Files were not saved.")

if __name__ == "__main__":
    train()
