from elasticsearch5 import Elasticsearch
import random
import numpy as np
from elasticsearch.exceptions import TransportError
import os
from typing import List, Optional, Dict


class Searcher:
    def __init__(self, host="http://localhost:9200"):
        self.es = Elasticsearch([host])
        self.username = ""

    def set_username(self, username):
        self.username = username

    def search_repositories_P(
        self, search_term, include_readme, sort_order, user_interests, user_clicks
    ):
        fields = ["name", "description"]
        if include_readme == "yes":
            fields.append("readme")

        sort_logic = {}

        if sort_order == "pagerank":
            sort_logic = {"pagerank_score": "desc"}
        elif sort_order == "hits":
            sort_logic = {"hub_score": "desc"}
        elif sort_order == "hot":
            sort_logic = {"total_clicks": "desc"}
        elif sort_order == "latest":
            sort_logic = {"last_updated": "desc"}
        elif sort_order == "best_match":
            # 当sort_order为best_match时，使用自定义评分机制
            query = {
                "query": {
                    "function_score": {
                        "query": {
                            # 用match_phrase替换query_string进行短语搜索
                            "bool": {
                                "should": [
                                    {"match_phrase": {"name": search_term}},
                                    {"match_phrase": {"description": search_term}},
                                ]
                            }
                        },
                        "score_mode": "sum",
                        "boost_mode": "multiply",
                    }
                },
                "sort": {"_score": {"order": "desc"}},
                "size": 1000,
            }
            # 如果包括readme进行短语搜索，则添加相应语句
            if include_readme == "yes":
                query["query"]["function_score"]["query"]["bool"]["should"].append(
                    {"match_phrase": {"readme": search_term}}
                )

            try:
                # Elasticsearch搜索调用
                response = self.es.search(index="repositories", body=query)
                return response
            except TransportError as e:
                # 打印异常的错误信息
                print(f"Error: {e}")

        # 非best_match情况下的搜索
        query = {
            "query": {
                "function_score": {
                    "query": {
                        # 用match_phrase替换query_string进行短语搜索
                        "bool": {
                            "should": [
                                {"match_phrase": {"name": search_term}},
                                {"match_phrase": {"description": search_term}},
                            ]
                        }
                    },
                }
            },
            "sort": sort_logic,
            "size": 1000,
        }
        # 如果包括readme进行短语搜索，则添加相应语句
        if include_readme == "yes":
            query["query"]["function_score"]["query"]["bool"]["should"].append(
                {"match_phrase": {"readme": search_term}}
            )

        try:
            # Elasticsearch搜索调用
            response = self.es.search(index="repositories", body=query)
            return response
        except TransportError as e:
            # 打印异常的错误信息
            print(f"Error: {e}")

    def search_repositories(
        self, search_term, include_readme, sort_order, user_interests, user_clicks
    ):
        fields = ["name", "description"]
        if include_readme == "yes":
            fields.append("readme")

        sort_logic = {}

        if sort_order == "pagerank":
            sort_logic = {"pagerank_score": "desc"}
        elif sort_order == "hits":
            sort_logic = {"hub_score": "desc"}
        elif sort_order == "hot":
            sort_logic = {"total_clicks": "desc"}
        elif sort_order == "latest":
            sort_logic = {"last_updated": "desc"}
        elif sort_order == "best_match":
            # 当sort_order为best_match时，使用自定义评分机制
            query = {
                "query": {
                    "function_score": {
                        "query": {
                            "query_string": {
                                "fields": fields,
                                "query": f"{search_term}",
                                # "query": "/" + search_term + "/",
                                "analyze_wildcard": True,
                            }
                        },
                        "functions": [
                            {
                                # 评分函数 1：兴趣点匹配
                                "filter": {"terms": {"topics": user_interests}},
                                "weight": 2,  # 增加权重
                            },
                            {
                                # 评分函数 2：用户点击次数
                                "script_score": {
                                    "script": {
                                        "source": """
    int score = 0; // 初始化得分为 0
    for (String topic : doc['topics.keyword']) { // 迭代 topics 数组中的每个元素
        if (params.user_clicks.containsKey(topic)) { // 检查 user_clicks 是否包含该主题
            score += params.user_clicks[topic]; // 累加该主题对应的点击次数到得分
        }
    }
    return score > 0 ? score : 1; // 如果得分大于 0 则返回得分，否则返回 1
""",
                                        "params": {"user_clicks": user_clicks},
                                    }
                                }
                            },
                            {
                                # 评分函数 3：总点击次数
                                "field_value_factor": {
                                    "field": "total_clicks",
                                    "factor": 1.2,
                                    "modifier": "log1p",
                                }
                            },
                        ],
                        "score_mode": "sum",  # 根据需求选择适合的score_mode
                        "boost_mode": "multiply",
                    }
                },
                "sort": {"_score": {"order": "desc"}},  # 根据评分倒序排序
                "size": 1000,
            }
            try:
                # 假设这是触发异常的Elasticsearch搜索调用
                response = self.es.search(index="repositories", body=query)
            except TransportError as e:
                # 打印异常的错误信息
                print(f"Error: {e}")

                # 如果有额外的错误信息可用，将其打印出来
                if hasattr(e, "info"):
                    print("Additional info:", e.info)

                # 如果异常包含具体的HTTP状态码，也可以打印出来
                if hasattr(e, "status_code"):
                    print("HTTP status code:", e.status_code)
            # 文档的搜索结果写入总日志
            self.log_results(response, search_term)
            return response

        query = {
            "query": {
                "query_string": {
                    "fields": fields,
                    "query": "/" + search_term + "/",
                    # "query": search_term,
                    "analyze_wildcard": True,  # 允许分析通配符
                }
            },
            "sort": sort_logic,
            "size": 1000,
        }
        response = self.es.search(index="repositories", body=query)
        self.log_results(response, search_term)
        return self.es.search(index="repositories", body=query)

    def search_users(self, search_term):
        query = {
            "query": {
                "query_string": {
                    "fields": ["login", "name"],
                    "query": "/" + search_term + "/",
                    "analyze_wildcard": True,
                }
            },
            "sort": {"followers_count": "desc"},
            "size": 1000,
        }
        return self.es.search(index="users", body=query)

    def search_codes(self, search_term):
        query = {
            "query": {
                "query_string": {
                    "fields": ["content"],
                    "query": "/" + search_term + "/",
                    "analyze_wildcard": True,
                }
            },
            "highlight": {
                "fields": {
                    "content": {
                        "fragment_size": 300,  # 设置片段大小，根据需要调整
                        "number_of_fragments": 5,  # 设置返回片段的数量
                        "pre_tags": ["<mark>"],  # 设置高亮标签的开始标记
                        "post_tags": ["</mark>"],  # 设置高亮标签的结束标记
                    }
                }
            },
            "sort": {"starts": "desc"},
            "size": 1000,
        }
        return self.es.search(index="codes", body=query)

    def get_unique_field_values(self, index, field, size=10000):
        """
        Retrieve unique values of a specified field in an Elasticsearch index.

        :param index: The name of the index
        :param field: The field for which to retrieve unique values
        :param size: The number of unique values to retrieve (default is 10,000)
        :return: A list of unique values
        """
        keyword_field = f"{field}.keyword"
        # Build the aggregation query
        if field == "topics":
            query = {
                "size": 0,
                "aggs": {
                    "distinct_values": {
                        "terms": {"field": keyword_field, "size": size}  # 'size' 根据需要调整
                    }
                },
            }
        else:
            query = {
                "size": 0,
                "aggs": {
                    "distinct_values": {
                        "terms": {"field": field, "size": size}  # 'size' 根据需要调整
                    }
                },
            }

        # Execute the query
        response = self.es.search(index=index, body=query)

        # Extract the unique values
        unique_values = [
            bucket["key"]
            for bucket in response["aggregations"]["distinct_values"]["buckets"]
        ]

        return unique_values

    def generate_data(self, target, n):
        if target == "totalClicks":
            # 得到所有仓库id
            index = "repositories"

            # 执行搜索查询
            response = searcher.es.search(
                index=index,
                body={"query": {"match_all": {}}, "_source": False},  # 不返回_source字段
                size=10000,  # 设置合适的size值
            )

            # 提取所有文档的ID
            doc_ids = [doc["_id"] for doc in response["hits"]["hits"]]
            mu = 5000.5
            sigma = 2000
            data = np.random.normal(mu, sigma, len(doc_ids))
            data = np.clip(data, 1, 10000).astype(int)
            for doc_id, clicks in zip(doc_ids, data):
                self.es.update(
                    index=index,
                    doc_type="doc",
                    id=doc_id,
                    body={"doc": {"total_clicks": int(clicks)}},
                )

        elif target == "clickLog":
            # 得到所有仓库名称
            index = "repositories"
            field = "topics"  # 出于简单直接来到生成最后一步数据的地方
            unique_topics = self.get_unique_field_values(index, field)
            selected_topics = random.sample(unique_topics, n)

            # 生成正态分布的整数
            mu = 5.5
            sigma = 2.5
            normal_data = list(
                map(
                    int,
                    np.clip(np.random.normal(mu, sigma, len(selected_topics)), 1, 10),
                )
            )
            # 返回一个字典
            return dict(zip(selected_topics, normal_data))

        elif target == "intrest":
            # 得到所有仓库的主题
            index = "repositories"
            field = "topics"
            unique_topics = self.get_unique_field_values(index, field)
            # 随机选择n个主题组成列表并返回
            return random.sample(unique_topics, n)
        elif target == "testRecommend":
            # 得到所有仓库的名称
            index = "repositories"
            field = "name"
            unique_names = self.get_unique_field_values(index, field)
            # 随机选择n个仓库名称组成列表并返回
            return random.sample(unique_names, n)

    def print_results(self, response):
        for hit in response["hits"]["hits"]:
            print("匹配仓库名称:", hit["name"])
            print("匹配仓库得分:", hit["_score"])
            print("匹配仓库url:", hit["url"])

    def log_results(self, response, search_term):  # 往总日志里写
        path = os.path.join(os.getcwd(), "userLogs", "complexLog" + ".txt")
        with open(path, "a") as file:
            file.write("=======================================================")
            file.write("用户:" + self.username + "，搜索：" + search_term + ",得到结果如下：" + "\n")
            for hit in response["hits"]["hits"]:
                file.write("匹配仓库名称:" + hit["_source"]["name"] + "\n")
                file.write("匹配仓库得分:" + str(hit["_score"]) + "\n")
                file.write("匹配仓库url:" + hit["_source"]["url"] + "\n")
                file.write("\n")

    def log_search(self, username: str, search_info: dict):  # 往总日志里写
        """记录用户搜索日志"""
        path = os.path.join(os.getcwd(), "userLogs", "complexLog" + ".txt")
        with open(path, "a") as file:
            file.write("=======================================================")
            file.write("用户:" + username + "，搜索：" + search_info["search_query"] + "\n")
            file.write("用户的特征信息：/n")
            file.write("用户近期兴趣点：" + str(search_info["user_interests"]) + "\n")
            file.write("用户近期访问各网页次数：" + str(search_info["user_clicks"]) + "\n\n")

            file.write("用户搜索类型：" + search_info["search_type"] + "\n")
            file.write("用户选用排序方式：" + search_info["sort_order"] + "\n")
            file.write("用户是否选择包含readme：" + search_info["include_readme"] + "\n")


