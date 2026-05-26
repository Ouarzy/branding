"""Publication sur BlueSky via atproto."""
import os
from atproto import Client

BLUESKY_LIMIT = 300


def _client() -> Client:
    client = Client()
    client.login(
        os.environ["BLUESKY_HANDLE"],
        os.environ["BLUESKY_APP_PASSWORD"],
    )
    return client


def split_into_parts(text: str) -> list[str]:
    """Découpe le texte en parties par paragraphe, ≤ BLUESKY_LIMIT chars chacune."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    parts: list[str] = []
    current = ""

    for para in paragraphs:
        if len(para) > BLUESKY_LIMIT:
            if current:
                parts.append(current)
                current = ""
            parts.append(para[:BLUESKY_LIMIT])
        elif current and len(current) + 2 + len(para) <= BLUESKY_LIMIT:
            current = current + "\n\n" + para
        else:
            if current:
                parts.append(current)
            current = para

    if current:
        parts.append(current)

    return parts


def publish_to_bluesky(text: str) -> str:
    """Publie un post BlueSky (ou un thread si > 300 chars) et retourne l'URI du premier post."""
    client = _client()
    parts = split_into_parts(text)

    if len(parts) == 1:
        response = client.send_post(text=parts[0])
        return response.uri

    # Thread : chaque partie est une réponse à la précédente
    from atproto import models

    first = client.send_post(text=parts[0])
    root_ref = models.ComAtprotoRepoStrongRef.Main(cid=first.cid, uri=first.uri)
    parent_ref = root_ref

    for part in parts[1:]:
        reply_to = models.AppBskyFeedPost.ReplyRef(root=root_ref, parent=parent_ref)
        response = client.send_post(text=part, reply_to=reply_to)
        parent_ref = models.ComAtprotoRepoStrongRef.Main(cid=response.cid, uri=response.uri)

    return first.uri
