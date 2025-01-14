# Image Organiser by Location

This Python script organises images into folders based on locations specified in a JSON file. It's designed to efficiently handle large image datasets and prevent overwriting existing folders.

## Features

* **Organises images from a source directory into subfolders based on location names.**
* **Reads location names from a JSON file for flexibility.**
* **Sanitises location names to create valid folder names.**
* **Uses a state file to track processed locations and resume from where it left off.**
* **Processes locations in batches for better control and to handle large datasets.**
* **Cycles through multiple original folders to distribute images evenly.**
* **Handles cases where there are not enough images in an original folder.**
* **Warns if a folder for a location already exists and skips that location.**
* **Provides clear console output for progress tracking and error handling.**
* **Allows loading configuration from environment variables or a `.env` file.**

## Requirements

* Python 3
* Libraries: `os`, `json`, `shutil`, `sys`, `dotenv`, `argparse`

## Usage

1. **Install the required libraries.** 
   ``pip install os json shutil sys dotenv argparse``
2. Prepare your input:
  ◦ Source Directory (SOURCE_DIR): A directory containing subfolders of images. Each subfolder can represent a different category or source.
  ◦ Target Directory (TARGET_DIR): The directory where new folders will be created for each location.
  ◦ Locations JSON (LOCATIONS_JSON): A JSON file containing an array of location names.
  ◦ State File (STATE_FILE): (Optional) A file to store the progress of the script (default: state.json).
3. Configure the script:
  ◦ Environment Variables: You can set the above paths as environment variables.
  ◦ .env File: Create a .env file in the same directory as the script and define the variables there.
  ◦ Command Line Arguments: Use the --env flag to load configuration from the .env file.
4. Run the script:
5. The script will prompt you for any missing configuration values.

## Configuration

• BATCH_SIZE: The number of locations to process per run (default: 20).
• IMAGES_PER_FOLDER: The number of images to copy to each new location folder (default: 6).
Example
```
{
  "locations": [
    "London",
    "Paris",
    "Tokyo",
    "New York",
    "Sydney"
  ]
}
```

## How it works

• The script reads locations from the locations.json file.

• It checks the state.json file to determine which locations have already been processed.

• It processes locations in batches, creating a new folder for each location in the target directory.

• Images are selected from the original folders in a cyclical manner, ensuring even distribution.

• If a location folder already exists, the script skips that location to prevent overwriting.

• The script updates the state.json file after each batch, so you can resume the process if interrupted.



## Notes

• The script sanitises location names to remove invalid characters for folder names.

• If there are not enough images in an original folder to meet the IMAGES_PER_FOLDER requirement, the script will copy all available images and issue a warning.

• Make sure the source_dir contains subfolders with images, as the script relies on these to distribute images across location folders.
