import os


def delete_file(file_path):
    """Delete a file if it exists."""
    try:
        os.remove(file_path)
        print(f"Deleted file: {file_path}")
    except OSError as e:
        print(f"Error deleting file {file_path}: {e}")


delete_file("result.json")
delete_file("scan_signal.txt")
