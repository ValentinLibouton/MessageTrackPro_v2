import os
import glob

def find_email_files(directory_path):
    """
    Recursively searches the given directory for .mbox and .eml files.

    :param directory_path: The root directory path to start the search from.
    :return: A dictionary with two keys, 'mbox' and 'eml', each containing a list
             of file paths matching the respective file extensions found within the
             directory and its subdirectories.
    """
    # ToDo: This function must to be tested !
    result = {'mbox': [], 'eml': []}

    for root, dirs, files in os.walk(directory_path):
        for extension in ['mbox', 'eml']:
            for filepath in glob.glob(os.path.join(root, f'*.{extension}')):
                result[extension].append(filepath)

    return result
