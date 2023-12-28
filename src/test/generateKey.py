import os
import secrets

secret_key = secrets.token_hex(16)
print("Your secret key is:", secret_key)
