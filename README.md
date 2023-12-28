# search-engine

NKU2023Fall Information retrieval project——search engine based on GIthub repository



## 一、项目运行

#### 爬虫爬取数据

先通过`crawler`文件夹下的`crawl_url.py`爬取仓库链接，然后用`real_crawl_repos.py`爬取指定链接的仓库

`crawlerMOD.py`中的代码可以爬取小部分数据，构建搜索引擎需要大量数据需要用上面的方法

#### 搜索引擎启动

在根目录下

- `python -u .\src\test\open_service.py`：开启Elasticsearch服务（注：Elasticsearch和相应的可视化插件位置需要变化）
- `python -u  .\src\run.py`运行搜索引擎

> 想使用代码需要先在根目录下创建data文件夹，里面放你的GIthub access_token
>
> 还需要下载Elasticsearch5.6.8和对应的可视化工具elasticsearch-head，并修改open_service.py中的路径



## 二、实现的功能

#### 1、搜索功能

- 基础仓库搜索：
  - 短语查询
  - 通配查询
  - 站内查询
  - 高级搜索：
    - 可以指定词项在匹配文档的时候匹配哪些字段值
    - 多种排序方式（热度【所有网页访问总次数】、pagerank得分、HITS算法计算得分）
  - 统配查询，得定义统配查询的语法
- 代码搜索：
  - 在代码数据库中搜索，匹配文档返回相应链接和代码所在仓库介绍
- 用户搜索
  - 在用户数据库中搜索，匹配用户信息文档，返回相应链接和用户个人信息介绍

#### 2、日志功能

- 复杂的总日志：
  - 搜索的配置记录：包括此次搜索的词项、是否包含readme、搜索的类型是仓库/代码/用户
  - 搜索的结果记录：搜索的用户是谁，这个用户的个人信息包含什么，搜索的结果有哪些，每个结果的得分是多少
- 用户日志：
  - 用户搜索记录：记录什么时候哪个用户搜索了什么
  - 用户访问记录：记录什么时候哪个用户点击了哪个链接

#### **3、快照功能**

把网页内容变成图片存在本机，在本地存在快照的时候前端显示按钮可以直接点开图片，省去网页的加载时间

#### **4、个性化查询**

**（1）个性化查询的逻辑**

- 对于网页topic字段中包含用户兴趣点和技术栈的网页有更大的权重
- 网页点击次数字典中，点击次数多的网页对应主题的网页有更大的权重（我认为可以从用户点击的所有网页中将主题和点击次数做乘积，得到每一个主题的总次数，然后这个主题有关的网页搜索结果的评分和该主题对应的总次数成正比）
- 搜索结果中，网页对应总点击次数大的网页有更大的权重
- 结合Elasticsearch 自带的评分机制**Practical Scoring Function**计算综合评分

#### 5、个性化推荐

**（1）个性化推荐逻辑**

1、首先**基于内容的推荐**缩小范围

- 根据用户的技术栈和兴趣点，查询Elasticsearch获取匹配的数据。
- 使用multi_match查询来匹配用户的技术栈等与存储库的语言、描述和话题。

2、然后**协同过滤**考虑用户相似性

- 根据目标用户和相似用户的喜好（例如星标和fork的仓库），生成推荐列表。
  - 计算Jaccard相似度（衡量两个集合相似度的指标）并寻找相似用户
- 通常从相似用户喜欢的项中提取出一些尚未被目标用户发现的项作为推荐。

3、根据本用户**实时行为调整**

- 根据用户的实时行为（如最近的搜索或浏览记录）来调整推荐列表。
- 这个环节可以使推荐更加灵活和个性化，但实现细节在这里被省略了。

通俗解释一下个性化推荐的三个部分做的事情

1、根据用户兴趣，总数据库中拿一小部分

2、打破人与人之间的信息壁垒，找到和用户需求相似的其他用户，看看他们都喜欢什么（start/fork了什么仓库）

3、但是和我相似的人喜欢的东西不一定是我最近感兴趣的东西（我之前写大数据，start很多大数据仓库，最近写IR，需要的事IR仓库），那么就需要在上面的基础上再根据我最近历史过滤一下

**（2）个性化推荐功能**

功能方面分成了：

