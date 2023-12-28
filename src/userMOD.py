import hashlib
from typing import List, Dict, Optional


class User:
    def __init__(
        self,
        username: str,
        password: str,
        age: int,
        gender: str,
        tech_stack: Optional[List[str]] = None,
        interests: Optional[List[str]] = None,
        starred_repos: Optional[List[str]] = None,
        forked_repos: Optional[List[str]] = None,
    ):
        self.username = username
        self.password_hash = self._hash_password(password)
        self.age = age
        self.gender = gender
        self.tech_stack = tech_stack if tech_stack is not None else []
        self.interests = interests if interests is not None else []
        self.starred_repos = starred_repos if starred_repos is not None else []
        self.forked_repos = forked_repos if forked_repos is not None else []
        self.search_history = []
        self.web_visit_history = {}

    def _hash_password(self, password: str) -> str:
        """Return the hashed version of the password."""
        return hashlib.sha256(password.encode()).hexdigest()

    def add_search_history(self, search: str):
        """Add a search to the user's search history."""
        self.search_history.append(search)

    def add_web_visit(self, url: str, duration: int):
        """Add a web visit to the user's web visit history."""
        self.web_visit_history[url] = self.web_visit_history.get(url, 0) + duration

    def add_interest(self, interest: str):
        """Add an interest to the user's interests."""
        self.interests.append(interest)

    def add_tech_stack(self, tech: str):
        """Add a tech to the user's tech stack."""
        self.tech_stack.append(tech)

    def add_starred_repo(self, repo: str):
        """Add a repo to the user's starred repos."""
        self.starred_repos.append(repo)

    def add_forked_repo(self, repo: str):
        """Add a repo to the user's forked repos."""
        self.forked_repos.append(repo)


# Example of using the User class
user = User(
    username="sampleUser",
    password="password123",
    age=30,
    gender="Male",
    tech_stack=["Python", "Django"],
    interests=["Web Development"],
    starred_repos=["repo1", "repo2"],
    forked_repos=["repo3"],
)

# Adding a search history and web visit
user.add_search_history("Python tutorials")
user.add_web_visit("https://github.com/repo1", 120)
