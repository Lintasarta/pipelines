"""A manifold to integrate OpenAI's ImageGen models into Open-WebUI"""

from typing import List, Union, Generator, Iterator

from pydantic import BaseModel

import requests
import json

def text2img(host,params: dict) -> dict:
    """
    text to image
    """
    result = requests.post(url=f"{host}/v1/generation/text-to-image",
                           data=json.dumps(params),
                           headers={"Content-Type": "application/json"})
    return result.json()

class Pipeline:
    """OpenAI ImageGen pipeline"""

    class Valves(BaseModel):
        """Options to change from the WebUI"""

        HOST: str = "http://10.1.60.62:8888"
        # NUM_IMAGES: int = 1
        PERFORMANCE_SELECTION: str = "Quality"

    def __init__(self):
        # self.type = "manifold"
        self.name = "ImageGen"
        self.valves = self.Valves()

    async def on_startup(self) -> None:
        """This function is called when the server is started."""
        print(f"on_startup:{__name__}")

    async def on_shutdown(self):
        """This function is called when the server is stopped."""
        print(f"on_shutdown:{__name__}")

    async def on_valves_updated(self):
        """This function is called when the valves are updated."""
        print(f"on_valves_updated:{__name__}")


    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        print(f"pipe:{__name__}")

        response = text2img(host=self.valves.HOST,params={
                    "prompt": user_message,
                    "performance_selection":self.valves.PERFORMANCE_SELECTION,
                    "async_process": False})
        message = ""
        for image in response:
            if image["url"]:
                image['url'] = image['url'].replace('http://127.0.0.1:8888', self.valves.HOST)
                message += "![image](" + image["url"] + ")\n"

        yield message