1. **强烈推荐**，大部分其他相似用户都有，但是你没有的——具体实现就是：用协同过滤产生的那个字典（记录了相似用户start的仓库和这个仓库被多少个相似用户start），如果某个仓库被超过一半相似用户start，且这个仓库的主题在本用户的兴趣点中，说明这个仓库是“沧海遗珠”值得强力推荐
2. **一般推荐**：修正协同过滤得到的列表——和我相似用户喜欢（start）的仓库不一定是我最近关注的，根据最近访问仓库主题出现的频度，为协同过滤产生的仓库列表打分，遍历每一个协同过滤产生结果，这个结果仓库中各主题在最近出现频度高则得分高，然后根据得分综合排序并输出





## 三、项目目录

src目录下

```
│  logMOD.py                      # 日志模块
│  recommandMOD.py                # 推荐模块
│  run.py                         # 搜索引擎启动文件
│  searcherMOD.py                 # 搜索模块
│  shotMOD.py                     # 快照模块
│  uploadCodes.py                 # 上传代码数据到Elasticsearch
│  uploadRepos.py                 # 上传仓库数据到Elasticsearch
│  uploadUsers.py                 # 上传用户数据到Elasticsearch
│  userMOD.py                     # 用户模块
│
├─app
│  │  routes.py                   # flask的路由函数集合
│  │  __init__.py                 # flask的初始化文件
│  │
│  ├─templates
│  │      codes_results.html      # 代码搜索结果页面
│  │      index.html              # 主页
│  │      login.html              # 登录页面
│  │      recommendations.html    # 推荐结果页面  
│  │      repos_results.html      # 仓库搜索结果页面
│  │      search.html             # 搜索页面
│  │      users_results.html      # 用户搜索结果页面
│  │
├─crawler                         # 爬虫文件夹
│      check_githubAPI.py         # 检查githubAPI配额情况
│      crawlerMOD.py              # 爬虫模块封装
│      crawl_codes.py             # 爬取代码数据
│      crawl_repos.py             # 爬取仓库数据
│      crawl_users.py             # 爬取用户数据
│      real_crawl_repos.py        # 爬取指定仓库
│
├─test
│  │  generateKey.py              # 生成密钥
│  │  HITS.py                     # HITS算法
│  │  open_service.py             # 开启Elasticsearch服务
│  │  pagerank.py                 # pagerank算法
│  │  __init__.py
│  │
│  |
```



## 四、代码分析

#### 1、爬虫部分
爬虫部分直接使用了githubAPI，爬取了github上的仓库、用户和代码数据，爬取的数据存储在本地，然后上传到Elasticsearch中

##### （1）仓库爬取部分

- 通过crawl_url.py爬取仓库链接，然后用real_crawl_repos.py爬取指定链接的仓库
- 爬取到的仓库储存在data中，后续经过pagerank和HITS算法进行链接分析之后上传到Elasticsearch中
- 仓库数据包括：仓库名、仓库描述、仓库链接、仓库主题、仓库语言、仓库star数、仓库fork数、仓库创建时间、仓库更新时间、仓库对应readme文件内容



其中获取url的时候定义下面的函数，接收搜索关键词、请求头、页码和星星数量作为参数，然后构建一个 URL以获取到指定页数的仓库链接

```python
def get_results(search, headers, page, stars):
    url = (
        "https://api.github.com/search/repositories?q={search}%20stars:<={stars}&page={num}&per_page=100&sort=stars"
        "&order=desc".format(search=search, num=page, stars=stars)
    )
    req = Request(url, headers=headers)
    response = urlopen(req).read()
    result = json.loads(response.decode())
    return result
```
随后在主函数中下面的主函数中，每次循环都会调用 get_results 函数来获取一页的仓库信息。对于每个返回的仓库，它都会将仓库的信息添加到 repos_list 列表中，并将仓库的星星数量添加到 stars_list 列表中。然后，它将 stars_list 的最后一个元素设置为下一次搜索的星星数量。

```python
for i in range(0, 15):
        print("batch: ", i)
        repos_list = []
        stars_list = []
        for page in range(1, 11):
            results = get_results(search, headers, page, stars)
            for item in results["items"]:
                repos_list.append([count, item["name"], item["html_url"]])
                stars_list.append(item["stargazers_count"])
                count += 1
            print(len(repos_list))
        stars = stars_list[-1]
        print(stars)
        with open("./top15000Repos.txt", "a", encoding="utf-8") as f:
            for i in range(len(repos_list)):
                f.write(
                    str(repos_list[i][0])
                    + ","
                    + repos_list[i][1]
                    + ","
                    + repos_list[i][2]
                    + "\n"
                )
```

随后在real_crawl_repos.py中，通过读取上面爬取到的仓库链接，爬取仓库数据，爬取到的数据存储在data中，后续经过pagerank和HITS算法进行链接分析之后上传到Elasticsearch中

