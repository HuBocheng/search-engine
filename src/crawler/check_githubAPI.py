from github import Github
import json


with open("data/access.txt", "r") as file:
    access_token = file.readline().strip()
g = Github(access_token)
rate_limit = g.get_rate_limit()
print(rate_limit.core)
