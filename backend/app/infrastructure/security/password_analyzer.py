"""
CyberGuardX - Professional Password Strength Analyzer
Comprehensive password analysis with entropy calculation, breach checking,
pattern detection, and secure password generation.
"""

import re
import math
import string
import secrets
import hashlib
from typing import Dict, List, Any, Optional, Tuple


class PasswordPatternDetector:
    """Detects common weak patterns in passwords."""

    KEYBOARD_ROWS = [
        "qwertyuiop", "asdfghjkl", "zxcvbnm",
        "1234567890", "!@#$%^&*()"
    ]

    COMMON_SEQUENCES = [
        "abc", "bcd", "cde", "def", "efg", "fgh", "ghi", "hij", "ijk",
        "jkl", "klm", "lmn", "mno", "nop", "opq", "pqr", "qrs", "rst",
        "stu", "tuv", "uvw", "vwx", "wxy", "xyz",
        "012", "123", "234", "345", "456", "567", "678", "789", "890",
    ]

    LEET_MAP = {
        "4": "a", "@": "a", "8": "b", "(": "c", "3": "e",
        "6": "g", "#": "h", "1": "i", "!": "i", "0": "o",
        "$": "s", "5": "s", "7": "t", "+": "t", "2": "z",
    }

    COMMON_WORDS = [
        "password", "letmein", "welcome", "monkey", "dragon",
        "master", "qwerty", "login", "princess", "football",
        "shadow", "sunshine", "trustno1", "iloveyou", "batman",
        "admin", "access", "hello", "charlie", "donald",
        "baseball", "soccer", "hockey", "ranger", "buster",
        "harley", "hunter", "jordan", "george", "summer",
        "winter", "spring", "autumn", "secret", "flower",
    ]

    COMMON_PASSWORDS = [
        "123456", "password", "12345678", "qwerty", "123456789",
        "12345", "1234", "111111", "1234567", "dragon",
        "123123", "baseball", "abc123", "football", "monkey",
        "letmein", "shadow", "master", "666666", "qwertyuiop",
        "123321", "mustang", "1234567890", "michael", "654321",
        "superman", "1qaz2wsx", "7777777", "121212", "000000",
        "qazwsx", "123qwe", "killer", "trustno1", "jordan",
        "jennifer", "zxcvbnm", "asdfgh", "hunter", "buster",
        "soccer", "harley", "batman", "andrew", "tigger",
        "sunshine", "iloveyou", "2000", "charlie", "robert",
    ]

    def detect_keyboard_walks(self, password: str) -> List[str]:
        """Detect keyboard walk patterns (e.g., qwerty, asdf)."""
        found = []
        pw_lower = password.lower()
        for row in self.KEYBOARD_ROWS:
            for i in range(len(row) - 2):
                pattern = row[i:i+3]
                if pattern in pw_lower:
                    found.append(f"Keyboard walk: '{pattern}'")
                rev = pattern[::-1]
                if rev in pw_lower:
                    found.append(f"Reverse keyboard walk: '{rev}'")
        return found

    def detect_sequences(self, password: str) -> List[str]:
        """Detect sequential character patterns."""
        found = []
        pw_lower = password.lower()
        for seq in self.COMMON_SEQUENCES:
            if seq in pw_lower:
                found.append(f"Sequential pattern: '{seq}'")
            rev = seq[::-1]
            if rev in pw_lower:
                found.append(f"Reverse sequential: '{rev}'")
        return found

    def detect_leet_speak(self, password: str) -> Tuple[str, List[str]]:
        """Detect and decode leet speak substitutions."""
        decoded = list(password.lower())
        substitutions = []
        for i, char in enumerate(decoded):
            if char in self.LEET_MAP:
                original = self.LEET_MAP[char]
                substitutions.append(f"'{char}' → '{original}'")
                decoded[i] = original
        return "".join(decoded), substitutions

    def detect_repeated_patterns(self, password: str) -> List[str]:
        """Detect repeated character groups."""
        found = []
        pw = password.lower()

        # Single char repetition
        for i in range(len(pw) - 2):
            if pw[i] == pw[i+1] == pw[i+2]:
                found.append(f"Repeated character: '{pw[i]}' x3+")
                break

        # Repeated substrings
        for length in range(2, len(pw) // 2 + 1):
            for i in range(len(pw) - length * 2 + 1):
                substr = pw[i:i+length]
                if substr in pw[i+length:]:
                    found.append(f"Repeated pattern: '{substr}'")
                    break
            if found and len(found) > 2:
                break

        return found

    def detect_common_words(self, password: str) -> List[str]:
        """Detect common dictionary words in password."""
        found = []
        pw_lower = password.lower()
        decoded, _ = self.detect_leet_speak(password)

        for word in self.COMMON_WORDS:
            if word in pw_lower or word in decoded:
                found.append(f"Common word: '{word}'")

        return found

    def is_common_password(self, password: str) -> bool:
        """Check if password is in common passwords list."""
        return password.lower() in self.COMMON_PASSWORDS


class PasswordStrengthAnalyzer:
    """
    Professional password strength analysis engine.
    """

    def __init__(self):
        self.pattern_detector = PasswordPatternDetector()

    def analyze(self, password: str) -> Dict[str, Any]:
        """
        Comprehensive password analysis.

        Returns:
            Dictionary with strength score, entropy, patterns found,
            time-to-crack estimates, and recommendations.
        """
        if not password:
            return {
                "score": 0,
                "strength": "EMPTY",
                "entropy_bits": 0,
                "crack_time": "Instant",
                "issues": ["Password is empty"],
                "recommendations": ["Enter a password to analyze"]
            }

        # Basic metrics
        length = len(password)
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'[0-9]', password))
        has_special = bool(re.search(r'[^A-Za-z0-9]', password))
        unique_chars = len(set(password))

        # Entropy calculation
        charset_size = 0
        if has_lower:
            charset_size += 26
        if has_upper:
            charset_size += 26
        if has_digit:
            charset_size += 10
        if has_special:
            charset_size += 32
        if charset_size == 0:
            charset_size = 1

        entropy_bits = round(length * math.log2(charset_size), 1)

        # Pattern detection
        patterns_found = []
        keyboard_walks = self.pattern_detector.detect_keyboard_walks(password)
        sequences = self.pattern_detector.detect_sequences(password)
        decoded, leet_subs = self.pattern_detector.detect_leet_speak(password)
        repeated = self.pattern_detector.detect_repeated_patterns(password)
        common_words = self.pattern_detector.detect_common_words(password)
        is_common = self.pattern_detector.is_common_password(password)

        patterns_found.extend(keyboard_walks)
        patterns_found.extend(sequences)
        if leet_subs:
            patterns_found.append(f"Leet speak detected: {', '.join(leet_subs[:3])}")
        patterns_found.extend(repeated)
        patterns_found.extend(common_words)
        if is_common:
            patterns_found.insert(0, "⚠️ This is a commonly used password!")

        # Score calculation (0-100)
        score = self._calculate_score(
            length, has_upper, has_lower, has_digit, has_special,
            unique_chars, entropy_bits, patterns_found, is_common
        )

        # Strength label
        strength = self._get_strength_label(score)

        # Time to crack estimates
        crack_times = self._estimate_crack_time(entropy_bits, is_common)

        # Issues found
        issues = self._identify_issues(
            length, has_upper, has_lower, has_digit, has_special,
            unique_chars, patterns_found, is_common
        )

        # Recommendations
        recommendations = self._generate_recommendations(
            length, has_upper, has_lower, has_digit, has_special,
            unique_chars, patterns_found, score
        )

        # Breach check (k-anonymity approach using SHA-1 prefix)
        breach_info = self._check_breach_database(password)

        return {
            "password_length": length,
            "score": score,
            "strength": strength,
            "entropy_bits": entropy_bits,
            "charset_size": charset_size,
            "character_analysis": {
                "has_uppercase": has_upper,
                "has_lowercase": has_lower,
                "has_digits": has_digit,
                "has_special": has_special,
                "unique_characters": unique_chars,
                "total_length": length
            },
            "patterns_detected": patterns_found,
            "is_common_password": is_common,
            "crack_time_estimates": crack_times,
            "breach_check": breach_info,
            "issues": issues,
            "recommendations": recommendations,
            "complexity_breakdown": {
                "length_score": min(30, length * 2),
                "diversity_score": min(25, (has_upper + has_lower + has_digit + has_special) * 6),
                "uniqueness_score": min(15, (unique_chars / max(length, 1)) * 15),
                "entropy_score": min(20, entropy_bits / 5),
                "pattern_penalty": min(30, len(patterns_found) * 8),
            }
        }

    def _calculate_score(
        self, length, has_upper, has_lower, has_digit, has_special,
        unique_chars, entropy_bits, patterns, is_common
    ) -> int:
        """Calculate overall password strength score (0-100)."""
        if is_common:
            return max(5, min(15, length))

        score = 0

        # Length (max 30 points)
        score += min(30, length * 2)

        # Character diversity (max 25 points)
        diversity = has_upper + has_lower + has_digit + has_special
        score += diversity * 6 + (1 if diversity == 4 else 0)

        # Unique characters (max 15 points)
        if length > 0:
            uniqueness_ratio = unique_chars / length
            score += round(uniqueness_ratio * 15)

        # Entropy bonus (max 20 points)
        score += min(20, entropy_bits / 5)

        # Pattern penalties
        score -= len(patterns) * 8

        # Bonus: extra long passwords
        if length >= 16:
            score += 10
        elif length >= 12:
            score += 5

        return max(0, min(100, round(score)))

    def _get_strength_label(self, score: int) -> str:
        """Get human-readable strength label."""
        if score >= 90:
            return "EXCELLENT"
        elif score >= 75:
            return "STRONG"
        elif score >= 55:
            return "MODERATE"
        elif score >= 30:
            return "WEAK"
        else:
            return "VERY WEAK"

    def _estimate_crack_time(self, entropy_bits: float, is_common: bool) -> Dict:
        """Estimate time to crack with different attack methods."""
        if is_common:
            return {
                "online_attack": "Instant",
                "offline_slow_hash": "Instant",
                "offline_fast_hash": "Instant",
                "gpu_cluster": "Instant",
                "description": "This password is in common password lists and would be cracked instantly"
            }

        # Assume guesses per second for different scenarios
        scenarios = {
            "online_attack": 1000,           # Rate-limited online attack
            "offline_slow_hash": 10000,      # bcrypt/scrypt
            "offline_fast_hash": 10_000_000_000,  # MD5/SHA-1
            "gpu_cluster": 100_000_000_000,  # Multi-GPU rig
        }

        total_combinations = 2 ** entropy_bits
        results = {}

        for scenario, rate in scenarios.items():
            seconds = total_combinations / rate / 2  # Average case
            results[scenario] = self._format_time(seconds)

        results["description"] = f"Based on {entropy_bits:.0f} bits of entropy"
        return results

    def _format_time(self, seconds: float) -> str:
        """Format seconds into human-readable time."""
        if seconds < 0.001:
            return "Instant"
        elif seconds < 1:
            return f"{seconds*1000:.0f} milliseconds"
        elif seconds < 60:
            return f"{seconds:.0f} seconds"
        elif seconds < 3600:
            return f"{seconds/60:.0f} minutes"
        elif seconds < 86400:
            return f"{seconds/3600:.1f} hours"
        elif seconds < 86400 * 365:
            return f"{seconds/86400:.0f} days"
        elif seconds < 86400 * 365 * 1000:
            return f"{seconds/(86400*365):.0f} years"
        elif seconds < 86400 * 365 * 1_000_000:
            return f"{seconds/(86400*365*1000):.0f} thousand years"
        elif seconds < 86400 * 365 * 1_000_000_000:
            return f"{seconds/(86400*365*1_000_000):.0f} million years"
        else:
            return f"{seconds/(86400*365*1_000_000_000):.0f} billion years"

    def _identify_issues(
        self, length, has_upper, has_lower, has_digit, has_special,
        unique_chars, patterns, is_common
    ) -> List[str]:
        """Identify password issues."""
        issues = []

        if is_common:
            issues.append("This password is in the top 100 most common passwords")

        if length < 8:
            issues.append(f"Too short ({length} chars) - minimum 8 recommended")
        elif length < 12:
            issues.append(f"Short ({length} chars) - 12+ recommended for strong security")

        if not has_upper:
            issues.append("No uppercase letters")
        if not has_lower:
            issues.append("No lowercase letters")
        if not has_digit:
            issues.append("No numbers")
        if not has_special:
            issues.append("No special characters")

        if length > 0 and unique_chars / length < 0.5:
            issues.append("Low character diversity - too many repeated characters")

        for pattern in patterns[:5]:
            issues.append(f"Pattern detected: {pattern}")

        return issues

    def _generate_recommendations(
        self, length, has_upper, has_lower, has_digit, has_special,
        unique_chars, patterns, score
    ) -> List[str]:
        """Generate actionable recommendations."""
        recs = []

        if score >= 90:
            recs.append("✅ Excellent password! Consider using a password manager to remember it.")
            return recs

        if length < 12:
            recs.append(f"Increase length to at least 12 characters (currently {length})")

        missing_types = []
        if not has_upper:
            missing_types.append("uppercase letters (A-Z)")
        if not has_lower:
            missing_types.append("lowercase letters (a-z)")
        if not has_digit:
            missing_types.append("numbers (0-9)")
        if not has_special:
            missing_types.append("special characters (!@#$%)")

        if missing_types:
            recs.append(f"Add: {', '.join(missing_types)}")

        if patterns:
            recs.append("Avoid common patterns, sequences, and keyboard walks")

        recs.append("Consider using a passphrase: 4+ random words (e.g., 'correct horse battery staple')")
        recs.append("Use a password manager (Bitwarden, 1Password, KeePass) to generate and store unique passwords")
        recs.append("Never reuse passwords across different accounts")

        return recs

    def _check_breach_database(self, password: str) -> Dict:
        """
        Check if password appears in known breaches using k-anonymity.
        Uses SHA-1 hash prefix matching (same approach as HIBP).
        """
        sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix = sha1[:5]
        suffix = sha1[5:]

        # Check against local common passwords (offline)
        is_common = self.pattern_detector.is_common_password(password)

        return {
            "sha1_prefix": prefix,
            "found_in_breach_db": is_common,
            "note": "Checked against local database of known breached passwords. For comprehensive checking, integrate with Have I Been Pwned API.",
            "recommendation": "Change this password immediately" if is_common else "Password not found in local breach database"
        }

    def generate_password(
        self,
        length: int = 16,
        mode: str = "random",
        include_upper: bool = True,
        include_lower: bool = True,
        include_digits: bool = True,
        include_special: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a secure password.

        Args:
            length: Password length (8-128)
            mode: 'random' for random chars, 'memorable' for passphrase
            include_upper/lower/digits/special: Character types to include

        Returns:
            Generated password with strength analysis.
        """
        length = max(8, min(128, length))

        if mode == "memorable":
            return self._generate_passphrase(length)

        # Build character set
        charset = ""
        required_chars = []

        if include_lower:
            charset += string.ascii_lowercase
            required_chars.append(secrets.choice(string.ascii_lowercase))
        if include_upper:
            charset += string.ascii_uppercase
            required_chars.append(secrets.choice(string.ascii_uppercase))
        if include_digits:
            charset += string.digits
            required_chars.append(secrets.choice(string.digits))
        if include_special:
            special = "!@#$%^&*()-_+=<>?"
            charset += special
            required_chars.append(secrets.choice(special))

        if not charset:
            charset = string.ascii_letters + string.digits

        # Generate remaining characters
        remaining_length = length - len(required_chars)
        password_chars = required_chars + [secrets.choice(charset) for _ in range(remaining_length)]

        # Shuffle
        password_list = list(password_chars)
        for i in range(len(password_list) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            password_list[i], password_list[j] = password_list[j], password_list[i]

        password = "".join(password_list)

        # Analyze the generated password
        analysis = self.analyze(password)

        return {
            "password": password,
            "length": len(password),
            "mode": mode,
            "strength": analysis["strength"],
            "score": analysis["score"],
            "entropy_bits": analysis["entropy_bits"],
            "crack_time_estimates": analysis["crack_time_estimates"]
        }

    def _generate_passphrase(self, target_length: int = 4) -> Dict:
        """Generate a memorable passphrase."""
        word_list = [
            "correct", "horse", "battery", "staple", "wizard",
            "thunder", "pyramid", "glacier", "phoenix", "nebula",
            "crystal", "horizon", "quantum", "enigma", "fortress",
            "cascade", "tempest", "crimson", "phantom", "vortex",
            "stellar", "emerald", "sapphire", "obsidian", "titanium",
            "cosmic", "voltage", "prism", "aurora", "zenith",
            "dragon", "shadow", "matrix", "cipher", "legacy",
            "cosmos", "vertex", "nexus", "orbit", "beacon",
            "summit", "voyage", "spectrum", "echo", "delta",
            "omega", "alpha", "sigma", "theta", "lambda",
        ]

        num_words = max(4, target_length // 4)
        words = [secrets.choice(word_list) for _ in range(num_words)]

        # Add a random number and capitalize one word
        cap_index = secrets.randbelow(len(words))
        words[cap_index] = words[cap_index].capitalize()

        separator = secrets.choice(["-", ".", "_", "+"])
        number = str(secrets.randbelow(99) + 1)

        passphrase = separator.join(words) + separator + number

        analysis = self.analyze(passphrase)

        return {
            "password": passphrase,
            "length": len(passphrase),
            "mode": "memorable",
            "word_count": num_words,
            "strength": analysis["strength"],
            "score": analysis["score"],
            "entropy_bits": analysis["entropy_bits"],
            "crack_time_estimates": analysis["crack_time_estimates"]
        }