核心函数如下

```python
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
```

##### （2）代码爬取部分

```python
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
```
爬虫的基类定义了一些基本的函数，包括检查API限制、读取密钥、读取预加载数据、保存数据到json文件

其子类代码爬虫器继承了基类，实现了代码爬取的功能，核心代码如下

```python
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
```
1. `get_file_content`：获取特定仓库中文件的内容。首先检查 API 限制，然后尝试获取文件内容。如果出现异常，打印错误信息并返回 None。
2. `loadPrefetchData`：从指定的文件路径加载预获取的数据。这些数据是一个包含仓库信息的 JSON 文件。每个仓库的信息被添加到 `nameAndLanguageDic` 列表中。
3. `save2Json`：将数据保存为 JSON 文件。如果没有指定数据，将使用爬虫获取的用户信息。保存后，清空 `nameAndLanguageDic` 列表。
4. `crawl_repo`：爬取单个仓库中的代码文件内容。只处理 Python、Java、C 和 C++ 这四种语言的仓库。首先检查 API 限制，然后获取仓库的内容。对于每个文件，如果它是一个目录，就获取该目录下的所有文件。如果它是一个代码文件，就获取其内容并添加到结果列表中。
5. `crawl`：实现特定于代码数据的爬取逻辑。对于 `nameAndLanguageDic` 列表中的每个仓库，调用 `crawl_repo` 方法获取其代码文件的内容。每当获取到 1000 个文件时，就将这些文件保存为一个 JSON 文件，并清空结果列表。最后，将剩余的文件保存为一个 JSON 文件。

##### （3）用户爬取部分

实现和代码爬虫类十分类似，不过多赘述



#### 2、索引构建

##### （1）上传本地json到Elasticsearch

直接使用Elasticsearch提供的`index`函数，将爬取到的数据上传到Elasticsearch中，上传的数据包括：仓库数据、用户数据、代码数据三部分。

首先读取爬到本地的文件为字典

```python
# 读取JSON文件
with open("data/allRepositories.json", "r", encoding="utf-8") as file:
    repos_data = json.load(file)
print("读取数据完成，共" + str(len(repos_data)) + "个仓库")
```

遍历 `repos_data` 中的每个仓库，使用 `es.index(index=index_name, body=repo, doc_type="doc")` 将每个仓库的数据添加到 Elasticsearch 索引中。

```python
# 构建Elasticsearch索引
index_name = "repositories"

# 确保索引不存在
if not es.indices.exists(index=index_name):
    # 创建索引
    es.indices.create(index=index_name)

# 向Elasticsearch中添加数据
for i, repo in enumerate(repos_data):
    es.index(index=index_name, body=repo, doc_type="doc")
    if (i + 1) % 2000 == 0:
        print("已上传" + str(i + 1) + "个仓库数据")
```

`index`函数参数是`index`、`doc_type`、`id`、`body`。其中`index`是索引名，`doc_type`是文档类型，`id`是文档id，`body`是文档内容，这里的id是自动生成的，`body`是一个字典，包含了文档的内容，具体的内容可以参考代码。

##### （2）添加中文分词器

需要在创建索引之前进行这个工作，这里定义字段的分析器为`ik_smart`

```python
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
                    "search_analyzer": "ik_smart"  # 搜索时使用ik_smart分词器
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
```



#### 3、链接分析

实现了pagerank算法和HITS算法，但是由于pagerank算法计算得到的数据区别不是很大，所以最后使用了HITS算法。至于为什么PageRank算法性能不好，我猜想是爬取仓库数目相较于整个GitHub网站还是太小了，导致仓库与仓库间的内部链接数目很少，外部连接数目很多，对于链接稀疏的图，PageRank算法性能不会很好。

##### （1）算法介绍

 - **PageRank**通过一个迭代过程计算页面的重要性。每个页面的初始PageRank分布均等，然后通过迭代更新每个页面的PageRank值，直到达到稳定状态。页面的PageRank值是所有指向它的页面的PageRank值的总和，经过一个衰减因子的调整。
 - **HITS算法**是一种基于超链接分析的算法，它通过迭代计算两个值：hub和authority。hub表示一个页面指向其他页面的数量，authority表示一个页面被其他页面指向的数量。HITS算法的核心思想是：一个页面的重要性可以通过它指向的其他页面的重要性来计算，以及指向它的其他页面的重要性来计算。

##### （2）代码实现

