
def truncate_dictionary(dictionary:dict[str, object]):
    MAX_LENGTH = 100
    return {
        k: str(v)[:MAX_LENGTH] + "..."
        if len(str(v)) > MAX_LENGTH
        else str(v)
        for k,v in dictionary.items()
    }
