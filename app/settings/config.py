import yaml
import os
from dataclasses import dataclass, field
import datetime
from app.settings import paths
from app.settings.bot import Bot, get_parse_mode
from app.settings.camera import CameraConfig, get_cameras
from app.settings.database import DB, Redis
from app.settings.terminal import Terminal, get_terminals


@dataclass
class Constants:
    photo_update_delay: int
    users_use_command_delay: int
    operator_camera_block_start_time: datetime.time
    operator_camera_block_end_time: datetime.time


def get_constants(constants_config: dict) -> Constants:
    return Constants(
        photo_update_delay=constants_config["photo_update_delay"],
        users_use_command_delay=constants_config["users_use_command_delay"],
        operator_camera_block_start_time=datetime.time.fromisoformat(
            constants_config["operator_camera_block_start_time"]
        ),
        operator_camera_block_end_time=datetime.time.fromisoformat(
            constants_config["operator_camera_block_end_time"]
        ),
    )


@dataclass
class Config:
    """Configurator"""

    constants: Constants
    bot: Bot
    db: DB
    redis: Redis
    terminals: list[Terminal] = field(default_factory=list)
    cameras: list[CameraConfig] = field(default_factory=list)


def load_config() -> Config:
    config_file_path = paths.ROOT_DIR / "config.yml"

    if not os.path.exists(config_file_path):
        raise ValueError("config.yml does't exists!")

    with open(config_file_path, "r") as file:
        config = yaml.safe_load(file)

    constants = config["constants"]
    bot = config["bot"]
    db = config["database"]
    redis = config["redis"]

    return Config(
        constants=get_constants(constants),
        bot=Bot(token=bot["token"], parse_mode=get_parse_mode(bot)),
        db=DB(
            host=db["host"], name=db["name"], user=db["user"], password=db["password"]
        ),
        redis=Redis(
            host=redis["host"],
            port=redis["port"],
            db=redis["db"],
            user=redis["user"],
            password=redis["password"],
        ),
        terminals=get_terminals(config),
        cameras=get_cameras(config),
    )
