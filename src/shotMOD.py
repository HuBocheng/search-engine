from github import Github
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from PIL import Image
from io import BytesIO
import time


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


# 使用示例
# with open("data/access.txt", "r") as file:
#     github_token = file.readline()
# repo_name = "HuBocheng/Fake-News-Detection"  # 替换为目标 GitHub 仓库的名称
# save_path = "static/snapshot2.png"  # 快照保存路径

# snapshot = GithubRepoSnapshot(github_token)
# repo_url = snapshot.get_repo_url(repo_name)


# snapshot.capture_full_page_snapshot(repo_url, save_path)
# snapshot.close()

with open("data/access.txt", "r") as file:
    github_token = file.readline()
snapshot = GithubRepoSnapshot(github_token)
with open("data/top10000Repos.txt", "r") as file:
    for i, line in enumerate(file):
        if i % 10 == 0:
            print("快照第", i, "个仓库成功")
        if i > 1000:
            break
        save_path = "static/snapshot/" + line.split(",")[1] + ".png"  # 快照保存路径
        repo_url = line.split(",")[2]
        snapshot.capture_full_page_snapshot(repo_url, save_path)
        print("save " + line.split(",")[1] + " success")
    snapshot.close()
