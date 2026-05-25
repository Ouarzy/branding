"""Parse AsciiDoc post files and extract metadata + content."""
import re
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime


@dataclass
class Post:
    path: Path
    title: str
    date: datetime | None
    networks: list[str]
    status: str
    tags: list[str]
    body: str

    @property
    def is_ready(self) -> bool:
        return self.status == "ready"

    @property
    def is_due(self) -> bool:
        if self.date is None:
            return self.is_ready
        return self.is_ready and self.date <= datetime.now()


def parse_post(path: Path) -> Post:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    title = ""
    attrs: dict[str, str] = {}
    body_lines: list[str] = []
    in_body = False

    for line in lines:
        if not title and line.startswith("= "):
            title = line[2:].strip()
            continue
        if not in_body and line.startswith(":") and ":" in line[1:]:
            key, _, val = line[1:].partition(":")
            attrs[key.strip()] = val.strip()
            continue
        if not line.strip() and not in_body:
            in_body = True
            continue
        if in_body and not line.startswith("//"):
            body_lines.append(line)

    date = None
    if "date" in attrs:
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                date = datetime.strptime(attrs["date"], fmt)
                break
            except ValueError:
                continue

    networks = [n.strip() for n in attrs.get("networks", "x,bluesky").split(",")]
    tags = [t.strip() for t in attrs.get("tags", "").split(",") if t.strip()]

    return Post(
        path=path,
        title=title,
        date=date,
        networks=networks,
        status=attrs.get("status", "draft"),
        tags=tags,
        body="\n".join(body_lines).strip(),
    )


def load_posts(content_dir: Path, status: str | None = None) -> list[Post]:
    posts = []
    for adoc in sorted(content_dir.rglob("*.adoc")):
        if adoc.name.startswith("_"):
            continue
        post = parse_post(adoc)
        if status is None or post.status == status:
            posts.append(post)
    return posts


def mark_published(post: Post) -> None:
    text = post.path.read_text(encoding="utf-8")
    text = re.sub(r":status: \w+", ":status: published", text)
    post.path.write_text(text, encoding="utf-8")
