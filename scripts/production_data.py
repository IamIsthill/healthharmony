from django.core.management.utils import get_random_secret_key


def generate_secret_key():
    secret_key = get_random_secret_key()
    print(f"Secret key: {secret_key}")


if __name__ == "__main__":
    print()
    print("Update the data in the env file...")
    generate_secret_key()
