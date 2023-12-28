from datetime import datetime
from typing import List, Dict, Tuple
import os
import json


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


if __name__ == "__main__":  # 测试类
    # Example Usage
    logger = UserActivityLogger()
    logger.openLogFile("user123")
    logger.log_search("user123", "Python tutorials")
    logger.log_web_visit("user123", "https://www.example.com")

    # Get user search and visit history
    search_history = logger.get_user_search_history("user123")
    visit_history = logger.get_user_web_visit_history("user123")
