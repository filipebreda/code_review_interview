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


@dataclass(frozen=True)
class User:
    id: int
    name: str
    email: str
    phone: str
    posts: list[Post]

    @classmethod
    def from_json(cls, data: dict) -> "User":
        return cls(
            id=data["id"],
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            posts=[]
        )


class ForumClient:
    def __init__(self, base_url: str, retry: Retry | None = None):
        prefix = "https://"
        self.base_url = (base_url if base_url.startswith(prefix) else f"{prefix}{base_url}").rstrip("/")
        self.session = requests.Session()
        self.session.mount(
            prefix,
            HTTPAdapter(max_retries=retry or Retry(
                total=4,
                status_forcelist=[429, 500, 502, 503, 504],
            ))
        )

    def get_user(self, user_id: int) -> User:
        response = self._get(f"/users/{user_id}")
        return User.from_json(response.json())

    def get_posts(self, user_id: int | None = None) -> list[Post]:
        response = self._get(f"{self.base_url}/posts", params={"userId": user_id})
        return [Post.from_json(post) for post in response.json()]

    def get_user_posts(self, user_id: int) -> User:
        user = self.get_user(user_id)
        posts = self.get_posts()
        user.posts.extend(posts)
        return user

    def _get(self, path: str, params: dict = None) -> requests.Response:
        response = self.session.get(f"{self.base_url}/{path}", params=params)
        response.raise_for_status()
        return response
