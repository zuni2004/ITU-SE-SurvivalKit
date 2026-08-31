import string

# Standard English letter frequencies
ENGLISH_FREQ = {
    "A": 0.0817,
    "B": 0.0150,
    "C": 0.0278,
    "D": 0.0425,
    "E": 0.1270,
    "F": 0.0223,
    "G": 0.0202,
    "H": 0.0609,
    "I": 0.0697,
    "J": 0.0015,
    "K": 0.0077,
    "L": 0.0403,
    "M": 0.0241,
    "N": 0.0675,
    "O": 0.0751,
    "P": 0.0193,
    "Q": 0.0010,
    "R": 0.0599,
    "S": 0.0633,
    "T": 0.0906,
    "U": 0.0276,
    "V": 0.0098,
    "W": 0.0236,
    "X": 0.0015,
    "Y": 0.0197,
    "Z": 0.0007,
}


def caesar_encrypt(text, shift):
    result = ""
    for char in text:
        if char.isalpha():
            base = ord("A") if char.isupper() else ord("a")
            result += chr((ord(char) - base + shift) % 26 + base)
        else:
            result += char
    return result


def caesar_decrypt(text, shift):
    return caesar_encrypt(text, -shift)


def score_text(text):
    """Scores text based on English letter frequencies."""
    score = 0
    total_letters = sum(1 for c in text if c.isalpha())
    if total_letters == 0:
        return 0

    text = text.upper()
    for char in string.ascii_uppercase:
        count = text.count(char)
        freq = count / total_letters
        # Chi-squared inspired scoring (lower difference is better, so we negate it)
        score -= abs(freq - ENGLISH_FREQ[char])
    return score


def break_caesar(ciphertext):
    """Automatically breaks a Caesar cipher using frequency analysis."""
    best_score = -float("inf")
    best_shift = 0
    best_plaintext = ""

    for shift in range(26):
        plaintext = caesar_decrypt(ciphertext, shift)
        score = score_text(plaintext)
        if score > best_score:
            best_score = score
            best_shift = shift
            best_plaintext = plaintext

    return best_shift, best_plaintext


# --- Test Cases ---
if __name__ == "__main__":
    # Test your tool on at least five ciphertexts[cite: 21].
    ciphertexts = [
        caesar_encrypt("THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG", 7),
        caesar_encrypt("INFORMATION SECURITY IS FASCINATING", 12),
        caesar_encrypt("FREQUENCY ANALYSIS MAKES BREAKING CLASSICAL CIPHERS EASY", 23),
        caesar_encrypt("CRYPTOGRAPHY SECURES DIGITAL COMMUNICATIONS", 4),
        caesar_encrypt("AUTOMATED TOOLS CAN DECRYPT MESSAGES WITHOUT THE KEY", 15),
    ]

    print("--- Caesar Cipher Breaker Results ---")
    for i, ct in enumerate(ciphertexts):
        shift, plaintext = break_caesar(ct)
        print(f"Ciphertext {i+1}: {ct}")
        print(f"Recovered (Shift {shift}): {plaintext}\n")
