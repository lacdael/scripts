import subprocess

# Path to your external script (e.g., 'script.sh' or 'script.py')
script_path = 'your_script.py'

# Run the script and capture the output
try:
    # `subprocess.run` is recommended for Python 3.5+ for running commands
    result = subprocess.run(
        ['python', script_path],   # If the script is a Python script
        capture_output=True,       # Capture stdout and stderr
        text=True,                 # Decode the output as a string
        check=True                 # Raise an exception if the script returns an error code
    )

    # Access stdout and stderr
    print("Stdout:", result.stdout)
    print("Stderr:", result.stderr)

except subprocess.CalledProcessError as e:
    print(f"An error occurred while running the script: {e}")

