def pad(text, block_size=8):
    """Pads text to ensure it's a multiple of the block size."""
    padding_len = block_size - (len(text) % block_size)
    return text + chr(padding_len) * padding_len


def unpad(text):
    """Removes padding."""
    padding_len = ord(text[-1])
    return text[:-padding_len]


def custom_encrypt(plaintext, key):
    if len(key) < 8:
        raise ValueError("Key must be at least 64 bits (8 characters long).")

    plaintext = pad(plaintext)

    # Step 1: Substitution (Add key character value modulo 256)
    substituted = []
    for i, char in enumerate(plaintext):
        key_char = key[i % len(key)]
        sub_char = chr((ord(char) + ord(key_char)) % 256)
        substituted.append(sub_char)

    # Step 2: Transposition (Reverse every 8-character block)
    ciphertext = ""
    for i in range(0, len(substituted), 8):
        block = substituted[i : i + 8]
        ciphertext += "".join(block[::-1])

    return ciphertext


def custom_decrypt(ciphertext, key):
    # Step 1: Reverse Transposition (Reverse every 8-character block back)
    untransposed = []
    for i in range(0, len(ciphertext), 8):
        block = ciphertext[i : i + 8]
        untransposed.extend(list(block[::-1]))

    # Step 2: Reverse Substitution (Subtract key character value modulo 256)
    plaintext = ""
    for i, char in enumerate(untransposed):
        key_char = key[i % len(key)]
        orig_char = chr((ord(char) - ord(key_char)) % 256)
        plaintext += orig_char

    return unpad(plaintext)


# --- Test Cases ---
if __name__ == "__main__":
    key = "SuperSecretKey"  # > 64 bits
    messages = [
        "Hello, World!",
        "Information Security Assignment 4",
        "This is a strictly confidential test message.",
    ]

    for i, msg in enumerate(messages):
        cipher = custom_encrypt(msg, key)
        decrypted = custom_decrypt(cipher, key)
        print(f"--- Test {i+1} ---")
        print(f"Plaintext:  {msg}")
        print(f"Ciphertext: {repr(cipher)}")
        print(f"Decrypted:  {decrypted}\n")
