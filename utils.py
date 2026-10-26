import logging
from transformers import AutoTokenizer

logger = logging.getLogger("p-code")

# Cache for tokenizers to avoid reloading from disk/network on every call
_TOKENIZER = None

def truncate_dictionary(dictionary:dict[str, object]):
    MAX_LENGTH = 100
    return {
        k: str(v)[:MAX_LENGTH] + "..."
        if len(str(v)) > MAX_LENGTH
        else str(v)
        for k,v in dictionary.items()
    }

def count_tokens(text: str, model_name: str):
    if not text:
        return 0

    try:
        global _TOKENIZER
        if _TOKENIZER == None:
            _TOKENIZER = AutoTokenizer.from_pretrained(model_name)
        return len(_TOKENIZER.encode(text))
    except OSError as e:
        logger.warning(f"Tokenizer failed for model {model_name}, using fallback heuristic. Error: {e}")
        return int(len(text) / 4)
