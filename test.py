# from configparser import ConfigParser

# config = ConfigParser()
# config.read("config.ini")

# config.set("test", "user", "sohag")
# with open("config.ini", "w") as file:
#     config.write(file)
# a = config.get("test", "user")
# print(a)

to_use = {'reel.target_username': 'sohag', 'options.likes': '2',
    'options.accounts': '2', 'reel.range': '10'}

{
    'reel': {
        'target_username': 'sohag',
        'range': '10',
    },
    'options': {
        'likes': '2',
        'accounts': '2',
    }
}

from utils import update_config_file

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

con = convert_dict(to_use)

update_config_file('Facebook', con)

