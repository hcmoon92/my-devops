import sys
import datetime

# Get current time
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Print a message to standard output
print(f"[{current_time}] Hello from my_script.py!")

# Optional: Print to standard error to demonstrate capturing both outputs
print("This is an error message.", file=sys.stderr)
