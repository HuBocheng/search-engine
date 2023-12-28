import requests
from github import Github
import markdown
from bs4 import BeautifulSoup
import networkx as nx
from networkx.algorithms.link_analysis.hits_alg import hits
import json
import time
import itertools
import traceback
import datetime


class BaseCrawler:
    def __init__(self, access_file):
        self.access_token = self.read_access_token(access_file)
        self.github = Github(self.access_token)
        self.api_request_count = 0  # 新增变量来跟踪API请求次数
        self.start_time = time.time()

    def check_api_limit(self):
        """检查API限制，并在需要时暂停"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        if self.api_request_count >= 4800 and elapsed_time < 3600:
            sleep_time = 3600 - elapsed_time
            print(f"API请求达到限制，休眠{sleep_time}秒")
            time.sleep(sleep_time)
            # 重置计数器和计时器
            self.api_request_count = 0
            self.start_time = time.time()
        elif elapsed_time >= 3600:
            # 如果超过1小时，重置计数器和计时器
            self.api_request_count = 0
            self.start_time = time.time()

    @staticmethod
    def read_access_token(file_path):
        with open(file_path, "r") as file:
            return file.readline().strip()

    # 供子类重写的方法
    def loadPrefetchData(self, filepath):
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data

    def save2Json(self, data, filepath):
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)


class UserCrawler(BaseCrawler):
    def __init__(self, access_file):
        super().__init__(access_file)
        self.userNameList = []
        self.userInfo = []

    def loadPrefetchData(self, filepath):  # 需要的只是一个用户名的列表
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
            for user in data:
                self.userNameList.append(user.get("owner", None))
        return self.userNameList

    @staticmethod
    def datetime_handler(x):
        """处理数据中的datetime对象以便保存为JSON。"""
        if isinstance(x, datetime.datetime):
            return x.isoformat()
        raise TypeError("不支持的类型")

    def save2Json(self, filepath, data=None):  # 未定义data时，自动使用爬虫爬到的userInfo
        if data is None:
            data = self.userInfo
        try:
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=4,
                    default=self.datetime_handler,
                )
        except TypeError as e:
            print(f"保存JSON时出错：{e}")
        # 保存后清空数据以避免重复
        self.userInfo = []
        self.userNameList = []

    def crawl(self):
        count = 0
        # 实现特定于用户数据的爬取逻辑
        for username in self.userNameList:
            try:
                self.check_api_limit()
                count = count + 1

                user = self.github.get_user(username)
                user_info = {
                    "login": user.login,
                    "name": user.name,
                    "location": user.location,
                    "email": user.email,
                    "company": user.company,
                    "created_at": user.created_at,
                    "followers_count": user.followers,
                    "following_count": user.following,
                    "public_repos_count": user.public_repos,
                    "public_gists_count": user.public_gists,
                    "starred_repos_count": user.get_starred().totalCount,
                    "url": f"https://github.com/{user.login}",
                }
                self.userInfo.append(user_info)
            except Exception as e:
                print(f"Error processing {username}: {e}")
                path = f"data/partial_users{count}.json"
                self.save2Json(path)  # Saving the data gathered so far
                continue
            if count % 100 == 0:
                print(f"已处理{count}个用户")
            if count % 2000 == 0:
                path = f"data/users{count}.json"
                self.save2Json(path)
                print(f"已保存{count}个用户")
            self.api_request_count += 2
        pass


class RepoCrawler(BaseCrawler):
    def __init__(self, access_file):
        super().__init__(access_file)
        self.G = nx.DiGraph()
        self.repos_data = []

    def save2Json(self, filepath, data):  # 未定义data时，自动使用爬虫爬到的userInfo
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print("数据已保存到", filepath)

    def crawl(self, start_index, end_index, myQuery="stars:>1000"):
        # 实现特定于仓库数据的爬取逻辑
        repos_data = []
        repositories = self.github.search_repositories(query=myQuery)
        count = 0

        for repo in repositories[start_index:end_index]:
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
                        self.G.add_edge(repo.full_name, href)
                        external_links_count += 1

                # 添加外部链接数目
                repo_info["external_links_count"] = external_links_count

                # 获取README内容和话题标签
                repo_info["readme"] = content
                repo_info["topics"] = repo.get_topics()

                # 添加到列表
                repos_data.append(repo_info)

                count += 1
                if count % 200 == 0:
                    print("已处理", count, "个仓库")
            except Exception as e:
                print(f"Error processing {repo.full_name}: {e}")
        pagerank_scores = nx.pagerank(self.G)
        for repo_data in repos_data:
            repo_data["pagerank_score"] = pagerank_scores.get(repo_data["name"], 0)

        # hubs, authorities = hits(self.G, max_iter=100, normalized=True)
        # for node, hub_score in sorted(hubs.items(), key=lambda x: x[1], reverse=True):
        #     if self.G.nodes[node].get("url"):  # 只打印仓库节点的得分
        #         repo_data["HITS"]=
        #         print(node, hub_score)
        return repos_data


class CodeCrawler(BaseCrawler):
    def __init__(self, access_file):
        super().__init__(access_file)
        self.nameAndLanguageDic = []

    def get_file_content(self, repo, path):
        """获取特定仓库中文件的内容"""
        try:
            self.api_request_count += 1
            self.check_api_limit()  # 检查API限制
            file_content = repo.get_contents(path).decoded_content.decode("utf-8")
            return file_content
        except Exception as e:
            print(f"Error getting file content from {path}: {e}")
            return None

    def loadPrefetchData(self, filepath):
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
            for repo in data:
                repo_info = {
                    "name": repo["name"],
                    "language": repo.get("language", None),  # 假设所有未指明的仓库为公有
                    "url": repo["url"],
                    "stars": repo["stars"],
                }
                self.nameAndLanguageDic.append(repo_info)
        return self.nameAndLanguageDic

    def save2Json(self, filepath, data):  # 未定义data时，自动使用爬虫爬到的userInfo
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        # 存一次盘清空一次userInfo和userNameList
        self.nameAndLanguageDic = []

    def crawl_repo(self, repo_name, language, result):
        """爬取单个仓库中的代码文件内容"""
        if language not in ["Python", "Java", "C", "C++"]:
            return  # 跳过非目标语言的仓库
        try:
            self.api_request_count += 1
            self.check_api_limit()  # 检查API限制
            repo = self.github.get_repo(repo_name)
            self.api_request_count += 1
            self.check_api_limit()  # 检查API限制
            contents = repo.get_contents("")

            while contents:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    self.api_request_count += 1
                    self.check_api_limit()  # 检查API限制
                    contents.extend(repo.get_contents(file_content.path))
                else:
                    if file_content.name.endswith((".c", ".cpp", ".py", ".java")):
                        file_data = self.get_file_content(repo, file_content.path)
                        if file_data:
                            result.append(
                                {
                                    "url": file_content.html_url,
                                    "fileName": file_content.name,
                                    "content": file_data,
                                    "starts": repo.stargazers_count,
                                }
                            )
        except Exception as e:
            print(f"Error processing repo {repo_name}: {e}")

    def crawl(self):
        # 实现特定于代码数据的爬取逻辑
        files_data = []
        file_number = 1
        count = 0
        for repo in self.nameAndLanguageDic:
            count = count + 1
            if count % 100 == 0:
                print(f"已处理{count}个仓库")
            self.crawl_repo(repo["name"], repo["language"], files_data)
            if len(files_data) >= 1000:
                filePath = f"codes_files{file_number}.json"
                self.save2Json(filePath, files_data)
                files_data = []  # 重置结果列表
                file_number += 1
            if len(files_data) % 100 == 0:
                print(f"当前已获得代码文件个数：{len(files_data)}")
        self.save2Json("codes_files999.json", files_data)


if __name__ == "__main__":
    # # 实例化仓库爬虫
    # repo_crawler = RepoCrawler("data/access.txt")

    # # 设定每个文件要保存的仓库数量
    # repos_per_file = 2000
    # total_repos = 12000
    # files_to_save = total_repos // repos_per_file

    # # 爬取和保存仓库数据
    # for i in range(files_to_save):
    #     print(f"正在进行批次{i+1}")
    #     start_index = i * repos_per_file
    #     end_index = start_index + repos_per_file
    #     print(f"Crawling from repository {start_index + 1} to {end_index}")

    #     # 爬取仓库数据
    #     repos_data = repo_crawler.crawl(start_index, end_index)

    #     # 保存数据到JSON文件
    #     filename = f"repository_{i+1}.json"
    #     repo_crawler.save2Json(filename, repos_data)
    #     print(f"Saved {len(repos_data)} repositories to {filename}")

    #     # 延迟防止API速率限制
    #     time.sleep(1200)  # 延迟时间可能需要根据您的实际速率限制调整

    # # 实例化代码爬虫
    # code_crawler = CodeCrawler("data/access.txt")
    # code_crawler.loadPrefetchData("combined_repos_with_hits.json")
    # code_crawler.crawl()
    # 实例化用户爬虫
    user_crawler = UserCrawler("data/access.txt")
    # 从文件中加载用户名列表
    user_crawler.loadPrefetchData("combined_repos_with_hits.json")
    # 爬取用户数据
    user_crawler.crawl()
    # 保存用户数据
    user_crawler.save2Json("data/users9999.json")
