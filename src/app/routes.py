from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)  # 用于渲染 HTML 模板文件
from markupsafe import escape
from app import app  # 从 app 包导入 app 实例。这是在 app/__init__.py 文件中创建的 Flask 应用实例
import hashlib
import json
import markdown
import html2text
import os
from logMOD import UserActivityLogger  # 导入UserActivityLogger 类
from recommandMOD import HybridRecommenderSystem  # 导入 HybridRecommenderSystem 类


from userMOD import User  # 导入User 类
from searcherMOD import Searcher  # 导入Searcher 类

# 加载 JSON 文件
with open("data/myUsers.json") as f:
    users_data = json.load(f)

# 将 JSON 数据转换为 User 对象
users = {}
for username, user_info in users_data.items():
    users[username] = User(username, **user_info)

searcher = Searcher()


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


@app.route("/")
def index():
    # print("index")  # test point
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    user = users.get(username)
    if user and user.password_hash == hashlib.sha256(password.encode()).hexdigest():
        session["username"] = username
        prepareData(user)
        # search.set_username(username)
        return render_template("search.html")
    else:
        return redirect(url_for("index", login_failed=True))


# # test function
# @app.route("/link_clicked", methods=["POST"])
# def link_clicked():
#     session["counter"] = session.get("counter", 0) + 1
#     session.modified = True  # 告诉 Flask session 已被修改
#     clicked_link = request.json.get("link")
#     app.logger.info(f"链接 {clicked_link} 被点击了, 总点击次数: {session['counter']}")
#     return jsonify(success=True)


@app.route("/search", methods=["GET"])
def search():
    search_query = request.args.get("search_query")
    search_type = request.args.get("search_type")
    include_readme = request.args.get("include_readme", "no")
    sort_order = request.args.get("sort_order", "best_match")

    username = session.get("username")

    if username:
        logger = UserActivityLogger()
        logger.openLogFile(username)
        if search_type in ["repositories", "users", "codes"]:
            # 记录用户的搜索行为
            logger.log_search(username, search_query, search_type)

    # 根据用户选择的搜索类型调用不同的搜索方法
    if search_type == "repositories":
        """上面已经读取用户日志，用户日志信息就在logger中"""

        user_interests = session.get("user_intrests")
        user_clicks = session.get("user_clicks")
        print("user_interests", user_interests)  # test point
        print("user_clicks", user_clicks)
        print("sort_order", sort_order)
        print("include_readme", include_readme)
        print("search_query", search_query)

        # 将搜索类型信息写入总日志
        search_info = {
            "search_query": search_query,
            "search_type": search_type,
            "include_readme": include_readme,
            "sort_order": sort_order,
            "user_interests": user_interests,
            "user_clicks": user_clicks,
        }
        searcher.log_search(username, search_info)

        results = searcher.search_repositories(
            search_query, include_readme, sort_order, user_interests, user_clicks
        )
        """根据sort_order的值，看需不需要进行个性化排序"""
        if sort_order == "best_match":
            print("best_match opreated")

        # for hit in results["hits"]["hits"]:
        #     readme_md = hit["_source"]["readme"][:200]  # 截取前200个字符
        #     readme_html = markdown.markdown(readme_md)
        #     text_maker = html2text.HTML2Text()
        #     text_maker.ignore_links = False
        #     hit["_source"]["readme"] = text_maker.handle(readme_html)

        # for hit in results["hits"]["hits"]:
        #     print("hit", hit["_source"]["name"])

        # 检查快照是否存在
        for hit in results["hits"]["hits"]:
            repo_name = hit["_source"]["name"]
            # print("repo_name", repo_name.split("/")[1])  # test point
            snapshot_path = f"static/snapshot/{repo_name.split('/')[1]}.png"
            hit["_source"]["snapshot_exists"] = os.path.exists(snapshot_path)
            # print("snapshot_exists", hit["_source"]["snapshot_exists"]) # test point

        # 将搜索结果传递给渲染的模板
        # print("results", results["hits"]["total"])
        # for hit in results["hits"]["hits"]:
        #     print("hit", hit["_source"]["name"])
        logger.saveLogFile(username)
        return render_template("repos_results.html", results=results)

    elif search_type == "users":
        results = searcher.search_users(search_query)
        print("results", results["hits"]["total"])
        logger.saveLogFile(username)
        return render_template("users_results.html", results=results)  # 新的用户搜索结果页面

    elif search_type == "codes":
        results = searcher.search_codes(search_query)
        print("搜索结果共" + str(results["hits"]["total"]) + "条")
        for hit in results["hits"]["hits"]:
            url = hit["_source"]["url"]
            # print(url.split("/")[3] + "/" + url.split("/")[4])
            hit["_source"]["name/repos"] = url.split("/")[3] + "/" + url.split("/")[4]

            highlighted_fragments = hit.get("highlight", {}).get("content", [])
            # print("highlighted_fragments", highlighted_fragments)  # test point
            # 将每个片段转换为 HTML 安全的字符串
            hit["_source"]["highlighted"] = " ... ".join(
                escape(fragment) for fragment in highlighted_fragments
            )
        logger.saveLogFile(username)
        return render_template("codes_results.html", results=results)  # 新的代码搜索结果页面
    else:
        print("搜索类型错误")
        results = {}


@app.route("/log_click", methods=["POST"])
def log_click():
    print("log_click")  # test point
    clicked_link = request.json.get("link")
    username = session.get("username")
    print(f"username:{username},clicked_link:{clicked_link}")

    if username:
        logger = UserActivityLogger()
        logger.openLogFile(username)
        # 记录点击事件
        logger.log_web_click(username, clicked_link)
        logger.saveLogFile(username)

    return jsonify(success=True)


@app.route("/recommendations")
def recommendations():
    target_user = users["user2"]
    all_users = list(users.values())

    path = os.path.join(os.getcwd(), "data", "myUsers.json")
    recommender = HybridRecommenderSystem(path)
    # recommender.set_username(session.get("username"))

    personalized_data = recommender.recommend("user2", target_user, all_users)

    # 找到推荐的仓库URL然后查es得到response
    recommended_repos1 = personalized_data["final_recommendations"][
        "strong_recommendations"
    ]
    recommended_repos2 = personalized_data["final_recommendations"][
        "general_recommendations"
    ]
    recommended_reposAll = recommended_repos1
    recommended_reposAll.extend(recommended_repos2)
    for url in recommended_reposAll:
        query = {"query": {"match": {"url": url}}}  # 或者是仓库的ID或其他标识符
        response = searcher.es.search(index="repositories", body=query)

    personalized_data["repos_details"] = response
    for hit in personalized_data["repos_details"]["hits"]["hits"]:
        if hit["_source"]["url"] in recommended_repos1:
            hit["strongly"] = 1
        else:
            hit["strongly"] = 0
    personalized_data["maxStart"] = max(
        repo["popularity"] for repo in personalized_data["repo_popularity"]
    )
    print(personalized_data["maxStart"])
    # 使用个性化数据渲染推荐页面
    return render_template("recommendations.html", data=personalized_data)


# @app.route("/log_page_visit", methods=["POST"])
# def log_page_visit():
#     print("log_page_visit")  # test point
#     data = request.json
#     url = data.get("url")
#     stayDuration = data.get("stayDuration")
#     user_id = session.get("user_id")

#     if user_id:
#         logger = UserActivityLogger()
#         logger.openLogFile(user_id)
#         # 记录页面访问
#         logger.log_page_visit(user_id, url, stayDuration)
#         logger.saveLogFile(user_id)

#     return "", 204
