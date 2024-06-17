from aiogram import types
import cv2
import numpy as np
import time
from io import BytesIO
from app.services.cameras.video_capture import VideoCaptureThreaded

from app.settings.camera import CameraURI
from app.settings.config import Config


class CameraStream:
    def __init__(
        self, camera_uri: CameraURI, name: str, description: str, tags: list[str]
    ) -> None:
        self.name = name
        self.description = description
        self.tags = tags
        self.camera_uri = camera_uri
        self.cam = self._activate_camera()
        self.last_photo_time = 0
        self.image = None

    def _activate_camera(self):
        cam = VideoCaptureThreaded(self.camera_uri.url)
        cam.start()
        return cam

    def get_last_frame(self) -> tuple[bool, np.ndarray | None]:
        ret, frame = self.cam.read()
        self.last_photo_time = time.time()
        return ret, frame

    def update_image(self):
        grabbed, image = self.get_last_frame()
        if grabbed:
            self.image = image


def __convert_frame_to_str_image(frame: np.ndarray) -> np.ndarray:
    ret, image = cv2.imencode(".jpg", frame)
    if not ret:
        raise Exception("Can't convert image")
    return image


def get_image(camera: CameraStream, config: Config):
    if camera.image is None or __is_need_to_update_photo(camera, config):
        camera.update_image()
    if camera.image is None:
        raise ValueError("Image from camera is None")
    image = BytesIO(__convert_frame_to_str_image(camera.image).tobytes())
    image.seek(0)
    return image.read()


def get_input_media_photo_to_send(
    camera: CameraStream, config: Config
) -> types.InputMediaPhoto:
    return types.InputMediaPhoto(
        media=types.BufferedInputFile(
            file=get_image(camera, config), filename="file.txt"
        ),
        caption=camera.description,
    )


def __is_need_to_update_photo(camera: CameraStream, config: Config) -> bool:
    LAST_TAKEN = camera.last_photo_time
    CURRENT_TIME = time.time()
    return CURRENT_TIME - LAST_TAKEN > config.constants.photo_update_delay