if __name__ == "__main__":  # 测试函数
    searcher = Searcher()

    # 搜索仓库
    # repos_response = searcher.search_repositories("freeCodeCamp")
    # searcher.print_results(repos_response)

    # 搜索用户
    # users_response = searcher.search_users("John Doe")
    # searcher.print_results(users_response)

    # 搜索代码
    # codes_response = searcher.search_codes("function")
    # searcher.print_results(codes_response)

    # Example usage

    # searcher.generate_data("totalClicks", 10000)

    # index = "repositories"
    # field = "total_clicks"
    # unique_values = searcher.get_unique_field_values(index, field)
    # print(unique_values)

    user_interests = [
        "rails",
        "joi",
        "pulltorefresh",
        "computer-science",
        "user-experience",
        "shopex",
        "dashboard",
        "presentation",
        "cluster",
        "cnodejs",
    ]
    user_clicks = {
        "apple-foundation": 8,
        "blade": 4,
        "buttons": 5,
        "category": 7,
        "cobalt-strike": 7,
        "codeigniter": 6,
        "confuse": 3,
        "cordova-plugin": 5,
        "coredata-model": 3,
        "dex": 3,
        "display-youtube": 6,
        "ebook": 9,
        "electroacoustic-music": 6,
        "electron-builder": 6,
        "email": 3,
        "emojis": 5,
        "flux-application": 6,
        "gd": 7,
        "git-server": 10,
        "gokit": 5,
        "hapi": 3,
        "hypervisor": 4,
        "jcanvas": 10,
        "kittyverse": 5,
        "mithril": 6,
        "native": 5,
        "ndk": 3,
        "node-android": 6,
        "peripheralmanager": 6,
        "prebuilt-binaries": 6,
        "project-explorer": 6,
        "qrcode": 2,
        "qrcode-scanner": 5,
        "quickshot": 7,
        "random": 4,
        "relativelayout": 8,
        "rust": 4,
        "smart": 7,
        "submodules": 9,
        "swift-3": 4,
        "synchronization": 8,
        "theme": 4,
        "threejs": 4,
        "traffic": 5,
        "typeahead": 4,
        "virtualenvwrapper": 9,
        "visibility": 6,
        "vue": 6,
        "wkwebview": 5,
        "yaml": 7,
    }
    sort_order = "pagerank"
    include_readme = "yes"
    search_query = "free"
    results = searcher.search_repositories(
        search_query, include_readme, sort_order, user_interests, user_clicks
    )
    pass
