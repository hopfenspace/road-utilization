import json
import logging
import os

logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        self.ttn_app_id = ""
        self.ttn_access_key = ""
        self.ttn_mqtt_address = ""

    @classmethod
    def from_json(cls) -> dict:
        if not os.path.exists("config.json"):
            with open("config.json", "w") as fh:
                config = cls()
                json.dump(config.__dict__, fh, indent=2)
                logger.info("No config found, generating new one")
        return json.loads(open("config.json").read())