在爬虫的过程中对爬取到GitHub仓库的readme文档做链接分析，由于GitHub仓库页面大部分一致，其界面中蕴含的链接对于每个仓库基本相同，所以要想评判一个GitHub仓库内容丰富与否，我们可以关注其readme文档，要是其中链接很多，就侧面反映其更重要。

核心代码如下：

```python
# 创建一个有向图
G = nx.DiGraph()
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
            
            # ......其他代码省略
    pagerank_scores = nx.pagerank(G)
    for repo_data in repos_data:
        repo_data["pagerank_score"] = pagerank_scores.get(repo_data["name"], 0)

    return repos_data     
```

在爬取仓库的过程中，对整个图的边进行构建,在爬取到一个仓库各种信息后，先使用BeautifulSoup解析readme文档，然后提取其中的链接，将这些链接作为图的边，仓库名作为图的节点，将这些边和节点添加到图中。将所有仓库爬取完毕后，使用pagerank算法和HITS算法对图进行链接分析，最后将分析结果添加到仓库信息中，上传到Elasticsearch中。

> HITS算法代码和这个很像，详情见test/HITS.py，不过要区分枢纽得分和权威得分
>
> 枢纽得分衡量一个网页的链接质量，一个高枢纽得分的网页是指链接到多个高权威网页的页面。
>
> 权威得分是衡量一个网页内容质量和可信度的指标。一个高权威得分的网页通常含有大量的高质量信息，并且被许多其他页面引用。



#### 4、查询服务

本部分项目封装了一个searchMOD的py文件，其中有一个Search类。

```python
class Searcher:
    def __init__(self, host="http://localhost:9200"):
        self.es = Elasticsearch([host])
        self.username = ""

    def set_username(self, username):
        self.username = username
```

构造函数为其赋予一个Elasticsearch客户端

##### （1）短语查询和统配查询

这两个功能在Elasticsearch的实现中是两个不同的方向，这里编写了两个函数，**它们只是细节上有差异，前端的路由函数根据输入搜索框的内容来决定具体调用短语查询接口还是统配查询接口**

对于短语查询来说，实现下面的函数

```python
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
                        "functions": [
                            # 自定义的评分函数，用于个性化查询，这里省略
                        ],
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
```

这个函数参数有

- `search_term`：搜索关键词
- `include_readme`：是否包括readme
- `fields`：搜索字段
- `sort_order`：排序方式
- `user_interests`：用户兴趣点
- `user_clicks`：用户点击次数

其中，前三个参数适用于查询的一般配置，后面的用户点击次数和用户兴趣点是为了实现个性化查询而添加的，这里先不讨论，后面会详细介绍。

函数首先根据传输的配置参数构造一个`query`字典，然后调用`es.search`函数进行搜索，最后返回搜索结果。

返回的结果respone是一个复杂的字典，包含的信息如下

-  **took**：表示执行搜索所花费的时间（毫秒）。

- **timed_out**：布尔值，表示搜索是否超时。

- **_shards**：提供关于分片的信息，包括：
  - **total**：搜索涉及的分片总数。
  - **successful**：成功返回结果的分片数。
  - **skipped**：跳过的分片数。
  - **failed**：失败的分片数。

-  **hits**：这是一个包含了大量信息的嵌套字典，是使用者最关注的部分，它包含以下字段：
  - **total**：匹配查询的文档总数。它本身可能是一个包含`value`和`relation`的字典，`value`表示匹配的数量，`relation`表示这个值是精确的（`eq`）还是一个下限（`gte`）。
  - **max_score**：所有匹配到的文档中的最高分数。
    - **hits**：一个数组，包含了实际的匹配文档。每个匹配文档包含：
    - **_index**：文档所在的索引名。
    - **_type**：文档的类型。
    - **_id**：文档的ID。
    - **_score**：文档的相关性得分。
    - **_source**：文档的原始内容（除非在查询中指定不返回）。
    - 其他可能的元数据，如`_highlight`（如果请求了高亮显示）。

    

**对于通配查询**，我们只需要`query`字典的“query”字段换成下面的样子即可，其余不变

```python
"query": {
                "query_string": {
                    "fields": fields,
                    "query": "/" + search_term + "/",
                    # "query": search_term,
                    "analyze_wildcard": True,  # 允许分析通配符
                }
            },
```

##### （2）日志部分

对于用户数据部分，写了一个日志类来管理全部日志

