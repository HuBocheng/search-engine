import time
from urllib.request import urlopen
from urllib.request import Request
import json


def get_results(search, headers, page, stars):
    url = (
        "https://api.github.com/search/repositories?q={search}%20stars:<={stars}&page={num}&per_page=100&sort=stars"
        "&order=desc".format(search=search, num=page, stars=stars)
    )
    req = Request(url, headers=headers)
    response = urlopen(req).read()
    result = json.loads(response.decode())
    return result


if __name__ == "__main__":
    search = ""
    with open("data/access.txt", "r") as file:
        access_token = file.readline().strip()
    # Modify the GitHub token value
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Authorization": access_token,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    count = 1
    stars = 421701
    for i in range(0, 15):
        print("batch: ", i)
        repos_list = []
        stars_list = []
        for page in range(1, 11):
            results = get_results(search, headers, page, stars)
            for item in results["items"]:
                repos_list.append([count, item["name"], item["html_url"]])
                stars_list.append(item["stargazers_count"])
                count += 1
            print(len(repos_list))
        stars = stars_list[-1]
        print(stars)
        with open("./top15000Repos.txt", "a", encoding="utf-8") as f:
            for i in range(len(repos_list)):
                f.write(
                    str(repos_list[i][0])
                    + ","
                    + repos_list[i][1]
                    + ","
                    + repos_list[i][2]
                    + "\n"
                )
        # For authenticated requests, 30 requests per minute
        # For unauthenticated requests, the rate limit allows you to make up to 10 requests per minute.
        # time.sleep(60)
