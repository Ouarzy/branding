"""Publication sur BlueSky via atproto."""
import os
from atproto import Client


def _client() -> Client:
    client = Client()
    client.login(
        os.environ["BLUESKY_HANDLE"],
        os.environ["BLUESKY_APP_PASSWORD"],
    )
    return client


def publish_to_bluesky(text: str) -> str:
    """Publie un post BlueSky et retourne son URI."""
    client = _client()
    response = client.send_post(text=text)
    return response.uri
