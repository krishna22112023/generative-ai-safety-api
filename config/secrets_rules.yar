rule USER_ID {
    strings:
        $k1 = /(?:user[_-]?id|userid|userId|uid|user-ID)\s*[:=]\s*[\"']?[A-Za-z0-9_-]{3,}/ nocase
    condition:
        any of them
}

rule PASSWORD {
    strings:
        $k1 = /(?:password|passwd|pwd|pass|user_pwd|user-pass)\s*[:=]\s*[\"']?[^\s\"']{6,}/ nocase
        $url = /[A-Za-z]{3,10}:\/\/[A-Za-z0-9._%+-]{1,}:[^\/\s:@]{3,20}@/ nocase
    condition:
        any of them
}

rule API_KEY {
    strings:
        $generic = /api[_-]?key\s*[:=]\s*[\"']?[A-Za-z0-9_-]{16,}[\"']?/ nocase
        $openai  = /sk-[A-Za-z0-9]{20,}/
        $stripe2 = /rk-[A-Za-z0-9]{20,}/
        $google  = /AIza[0-9A-Za-z_-]{35}/
        $aws     = /(A3T|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}/
        $slack   = /xox[baprs]-[0-9A-Za-z]{10,48}/ nocase
    condition:
        any of them
}

rule ENCRYPTION_KEY {
    strings:
        $named = /(?:encryption|encrypt|secret|private|public)[_-]?key\s*[:=]\s*[\"']?[A-Za-z0-9+\/=]{16,}[\"']?/ nocase
        $pem   = /-----BEGIN (?:RSA |DSA |EC |PGP )?(?:PRIVATE|PUBLIC) KEY-----[\s\S]*?-----END (?:RSA |DSA |EC |PGP )?(?:PRIVATE|PUBLIC) KEY-----/ nocase
    condition:
        any of them
} 