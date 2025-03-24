import os

# Log
filename = input("Enter the name for the log file (default: log.txt): ").strip()
if not filename:
    filename = "log"
log_file_path = os.path.expanduser(f"~/{filename}.txt")
log_file = open(log_file_path, "a")
print(f"Log file: {log_file_path}")

def log_to_file(message):
    """Log messages to the log file."""
    log_file.write(message + "\n")
    log_file.flush()