```python
class SearchLogEntry:
    def __init__(
        self, user_id: str, search_query: str, search_type: str, timestamp: datetime
    ):
        self.user_id = user_id
        self.search_query = search_query
        self.search_type = search_type
        self.timestamp = timestamp

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "search_query": self.search_query,
            "search_type": self.search_type,
            "timestamp": self.timestamp,  # 将 datetime 对象转换为字符串
        }


class WebVisitLogEntry:
    def __init__(self, user_id: str, url: str, timestamp: datetime):
        self.user_id = user_id
        self.url = url
        self.timestamp = timestamp


class UserActivityLogger:
    def __init__(self):
        self.search_logs = []  # List to store search logs
        self.web_visit_logs = []  # 其实没用
        self.page_visit_logs = []  # List to store page visit logs
        self.web_click_logs = []  # List to store web click logs
        self.root = os.getcwd()
        # print(self.root)  # test point
        self.floder = "userLogs"

    def _initialize_logs(self):
        """Initialize all logs as empty lists."""
        self.search_logs = []
        self.web_visit_logs = []
        self.page_visit_logs = []
        self.web_click_logs = []

    def openLogFile(self, userName: str):
        """Open a log file and read the logs into memory."""
        logFile = os.path.join(self.root, self.floder, userName + ".json")
        if os.path.exists(logFile):
            try:
                with open(logFile, "r") as file:
                    # 检查文件是否为空
                    file_content = file.read()
                    if file_content:
                        data = json.loads(file_content)
                        self.search_logs = data.get("search_logs", [])
                        self.page_visit_logs = data.get("page_visit_logs", [])
                        self.web_click_logs = data.get("web_click_logs", [])
                    else:
                        self._initialize_logs()
            except json.JSONDecodeError:
                self._initialize_logs()
        else:
            os.makedirs(os.path.dirname(logFile), exist_ok=True)
            self._initialize_logs()
            with open(logFile, "w") as file:
                json.dump(
                    {
                        "search_logs": self.search_logs,
                        "web_visit_logs": self.web_visit_logs,
                        "page_visit_logs": self.page_visit_logs,
                        "web_click_logs": self.web_click_logs,
                    },
                    file,
                    indent=4,
                )

    def saveLogFile(self, userName: str):
        """Save the logs stored in memory to a log file."""
        logFile = os.path.join(self.root, self.floder, userName + ".json")
        data = {
            "search_logs": self.search_logs,
            "page_visit_logs": self.page_visit_logs,
            "web_click_logs": self.web_click_logs,
        }
        with open(logFile, "w") as file:
            json.dump(data, file, indent=4)

    def log_search(self, user_id: str, search_query: str, search_type: str):
        """Log a user's search query along with the current timestamp."""
        timestamp = datetime.now()
        # self.search_logs.append(
        #     SearchLogEntry(user_id, search_query, search_type, timestamp.isoformat())
        # )
        self.search_logs.append(
            {
                "search_query": search_query,
                "search_type": search_type,
                "timestamp": timestamp.isoformat(),
            }
        )

    def log_web_visit(self, user_id: str, url: str):
        """Log a user's web visit along with the current timestamp."""
        timestamp = datetime.now()
        self.web_visit_logs.append(
            WebVisitLogEntry(user_id, url, timestamp.isoformat())
        )

    def get_user_search_history(self, user_id: str) -> List[Tuple[str, datetime]]:
        """Retrieve the search history of a given user."""
        return [
            (entry.search_query, entry.timestamp)
            for entry in self.search_logs
            if entry.user_id == user_id
        ]

    def get_user_web_visit_history(self, user_id: str) -> List[Tuple[str, datetime]]:
        """Retrieve the web visit history of a given user."""
        return [
            (entry.url, entry.timestamp)
            for entry in self.web_visit_logs
            if entry.user_id == user_id
        ]

    def log_web_click(self, user_id: str, url: str):
        """Log a user's click on a URL."""
        timestamp = datetime.now()
        self.web_click_logs.append({"url": url, "timestamp": timestamp.isoformat()})
        print("成功添加一个点击记录")  # test point

    def log_page_visit(self, user_id: str, url: str, duration: int):
        """Log a user's visit duration on a page."""
        timestamp = datetime.now()
        self.page_visit_logs.append(
            {
                "url": url,
                "visit_duration": duration,
                "timestamp": timestamp.isoformat(),
            }
        )
        print("成功添加一个访问记录")  # test point
```

- `SearchLogEntry` 类
  - **目的**：用于存储单个搜索日志条目的详细信息。
  - **属性**：包括`user_id`（用户ID），`search_query`（搜索查询），`search_type`（搜索类型）以及`timestamp`（时间戳）。
  - **方法**：
    - `to_dict()`：将日志条目的属性转换为字典格式，这可能用于将数据转换为可存储或可传输的格式。

