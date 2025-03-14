import os
import random
import string
from cryptography.fernet import Fernet

def generate_secret_key():
    """Generate a new Django secret key."""
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.SystemRandom().choice(chars) for _ in range(50))

def generate_encryption_key():
    """Generate a key for encryption and decryption."""
    return Fernet.generate_key()

def encrypt_secret(secret, key):
    """Encrypt the secret using the provided key."""
    fernet = Fernet(key)
    return fernet.encrypt(secret.encode()).decode()

def decrypt_secret(encrypted_secret, key):
    """Decrypt the secret using the provided key."""
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_secret.encode()).decode()

def update_env_file(env_path=".env"):
    """Update or add the DJANGO_SECRET_KEY in the .env file."""
    try:
        if not os.path.exists(env_path):
            print(f"{env_path} not found. Creating a new one...")
            with open(env_path, 'w') as file:
                encryption_key = generate_encryption_key()
                encrypted_secret = encrypt_secret(generate_secret_key(), encryption_key)
                file.write(f"DJANGO_SECRET_KEY={encrypted_secret}\n")
                file.write(f"ENCRYPTION_KEY={encryption_key.decode()}\n")
            return

        with open(env_path, 'r') as file:
            lines = file.readlines()

        updated = False
        with open(env_path, 'w') as file:
            for line in lines:
                if line.startswith("DJANGO_SECRET_KEY="):
                    encrypted_secret = encrypt_secret(generate_secret_key(), encryption_key)
                    file.write(f"DJANGO_SECRET_KEY={encrypted_secret}\n")
                    updated = True
                else:
                    file.write(line)
            if not updated:
                encrypted_secret = encrypt_secret(generate_secret_key(), encryption_key)
                file.write(f"DJANGO_SECRET_KEY={encrypted_secret}\n")
                file.write(f"ENCRYPTION_KEY={encryption_key.decode()}\n")
        print(f"Updated {env_path} with a new Django secret key.")
    except Exception as e:
        print(f"Error updating {env_path}: {e}")

if __name__ == "__main__":
    update_env_file()