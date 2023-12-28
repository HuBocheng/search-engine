from github import Github
import json
import os

# 初始化Github实例
with open("data/access.txt", "r") as file:
    access_token = file.readline().strip()
g = Github(access_token)


# 函数：从文件中读取仓库数据
def read_repo_data(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


# 函数：获取用户信息
def get_user_info(username):
    user = g.get_user(username)
    user_info = {
        "login": user.login,
        "name": user.name,
        "location": user.location,
        "email": user.email,
        "company": user.company,
        "created_at": user.created_at,
        "followers_count": user.followers,
        "following_count": user.following,
        "public_repos_count": user.public_repos,
        "public_gists_count": user.public_gists,
        "starred_repos_count": user.get_starred().totalCount,
        "url": f"https://github.com/{user.login}",
    }
    return user_info


# 主程序
def main():
    all_users_info = []

    # 假设有10个文件
    for i in range(1, 11):
        filename = f"github_repos{i}.json"
        if os.path.exists(filename):
            repos = read_repo_data(filename)
            for repo in repos:
                owner = repo.get("owner", None)
                if owner:
                    user_info = get_user_info(owner)
                    all_users_info.append(user_info)

    # 保存所有用户信息到一个新文件
    with open("all_users_info.json", "w", encoding="utf-8") as f:
        json.dump(all_users_info, f, ensure_ascii=False, indent=4)

    print("所有用户信息已保存到 all_users_info.json")


if __name__ == "__main__":
    main()
