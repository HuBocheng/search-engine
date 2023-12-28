import json
import networkx as nx
from networkx.algorithms.link_analysis.hits_alg import hits
import markdown
from bs4 import BeautifulSoup

all_data = []
file_names = [
    "repository1.json",
    "repository2.json",
    "repository3.json",
    "repository4.json",
    "repository5.json",
    "repository6.json",
    "repository7.json",
]

# 载入所有JSON数据
for file_name in file_names:
    with open(file_name, "r", encoding="utf-8") as file:
        repos_data = json.load(file)
        all_data.extend(repos_data)
print("数据载入完毕")

# 创建一个有向图
G = nx.DiGraph()

# 添加节点和边
for repo in all_data:
    G.add_node(repo["url"], **repo)

    content = repo.get("readme")
    if content:
        html = markdown.markdown(content)
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.find_all("a", href=True):
            href = link.get("href")
            if href and href.startswith("http"):
                G.add_edge(repo["url"], href)
print("图创建完毕")

# 使用HITS算法计算每个节点的权威和枢纽得分
hubs, authorities = hits(G, max_iter=100, normalized=True)
print("HITS算法计算完毕")

# 将得分添加到原始数据中
for repo in all_data:
    repo["hub_score"] = hubs.get(repo["url"], 0)

# 保存到一个新的JSON文件
with open("combined_repos_with_hits.json", "w", encoding="utf-8") as file:
    json.dump(all_data, file, ensure_ascii=False, indent=4)
