def remove_none_values_from_dict(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}