- `WebVisitLogEntry` 类
  - **目的**：用于存储单个网页访问日志的详细信息。
  - **属性**：包括`user_id`（用户ID），`url`（访问的URL），以及`timestamp`（时间戳）。

- `UserActivityLogger` 类
  - **目的**：作为主要的日志处理器，用于记录、存储和检索用户活动日志。
  - **属性**：
    - 多个列表，用于存储不同类型的日志，如搜索日志、网页访问日志、页面访问日志和点击日志。
    - `root` 和 `floder` 用于定义日志文件存储的目录。
  - **方法**：
    - `_initialize_logs()`：初始化所有日志列表为空列表。
    - `openLogFile(userName)`：打开特定用户的日志文件，读取日志条目到内存中的对应列表。
    - `saveLogFile(userName)`：将内存中的日志条目保存回用户的日志文件。
    - `log_search()`：记录一条搜索日志。
    - `log_web_visit()`：记录一条网页访问日志。
    - `get_user_search_history()`：检索指定用户的搜索历史。
    - `get_user_web_visit_history()`：检索指定用户的网页访问历史。
    - `log_web_click()`：记录用户对某个URL的点击。
    - `log_page_visit()`：记录用户对某个页面的访问时长。



此外，还在查询服务的Search类中实现了复杂日志的写入接口

```python
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
```
上面的代码分别用于记录用户的搜索结果和用户的搜索信息，这里的搜索信息包括用户的兴趣点、用户的点击次数、用户的搜索类型、用户的排序方式、用户是否选择包含readme。


##### （3）快照部分
网页快照需要将网页的全部信息以图片的形式存在本地，这里使用了`selenium`库，它可以模拟浏览器的行为，打开网页，截图，关闭网页。同时还使用了`PIL`库和`io`库，将截图的图片拼接到一张大图当中，再转换为二进制流，然后存储到本地。

```python
class GithubRepoSnapshot:
    def __init__(self, github_token):
        self.github = Github(github_token)
        edge_options = EdgeOptions()
        edge_options.use_chromium = True
        edge_options.add_argument("--headless")
        edge_options.add_argument("--disable-gpu")
        edge_options.add_argument("--window-size=1920,1080")
        service = Service(EdgeChromiumDriverManager().install())
        self.driver = webdriver.Edge(service=service, options=edge_options)

    def get_repo_url(self, repo_name):
        """Get the URL of a GitHub repository."""
        repo = self.github.get_repo(repo_name)
        return repo.html_url

    def capture_full_page_snapshot(self, url, save_path):
        """Capture and save a full page snapshot of the given URL."""
        self.driver.get(url)
        time.sleep(5)  # 等待页面加载

        total_height = self.driver.execute_script("return document.body.scrollHeight")
        view_height = self.driver.execute_script("return window.innerHeight")
        slices = []
        offset = 0
        while offset < total_height:
            self.driver.execute_script("window.scrollTo(0, %s);" % offset)
            time.sleep(2)  # 等待滚动和内容加载
            img_binary = self.driver.get_screenshot_as_png()
            img = Image.open(BytesIO(img_binary))
            slices.append(img)
            offset += view_height - 55
            # 把每张截的图都保存下来
            img.save("everysnapshot{}.png".format(offset))

        final_img = Image.new("RGB", (slices[0].size[0], total_height))
        offset = 0
        for img in slices[:-1]:
            final_img.paste(img, (0, offset))
            offset += view_height
        final_img.paste(slices[-1], (0, total_height - slices[-1].size[1]))  # 粘贴最后一片

        final_img.save(save_path)

    def close(self):
        """Close the WebDriver."""
        self.driver.quit()

```

- 类的构造函数初始化了Github客户端并配置`Selenium`的**Edge浏览器驱动**
  - `edge_options = EdgeOptions()`: 创建一个EdgeOptions对象，该对象将被用来配置Edge浏览器的启动选项。
  - `edge_options.use_chromium = True`: 指定Selenium使用Chromium版的Edge浏览器。这是必须的，因为现在Edge浏览器基于Chromium。
  - `edge_options.add_argument("--headless")`: 添加无头模式参数。无头模式下，浏览器界面不会在屏幕上显示，适合后台运行和自动化任务。
  - `edge_options.add_argument("--disable-gpu")`: 添加禁用GPU加速参数。在某些环境和版本的浏览器中，禁用GPU加速可以避免一些问题。
  - `edge_options.add_argument("--window-size=1920,1080")`: 设置浏览器窗口大小。这对于确定页面如何布局，以及截图的大小有影响。
  - `service = Service(EdgeChromiumDriverManager().install())`: 使用`webdriver_manager`库来自动管理Edge驱动的安装和更新。这样可以确保使用的驱动与浏览器版本兼容。
  - `self.driver = webdriver.Edge(service=service, options=edge_options)`: 创建WebDriver实例，用于控制Edge浏览器。这个`driver`对象将被用于加载网页、执行JavaScript、捕获屏幕截图等操作。
