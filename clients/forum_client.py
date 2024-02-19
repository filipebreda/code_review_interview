from dataclasses import dataclass

import requests
from requests.adapters import Retry, HTTPAdapter


@dataclass(frozen=True)
class Post:
    id: int
    user_id: int
    title: str
    body: str

    @classmethod
    def from_json(cls, data: dict) -> "Post":
        return cls(
            id=data["id"],
            user_id=data["userId"],
            title=data["title"],
            body=data["body"]
        )


class ForumClient:
    def __init__(self, base_url: str, retry: Retry | None = None):
        prefix = "https://"
        self.base_url = base_url if base_url.startswith(prefix) else f"{prefix}{base_url}"
        self.session = requests.Session()
        self.session.mount(
            prefix,
            HTTPAdapter(max_retries=retry or Retry(
                total=4,
                status_forcelist=[429, 500, 502, 503, 504],
            ))
        )

    def get_posts(self) -> list[Post]:
        response = self._get(f"{self.base_url}/posts")
        return [Post.from_json(post) for post in response.json()]

    def _get(self, path: str, params: dict = None) -> requests.Response:
        response = self.session.get(f"{self.base_url}/{path}", params=params)
        response.raise_for_status()
        return response
