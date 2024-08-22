import json


def calculate_score(form_data: str, scoring_schema: str) -> int:
    """Calculates the score of a form.

    Args:
        form_data: A string containing the JSON of the form data with key-value pairs.
        scoring_scheme: A string containing the JSON of the scoring schema. The schema should
        be formated as a list of dictionaries, where each dictionary contains the following keys:
            var: The key of the form data to score.
            includes: A list of values that the form data should include to be scored.
            score: The score to add if the form data meets the criteria.

    Returns:
        int: The total score of the form.
    """
    score = 0

    if not form_data or not scoring_schema:
        return score

    form_vals = json.loads(form_data)
    scoring = json.loads(scoring_schema)

    for s in scoring:
        # get the value of the form data based on the key
        if (var := form_vals.get(s.get("var"))) and (includes := s.get("includes")):
            # if any element in the form data is in the includes list, add the score
            if any(v in includes for v in var):
                score += s.get("score", 0)

    return score
