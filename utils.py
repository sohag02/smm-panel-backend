import subprocess
import os
import configparser


def run_script_async(script_path):
    cmd = f"python {script_path}"
    process = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process


def load_scripts():
    return os.listdir("services")


def convert_dict(input_dict):
    result = {}
    for key, value in input_dict.items():
        # Split the key into parts
        parts = key.split('.')
        # Reference to the current level of the result dictionary
        current_level = result
        # Iterate through the parts except for the last one
        for part in parts[:-1]:
            # If the part doesn't exist, create a nested dictionary
            if part not in current_level:
                current_level[part] = {}
            # Move one level deeper
            current_level = current_level[part]
        # Assign the value to the last part of the key
        current_level[parts[-1]] = value
    return result


def update_config_file(script_name: str, data: dict):
    converted_data = convert_dict(data)
    config_file = os.path.join("services", script_name, "config.ini")
    config = configparser.ConfigParser()
    config.read(config_file)

    for section, options in converted_data.items():
        if not config.has_section(section):
            config.add_section(section) 
        for key, value in options.items():
            config.set(section, key, value)

    with open(config_file, 'w') as configfile:
        config.write(configfile)
