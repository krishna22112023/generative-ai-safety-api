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
        # Basic user ID patterns with assignment operators
        re.compile(r"(?:user[_-]?id|userid|uid|userId|user-ID)\s*[:=]\s*[\"']?([A-Za-z0-9_-]{3,})[\"']?", re.IGNORECASE),
        
        # JSON format user IDs
        re.compile(r"\"user_id\"\s*:\s*\"[A-Za-z0-9_-]{3,}\"", re.IGNORECASE),
        re.compile(r"\"userId\"\s*:\s*\"[A-Za-z0-9_-]{3,}\"", re.IGNORECASE),
        re.compile(r"\"uid\"\s*:\s*\"[A-Za-z0-9_-]{3,}\"", re.IGNORECASE),
        
        # XML format user IDs
        re.compile(r"<user[_-]?id>[A-Za-z0-9_-]{3,}</user[_-]?id>", re.IGNORECASE),
        
        # Query parameter format
        re.compile(r"[?&]user[_-]?id=[A-Za-z0-9_-]{3,}", re.IGNORECASE),
        
        # Environment variable format
        re.compile(r"USER[_-]?ID\s*=\s*[\"']?[A-Za-z0-9_-]{3,}[\"']?"),
    ],
    
    "PASSWORD": [
        # Basic password patterns
        re.compile(r"(?:password|passwd|pwd|pass|user_pwd|user-pass)\s*[:=]\s*[\"']?([^\s\"']{6,})[\"']?", re.IGNORECASE),
        
        # JSON format passwords
        re.compile(r"\"password\"\s*:\s*\"[^\s\"']{6,}\"", re.IGNORECASE),
        re.compile(r"\"passwd\"\s*:\s*\"[^\s\"']{6,}\"", re.IGNORECASE),
        re.compile(r"\"pwd\"\s*:\s*\"[^\s\"']{6,}\"", re.IGNORECASE),
        
        # URLs with embedded credentials
        re.compile(r"[A-Za-z]{3,10}:\/\/[^\/\s:@]{3,20}:[^\/\s:@]{3,20}@", re.IGNORECASE),
        
        # Database connection strings
        re.compile(r"password\s*=\s*[^\s;\"']{6,}", re.IGNORECASE),
        re.compile(r"pwd\s*=\s*[^\s;\"']{6,}", re.IGNORECASE),
        
        # Environment variables
        re.compile(r"PASSWORD\s*=\s*[\"']?[^\s\"']{6,}[\"']?"),
        re.compile(r"PWD\s*=\s*[\"']?[^\s\"']{6,}[\"']?"),
        
        # XML format
        re.compile(r"<password>[^\s<>]{6,}</password>", re.IGNORECASE),
        
        # YAML format
        re.compile(r"password\s*:\s*[^\s]{6,}", re.IGNORECASE),
        
        # PEM / PGP key blocks (multiline, DOTALL)
        re.compile(r"-----BEGIN (?:RSA |DSA |EC |PGP )?(?:PRIVATE|PUBLIC) KEY-----[\s\S]*?-----END (?:RSA |DSA |EC |PGP )?(?:PRIVATE|PUBLIC) KEY-----", re.IGNORECASE),
    ],
    
    "API_KEY": [
        # Generic API key patterns
        re.compile(r"api[_-]?key\s*[:=]\s*[\"']?[A-Za-z0-9_-]{16,}[\"']?", re.IGNORECASE),
        re.compile(r"apikey\s*[:=]\s*[\"']?[A-Za-z0-9_-]{16,}[\"']?", re.IGNORECASE),
        
        # OpenAI API keys
        re.compile(r"sk-[A-Za-z0-9]{20,}"),
        
        # Stripe keys
        re.compile(r"sk_live_[A-Za-z0-9]{24}"),
        re.compile(r"sk_test_[A-Za-z0-9]{24}"),
        re.compile(r"rk_live_[A-Za-z0-9]{24}"),
        re.compile(r"pk_(?:live|test)_[A-Za-z0-9]{24}"),
        
        # Google API keys
        re.compile(r"AIza[0-9A-Za-z_-]{35}"),
        
        # AWS Access Key IDs
        re.compile(r"(?:A3T|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}"),
        
        # Slack tokens
        re.compile(r"xoxb-[0-9A-Za-z]{10,48}", re.IGNORECASE),
        re.compile(r"xoxp-[0-9A-Za-z]{10,48}", re.IGNORECASE),
        re.compile(r"xoxa-[0-9A-Za-z]{10,48}", re.IGNORECASE),
        re.compile(r"xoxr-[0-9A-Za-z]{10,48}", re.IGNORECASE),
        
        # GitHub tokens
        re.compile(r"ghp_[A-Za-z0-9]{36}"),
        re.compile(r"gho_[A-Za-z0-9]{36}"),
        re.compile(r"ghs_[A-Za-z0-9]{36}"),
        re.compile(r"ghr_[A-Za-z0-9]{36}"),
        
        # Twitter API keys
        re.compile(r"[A-Za-z0-9]{25}"),
        re.compile(r"AAAA[A-Za-z0-9%]{80,}"),
        
        # JSON format
        re.compile(r"\"api_key\"\s*:\s*\"[A-Za-z0-9_-]{16,}\"", re.IGNORECASE),
        re.compile(r"\"apiKey\"\s*:\s*\"[A-Za-z0-9_-]{16,}\"", re.IGNORECASE),
        
        # Environment variables
        re.compile(r"API[_-]?KEY\s*=\s*[\"']?[A-Za-z0-9_-]{16,}[\"']?"),
        
        # Azure keys
        re.compile(r"[A-Za-z0-9+/]{88}=="),
        
        # SendGrid
        re.compile(r"SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}"),
        
        # Mailgun
        re.compile(r"key-[A-Za-z0-9]{32}"),
        
        # Discord
        re.compile(r"[MN][A-Za-z\d]{23}\.[A-Za-z\d_-]{6}\.[A-Za-z\d_-]{27}"),
        
        # Facebook Access Token
        re.compile(r"EAA[A-Za-z0-9]{100,}"),
        
        # Firebase
        re.compile(r"[A-Za-z0-9_-]{39}"),
        
        # Heroku API Key
        re.compile(r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"),
        
        # JWT tokens (basic pattern)
        re.compile(r"eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*"),
    ],
    
    "ENCRYPTION_KEY": [
        # Generic encryption key patterns
        re.compile(r"(?:encryption|encrypt|secret|private|public)[_-]?key\s*[:=]\s*[\"']?[A-Za-z0-9+/=]{16,}[\"']?", re.IGNORECASE),
        
        # PEM private keys
        re.compile(r"-----BEGIN RSA PRIVATE KEY-----[\s\S]*?-----END RSA PRIVATE KEY-----"),
        re.compile(r"-----BEGIN PRIVATE KEY-----[\s\S]*?-----END PRIVATE KEY-----"),
        re.compile(r"-----BEGIN EC PRIVATE KEY-----[\s\S]*?-----END EC PRIVATE KEY-----"),
        re.compile(r"-----BEGIN DSA PRIVATE KEY-----[\s\S]*?-----END DSA PRIVATE KEY-----"),
        
        # PEM public keys
        re.compile(r"-----BEGIN RSA PUBLIC KEY-----[\s\S]*?-----END RSA PUBLIC KEY-----"),
        re.compile(r"-----BEGIN PUBLIC KEY-----[\s\S]*?-----END PUBLIC KEY-----"),
        
        # PGP keys
        re.compile(r"-----BEGIN PGP PRIVATE KEY BLOCK-----[\s\S]*?-----END PGP PRIVATE KEY BLOCK-----"),
        re.compile(r"-----BEGIN PGP PUBLIC KEY BLOCK-----[\s\S]*?-----END PGP PUBLIC KEY BLOCK-----"),
        
        # SSH keys
        re.compile(r"ssh-rsa [A-Za-z0-9+/]{100,}"),
        re.compile(r"ssh-dss [A-Za-z0-9+/]{100,}"),
        re.compile(r"ssh-ed25519 [A-Za-z0-9+/]{68}"),
        re.compile(r"ecdsa-sha2-[A-Za-z0-9]+ [A-Za-z0-9+/]{100,}"),
        
        # JSON Web Keys (JWK)
        re.compile(r"\"kty\"\s*:\s*\"(?:RSA|EC|oct)\""),
        
        # Base64 encoded keys (longer patterns, 32+ chars)
        re.compile(r"[A-Za-z0-9+/]{64,}={0,2}"),
        
        # Hex encoded keys
        re.compile(r"[0-9a-fA-F]{64}"),  # 32 byte key in hex
        re.compile(r"[0-9a-fA-F]{32}"),  # 16 byte key in hex
        
        # JSON format
        re.compile(r"\"encryption_key\"\s*:\s*\"[A-Za-z0-9+/=]{16,}\"", re.IGNORECASE),
        re.compile(r"\"encryptionKey\"\s*:\s*\"[A-Za-z0-9+/=]{16,}\"", re.IGNORECASE),
        re.compile(r"\"secret_key\"\s*:\s*\"[A-Za-z0-9+/=]{16,}\"", re.IGNORECASE),
        
        # Environment variables
        re.compile(r"ENCRYPTION[_-]?KEY\s*=\s*[\"']?[A-Za-z0-9+/=]{16,}[\"']?"),
        re.compile(r"SECRET[_-]?KEY\s*=\s*[\"']?[A-Za-z0-9+/=]{16,}[\"']?"),
        re.compile(r"PRIVATE[_-]?KEY\s*=\s*[\"']?[A-Za-z0-9+/=]{16,}[\"']?"),
        
        # Certificate files
        re.compile(r"-----BEGIN CERTIFICATE-----[\s\S]*?-----END CERTIFICATE-----"),
        
        # AWS Secret Access Keys
        re.compile(r"[A-Za-z0-9/+=]{40}"),
        
        # Kubernetes service account tokens
        re.compile(r"eyJhbGciOiJSUzI1NiIsImtpZCI6[A-Za-z0-9_-]*"),
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
        "API_KEY": ["api_key", "apikey", "api-key"],
        "ENCRYPTION_KEY": ["encryption_key", "encryptionkey", "encryption-key"],
    }
    for label, variants in label_variants.items():
        if label not in counts:
            continue
        for variant in variants:
            counts[label] += len(parse_regex(text, variant))

    return counts

# ----------------------------------------------------------------------