- `get_repo_url` 方法：用于获取指定GitHub仓库的URL
  - 通过`self.github.get_repo(repo_name)`调用GitHub API来获取仓库对象。
  - 返回仓库对象的`html_url`属性，即仓库的网页地址。
- `capture_full_page_snapshot`方法：捕获给定URL的完整页面快照，并将其保存为PNG文件
  - 使用WebDriver打开指定的`url`。
  - 等待页面加载（硬编码延时，`time.sleep(5)`）。
  - 计算页面总高度和可视区域高度。
  - 循环滚动页面，并在每个位置上捕获视口内的屏幕截图，将截图保存到`slices`列表中。
  - 将所有分片的图像拼接成一张完整的图像。
  - 保存最终的图像到`save_path`指定的文件路径。
- `close`方法：关闭WebDriver会话，关闭浏览器窗口。



#### 5、个性化查询

在搜索模块的逻辑中定义了个性化查询所用的评分详细逻辑

```python
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
```

分别满足个性化查询的三个方面：

- 对于网页topic字段中包含用户兴趣点和技术栈的网页有更大的权重
- 网页点击次数字典中，点击次数多的网页对应主题的网页有更大的权重（我认为可以从用户点击的所有网页中将主题和点击次数做乘积，得到每一个主题的总次数，然后这个主题有关的网页搜索结果的评分和该主题对应的总次数成正比）
- 搜索结果中，网页对应总点击次数大的网页有更大的权重

最后将自定义评分加和，并和Elasticsearch自带的评分机制得分相乘得到最终得分，按照这个得分排序实现个性化查询。



Elasticsearch 自带的评分机制**Practical Scoring Function**计算综合评分，它计算综合评分的主要组成部分如下:

1. **TF（词频）**

- **含义**：TF表示词条（term）在文档中出现的频率。词条在文档中出现次数越多，它对文档的贡献就越大。
- **计算**：通常采用的是词条频率的平方根。

2. **IDF（逆文档频率）**

- **含义**：IDF衡量一个词条的通用性。如果一个词条在很多文档中出现，则它不太有助于区分文档，因此其IDF值会低。
- **计算**：IDF是文档总数除以包含该词条的文档数的对数。Elasticsearch使用一种稍微变体的IDF，以防止分母为0。

3. **Field-Length Norm**

- **含义**：文档中字段的长度也会影响评分。通常情况下，相同数量的词条在较短文本中出现，意味着单个词条对文档主题的影响更大。
- **计算**：字段长度规范化通常是字段长度的倒数或其平方根的倒数。

4. **Coordinate Factor**

- **含义**：坐标因子考虑查询中的词条与文档中的词条匹配的程度。
- **计算**：它是查询中匹配的词条数与查询中总词条数的比率。

5. **Query-Time Boosting**

- 查询时可以对特定的文档字段或文档进行加权，以提高其在结果中的排名。

**综合评分计算**

综合评分通常是这些因素的乘积，即：
$$
\text{Score}(d, q) = \text{TF}(d, q) \times \text{IDF}(d, q)^2 \times \text{Field-Length Norm}(d, q) \times \text{Coordinate Factor}(d, q) \times \text{Query-Time Boosting}(q)
$$


#### 6、个性化推荐

个性化推荐分为三部分：**基于内容的推荐**、**协同过滤**（基于用户群体推荐）、**用户实时行为调整**（基于历史数据推荐）

通俗解释一下个性化推荐的三个部分做的事情

1、根据用户兴趣，总数据库中拿一小部分

2、打破人与人之间的信息壁垒，找到和用户需求相似的其他用户，看看他们都喜欢什么（start/fork了什么仓库）

3、但是和我相似的人喜欢的东西不一定是我最近感兴趣的东西（我之前写大数据，start很多大数据仓库，最近写IR，需要的事IR仓库），那么就需要在上面的基础上再根据我最近历史过滤一下



##### （1）基于内容推荐

```python
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
```

函数本质上是先读取相关用户的日志文件（就是日志模块记录的那些和用户信息带的那些），再根据用户的兴趣点和技术栈拼接成一个字符串，然后根据这个字符串去Elasticsearch中搜索，返回匹配的仓库。

