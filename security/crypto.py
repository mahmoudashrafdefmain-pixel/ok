"""
security/crypto.py — High-security binary encryption and decryption for question banks.
Encrypts CSV data structures into .qbank binary payloads using salted obfuscation + AES-style keystream.
"""
import json
import base64
import hashlib
from pathlib import Path

# Secret salt key for the game question bank encryption
_SECRET_KEY = b"DUMPS_TEST_SUPER_SECRET_QBANK_KEY_2026_V2"

def _derive_keystream(length: int, salt: bytes) -> bytes:
    """Derive a deterministic keystream of exact length from secret key and salt."""
    keystream = bytearray()
    counter = 0
    while len(keystream) < length:
        h = hashlib.sha256(_SECRET_KEY + salt + counter.to_bytes(4, 'big')).digest()
        keystream.extend(h)
        counter += 1
    return bytes(keystream[:length])

def encrypt_data(data: list | dict) -> bytes:
    """Serialize JSON data and encrypt it into a binary byte string."""
    json_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')
    salt = hashlib.md5(json_bytes[:64] + _SECRET_KEY).digest()
    keystream = _derive_keystream(len(json_bytes), salt)
    
    cipher_bytes = bytes(b ^ k for b, k in zip(json_bytes, keystream))
    # Magic header (4 bytes) + salt (16 bytes) + cipher bytes
    payload = b"QBNK" + salt + cipher_bytes
    return payload

def decrypt_data(encrypted_payload: bytes) -> list | dict:
    """Decrypt binary byte payload back into data structure in memory."""
    if not encrypted_payload.startswith(b"QBNK"):
        raise ValueError("Invalid qbank header format.")
    
    salt = encrypted_payload[4:20]
    cipher_bytes = encrypted_payload[20:]
    keystream = _derive_keystream(len(cipher_bytes), salt)
    
    plain_bytes = bytes(c ^ k for c, k in zip(cipher_bytes, keystream))
    json_str = plain_bytes.decode('utf-8')
    return json.loads(json_str)

def encrypt_file(input_csv_path: Path, output_qbank_path: Path):
    """Read CSV file, parse rows, encrypt, and save to output .qbank file."""
    import csv
    with open(input_csv_path, newline='', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    
    encrypted_bytes = encrypt_data(rows)
    with open(output_qbank_path, 'wb') as f:
        f.write(encrypted_bytes)
    print(f"Encrypted {input_csv_path.name} -> {output_qbank_path.name} ({len(rows)} rows, {len(encrypted_bytes)} bytes)")

def load_qbank(qbank_path: Path) -> list[dict]:
    """Load and decrypt a .qbank file directly into memory."""
    with open(qbank_path, 'rb') as f:
        encrypted_bytes = f.read()
    return decrypt_data(encrypted_bytes)

def save_qbank(qbank_path: Path, rows: list[dict]):
    """Encrypt and save rows list directly into a .qbank file."""
    encrypted_bytes = encrypt_data(rows)
    with open(qbank_path, 'wb') as f:
        f.write(encrypted_bytes)
