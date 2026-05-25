"""Publication sur X (Twitter) via tweepy."""
import os
import tweepy


def _client() -> tweepy.Client:
    return tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )


def publish_to_x(text: str) -> str:
    """Publie un tweet et retourne son ID."""
    client = _client()
    response = client.create_tweet(text=text)
    return str(response.data["id"])
