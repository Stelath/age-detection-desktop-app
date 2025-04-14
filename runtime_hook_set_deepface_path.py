# runtime_hook_set_deepface_path.py
import os
from pathlib import Path

# Define the hidden folder in the user's home directory where models should be stored.
model_dir = Path.home() / ".deepface" / "weights"

# Set an environment variable that DeepFace can check (adjust the variable name if needed)
os.environ["DEEPFACE_HOME"] = str(model_dir)

# Ensure the directory exists so that models are downloaded here.
model_dir.mkdir(parents=True, exist_ok=True)