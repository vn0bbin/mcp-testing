import os
import re
import requests
import sys

GITHUB_TOKEN = os.environ.get("GH_TOKEN")
REPO = os.environ.get("GITHUB_REPOSITORY")
PR_NUMBER = os.environ.get("PR_NUMBER")
REVIEW_FILE = sys.argv[1] if len(sys.argv) > 1 else "mcp_review.txt"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Example flake8 output: /path/to/file.py:4:6: E225 missing whitespace around operator
flake8_re = re.compile(r"^(.*?):(\d+):(\d+): ([A-Z]\d+) (.*)$")

comments = []

with open(REVIEW_FILE) as f:
    for line in f:
        m = flake8_re.match(line)
        if m:
            file_path, line_num, col, code, msg = m.groups()
            # Only use the filename, not the temp path
            filename = os.environ.get("REVIEW_FILENAME", "test_file.py")
            comments.append({
                "path": filename,
                "line": int(line_num),
                "side": "RIGHT",
                "body": f"{code}: {msg}"
            })

if not comments:
    print("No inline comments to post.")
    sys.exit(0)

# Create a review with comments
url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}/reviews"
review = {
    "body": "Automated MCP inline review.",
    "event": "COMMENT",
    "comments": comments
}
resp = requests.post(url, headers=headers, json=review)
print(resp.status_code, resp.text)
