import subprocess
import time


def open_service():
    # Elasticsearch服务启动命令
    es_command = "D:\\codeing\\pycoding\\IR\\elasticsearch_tools\\elasticsearch-5.6.8\\bin\\elasticsearch"

    # Elasticsearch Head可视化服务启动命令
    es_head_command = "cd /d D:\\codeing\\pycoding\\IR\\elasticsearch_tools\\elasticsearch-head-master && npm run start"

    # 启动Elasticsearch服务
    subprocess.Popen(["start", "cmd", "/k", es_command], shell=True)

    # 等候一段时间等待Elasticsearch启动
    time.sleep(15)

    # 启动Elasticsearch Head可视化服务
    subprocess.Popen(["start", "cmd", "/k", es_head_command], shell=True)
    time.sleep(5)
    return


if __name__ == "__main__":
    open_service()
