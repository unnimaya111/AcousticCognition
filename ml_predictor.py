import os
import joblib
import numpy as np
import pandas as pd

def predict_ml_risk(features_dict):
    try:
        model_path = "dementia_risk_model.pkl"
        gender_enc_path = "gender_encoder.pkl"
        label_enc_path = "risk_label_encoder.pkl"

        # 2. Verify files exist before loading
        if not (os.path.exists(model_path) and os.path.exists(gender_enc_path) and os.path.exists(label_enc_path)):
            return {
                "available": False,
                "predicted_risk": None,
                "confidence": None,
                "message": "ML model not trained yet"
            }

        # 1. Load model and encoders
        clf = joblib.load(model_path)
        gender_enc = joblib.load(gender_enc_path)
        label_enc = joblib.load(label_enc_path)

        # 4. Validate input data (fill missing with 0)
        numeric_cols = [
            'age', 'memory_score', 'object_score', 'sequencing_score',
            'clock_score', 'voice_score', 'wpm', 'pause_count', 'long_pause_count',
            'silence_ratio', 'hesitation_count', 'fluency_score'
        ]
        
        parsed_data = {}
        for col in numeric_cols:
            val = features_dict.get(col, 0)
            try:
                val = float(val)
            except (ValueError, TypeError):
                val = 0.0
            parsed_data[col] = val

        # Handle Gender fallback
        gender_val = str(features_dict.get('gender', 'Unknown'))
        
        # 5. Encode gender safely
        if gender_val in gender_enc.classes_:
            encoded_gender = gender_enc.transform([gender_val])[0]
        else:
            if "Unknown" in gender_enc.classes_:
                encoded_gender = gender_enc.transform(["Unknown"])[0]
            else:
                encoded_gender = 0

        # 6. Create the feature vector
        # Note: We use pandas DataFrame here to guarantee the columns map correctly 
        # against the model which was trained using pandas DataFrames.
        feature_vector = pd.DataFrame([{
            'age': parsed_data['age'],
            'memory_score': parsed_data['memory_score'],
            'object_score': parsed_data['object_score'],
            'sequencing_score': parsed_data['sequencing_score'],
            'clock_score': parsed_data['clock_score'],
            'voice_score': parsed_data['voice_score'],
            'wpm': parsed_data['wpm'],
            'pause_count': parsed_data['pause_count'],
            'long_pause_count': parsed_data['long_pause_count'],
            'silence_ratio': parsed_data['silence_ratio'],
            'hesitation_count': parsed_data['hesitation_count'],
            'fluency_score': parsed_data['fluency_score'],
            'gender_encoded': encoded_gender
        }])

        # 7. Predict
        pred_encoded = clf.predict(feature_vector)[0]
        
        # 8. Get confidence
        probabilities = clf.predict_proba(feature_vector)[0]
        max_prob = float(np.max(probabilities)) * 100

        # 9. Decode prediction
        pred_label = label_enc.inverse_transform([pred_encoded])[0]

        # 10. Return final dictionary
        return {
            "available": True,
            "predicted_risk": pred_label,
            "confidence": round(max_prob, 1),
            "message": "ML prediction successful"
        }

    except Exception as e:
        # 11. Catch all exception handling
        return {
            "available": False,
            "predicted_risk": None,
            "confidence": None,
            "message": str(e)
        }

# 12. Test Block
if __name__ == "__main__":
    import json
    
    sample_data = {
        "age": 68,
        "gender": "Female",
        "memory_score": 80,
        "object_score": 75,
        "sequencing_score": 90,
        "clock_score": 85,
        "voice_score": 70,
        "wpm": 110,
        "pause_count": 3,
        "long_pause_count": 1,
        "silence_ratio": 0.18,
        "hesitation_count": 2,
        "fluency_score": 72
    }
    
    print("Testing ML Predictor...")
    print("\nInput data:")
    print(json.dumps(sample_data, indent=4))
    
    result = predict_ml_risk(sample_data)
    
    print("\nPrediction Result:")
    print(json.dumps(result, indent=4))
