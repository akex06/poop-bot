import json
import random


class Config:
    def __init__(self) -> None:
        with open("files/config.json", encoding = "utf-8") as f:
            self.config = json.load(f)

    @property
    def poop_infos(self) -> dict:
        return self.config["poops"]

    def get_poop_info(self, poop: str) -> dict:
        return self.poop_infos.get(poop)

    @property
    def toilets(self) -> dict:
        return self.config["toilets"]

    def get_toilet(self, toilet: str) -> str:
        return self.toilets.get(toilet)

    @property
    def cooldowns(self) -> dict:
        return self.config["cooldowns"]

    def get_cooldown(self, toilet: str) -> int:
        return self.cooldowns.get(toilet)

    @property
    def winnings(self) -> dict:
        return self.config["winnings"]

    def get_winning(self, level: int) -> dict:
        return self.winnings.get(str(level))

    def generate_winnings(self, level: int):
        return {
            poop: random.randint(*_range) for poop, _range
            in self.get_winning(level).items()
        }

    @property
    def emojis(self) -> dict:
        return self.config["emojis"]

    def get_emoji(self, emoji: str) -> str:
        return self.emojis.get(emoji)

    @property
    def levelups(self) -> dict:
        return self.config["levelup"]

    def get_levelup(self, level: str) -> dict:
        return self.levelups.get(level)
