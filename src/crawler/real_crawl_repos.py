import requests
from github import Github
import markdown
from bs4 import BeautifulSoup
import networkx as nx
import json
import time
import itertools

# GitHub访问令牌
with open("data/access.txt", "r") as file:
    access_token = file.readline().strip()

# 初始化GitHub
g = Github(access_token, per_page=100)

# 创建一个有向图
G = nx.DiGraph()

# 初始化一个列表来存储仓库数据
repos_data = []


def extract_url_from_line(line):
    """从每行文本中提取仓库的 URL"""
    owner_repo = line.split("github.com/")[1]
    return owner_repo.strip()


def save_data(repos_data, file_number):
    """将爬取的数据保存到文件"""
    filename = f"repository{file_number}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(repos_data, f, ensure_ascii=False, indent=4)
    print(f"数据已保存到 {filename}")


def get_repo_data_from_file(file_path):
    """从文件中读取仓库 URL 并获取仓库数据"""
    repos_data = []
    num = 0
    with open(file_path, "r", encoding="utf-8") as file:
        urls = [extract_url_from_line(line) for line in file]

    for url in urls[10000:15000]:
        if not url:
            continue

        try:
            repo = g.get_repo(url)
            # 提取每个仓库的相关信息
            repo_info = {
                "name": repo.full_name,
                "url": repo.html_url,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,  # 添加仓库的fork数目
                "language": repo.language,  # 添加仓库的主要语言
                "created_at": repo.created_at.isoformat(),  # 添加创建时间
                "last_updated": repo.updated_at.isoformat(),  # 添加仓库的最后更新时间
                "owner": repo.owner.login,  # 添加作者信息
                "description": repo.description,  # 添加仓库的描述信息
            }
            # 获取README文件
            readme = repo.get_readme()
            content = readme.decoded_content.decode("utf-8")

            # 将Markdown内容转换为HTML
            html = markdown.markdown(content)
            soup = BeautifulSoup(html, "html.parser")

            # 提取所有的链接
            external_links_count = 0
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if href.startswith("http"):
                    # 在图中添加一条边
                    G.add_edge(repo.full_name, href)
                    external_links_count += 1

            # 添加外部链接数目
            repo_info["external_links_count"] = external_links_count

            # 获取README内容和话题标签
            repo_info["readme"] = content
            repo_info["topics"] = repo.get_topics()

            # 添加到列表
            repos_data.append(repo_info)

            num += 1
            if num == 500:
                save_data(repos_data, 999)
                repos_data = []
                time.sleep(900)
            if num % 100 == 0:
                print("已处理", num, "个仓库")
            if num % 1500 == 0:
                save_data(repos_data, (num // 1500) + 7)
                repos_data = []
                time.sleep(900)

        except Exception as e:
            print(f"Error processing {url}: {e}")

    pagerank_scores = nx.pagerank(G)
    for repo_data in repos_data:
        repo_data["pagerank_score"] = pagerank_scores.get(repo_data["name"], 0)

    return repos_data


# 调用函数获取数据
file_path = "top15000Repos.txt"  # 替换为您的文件路径
repos_data = get_repo_data_from_file(file_path)

# 保存数据
# save_data(repos_data, 99)
