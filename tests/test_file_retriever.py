import unittest
from aggregator.file_retriever import FileRetriever
from aggregator.file_detector import FileDetector

class TestFileRetriever(unittest.TestCase):

    def test_retrieve_files_path_directory(self):
        # Utilisez un répertoire de test pour cela
        retriever = FileRetriever('test_directory', supported_extensions=['.eml', '.mbox'], file_detector_class=FileDetector)
        retriever.retrieve_files_path()
        self.assertGreater(len(retriever.filepath_dict['emails']), 0)
        self.assertGreater(len(retriever.filepath_dict['mbox']), 0)

    def test_retrieve_files_path_file(self):
        retriever = FileRetriever('test_email.eml', supported_extensions=['.eml'], file_detector_class=FileDetector)
        retriever.retrieve_files_path()
        self.assertIn('test_email.eml', retriever.filepath_dict['emails'])

    def test_invalid_path(self):
        retriever = FileRetriever('invalid_path', supported_extensions=['.eml'], file_detector_class=FileDetector)
        with self.assertRaises(ValueError):
            retriever.retrieve_files_path()

if __name__ == '__main__':
    unittest.main()
