import unittest
from aggregator.file_detector import FileDetector

class TestFileDetector(unittest.TestCase):

    def test_is_email(self):
        detector = FileDetector("test_email.eml")
        self.assertTrue(detector.is_email())

    def test_is_mbox(self):
        detector = FileDetector("test_mbox.mbox")
        self.assertTrue(detector.is_mbox())

    def test_detect_email(self):
        detector = FileDetector("test_email.eml")
        self.assertEqual(detector.detect_type(), 'email')

    def test_detect_mbox(self):
        detector = FileDetector("test_mbox.mbox")
        self.assertEqual(detector.detect_type(), 'mbox')

    def test_detect_unknown(self):
        detector = FileDetector("unknown_file.txt")
        self.assertEqual(detector.detect_type(), 'unknown')

if __name__ == '__main__':
    unittest.main()
