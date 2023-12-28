from elasticsearch5 import Elasticsearch
import json
import numpy as np
from scipy.spatial.distance import cosine
from collections import defaultdict
from typing import List, Optional
import hashlib
from userMOD import User
from searcherMOD import Searcher
import os


class HybridRecommenderSystem:
    def __init__(self, user_data_path, host="http://localhost:9200"):
        self.es = Elasticsearch([host])
        self.user_data_path = user_data_path
        self.user_data = self.load_user_data()  # 所有测试用户的数据
        self.user_now = None  # 当前登录用户

        self.infoDic = {}  # 储存和个性化推荐的所有信息，用于前端输出

    def set_username(self, username):
        self.user_now = username

    def load_user_data(self):
        """加载用户数据"""
        with open(self.user_data_path, "r") as file:
            data = json.load(file)
        return data

    def content_based_filtering(self, user_id):
        """基于内容的推荐逻辑"""
        # 获取用户数据，如技术栈和兴趣点
        user_info = self.user_data.get(user_id, {})
        # 根据用户信息查询Elasticsearch，返回匹配的仓库
        interests = user_info.get("interests", [])
        if isinstance(interests, list):  # 确保interests是列表
            interests_str = " ".join(interests)  # 将列表转换为字符串
        else:
            interests_str = interests  # 或者它已经是一个字符串
        query = {
            "query": {
                "multi_match": {
                    "query": interests_str,
                    "fields": ["language", "description", "topics"],
                }
            },
            "size": 200,
        }
        response = self.es.search(index="repositories", body=query)
        # 处理查询结果...
        return response

    # =======================协同过滤两个辅助函数=======================
    def jaccard_similarity(self, list1: List[str], list2: List[str]) -> float:
        """计算两个列表的Jaccard相似度"""
        set1, set2 = set(list1), set(list2)
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union != 0 else 0

    def find_similar_users(
        self, target_user: User, all_users: List[User], top_n: int = 3
    ) -> List[User]:
        """找到最相似的用户"""
        similarities = []
        for user in all_users[1:6]:
            if user.username != target_user.username:
                sim_score = max(
                    self.jaccard_similarity(
                        target_user.starred_repos, user.starred_repos
                    ),
                    self.jaccard_similarity(
                        target_user.forked_repos, user.forked_repos
                    ),
                )
                print(
                    f"Similarity between {target_user.username} and {user.username}: {sim_score}"
                )
                similarities.append((user, sim_score))
        # 按相似度排序
        sorted_users = sorted(similarities, key=lambda x: x[1], reverse=True)

        # 将和自己相似度最高的n个用户的信息保存在字典中
        self.infoDic["similar_users"] = []
        for user in sorted_users[:top_n]:
            self.infoDic["similar_users"].append(
                {
                    "username": user[0].username,
                    "starred_repos": user[0].starred_repos,
                    # "forked_repos": user[0].forked_repos,
                    "intrerests_and_tech": user[0].interests,
                    "similarity": user[1],
                }
            )
        return [user for user, sim in sorted_users[:top_n]]

    def collaborative_filtering(
        self,
        target_user: User,
        all_users: List[User],
        existing_recommendations,
    ):
        """根据协同过滤调整推荐列表"""
        # 找到相似用户
        similar_users = self.find_similar_users(target_user, all_users, top_n=3)

        # 获取内容推荐的仓库URL列表
        recommended_urls = [
            hit["_source"]["url"] for hit in existing_recommendations["hits"]["hits"]
        ]

        # 获取每个仓库的popularity和topics
        repo_details = []
        for url in recommended_urls:
            repo_popularity = sum(
                1 for user in similar_users if url in user.starred_repos
            )
            if repo_popularity > 0:
                repo_topics = self.get_repo_topics_and_language(
                    url
                )  # 假设URL可以直接用于获取仓库主题
                repo_details.append(
                    {
                        "url": url,
                        "topics": repo_topics,
                        "popularity": repo_popularity,  # 这个用于后续的评分机制
                    }
                )
        # 按照popularity排序，这样协同过滤结果前面的更可能被推荐
        sorted_repo_details = sorted(
            repo_details, key=lambda x: x["popularity"], reverse=True
        )

        self.infoDic["repo_popularity"] = sorted_repo_details

        return sorted_repo_details

    # =======================用户过滤两个辅助函数=======================
    # 获取仓库的主题和主要语言
    def get_repo_topics_and_language(self, url):
        # 构造查询以从Elasticsearch获取仓库主题
        try:
            query = {"query": {"match": {"url": url}}}  # 或者是仓库的ID或其他标识符
            response = self.es.search(index="repositories", body=query)
            # 假设每个仓库的文档中有一个topics字段，包含了主题的列表
            topics = response["hits"]["hits"][0]["_source"].get("topics", [])
            language = response["hits"]["hits"][0]["_source"].get("language", "")
            if isinstance(language, str):
                language = [language]
            return topics + language
        except Exception as e:
            # 在这里处理异常情况，比如打印错误日志，并返回一个空列表
            print(f"Failed to get topics for repo {url}: {e}")
            return []  # 返回空列表作为默认值

    # 获取用户最近搜索历史
    def get_recent_search_history(self, user_id):
        # 从用户日志文件中获取最近的搜索记录，并计算每个主题的出现频率
        log_file_path = os.path.join(os.getcwd(), "userLogs", user_id + ".json")
        with open(log_file_path, "r") as file:
            data = json.load(file)
        search_history = data["web_click_logs"]
        # 计算频率
        topic_frequency = defaultdict(int)

        for search in search_history:
            url = search["url"]
            if url.startswith("https://github.com"):
                # 假设每个搜索可能对应多个仓库，需要获取每个仓库的主题
                repo_topics = self.get_repo_topics_and_language(
                    url
                )  # 从Elasticsearch获取每个搜索对应仓库的主题
                for topic in repo_topics:
                    topic_frequency[topic] += 1
        return topic_frequency

    def adjust_with_realtime_behavior(self, user_id, recommendations) -> dict:
        """根据用户实时行为调整推荐列表"""

        # 获取用户兴趣点
        user_interests = self.user_data[user_id].get("interests", [])

        # 强烈推荐逻辑
        strong_recommendations = []
        # 遍历协同过滤的结果
        for auto in self.infoDic["repo_popularity"]:
            count = auto["popularity"]
            topics = auto["topics"]
            url = auto["url"]
            if count > len(self.infoDic["similar_users"]) / 2:  # 超过一半相似用户star
                # 检查仓库主题是否在用户兴趣点中
                if any(interest in topics for interest in user_interests):
                    strong_recommendations.append(url)

        # 一般推荐逻辑 - 修正协同过滤得到的列表
        # 加载用户最近的搜索和浏览历史

        recent_topic_frequency = self.get_recent_search_history(user_id)

        # 为每个推荐计算得分
        scored_recommendations = {}
        # 得到协同过滤仓库的主题
        for repo in recommendations:
            # 评分机制：考虑协同过滤的popularity和最近访问主题的匹配度
            repo_score = 0
            repo_score += repo["popularity"]  # 协同过滤得到结果中排前的结果得分高
            for topic in repo["topics"]:  # 主题出现在用户最近访问数据的仓库得分高
                repo_score += recent_topic_frequency.get(topic, 0)
            scored_recommendations[repo["url"]] = repo_score
        # 排序：根据得分高低排序
        sorted_recommendations = sorted(
            scored_recommendations, key=scored_recommendations.get, reverse=True
        )

        # 结合强烈推荐和一般推荐
        final_recommendations = {
            "strong_recommendations": strong_recommendations,
            "general_recommendations": sorted_recommendations,
        }
        self.infoDic["final_recommendations"] = final_recommendations

        return self.infoDic["final_recommendations"]

    def recommend(self, username, target_user: User, all_users: List[User]) -> dict:
        """生成推荐列表"""
        recommendations = self.content_based_filtering(username)
        recommendations = self.collaborative_filtering(
            target_user, all_users, recommendations
        )
        recommendations = self.adjust_with_realtime_behavior(username, recommendations)
        return self.infoDic


