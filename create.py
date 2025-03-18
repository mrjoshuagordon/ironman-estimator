import os

# Define the folder structure
folders = [
    "backend",
    "backend/templates",
    "backend/static",
    "ml",
    "frontend",
    "tests",
    "scripts",
    "notebooks",
    "config"
]

# Define the files to create in each directory
files = {
    "backend": ["api.py", "data_parser.py", "models.py", "utils.py", "config.py", "__init__.py"],
    "ml": ["cycling_model.py", "running_model.py", "swimming_model.py", "fatigue_model.py", "predictor.py", "__init__.py"],
    "frontend": ["app.py", "routes.py", "__init__.py"],
    "tests": ["test_api.py", "test_models.py", "test_utils.py", "__init__.py"],
    "scripts": ["fetch_strava_data.py", "setup_db.py"],
    "notebooks": ["model_exploration.ipynb"],
    "config": ["config.yaml", ".env"],
}

# Create directories
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# Create files inside directories
for folder, filenames in files.items():
    for filename in filenames:
        file_path = os.path.join(folder, filename)
        with open(file_path, "w") as f:
            f.write("")  # Create an empty file

# Create additional standalone files in root directory
root_files = ["requirements.txt", "setup.py", "run.py", "README.md", ".gitignore"]
for filename in root_files:
    with open(filename, "w") as f:
        f.write("")  # Create an empty file

print("✅ Project structure successfully created!")
