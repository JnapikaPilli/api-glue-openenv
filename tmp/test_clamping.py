
def _clamp_score(score: float) -> float:
    return round((score * 0.98) + 0.01, 3)

test_cases = [0.0, 0.5, 1.0, 0.25, 0.75]
print("Score Mapping Test:")
for s in test_cases:
    mapped = _clamp_score(s)
    print(f"  {s} -> {mapped}  (Strictly between 0 and 1: {0 < mapped < 1})")
