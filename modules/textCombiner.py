import os
import json

class FileReader:
    def __init__(self, folder_path):
        """
        Initialize the FileReader object with a folder path.
        
        Args:
            folder_path (str): The path to the folder containing the files.
        """
        self.folder_path = folder_path
        self.combined_text = ""

    def _read_markdown(self, file_path):
        """
        Reads a Markdown file and returns its content.
        
        Args:
            file_path (str): The path to the Markdown file.
        
        Returns:
            str: The content of the Markdown file.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def _read_json(self, file_path):
        """
        Reads a JSON file and returns its formatted content as a string.
        
        Args:
            file_path (str): The path to the JSON file.
        
        Returns:
            str: The formatted content of the JSON file.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return json.dumps(data, indent=4)

    def read_files(self):
        """
        Reads all Markdown and JSON files in the folder and concatenates their contents.
        
        Returns:
            str: A single string containing the concatenated contents of all files.
        """
        for file_name in os.listdir(self.folder_path):
            file_path = os.path.join(self.folder_path, file_name)

            if os.path.isfile(file_path) and file_name.endswith(('.md', '.json')):
                try:
                    if file_name.endswith('.md'):
                        self.combined_text += self._read_markdown(file_path) + "\n"
                    elif file_name.endswith('.json'):
                        self.combined_text += self._read_json(file_path) + "\n"
                except Exception as e:
                    print(f"Error reading {file_name}: {e}")

        return self.combined_text

# Example usage
# if __name__ == "__main__":
#     folder_path = "./your_folder"  # Replace with your folder path
#     file_reader = FileReader(folder_path)
#     all_text = file_reader.read_files()
#     print(all_text)
