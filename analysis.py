import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.api as sm
from database import fetch_all_assessments
import io

def run_hypothesis_testing():
    """
    Validates the system by running an Independent T-Test separating 
    the "Low Risk" (Healthy) and "High Risk" (At-Risk) groups to see
    if their speech features significantly differ.
    """
    df = fetch_all_assessments()
    
    if df.empty:
        print("Not enough data in the database to run analysis.")
        return
        
    # We define "Healthy" as Low Risk and "At-Risk" as High Risk for this hypothesis testing
    healthy = df[df['risk_level'] == 'Low']
    at_risk = df[df['risk_level'] == 'High']
    
    if len(healthy) < 2 or len(at_risk) < 2:
        print("Need at least 2 samples in both 'Low' and 'High' risk categories to perform a T-test.")
        return
        
    print(f"--- Data Science Validation Report ---")
    print(f"Healthy control (Low Risk) N={len(healthy)}")
    print(f"At-Risk group (High Risk) N={len(at_risk)}")
    print("-" * 40)
    
    # Analyze Speech Rate
    t_stat, p_val = stats.ttest_ind(healthy['speech_rate'], at_risk['speech_rate'], equal_var=False)
    print(f"Speech Rate -> T-Statistic: {t_stat:.3f}, P-Value: {p_val:.3f}")
    if p_val < 0.05:
        print("  Result: Significant difference in speaking rate between healthy and at-risk.")
    else:
        print("  Result: No significant difference in speaking rate.")
        
    # Analyze Pause Frequency
    t_stat_pause, p_val_pause = stats.ttest_ind(healthy['pause_frequency'], at_risk['pause_frequency'], equal_var=False)
    print(f"Pause Frequency -> T-Statistic: {t_stat_pause:.3f}, P-Value: {p_val_pause:.3f}")
    if p_val_pause < 0.05:
        print("  Result: Significant difference in pause frequency between healthy and at-risk.")
    else:
        print("  Result: No significant difference in pause frequency.")
        
    # Statsmodels OLS summary (Correlation Analysis via Regression)
    # Predict Fluency Score based on Cognitive Tasks
    print("\n--- Correlation Analysis (Statsmodels OLS) ---")
    try:
        y = df['fluency_score']
        X = df[['memory_recall_score', 'verbal_fluency_score', 'sentence_repetition_score']]
        X = sm.add_constant(X)
        model = sm.OLS(y, X).fit()
        print(model.summary())
    except Exception as e:
        print(f"Could not run regression: {e}")

if __name__ == "__main__":
    run_hypothesis_testing()
