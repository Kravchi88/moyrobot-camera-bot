import unittest
from unittest.mock import patch, MagicMock
from app.services.cameras.camera_stream import CameraStream, get_image, get_input_media_photo_to_send
from app.settings.camera import CameraURI
from app.settings.config import Config
import numpy as np


class TestCameraStream(unittest.TestCase):
    def setUp(self):
        self.camera_uri = CameraURI(url="test_url")
        self.config = Config()
        self.config.constants = MagicMock()
        self.config.constants.photo_update_delay = 10
        self.camera_stream = CameraStream(
            camera_uri=self.camera_uri,
            name="Test Camera",
            description="Test Description",
            tags=["test"]
        )

    @patch('app.services.cameras.camera_stream.VideoCaptureThreaded')
    def test_activate_camera(self, mock_VideoCaptureThreaded):
        self.camera_stream._activate_camera()
        mock_VideoCaptureThreaded.assert_called_with("test_url")

    @patch('app.services.cameras.camera_stream.CameraStream.get_last_frame')
    def test_update_image(self, mock_get_last_frame):
        mock_get_last_frame.return_value = (True, np.array([1, 2, 3]))
        self.camera_stream.update_image()
        self.assertTrue((self.camera_stream.image == np.array([1, 2, 3])).all())

    @patch('app.services.cameras.camera_stream.CameraStream.update_image')
    def test_get_image(self, mock_update_image):
        self.camera_stream.image = np.array([1, 2, 3])
        img = get_image(self.camera_stream, self.config)
        self.assertIsNotNone(img)

    @patch('app.services.cameras.camera_stream.get_image')
    def test_get_input_media_photo_to_send(self, mock_get_image):
        mock_get_image.return_value = b"image_data"
        media_photo = get_input_media_photo_to_send(self.camera_stream, self.config)
        self.assertEqual(media_photo.media.filename, "file.txt")
        self.assertEqual(media_photo.media.file.read(), b"image_data")

    def tearDown(self):
        self.camera_stream.cam.stop()


if __name__ == '__main__':
    unittest.main()