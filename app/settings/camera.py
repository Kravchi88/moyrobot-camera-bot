from dataclasses import dataclass


@dataclass
class CameraURI:
    """Dataclass for configuration URI"""

    login: str
    password: str
    host: str
    port: str
    protocol: str
    path: str

    @property
    def url(self) -> str:
        address = ""
        address += self.protocol + "://"
        if self.login != "" and self.password != "":
            address += f"{self.login}:{self.password}@"

        address += f"{self.host}"
        if self.port != "":
            address += f":{self.port}"

        address += "/"
        address += self.path
        return address + "?tcp"


@dataclass
class CameraConfig:
    """Dataclass for camera configuration"""

    camera_uri: CameraURI
    name: str
    description: str
    tags: list[str]


def get_cameras(config: dict) -> list[CameraConfig]:
    cameras: list[CameraConfig] = []
    cameras_dict = config.get("cameras")
    if cameras_dict is None:
        return cameras

    for camera_dict in cameras_dict:
        camera = camera_dict["camera"]
        cameras.append(
            CameraConfig(
                camera_uri=CameraURI(
                    login=camera["login"],
                    password=camera["password"],
                    host=camera["host"],
                    port=camera["port"],
                    protocol=camera["protocol"],
                    path=camera["path"],
                ),
                name=camera["name"],
                description=camera["description"],
                tags=camera["tags"],
            )
        )

    return cameras
