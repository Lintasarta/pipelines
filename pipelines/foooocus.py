import requests
import json
from typing import List, Union, Generator, Iterator
from pydantic import BaseModel

from utils.pipelines.decorator import log_time
from utils.fooocus.utils import PromptExtractor, prompt_cleaner

@log_time
def text2img(host: str, params: dict) -> dict:
    """
    text to image
    """
    result = requests.post(
        url=f"{host}/v1/generation/text-to-image",
        data=json.dumps(params),
        headers={"Content-Type": "application/json"}
    )
    return result.json()

class Pipeline:
    """OpenAI ImageGen pipeline"""

    class Valves(BaseModel):
        """Options to change from the WebUI"""
        HOST: str = "http://10.250.150.187:8888"
        PERFORMANCE_SELECTION: str = "Quality"
        IMAGE_RATIO: str = "1024*1024"

    def __init__(self):
        self.name = "Enhanced Stable Diffusion"
        self.valves = self.Valves()
        self.prompt_extractor = PromptExtractor()

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

        # Extract style from user_message
        styles = self.prompt_extractor.style_extractor(user_message)

        # Clean user_message
        user_message = prompt_cleaner(user_message)
        print(f"user message: {user_message}")

        # Call the text-to-image API
        response = text2img(
            host=self.valves.HOST,
            params={
                "prompt": user_message,
                "performance_selection": self.valves.PERFORMANCE_SELECTION,
                "style_selections": styles,
                "async_process": False,
                "require_base64": False,
                "aspect_ratios_selection": self.valves.IMAGE_RATIO
            }
        )

        # Build a markdown response using the URL from the response
        message = ""
        for image in response:
            if image.get("url"):
                message += f"![image]({image['url']})\n"

        # Yield the result
        yield message