**（2）协同过滤找寻相似用户**

需要用到两个辅助函数

```python
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
```

两个辅助函数分别用于计算两个列表的Jaccard相似度和找到最相似的用户，Jaccard相似度衡量两个集合的相似度，计算公式如下：
$$
J(A, B) = \frac{|A \cap B|}{|A \cup B|}
$$
而寻找最相似的用户的函数，本质上是计算当前用户和其他用户的相似度，然后按照相似度排序，返回相似度最高的几个用户。



协同过滤函数具体如下

```python
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
```

使用相关的辅助函数先得到n个和当前用户最相似的用户，然后根据这些用户的starred_repos（start的仓库）计算每个仓库的popularity（被多少用户start过），然后按照popularity排序，这样协同过滤结果前面的更可能被推荐。

协同过滤打破了人与人之间的信息壁垒，找到和用户需求相似的其他用户，看看他们都喜欢什么（start/fork了什么仓库）。

**（3）根据用户历史行为实时调整**

用到的辅助函数如下

```python
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
```
两个辅助函数分别用于获取仓库的主题和主要语言和获取用户最近搜索历史，这里的主题和主要语言是从Elasticsearch中获取的，需要编写一个query字典做匹配，而用户最近搜索历史是从用户日志文件中获取的。



最后的根据用户历史行为实时调整函数如下

```python
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
```

这个函数从强烈推荐和一般推荐两个方面来调整推荐列表，强烈推荐是指协同过滤得到的结果中，被超过一半相似用户star的仓库，且仓库主题在用户兴趣点中的仓库，这些仓库被认为是强烈推荐的，然后一般推荐是指协同过滤得到的结果中，根据协同过滤的popularity和最近访问主题的匹配度来计算得分，得分高的仓库被认为是一般推荐的，最后将强烈推荐和一般推荐结合起来，返回最终的推荐列表。


#### 7、前端交互

使用flask框架，后端通过自定义路由函数和前端交互

本质上是调用前面封装好的各种类的实例实现各种功能，需要使用GET POST等方法在前后端传递数据，同时对传来的数据进行处理，不过多赘述。详情见app/routes.py

#### 8、其他

有一些用于生成随机数据和测试数据的函数

```python
def prepareData(user):
    """
    用于生成测试个性化查询和推荐的数据
    """
    username = user.username
    if username == "user1":
        # 生成测试用户user1的数据
        root = os.getcwd()
        floder = "userLogs"
        testName = "user1_temp"
        logFile = os.path.join(root, floder, testName + ".json")
        if not os.path.exists(logFile):
            # 生成兴趣点记录,直接存储在session中
            session["user_intrests"] = searcher.generate_data("intrest", 10)
            # 生成点击记录，直接存储在session中
            session["user_clicks"] = searcher.generate_data("clickLog", 50)
            # 将搜索记录存盘
            with open(logFile, "w") as file:
                json.dump(
                    {
                        "user_intrests": session["user_intrests"],
                        "user_clicks": session["user_clicks"],
                    },
                    file,
                )
            print("目前登录用户user1,测试数据准备成功")
            return
        print("目前登录用户user1,已发现其测试数据，无需再次生成")
        with open(logFile, "r") as file:
            data = json.loads(file.read())
            session["user_intrests"] = data["user_intrests"]
            session["user_clicks"] = data["user_clicks"]
        return

    elif username == "user2":
        # 生成测试用户user2的数据
        root = os.getcwd()
        floder = "userLogs"
        testName = "user2_temp"
        logFile = os.path.join(root, floder, testName + ".json")
        if not os.path.exists(logFile):
            # 生成兴趣点记录,直接存储在session中
            session["user_intrests"] = searcher.generate_data("intrest", 10)
            # 生成点击记录，直接存储在session中
            session["user_clicks"] = searcher.generate_data("clickLog", 50)
            # 将搜索记录存盘
            with open(logFile, "w") as file:
                json.dump(
                    {
                        "user_intrests": session["user_intrests"],
                        "user_clicks": session["user_clicks"],
                    },
                    file,
                )
            print("目前登录用户user2,测试数据准备成功")
            return
        print("目前登录用户user2,已发现其测试数据，无需再次生成")
        with open(logFile, "r") as file:
            data = json.loads(file.read())
            session["user_intrests"] = data["user_intrests"]
            session["user_clicks"] = data["user_clicks"]
        return

```



## 附录

github仓库链接：[HuBocheng/search-engine](https://github.com/HuBocheng/search-engine)