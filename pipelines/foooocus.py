import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import requests
import json
import base64
from typing import List, Union, Generator, Iterator
from pydantic import BaseModel

def text2img(host: str, params: dict) -> dict:
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
        IMAGE_RATIO: str = "1024*1024"
        S3_BUCKET_NAME: str = "ai-cloudeka"
        S3_URL: str = "https://parahu.box.cloudeka.id"
        S3_REGION: str = "parahu"
        S3_ACCESS_KEY: str = "A8IKIIB1Z7V3L1YNXOOX"
        S3_SECRET_KEY: str = "bVrrv1QbD/1Ta98qH62KLmjy28WIa/52CXgJznnB"

    def __init__(self):
        # self.type = "manifold"
        self.name = "ImageGen"
        self.valves = self.Valves()
        self.s3_client = boto3.client(
            's3',
            region_name=self.valves.S3_REGION,
            aws_access_key_id=self.valves.S3_ACCESS_KEY,
            aws_secret_access_key=self.valves.S3_SECRET_KEY,
            endpoint_url=self.valves.S3_URL
        )

    async def on_startup(self) -> None:
        """This function is called when the server is started."""
        print(f"on_startup:{__name__}")

    async def on_shutdown(self):
        """This function is called when the server is stopped."""
        print(f"on_shutdown:{__name__}")

    async def on_valves_updated(self):
        """This function is called when the valves are updated."""
        print(f"on_valves_updated:{__name__}")

    def upload_image_to_s3(self, base64_image: str, bucket_name: str, object_name: str) -> str:
        """Upload a base64-encoded image to an S3 bucket and return a presigned URL."""
        import mimetypes
        try:
            # Ensure the base64 string is properly padded
            if "," in base64_image:
                header, encoded = base64_image.split(",", 1)

                image_data = base64.b64decode(encoded)
            else:
                # Decode the base64 image
                image_data = base64.b64decode(base64_image)

            # Upload the image to S3
            self.s3_client.put_object(Bucket=bucket_name, Key=object_name, Body=image_data, ContentType='image/png')
            # Generate a presigned URL
            url = self.s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': object_name}, ExpiresIn=3600)
            return url
        except (base64.binascii.Error, NoCredentialsError, PartialCredentialsError) as e:
            print(f"Error uploading image to S3: {e}")
            return None  # Return None in case of error

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        print(f"pipe:{__name__}")

        response = text2img(host=self.valves.HOST, params={
            "prompt": user_message,
            "performance_selection": self.valves.PERFORMANCE_SELECTION,
            "async_process": False,
            "require_base64": True,
            "aspect_ratios_selection": self.valves.IMAGE_RATIO
        })
        message = ""
        for image in response:
            if image["base64"]:
                # Upload the image to S3 and get the presigned URL
                object_name = f"images/{user_message.replace(' ', '_')}.png"
                image_url = self.upload_image_to_s3(image['base64'], self.valves.S3_BUCKET_NAME, object_name)
                if image_url:
                    message += "![image](" + image_url + ")\n"
        yield message