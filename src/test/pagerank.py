# 1000个仓库离线计算PageRank
import requests
from github import Github
import markdown
from bs4 import BeautifulSoup
import networkx as nx
import json
import time
import itertools

with open("github_repos2.json", "r", encoding="utf-8") as file:
    repos_data = json.load(file)

G = nx.DiGraph()
inner_pagerank_scores = []  # 用于存储内部节点的PageRank分数

start = time.time()
countResolve = 0
show_prompt_count = 100

# 遍历搜索结果
for repo in repos_data:
    # 获取README文件
    content = repo.get("readme")
    if content is None:
        continue
    html = markdown.markdown(content)
    soup = BeautifulSoup(html, "html.parser")

    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.startswith("http"):
            # 在图中添加一条边
            G.add_edge(repo["url"], href)

    countResolve += 1
    if countResolve % show_prompt_count == 0:
        print("已处理", countResolve, "个仓库")


end_crawl = time.time()
print("数据爬取完毕，用时：", end_crawl - start, "秒")

# 应用PageRank算法
pagerank_scores = nx.pagerank(G)

for repo_data in repos_data:
    url = repo_data["url"]
    temp = {"url": url, "pagerank_score": pagerank_scores.get(url, 0)}
    inner_pagerank_scores.append(temp)

pass
