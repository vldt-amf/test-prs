import sys
import os
import re
from datetime import date

# hi! hello! hey there! one more! one one more! one one one. another hi. another another hi. another hihihi. hi. hi. hi.

from scripts.generate_changelog import (
    get_sprint_id,
    # build_insert_sql,
    get_github_issue_url,
    # merge_change_log_md,
    # auto_git_commit_push,
)
# from vh_core import db_connection
# from vh_core.db_connection import DB_CONNECT_TYPE


pr_body = os.environ.get("PR_BODY", "")
branch = os.environ.get("PR_BRANCH", "")
repo = os.environ.get("PR_REPO", "")
author = os.environ.get("PR_AUTHOR", "github-action")
commit = os.environ.get("PR_COMMIT", "")
entry_date = date.today()
sprint_number = get_sprint_id(entry_date)
github_issue_url = get_github_issue_url(branch, repo)


def extract(tag: str) -> str:
    match = re.search(
        rf"<!-- {tag}: Start here -->(.*?)##", pr_body + "##", re.DOTALL
    )
    return match.group(1).strip() if match else ""


summary = extract("summary_changes")
impact = extract("impact_summary")
products = extract("impact_project")

if not (summary and impact and products):
    print("One or more required fields are empty — skipping changelog log.")
    sys.exit(0)


values = {
    "branch": branch,
    "master-branch": pr_body, # this one is new
    "repo": repo, #this is also new
    "git_commit_hash": commit,
    "summary_changes": summary,
    "impact_summary": impact,
    "impact_project": products,
    "entry_date": entry_date.isoformat(),
    "sprint_number": sprint_number,
    "github_issue_url": github_issue_url,
    "logged_by": author,
}

print(values)
