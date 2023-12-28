from elasticsearch import Elasticsearch
import json

# 连接到Elasticsearch
es = Elasticsearch("http://localhost:9200/")  # 默认端口是9200

# 确保Elasticsearch已启动并可连接
if not es.ping():
    raise ValueError("连接Elasticsearch失败")

# 读取JSON文件
with open("data/allRepositories.json", "r", encoding="utf-8") as file:
    repos_data = json.load(file)
print("读取数据完成，共" + str(len(repos_data)) + "个仓库")

# 构建Elasticsearch索引
index_name = "repositories"

# 确保索引不存在
if not es.indices.exists(index=index_name):
    # 定义索引的mappings设置，使用ik分词器
    settings = {
        "mappings": {
            "properties": {
                "readme": {  # 假设你要分词的字段名为content
                    "type": "text",
                    "analyzer": "ik_max_word",  # 使用ik_max_word分词器
                    "search_analyzer": "ik_smart",  # 搜索时使用ik_smart分词器
                }
            }
        }
    }
    # 创建索引
    es.indices.create(index=index_name, body=settings)

# 向Elasticsearch中添加数据
for i, repo in enumerate(repos_data):
    es.index(index=index_name, body=repo, doc_type="doc")
    if (i + 1) % 2000 == 0:
        print("已上传" + str(i + 1) + "个仓库数据")

print("数据上传完成")
