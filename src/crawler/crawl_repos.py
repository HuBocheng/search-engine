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


def save_data(repos_data, file_number):
    """将爬取的数据保存到文件"""
    filename = f"github_repos{file_number}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(repos_data, f, ensure_ascii=False, indent=4)
    print(f"数据已保存到 {filename}")


def get_repo_data(start_index, end_index, query="stars:>1000"):
    """获取仓库的数据"""
    repos_data = []
    repositories = g.search_repositories(query=query)
    num = 0

    for repo in repositories:
        try:
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
            if num % 200 == 0:
                print("已处理", num, "个仓库")
            if num == end_index:
                break
        except Exception as e:
            print(f"Error processing {repo.full_name}: {e}")
    pagerank_scores = nx.pagerank(G)
    for repo_data in repos_data:
        repo_data["pagerank_score"] = pagerank_scores.get(repo_data["name"], 0)
    return repos_data


def main():
    # # 每批处理5000个仓库
    # repos_per_batch = 5000
    # total_repos = 30000
    # batches = total_repos // repos_per_batch

    # for i in range(batches):
    #     print(f"正在处理第{i+1}批仓库...")
    #     start_index = i * repos_per_batch
    #     end_index = start_index + repos_per_batch
    #     repos_data = get_repo_data(start_index, end_index)
    #     save_data(repos_data, i + 1)
    #     # time.sleep(600)
    start_index = 0
    end_index = 1000

    # repos_data = get_repo_data(start_index, end_index, query=f"stars:<10000")
    # repos_data = get_repo_data(start_index, end_index, query=f"stars:<{maxStart}")
    # repos_data = get_repo_data(start_index, end_index, query="stars:>1000 stars:<21795")

    # repos_data = get_repo_data(
    #     start_index, end_index, query="stars:<21795 stars:>20000"
    # )
    # save_data(repos_data, 20000)
    # print("在20000-21795之间的仓库有", len(repos_data), "个")

    repos_data = get_repo_data(
        start_index, end_index, query="stars:<10000 starts:>5000"
    )
    save_data(repos_data, 10000)
    print("在5000-10000之间的仓库有", len(repos_data), "个")

    time.sleep(1200)

    repos_data = get_repo_data(
        start_index, end_index, query="stars:<19000 starts:>18000"
    )
    save_data(repos_data, 18000)
    print("在18000-19000之间的仓库有", len(repos_data), "个")

    repos_data = get_repo_data(
        start_index, end_index, query="stars:<18000 starts:>17000"
    )
    save_data(repos_data, 17000)
    print("在17000-18000之间的仓库有", len(repos_data), "个")

    time.sleep(1200)

    repos_data = get_repo_data(
        start_index, end_index, query="stars:<17000 starts:>16000"
    )
    save_data(repos_data, 16000)
    print("在16000-17000之间的仓库有", len(repos_data), "个")

    repos_data = get_repo_data(
        start_index, end_index, query="stars:<16000 starts:>15000"
    )
    save_data(repos_data, 15000)
    print("在15000-16000之间的仓库有", len(repos_data), "个")

    time.sleep(1200)

    repos_data = get_repo_data(
        start_index, end_index, query="stars:<15000 starts:>14000"
    )
    save_data(repos_data, 14000)
    print("在14000-15000之间的仓库有", len(repos_data), "个")

    repos_data = get_repo_data(
        start_index, end_index, query="stars:<14000 starts:>13000"
    )
    save_data(repos_data, 13000)
    print("在13000-14000之间的仓库有", len(repos_data), "个")

    time.sleep(1200)

    repos_data = get_repo_data(
        start_index, end_index, query="stars:<13000 starts:>12000"
    )
    save_data(repos_data, 12000)
    print("在12000-13000之间的仓库有", len(repos_data), "个")

    repos_data = get_repo_data(
        start_index, end_index, query="stars:<12000 starts:>11000"
    )
    save_data(repos_data, 11000)
    print("在11000-12000之间的仓库有", len(repos_data), "个")

    time.sleep(1200)

    repos_data = get_repo_data(
        start_index, end_index, query="stars:<11000 starts:>10000"
    )
    save_data(repos_data, 10000)
    print("在10000-11000之间的仓库有", len(repos_data), "个")


if __name__ == "__main__":
    main()
