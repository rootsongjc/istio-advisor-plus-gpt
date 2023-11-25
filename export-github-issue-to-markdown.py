import argparse
import requests
import re

# 解析命令行参数
parser = argparse.ArgumentParser(description="Export GitHub issue to Markdown")
parser.add_argument("--url", help="GitHub Issue URL")
parser.add_argument("-f", "--output_file", help="Output file name (optional)")
args = parser.parse_args()

# 检查是否提供了输出文件名，如果未提供，则使用默认格式
if args.output_file is None and args.url:
    match = re.match(r"https://github\.com/([^/]+)/([^/]+)/issues/(\d+)", args.url)
    if match:
        issue_number = match.group(3)
        args.output_file = f"issue_{issue_number}.md"

# 提取仓库所有者和仓库名称
if args.url and re.match(r"https://github\.com/([^/]+)/([^/]+)/issues/(\d+)", args.url):
    match = re.match(r"https://github\.com/([^/]+)/([^/]+)/issues/(\d+)", args.url)
    owner = match.group(1)
    repo = match.group(2)
    issue_number = int(match.group(3))
    # 构建GitHub API URL
    issue_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"

    # 发送GET请求以获取Issue数据
    response = requests.get(issue_url, headers={"Accept": "application/vnd.github.v3+json"})

    # 检查响应是否成功
    if response.status_code == 200:
        issue_data = response.json()
        # 创建Markdown文档
        markdown_content = f"# {issue_data['title']}\n\n"
        markdown_content += f"{issue_data['body']}\n\n"

        # 获取评论数据
        comments_url = issue_data['comments_url']
        comments_response = requests.get(comments_url, headers={"Accept": "application/vnd.github.v3+json"})

        if comments_response.status_code == 200:
            comments_data = comments_response.json()
            for comment in comments_data:
                markdown_content += f"## Comment by {comment['user']['login']} on {comment['created_at']}\n"
                markdown_content += f"{comment['body']}\n\n"

            # 保存Markdown文档
            with open(args.output_file, "w", encoding="utf-8") as file:
                file.write(markdown_content)
            print(f"Markdown document saved as {args.output_file}")
        else:
            print("Failed to fetch comments data")
    else:
        print("Failed to fetch issue data")
else:
    print("Invalid GitHub Issue URL or missing --url argument")
