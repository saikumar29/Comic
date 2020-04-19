import os
from google.cloud import vision

class api_call():

    def __init__(self,image_bytearray):
        credential_path = r"D:\Final DMDD Project\My First Project.json"
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
        self.image_bytes=bytes(image_bytearray)

    def detect_text(self):
        """Detects text in the file."""
        client = vision.ImageAnnotatorClient()
        content=self.image_bytes
        image = vision.types.Image(content=content)
        response = client.text_detection(image=image)
        texts = response.text_annotations
        bubble_text= texts[0].description
        bubble_text=str(bubble_text).strip()
        if len(bubble_text)<5:
            bubble_text=None

        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))
        return bubble_text


