import json
import itertools
from github import Github

# 初始化GitHub
with open("data/access.txt", "r") as file:
    access_token = file.readline().strip()
g = Github(access_token)


def load_repos_data(files):
    """从JSON文件中加载仓库名称"""
    repos = []
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            for repo in data:
                # for repo in itertools.islice(data, 10):
                repo_info = {
                    "name": repo["name"],
                    "language": repo.get("language", None),  # 假设所有未指明的仓库为公有
                }
                repos.append(repo_info)
    return repos


def get_file_content(repo, path):
    """获取特定仓库中文件的内容"""
    try:
        file_content = repo.get_contents(path).decoded_content.decode("utf-8")
        return file_content
    except Exception as e:
        print(f"Error getting file content from {path}: {e}")
        return None


def crawl_repo(repo_name, language, result):
    """爬取单个仓库中的代码文件内容"""
    if language not in ["Python", "Java", "C", "C++"]:
        return  # 跳过非目标语言的仓库
    try:
        repo = g.get_repo(repo_name)
        contents = repo.get_contents("")

        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                if file_content.name.endswith((".c", ".cpp", ".py", ".java")):
                    file_data = get_file_content(repo, file_content.path)
                    if file_data:
                        result.append(
                            {"url": file_content.html_url, "content": file_data}
                        )
    except Exception as e:
        print(f"Error processing repo {repo_name}: {e}")


def save_files_data(data, file_number):
    """保存爬取的数据到JSON文件"""
    filename = f"codes_files{file_number}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"数据已保存到 {filename}")


# 指定JSON文件的路径
json_files = ["github_repos_with_pagerank.json"]

# 加载仓库名称
repos_data = load_repos_data(json_files)

# 爬取仓库文件
files_data = []
file_number = 1

count = 0
printNum = 1

for repo in repos_data:
    crawl_repo(repo["name"], repo["language"], files_data)

    # 每3000个文件保存一次
    if len(files_data) >= 3000:
        save_files_data(files_data, file_number)
        files_data = []  # 重置结果列表
        file_number += 1

    # 每3000个文件保存一次
    if len(files_data) >= 3000:
        save_files_data(files_data, file_number)
        files_data = []  # 重置结果列表
        file_number += 1


# 保存剩余数据
if files_data:
    save_files_data(files_data, file_number)
