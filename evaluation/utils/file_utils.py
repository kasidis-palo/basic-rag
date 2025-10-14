import os
import json
import time


def write_jsonl_file(dir_path, file_name, data_list) -> str:
    # if folder does not exist, create it
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    # if file already exists, delete it
    file_path = os.path.join(dir_path, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Write the content to the JSONL file
    with open(file_path, "w") as file:
        for item in data_list:
            json_line = json.dumps(item, ensure_ascii=False)
            file.write(json_line + "\n")
    print(f"JSONL content written to {file_path}")

    return file_path


def read_jsonl_file(file_path: str) -> list:
    """
    Read a JSONL file and return a list of dictionaries.

    :param file_path: Path to the JSONL file.
    :return: List of dictionaries.
    """
    data = []
    with open(file_path, "r") as file:
        for line in file:
            data.append(json.loads(line))
    return data

def get_unique_name_for_file_name(file_name: str) -> str:
    """
    Get a unique file name by appending the current timestamp to the file name.

    :param file_name: Original file name.
    :return: Unique file name.
    """
    # Get the current timestamp
    timestamp = int(time.time())
    # Append the timestamp to the file name
    unique_file_name = f"{timestamp}_{file_name}"
    return unique_file_name