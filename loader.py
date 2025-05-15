import json
import yaml
import os

def load_config(file_path) -> dict[str, any]:
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    try:
        with open(file_path, 'r') as file:
            match ext:
                case ".json":
                    return json.load(file)
                case '.yml', '.yaml':
                    return yaml.safe_load(file)
                case _:
                    raise ValueError(f"Unsupported file extension: {ext}")
    except Exception as ex:
        raise Exception(f"Failed to load '{file_path}': {ex}")