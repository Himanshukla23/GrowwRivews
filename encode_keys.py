import base64
import os

def encode_file(filepath):
    try:
        with open(filepath, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except Exception as e:
        return f"Error reading {filepath}: {e}"

creds_b64 = encode_file('credentials.json')
token_b64 = encode_file('data/google_token.json')

with open('render_env_keys.txt', 'w') as f:
    f.write("Add these two environment variables to your Render dashboard:\n\n")
    f.write(f"Key: GOOGLE_CREDENTIALS_BASE64\n")
    f.write(f"Value: {creds_b64}\n\n")
    f.write(f"Key: GOOGLE_TOKEN_BASE64\n")
    f.write(f"Value: {token_b64}\n")

print("Successfully generated render_env_keys.txt")
