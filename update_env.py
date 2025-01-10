import os
import random
import string

def generate_secret_key():
    """Generate a new Django secret key."""
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.SystemRandom().choice(chars) for _ in range(50))

def update_env_file(env_path=".env"):
    """Update or add the DJANGO_SECRET_KEY in the .env file."""
    try:
        if not os.path.exists(env_path):
            print(f"{env_path} not found. Creating a new one...")
            with open(env_path, 'w') as file:
                file.write(f"DJANGO_SECRET_KEY={generate_secret_key()}\n")
            return

        with open(env_path, 'r') as file:
            lines = file.readlines()

        updated = False
        with open(env_path, 'w') as file:
            for line in lines:
                if line.startswith("DJANGO_SECRET_KEY="):
                    file.write(f"DJANGO_SECRET_KEY={generate_secret_key()}\n")
                    updated = True
                else:
                    file.write(line)
            if not updated:
                file.write(f"DJANGO_SECRET_KEY={generate_secret_key()}\n")
        print(f"Updated {env_path} with a new Django secret key.")
    except Exception as e:
        print(f"Error updating {env_path}: {e}")

if __name__ == "__main__":
    update_env_file()