import os

def load_services():
    services = []
    for folder in os.listdir('services'):
        services.append(folder)
    return services


def rename_folder(old_name, new_name):
    if os.path.exists(old_name) and os.path.isdir(old_name):
        os.rename(old_name, new_name) 
        
def rename_service(old_name, new_name):
    rename_folder(f'services/{old_name}', f'services/{new_name}')

# Example usage
if __name__ == '__main__':
    rename_service('Instabot', 'Instagram Service')
    print(load_services())