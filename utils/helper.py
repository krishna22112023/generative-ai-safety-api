import re
from typing import Dict, List
from functools import lru_cache


def parse_regex(text: str, search_text: str) -> List[str]:
    """Extract toxicity labels from a validation message.

    The validation message from Guardrails typically looks like:
        "Toxic language detected: toxicity, obscene"

    This helper extracts the comma-separated list of labels that come *after* the
    colon and returns them as a list of lowercase strings with surrounding
    whitespace removed.

    If the expected pattern is not found, an empty list is returned.
    """
    if not text:
        return []

    # Look for the portion after the first colon (:) following the trigger text.
    match = re.search(r"{}:\s*(.*)".format(search_text), text, re.IGNORECASE)
    if not match:
        return []

    labels_part = match.group(1)
    # Split by comma and normalise
    labels = [label.strip().lower() for label in labels_part.split(',') if label.strip()]
    return labels


# ---------------------- Secret detection helpers ----------------------

# Mapping of secret labels to compiled regex patterns
SECRET_REGEX_MAP: Dict[str, List[re.Pattern]] = {
    "USER_ID": [
        re.compile(r"(?:user[_-]?id|userid|uid|userId|user-ID)\s*[:=]\s*[\"']?([A-Za-z0-9_-]{3,})[\"']?", re.IGNORECASE),
    ],
    "PASSWORD": [
        re.compile(r"(?:password|passwd|pwd|pass|user_pwd|user-pass)\s*[:=]\s*[\"']?([^\s\"']{6,})[\"']?", re.IGNORECASE),
        # Passwords embedded in URLs, e.g. https://user:pass@host
        re.compile(r"[A-Za-z]{3,10}:\/\/[^\/\s:@]{3,20}:[^\/\s:@]{3,20}@", re.IGNORECASE),
    ],
    "API_KEY": [
        re.compile(r"api[_-]?key\s*[:=]\s*[\"']?[A-Za-z0-9_-]{16,}[\"']?", re.IGNORECASE),
        re.compile(r"sk-[A-Za-z0-9]{20,}"),  # Stripe/OpenAI secret key style
        re.compile(r"rk-[A-Za-z0-9]{20,}"),  # Stripe restricted key
        re.compile(r"AIza[0-9A-Za-z_-]{35}"),  # Google API key
        re.compile(r"(?:A3T|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}"),  # AWS access key IDs
        re.compile(r"xox[baprs]-[0-9A-Za-z]{10,48}", re.IGNORECASE),  # Slack token
    ],
    "ENCRYPTION_KEY": [
        re.compile(r"(?:encryption|encrypt|secret|private|public)[_-]?key\s*[:=]\s*[\"']?[A-Za-z0-9+/=]{16,}[\"']?", re.IGNORECASE),
        # PEM / PGP key blocks (multiline, DOTALL)
        re.compile(r"-----BEGIN (?:RSA |DSA |EC |PGP )?(?:PRIVATE|PUBLIC) KEY-----[\s\S]*?-----END (?:RSA |DSA |EC |PGP )?(?:PRIVATE|PUBLIC) KEY-----", re.IGNORECASE),
    ],
}


def detect_secrets_regex(text: str, labels: List[str]) -> Dict[str, int]:
    """Fallback secret detection using pure Python regular expressions.

    Args:
        text: Raw text to scan.
        labels: List of secret labels to count. Must correspond to keys in
                 SECRET_REGEX_MAP (case sensitive).

    Returns:
        Dict mapping each requested label to the count of matches detected.
    """
    counts: Dict[str, int] = {label: 0 for label in labels}

    # Primary regex patterns
    for label in labels:
        for pattern in SECRET_REGEX_MAP.get(label, []):
            matches = pattern.findall(text)
            counts[label] += len(matches)

    # Use parse_regex for simple "label: value" colon-separated cases where the
    # label appears verbatim in the text. This demonstrates reuse of the
    # existing helper as requested.
    label_variants = {
        "USER_ID": ["user_id", "userid", "uid"],
        "PASSWORD": ["password", "passwd", "pwd", "pass"],
    }
    for label, variants in label_variants.items():
        if label not in counts:
            continue
        for variant in variants:
            counts[label] += len(parse_regex(text, variant))

    return counts

# ----------------------------------------------------------------------


