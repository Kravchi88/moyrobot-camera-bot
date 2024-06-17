from dataclasses import dataclass


@dataclass
class Terminal:
    id: int
    url: str
    login: str
    password: str


def get_terminals(config: dict) -> list[Terminal]:
    terminals = []
    terminals_dict = config.get("terminals")
    if terminals_dict is None:
        return terminals

    for el in terminals_dict:
        terminal = el["terminal"]
        terminals.append(
            Terminal(
                id=terminal["id"],
                url=terminal["url"],
                login=terminal["login"],
                password=terminal["password"],
            )
        )
    return terminals
