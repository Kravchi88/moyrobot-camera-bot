from dataclasses import dataclass


@dataclass
class DB:
    """Database config"""

    host: str
    name: str
    user: str
    password: str

    @property
    def uri(self) -> str:
        """Returns uri of postgres database."""
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}/{self.name}"
        )


@dataclass
class Redis:
    """RedisStorage config"""

    host: str
    port: str
    db: str
    user: str
    password: str

    @property
    def url(self) -> str:
        if self.user == "":
            return f"redis://{self.host}:{self.port}/{self.db}"

        if self.password == "":
            return f"redis://{self.user}@{self.host}:{self.port}/{self.db}"

        return f"redis://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"
