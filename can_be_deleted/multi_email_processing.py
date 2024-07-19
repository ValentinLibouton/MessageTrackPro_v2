# Standard Python imports
import os
import glob
# Project imports
from can_be_deleted import single_email_processing


def find_email_files(directory_path):
    """
    Recursively searches the given directory for .mbox and .eml files.

    :param directory_path: The root directory path to start the search from.
    :return: A dictionary with two keys, 'mbox' and 'eml', each containing a list
             of file paths matching the respective file extensions found within the
             directory and its subdirectories.
    """
    result = {'mbox': [], 'eml': []}

    for root, dirs, files in os.walk(directory_path):
        for extension in ['mbox', 'eml']:
            for filepath in glob.glob(os.path.join(root, f'*.{extension}')):
                result[extension].append(filepath)
    result['mbox'].sort()
    result['eml'].sort()
    return result

def extract_email_data_from_emails_list(list_of_paths:list, with_attachments=False) -> list:
    """
    Extract email data from a list of email file paths.

    This function iterates through a list of file paths, each pointing to an email file, and
    extracts data from each email. The extracted data includes email headers and body content,
    and optionally, attachments. The results are aggregated into a list, with each element
    corresponding to the extracted data from a single email file.

    Args:
        list_of_paths (list): A list of file paths, each pointing to an individual email file.
        with_attachments (bool, optional): A flag indicating whether to extract attachments
                                            from the email files. Defaults to False, meaning
                                            attachments will not be extracted by default.

    Returns:
        list: A list of dictionaries, where each dictionary contains the extracted data from a
              single email file. The structure and content of the dictionary depend on the
              implementation of `single_email_processing.extract_email_data`.

    Note:
        - This function relies on `single_email_processing.extract_email_data` to process each
          email file individually. Changes or updates to the extraction process in that function
          will affect the output of this function.
        - The function does not handle errors that may occur during the processing of individual
          email files. It is assumed that `single_email_processing.extract_email_data` includes
          appropriate error handling or that the list of paths is pre-validated.
    """
    data = None
    data_list = []
    for file_path in list_of_paths:
        data = single_email_processing.extract_email_data(file_path=file_path, with_attachments=with_attachments)
        data_list.append(data)
    return data_list

def extract_email_data_from_mbox(file_path, with_attachments=False):
    pass

def extract_email_data_from_mboxs_list(list_of_paths:list, with_attachments=False) -> list:
    pass