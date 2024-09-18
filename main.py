import os
import json
import shutil
import sys
from dotenv import load_dotenv
import argparse

def load_environment():
    """
    Load environment variables from a .env file if it exists.
    """
    load_dotenv()  # Loads variables from .env into environment

def get_env_variable(var_name, prompt_text, default=None):
    """
    Retrieve an environment variable or prompt the user for input.
    """
    value = os.getenv(var_name)
    if not value:
        if default:
            user_input = input(f"{prompt_text} [Default: {default}]: ").strip()
            return user_input if user_input else default
        else:
            user_input = input(f"{prompt_text}: ").strip()
            while not user_input:
                print("This field is required.")
                user_input = input(f"{prompt_text}: ").strip()
            return user_input
    return value

def load_locations(json_path):
    """
    Load locations from the specified JSON file.
    """
    try:
        with open(json_path, 'r') as file:
            data = json.load(file)
        return data['locations']
    except Exception as e:
        print(f"Error loading locations.json: {e}")
        sys.exit(1)

def load_state(state_path):
    """
    Load the list of processed locations from the state file.
    """
    if not os.path.exists(state_path):
        return []
    try:
        with open(state_path, 'r') as file:
            state = json.load(file)
        return state.get('processed_locations', [])
    except Exception as e:
        print(f"Error loading state.json: {e}")
        sys.exit(1)

def save_state(state_path, processed_locations):
    """
    Save the list of processed locations to the state file.
    """
    try:
        with open(state_path, 'w') as file:
            json.dump({'processed_locations': processed_locations}, file, indent=4)
    except Exception as e:
        print(f"Error saving state.json: {e}")
        sys.exit(1)

def get_original_folders(source_dir):
    """
    Retrieve a list of subdirectories in the source directory.
    """
    return [f for f in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, f))]

def get_image_files(folder_path):
    """
    Retrieve a list of image files in the specified folder, sorted in the order they appear.
    """
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
    return sorted([
        f for f in os.listdir(folder_path) 
        if os.path.isfile(os.path.join(folder_path, f)) and os.path.splitext(f)[1].lower() in image_extensions
    ])

def sanitize_folder_name(folder_name):
    """
    Remove or replace characters that are not allowed in folder names.
    """
    # Define a list of invalid characters based on your OS
    invalid_chars = r'<>:"/\|?*'
    for char in invalid_chars:
        folder_name = folder_name.replace(char, '_')
    return folder_name

def main(config):
    """
    Main function to organize images based on the provided configuration.
    """
    # Load locations
    locations = load_locations(config['locations_json'])
    total_locations = len(locations)
    print(f"Total locations available: {total_locations}")

    # Load state
    processed_locations = load_state(config['state_file'])
    print(f"Already processed locations: {len(processed_locations)}")

    # Determine the next batch
    unprocessed_locations = [loc for loc in locations if loc not in processed_locations]
    if not unprocessed_locations:
        print("All locations have been processed.")
        return

    batch_size = config['batch_size']
    current_batch = unprocessed_locations[:batch_size]
    print(f"Processing {len(current_batch)} locations from index {locations.index(current_batch[0])} to {locations.index(current_batch[-1])}")

    # Get list of original folders
    original_folders = get_original_folders(config['source_dir'])
    total_original_folders = len(original_folders)
    print(f"Total original folders found: {total_original_folders}")

    if not original_folders:
        print("No original folders found. Exiting.")
        return

    # Ensure target directory exists
    os.makedirs(config['target_dir'], exist_ok=True)

    # Process each location in the current batch
    for i, location in enumerate(current_batch):
        # Sanitize folder name to remove invalid characters
        sanitized_location = sanitize_folder_name(location)
        new_folder_name = sanitized_location  # Use the exact location string as folder name, sanitized
        new_folder_path = os.path.join(config['target_dir'], new_folder_name)

        # Check if folder already exists to prevent overwriting
        if os.path.exists(new_folder_path):
            print(f"Folder '{new_folder_name}' already exists. Skipping this location.")
            processed_locations.append(location)  # Mark as processed to avoid retrying
            continue

        # Create the new folder
        try:
            os.makedirs(new_folder_path, exist_ok=False)
            print(f"Created new folder: {new_folder_path}")
        except Exception as e:
            print(f"Error creating folder '{new_folder_name}': {e}")
            continue

        # Determine which original folder to use (cycle if necessary)
        original_folder = original_folders[i % total_original_folders]
        original_folder_path = os.path.join(config['source_dir'], original_folder)
        print(f"Selecting from original folder: {original_folder}")

        # Get list of image files
        images = get_image_files(original_folder_path)
        if len(images) < config['images_per_folder']:
            print(f"Warning: Not enough images in '{original_folder}'. Needed {config['images_per_folder']}, found {len(images)}.")
            selected_images = images  # Take all available
        else:
            selected_images = images[:config['images_per_folder']]  # Take first N images

        # Copy images to the new folder
        for image in selected_images:
            src_image_path = os.path.join(original_folder_path, image)
            dest_image_path = os.path.join(new_folder_path, image)
            try:
                shutil.copy2(src_image_path, dest_image_path)
                print(f"Copied '{image}' to '{new_folder_name}'")
            except Exception as e:
                print(f"Error copying '{image}' to '{new_folder_name}': {e}")

        print(f"Finished processing location '{location}' into folder '{new_folder_name}'\n")

        # Mark as processed
        processed_locations.append(location)

    # Update state
    save_state(config['state_file'], processed_locations)
    print(f"Batch processing complete. {len(current_batch)} locations processed.")

if __name__ == "__main__":
    # Load environment variables
    load_environment()

    # Initialize argument parser for flexibility
    parser = argparse.ArgumentParser(description="Organize images into folders based on locations.json")
    parser.add_argument('--env', action='store_true', help="Load configuration from .env file")
    args = parser.parse_args()

    # Load environment variables from .env if --env flag is used or .env file exists
    if args.env or os.path.exists('.env'):
        load_environment()

    # Function to prompt or retrieve environment variables
    def retrieve_config():
        config = {}
        config['source_dir'] = get_env_variable('SOURCE_DIR', "Enter the path to the source directory containing original folders")
        config['target_dir'] = get_env_variable('TARGET_DIR', "Enter the path to the target directory where new folders will be created")
        config['locations_json'] = get_env_variable('LOCATIONS_JSON', "Enter the path to the locations.json file")
        config['state_file'] = get_env_variable('STATE_FILE', "Enter the path to the state file", default='state.json')
        config['batch_size'] = int(get_env_variable('BATCH_SIZE', "Enter the number of folders to process per run", default='20'))
        config['images_per_folder'] = int(get_env_variable('IMAGES_PER_FOLDER', "Enter the number of images to copy per new folder", default='6'))
        return config

    # Retrieve configuration
    config = retrieve_config()

    # Validate paths
    if not os.path.exists(config['source_dir']):
        print(f"Error: Source directory '{config['source_dir']}' does not exist.")
        sys.exit(1)
    if not os.path.exists(config['locations_json']):
        print(f"Error: JSON file '{config['locations_json']}' does not exist.")
        sys.exit(1)

    # Run the main function
    main(config)
