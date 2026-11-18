import math
import streamlit as st
def evaluate_risk(scores):
    """
    Evaluates early dementia risk using weighted scoring and provides explainable results.
    """
    
    # Extract raw scores
    s_mem = scores.get('memory', 0)    # 0-5
    s_nam = scores.get('naming', 0)    # 0-3
    s_clock = scores.get('clock_arrangement', 0) # 0-100 (percentage)
    s_seq = scores.get('sequencing', 0) # 0-100 (percentage)
    s_aco = scores.get('acoustic', {}).get('fluency_score', 0) if isinstance(scores.get('acoustic'), dict) else 0 # 0-100
    
    # 1. Normalization (0-100)
    norm_mem = (s_mem / 5) * 100 if s_mem else 0
    norm_nam = (s_nam / 3) * 100 if s_nam else 0
    norm_seq = s_seq if s_seq else 0
    norm_clock = s_clock if s_clock else 0
    norm_lang = norm_nam
    norm_aco = s_aco
    explanation = ""
    
    domain_scores = {
        "Memory Recall": norm_mem,
        "Object Identification": norm_lang,
        "Activity Sequencing": norm_seq,
        "Clock Arrangement": norm_clock,
        "Voice Analysis": norm_aco
    }
    
    # Age-based risk contribution (medically reasonable)
    try:
        age = st.session_state.get('patient_info', {}).get('age', None)
    except Exception:
        age = None
    if age is None:
        age_risk_modifier = 0
    elif age < 50:
        age_risk_modifier = 0
    elif 50 <= age < 65:
        age_risk_modifier = 3
    elif 65 <= age < 75:
        age_risk_modifier = 6
    else:
        age_risk_modifier = 10
    
    # 2. Smoothing Logic (Prevent one anomalous low score from dominating if others are very high)
    domain_values = list(domain_scores.values())
    min_score = min(domain_values)
    min_domain = [k for k, v in domain_scores.items() if v == min_score][0]
    
    if min_score < 20:
        other_scores = [v for k, v in domain_scores.items() if k != min_domain]
        avg_others = sum(other_scores) / len(other_scores) if other_scores else 0
        if avg_others > 80:
            domain_scores[min_domain] = 50 # Reduce penalty impact
            
    # 3. Calculate Weighted Final Score
    # Memory: 25%, Object: 20%, Activity: 20%, Clock: 15%, Voice: 20%
    base_score = (
        (domain_scores["Memory Recall"] * 0.25) +
        (domain_scores["Object Identification"] * 0.20) +
        (domain_scores["Activity Sequencing"] * 0.20) +
        (domain_scores["Clock Arrangement"] * 0.15) +
        (domain_scores["Voice Analysis"] * 0.20)
    )
    # Apply age risk modifier (subtract to lower the score)
    final_score = base_score - age_risk_modifier
    # Clamp between 0 and 100
    final_score = max(0, min(100, final_score))
    final_score = round(final_score, 1)

    # 4. Confidence Range Calculation
    mean_score = sum(domain_scores.values()) / 5
    variance = sum((x - mean_score) ** 2 for x in domain_scores.values()) / 5
    std_dev = math.sqrt(variance)

    if std_dev < 15:
        confidence_level = "High"
    elif std_dev <= 30:
        confidence_level = "Medium"
    else:
        confidence_level = "Low"
    
    # 5. Risk Level and Interpretations
    if final_score >= 75:
        risk_level = "Low Risk"
        risk_color = "#A8E6CF"
        interpretation = "Results are within normal variation, with age factored in."
    elif final_score >= 50:
        risk_level = "Moderate Risk"
        risk_color = "#FFD3B6"
        interpretation = "Mild cognitive variations detected; age contributes modestly. Monitor over time."
    else:
        risk_level = "High Risk"
        risk_color = "#FF8B94"
        interpretation = "Significant cognitive markers detected; age contributes to elevated risk. Consider clinical consultation."
    
    # 6. Plain Language Domain Labels
    # Audio: Good / Needs attention
    audio_label = "Good" if domain_scores["Voice Analysis"] >= 60 else "Needs attention"
    
    # Memory: Strong / Moderate / Weak
    if domain_scores["Memory Recall"] >= 80: mem_label = "Strong"
    elif domain_scores["Memory Recall"] >= 50: mem_label = "Moderate"
    else: mem_label = "Weak"
    
    # Sequencing & Clock
    seq_label = "Strong" if domain_scores["Activity Sequencing"] >= 60 else "Weak"
    clock_label = "Strong" if domain_scores["Clock Arrangement"] >= 60 else "Weak"
    
    # Language: Moderate / Strong
    if domain_scores["Object Identification"] >= 70: lang_label = "Strong"
    elif domain_scores["Object Identification"] >= 40: lang_label = "Moderate"
    else: lang_label = "Needs attention"

    # 7. Dynamic Explanation Text
    weak_domains = []
    if audio_label == "Needs attention": weak_domains.append("speech patterns")
    if mem_label in ["Weak", "Moderate"]: weak_domains.append("memory recall")
    if seq_label == "Weak" or clock_label == "Weak": weak_domains.append("executive reasoning")
    if lang_label in ["Needs attention", "Moderate"]: weak_domains.append("language tasks")
    
    if weak_domains:
        joined = " and ".join([", ".join(weak_domains[:-1]), weak_domains[-1]] if len(weak_domains) > 2 else weak_domains)
        prefix = "Slight difficulty" if final_score >= 50 else "Difficulty"
        explanation = f"{prefix} in {joined} contributed to a {risk_level.lower()} score."
    else:
        explanation = f"Strong consistent performance across all domains contributed to a {risk_level.lower()} score."
    
    # Append age explanation
    explanation = f"{explanation} Age is considered as a contributing dementia risk factor along with cognitive and speech-based assessment results."

    return {
        "final_score": final_score,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "interpretation": interpretation,
        "explanation": explanation,
        "confidence_level": confidence_level,
        "breakdown": {
            "Voice Analysis": {"value": round(domain_scores["Voice Analysis"], 1), "label": audio_label},
            "Memory Recall": {"value": round(domain_scores["Memory Recall"], 1), "label": mem_label},
            "Object Identification": {"value": round(domain_scores["Object Identification"], 1), "label": lang_label},
            "Activity Sequencing": {"value": round(domain_scores["Activity Sequencing"], 1), "label": seq_label},
            "Clock Arrangement": {"value": round(domain_scores["Clock Arrangement"], 1), "label": clock_label}
        }
    }
