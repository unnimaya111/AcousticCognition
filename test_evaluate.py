import json
from scoring_logic import evaluate_risk

sample_scores = {
    'memory': 4,
    'naming': 2,
    'odd_one_out': 70,
    'fluency': 10,
    'acoustic': {'fluency_score': 80}
}

result = evaluate_risk(sample_scores)
print(json.dumps(result, indent=2))
