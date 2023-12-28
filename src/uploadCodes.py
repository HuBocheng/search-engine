from elasticsearch import Elasticsearch
import json

# 连接到Elasticsearch
es = Elasticsearch("http://localhost:9200/")  # 默认端口是9200

# 确保Elasticsearch已启动并可连接
if not es.ping():
    raise ValueError("连接Elasticsearch失败")

repos_data = []
# 读取JSON文件
# with open("data/codes_files1.json", "r", encoding="utf-8") as file:
#     repos_data = json.load(file)
# with open("data/codes_files2.json", "r", encoding="utf-8") as file:
#     repos_data.extend(json.load(file))
# with open("data/codes_files3.json", "r", encoding="utf-8") as file:
#     repos_data.extend(json.load(file))
# with open("data/codes_files4.json", "r", encoding="utf-8") as file:
#     repos_data.extend(json.load(file))
# with open("data/codes_files5.json", "r", encoding="utf-8") as file:
#     repos_data.extend(json.load(file))
# with open("data/codes_files6.json", "r", encoding="utf-8") as file:
#     repos_data.extend(json.load(file))

for i in range(1, 13):
    with open("data/codes_files" + str(i) + ".json", "r", encoding="utf-8") as file:
        repos_data.extend(json.load(file))

# 构建Elasticsearch索引
index_name = "codes"

# 确保索引不存在
if not es.indices.exists(index=index_name):
    # 创建索引
    es.indices.create(index=index_name)

# 向Elasticsearch中添加数据
# for repo in repos_data:
#     es.index(index=index_name, body=repo, doc_type="doc")

for i, repo in enumerate(repos_data):
    es.index(index=index_name, body=repo, doc_type="doc")
    if (i + 1) % 2000 == 0:
        print("已上传" + str(i + 1) + "条代码数据")

print("数据上传完成")