if __name__ == "__main__":
    # 测试个性化推荐---》总体需要数据：个人的intrest，个人的start

    # 随机20个主题数据
    searcher = Searcher()
    all_topics = searcher.get_unique_field_values("repositories", "topics", 100)

    # 主题分给五个人做intrest——>user2到user6
    users_topics = [
        all_topics[4:8],
        all_topics[5:10],
        all_topics[4:6] + (all_topics[11:13]),
        all_topics[20:25],
        [(all_topics[4])] + (all_topics[26:30]),
    ]

    # 生成五个人的start仓库
    users_repo = []
    field_name = "topics"
    for auto in users_topics:
        query = {
            "query": {
                "bool": {"should": [{"match": {field_name: term}} for term in auto]}
            },
            "size": 20,
        }

        # 执行搜索
        response = searcher.es.search(index="repositories", body=query)

        # 提取hits部分
        hits = response["hits"]["hits"]
        # 转换为文档列表
        documents = [doc["_source"]["url"] for doc in hits]
        users_repo.append(documents)

    bufferList = []
    bufferList2 = []

    for auto in users_repo:
        print(auto)
        print(len(auto))

    pass

    path = os.path.join(os.getcwd(), "data", "myUsers.json")
    # 实例化user
    with open(path, "r") as file:
        data = json.load(file)
    users = {}
    for username, user_info in data.items():
        users[username] = User(username, **user_info)

    target_user = users["user2"]
    all_users = list(users.values())

    recommender = HybridRecommenderSystem(path)
    recommender.set_username("user2")

    # 假设get_personalized_data()是一个根据用户返回个性化数据的函数
    x = recommender.content_based_filtering("user2")
    y = recommender.collaborative_filtering(target_user, all_users, x)
    z = recommender.adjust_with_realtime_behavior("user2", y)

    personalized_data = recommender.recommend("user2", target_user, all_users)
    print(personalized_data)
    pass
