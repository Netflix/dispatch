def create_filter_expression(filters: dict, model: str) -> list[dict]:
    """Python implementation of @/search/utils/createFilterExpression"""

    filter_expression = []
    for key, value in filters.items():
        sub_filter = []

        # Check if a time window is specified
        if "start" in value:
            if value["start"]:
                sub_filter.append(
                    {
                        "and": [
                            {"model": model, "field": key, "op": ">=", "value": value["start"]},
                            {"model": model, "field": key, "op": "<=", "value": value["end"]},
                        ]
                    }
                )
        else:
            for val in value:
                if not val:
                    continue
                # Check if the filter is being applied to an id
                if "id" in val:
                    sub_filter.append(
                        {"model": key.title(), "field": "id", "op": "==", "value": val["id"]}
                    )
                # Check if the filter is being applied to a name
                elif "name" in val:
                    sub_filter.append(
                        {"model": key.title(), "field": "name", "op": "==", "value": val["name"]}
                    )
                # Check if the filter is being applied to a different model
                elif "model" in val:
                    if val["value"]:
                        sub_filter.append(
                            {
                                "model": val["model"],
                                "field": val["field"],
                                "op": "==",
                                "value": val["value"],
                            }
                        )
                # If no special condition is met, apply the filter to the current model
                else:
                    sub_filter.append({"model": model, "field": key, "op": "==", "value": val})

        # Only add the sub_filter to filter_expression if it has any filters in it
        if len(sub_filter) > 0:
            # If the key is "visibility", use "and" as the condition
            if key == "visibility":
                filter_expression.append({"and": sub_filter})
            # Use "or" as the condition for all other filters
            else:
                filter_expression.append({"or": sub_filter})

    return filter_expression
