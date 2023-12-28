from elasticsearch import Elasticsearch
import json

# 连接到Elasticsearch
es = Elasticsearch("http://localhost:9200/")  # 默认端口是9200

# 确保Elasticsearch已启动并可连接
if not es.ping():
    raise ValueError("连接Elasticsearch失败")

# 读取JSON文件
with open("data/users1.json", "r", encoding="utf-8") as file:
    repos_data = json.load(file)
with open("data/users2.json", "r", encoding="utf-8") as file:
    repos_data.extend(json.load(file))
with open("data/users3.json", "r", encoding="utf-8") as file:
    repos_data.extend(json.load(file))

# 构建Elasticsearch索引
index_name = "users"

# 确保索引不存在
if not es.indices.exists(index=index_name):
    # 创建索引
    es.indices.create(index=index_name)

# 向Elasticsearch中添加数据
for i, repo in enumerate(repos_data):
    loginName = repo.get("login")
    es.index(index=index_name, id=loginName, body=repo, doc_type="doc")
    if (i + 1) % 1000 == 0:
        print("已上传" + str(i + 1) + "个用户数据")

print("数据上传完成")
