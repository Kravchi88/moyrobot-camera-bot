import unittest
from unittest.mock import patch, MagicMock
import cv2
from app.services.cameras.video_capture import VideoCaptureThreaded


class TestVideoCaptureThreaded(unittest.TestCase):
    @patch('cv2.VideoCapture')
    def setUp(self, mock_VideoCapture):
        self.mock_cap = MagicMock()
        mock_VideoCapture.return_value = self.mock_cap
        self.video_capture = VideoCaptureThreaded("test_src")

    def test_initialization(self):
        self.mock_cap.set.assert_any_call(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.mock_cap.set.assert_any_call(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.assertTrue(self.video_capture.cap is not None)

    def test_start(self):
        self.video_capture.start()
        self.assertTrue(self.video_capture.started)
        self.assertTrue(self.video_capture.thread.is_alive())

    def test_read(self):
        self.mock_cap.read.return_value = (True, "frame")
        grabbed, frame = self.video_capture.read()
        self.assertTrue(grabbed)
        self.assertEqual(frame, "frame")

    def test_stop(self):
        self.video_capture.start()
        self.video_capture.stop()
        self.assertFalse(self.video_capture.started)

    @patch('cv2.VideoCapture')
    def test_read_no_frame(self, mock_VideoCapture):
        self.video_capture.frame = None
        self.video_capture.read()
        self.mock_cap.release.assert_called()
        mock_VideoCapture.assert_called_with("test_src")

    def tearDown(self):
        self.video_capture.stop()


if __name__ == '__main__':
    unittest.main()