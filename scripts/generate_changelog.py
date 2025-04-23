"""
generate_changelog.py

Semi-automated tool for logging logic and product changes, used to:
- Capture git commit, branch, and sprint information
- Prompt user for impact summary and affected products
- Write changes to `sources_apcd.change_log_all_hist` and generate a markdown changelog

"""


from datetime import date, timedelta
import subprocess
# from vh_core import db_connection
# from vh_core.db_connection import DB_CONNECT_TYPE
import pandas as pd
import re
import psycopg2

conn = psycopg2.connect(
    host='ec2-18-223-194-252.us-east-2.compute.amazonaws.com',
    port="5432",
    user='airflow',
    password='G7x@pV9zQ1#t',
    dbname="apcd"
)


def get_sprint_id(entry_date: date) -> str:
    first_sprint_start = date(2025, 1, 6)  # Sv5.1.1

    if entry_date < first_sprint_start:
        return "(Date before first sprint)"

    # Determine the quarter and quarter start date
    year = entry_date.year
    month = entry_date.month
    quarter = (month - 1) // 3 + 1
    quarter_start = date(year, 3 * (quarter - 1) + 1, 1)

    # Adjust to the first Monday on or after the quarter start
    offset = (7 - quarter_start.weekday()) % 7
    first_sprint_start_in_quarter = quarter_start + timedelta(days=offset)

    if entry_date < first_sprint_start_in_quarter:
        return "(Date before first sprint in quarter)"

    # Sprint index within the quarter
    sprint_index = (entry_date - first_sprint_start_in_quarter).days // 14
    sprint_number = sprint_index + 1

    year_suffix = str(year)[-1]
    return f"Sv{year_suffix}.{quarter}.{sprint_number}"


def get_git_info(path="."):
    try:
        branch = (
            subprocess.check_output(
                ["git", "-C", path, "rev-parse", "--abbrev-ref", "HEAD"]
            )
            .decode()
            .strip()
        )
        commit = (
            subprocess.check_output(["git", "-C", path, "rev-parse", "HEAD"])
            .decode()
            .strip()
        )
        return branch, commit
    except subprocess.CalledProcessError:
        return None, None


def get_github_issue_url(branch: str, repo: str = "vh_core") -> str:
    match = re.match(r"(\d+)-", branch)
    if match:
        issue_num = match.group(1)
        return f"https://github.com/validatehealth/{repo}/issues/{issue_num}"
    return ""


def build_insert_sql(table: str, values: dict) -> str:
    create_table = f"""
    CREATE TABLE IF NOT EXISTS {table} (
        branch TEXT,
        git_commit_hash TEXT,
        summary_changes TEXT,
        impact_summary TEXT,
        impact_project TEXT,
        entry_date DATE,
        sprint_number TEXT,
        github_issue_url TEXT,
        logged_by TEXT
    );
    """

    insert = f"""
    INSERT INTO {table} (
        branch,
        git_commit_hash,
        summary_changes,
        impact_summary,
        impact_project,
        entry_date,
        sprint_number,
        github_issue_url,
        logged_by
    )
    VALUES (
        '{values['branch']}',
        '{values['git_commit_hash']}',
        '{values['summary_changes']}',
        '{values['impact_summary']}',
        '{values['impact_project']}',
        '{values['entry_date']}',
        '{values['sprint_number']}',
        '{values['github_issue_url']}',
        '{values['logged_by']}'
    );
    """

    return create_table + "\n" + insert


def get_git_user_name() -> str:
    try:
        return (
            subprocess.check_output(["git", "config", "user.name"])
            .decode()
            .strip()
        )
    except subprocess.CalledProcessError:
        return ""


def confirm_product_choice(product_list):
    while True:
        print("\nSelect impacted product:")
        for idx, product in enumerate(product_list, 1):
            print(f"  {idx}: {product}")
        try:
            selection = int(input("Enter product number: "))
            product = product_list[selection - 1]
            confirm = (
                input(f"You selected: {product}. Is that correct? (y/n): ")
                .strip()
                .lower()
            )
            if confirm == "y":
                return product
        except (ValueError, IndexError):
            print("Invalid input. Please select a valid number.")


def merge_change_log_md(
    output_path: str = "product_changelog.md",
    table_name: str = "sources_apcd.change_log_all_hist",
) -> None:
    """
    Reads change log entries from the given table and generates a grouped markdown changelog file.
    """

    # Connect to the database
    conn = psycopg2.connect(
        host='ec2-18-223-194-252.us-east-2.compute.amazonaws.com',
        port="5432",
        user='airflow',
        password='G7x@pV9zQ1#t',
        dbname="apcd"
    )

    # Query the change log table
    df = db.execute_into_df(
        f"""
        SELECT
            sprint_number,
            entry_date,
            summary_changes,
            impact_summary,
            impact_project
        FROM {table_name}
        ORDER BY sprint_number DESC, impact_project ASC, entry_date DESC
        """
    )

    if df.empty:
        print("⚠️ No records found in change log table.")
        return

    df["entry_date"] = pd.to_datetime(df["entry_date"])

    # Build the markdown content
    markdown_output = "# Product Change Log\n"
    markdown_output += "**Commit hash and branch information stored in `sources_apcd.change_log_all_hist`**\n\n"

    for sprint, sprint_df in df.groupby("sprint_number", sort=False):
        markdown_output += f"# {sprint}\n\n"

        # Group within sprint by project, alphabetically
        for project, proj_df in sprint_df.groupby("impact_project", sort=True):
            markdown_output += "___\n\n"
            markdown_output += f"### {project}\n\n"

            # Sort most recent to oldest
            proj_df = proj_df.sort_values(by="entry_date", ascending=False)

            # Summary of Changes
            markdown_output += "**Summary of Changes**\n"
            for _, row in proj_df.iterrows():
                date_str = row["entry_date"].strftime("%B %d, %Y")
                markdown_output += f"- {row['summary_changes']} ({date_str})\n"
            markdown_output += "\n"

            # Impact
            markdown_output += "**Impact**\n"
            for _, row in proj_df.iterrows():
                date_str = row["entry_date"].strftime("%B %d, %Y")
                markdown_output += f"- {row['impact_summary']} ({date_str})\n"
            markdown_output += "\n"

        markdown_output += "___\n\n"

    with open(output_path, "w") as f:
        f.write(markdown_output.strip())

    print(f"✅ Markdown changelog generated: {output_path}")


def auto_git_commit_push(
    file_path: str, commit_message: str = "Update Saturn changelog"
):
    import subprocess
    import time

    max_attempts = 2
    for attempt in range(1, max_attempts + 1):
        try:
            branch = (
                subprocess.check_output(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"]
                )
                .decode()
                .strip()
            )

            print(f"🌀 Attempt {attempt}: staging and committing...")
            subprocess.check_call(["git", "add", file_path])
            subprocess.check_call(["git", "commit", "-m", commit_message])
            subprocess.check_call(["git", "push", "origin", branch])

            print(f"✅ Changelog committed and pushed to origin/{branch}")
            return  # success, exit function

        except subprocess.CalledProcessError as e:
            print(f"⚠️ Git command failed (attempt {attempt}): {e}")

            if attempt == max_attempts:
                print("❌ Final commit attempt failed. Please fix manually.")
                return

            print("🔁 Re-adding file in case pre-commit hooks modified it...")
            time.sleep(1)  # short delay for clarity/log spacing


def prompt_for_branch_and_commit() -> tuple[str, str]:
    while True:
        print("To get the branch name:  git rev-parse --abbrev-ref HEAD")
        branch = input("Enter branch name: ").strip()

        # Branch name validation
        if not branch:
            print("❌ Branch name is required.")
            continue
        if " " in branch:
            print("❌ Branch name cannot contain spaces.")
            continue
        if any(
            sub in branch
            for sub in ["..", "~", "^", ":", "?", "*", "[", "@{", "\\"]
        ):
            print("❌ Branch name contains invalid characters.")
            continue
        if (
            branch.startswith("-")
            or branch.startswith("/")
            or branch.endswith(".lock")
        ):
            print(
                "❌ Branch name cannot start with '-' or '/' or end with '.lock'."
            )
            continue

        print("\nTo get the current git commit hash for another repo:")
        print("Run:  git rev-parse HEAD")
        commit = input("Enter commit hash: ").strip()

        # Commit hash validation
        if not commit:
            print("❌ Commit hash is required.")
            continue
        if not re.fullmatch(r"[0-9a-f]{7,40}", commit):
            print(
                "❌ Commit hash must be a 7–40 character lowercase hex string (e.g., 'abc1234')."
            )
            continue

        return branch, commit


def prompt_for_repo_name(default: str = "vh_core") -> str:
    valid_repos = {"vh_core", "vldt_vrdc", "bricks_core"}
    while True:
        repo = input(
            f"Which repo was the change made in? ({', '.join(valid_repos)}): "
        ).strip()
        if not repo:
            return default
        if repo in valid_repos:
            return repo
        print("❌ Invalid repo. Please enter one of:", ", ".join(valid_repos))


def prompt_for_text_input(prompt_msg: str) -> str:
    while True:
        text = input(prompt_msg).strip()
        if text:
            return text
        print("❌ Input cannot be empty.")


def resolve_git_info_and_repo() -> tuple[str, str, str]:
    use_current = (
        input("Use current branch and commit from this repo? (y/n): ")
        .strip()
        .lower()
    )

    if use_current == "y":
        branch, commit = get_git_info()
        if branch and commit:
            return branch, commit, "vh_core"
        print("⚠️ Could not retrieve Git info. Falling back to manual entry.")

    # Ask for repo first if not using current
    repo_name = prompt_for_repo_name(default="vh_core")
    branch, commit = prompt_for_branch_and_commit()
    return branch, commit, repo_name


def preview_log_entry(values: dict) -> bool:
    print("\n📋 You are about to log the following change:\n")
    print(f"- 🧠 Product:         {values['impact_project']}")
    print(f"- 📝 Summary:         {values['summary_changes']}")
    print(f"- 💥 Impact:          {values['impact_summary']}")
    print(f"- 🌿 Branch:          {values['branch']}")
    print(f"- 🔗 Commit Hash:     {values['git_commit_hash']}")
    print(f"- 🏷️  Sprint:          {values['sprint_number']}")
    print(f"- 📅 Entry Date:      {values['entry_date']}")
    print(
        f"- 🔗 GitHub Issue:    {values['github_issue_url'] or '(None found)'}"
    )
    print(f"- 🙋 Logged By:       {values['logged_by']}")

    while True:
        confirm = (
            input("\n✅ Proceed with logging this entry? (y/n): ")
            .strip()
            .lower()
        )
        if confirm == "y":
            return True
        elif confirm == "n":
            print("❌ Cancelled. No changes were logged.")
            return False
        else:
            print("Please enter 'y' or 'n'.")


def resolve_entry_date() -> date:
    """
    Prompt the user for an optional override of the current entry date.
    Returns a valid `datetime.date` object.
    """
    today = date.today()
    use_custom = (
        input(f"Log with today’s date ({today})? (y/n): ").strip().lower()
    )

    if use_custom == "n":
        while True:
            user_input = input("Enter the entry date (YYYY-MM-DD): ").strip()
            try:
                custom_date = date.fromisoformat(user_input)
                return custom_date
            except ValueError:
                print("❌ Invalid format. Please use YYYY-MM-DD.")
    return today


def main():
    entry_date = resolve_entry_date()
    sprint_id = get_sprint_id(entry_date)
    sprint_id = get_sprint_id(entry_date)
    repo_name = "vh_core"

    branch, commit, repo_name = resolve_git_info_and_repo()
    github_issue_url = get_github_issue_url(branch, repo_name)

    summary = prompt_for_text_input("Enter summary of changes: ")
    impact = prompt_for_text_input("Enter impact summary: ")

    distinct_products = db.execute_into_df(
        sql_str="""
                    SELECT DISTINCT product FROM sources_apcd.deliv_index
                    where status not in ('Deprecated', 'Not Ready')
                    and product not in ('TBD'
                        , 'Vanessa: Attribution'
                        , 'SME-only'
                        , 'Saturn+Sco'
                        ,'SysAdmin'
                        ,'Atom'
                        ,'Verdi Hercules'
                        ,'Verdi Pirelli'
                        ,'Ad Hoc'
                        ,' Curif (Change)')
                    and product is not null
                    ORDER BY product
                """
    )

    manual_products = ["Scrappy", "Infrastructure", "Hercules", "Curif"]
    raw_product_list = sorted(
        distinct_products["product"].dropna().unique().tolist()
        + manual_products
    )
    raw_product_list = list(set(raw_product_list))
    product_list = sorted([p for p in raw_product_list if p != "Other"]) + [
        "Other"
    ]
    project = confirm_product_choice(product_list)

    # get username
    default_user = get_git_user_name() or "Unknown"

    values = {
        "branch": branch,
        "git_commit_hash": commit,
        "summary_changes": summary,
        "impact_summary": impact,
        "impact_project": project,
        "entry_date": entry_date.isoformat(),
        "sprint_number": sprint_id,
        "github_issue_url": github_issue_url,
        "logged_by": default_user,
    }

    if not preview_log_entry(values):
        return

    sql = build_insert_sql("sources_apcd.change_log_all_hist", values)
    db.execute(sql_str=sql)

    print(
        "\n✅ Entry successfully inserted into `sources_apcd.change_log_all_hist`."
    )
    print(f"Branch: {branch}")
    print(f"Commit: {commit}")
    print(f"Sprint: {sprint_id}")
    print(f"Project: {project}")

    merge_change_log_md()
    auto_git_commit_push("product_changelog.md")


if __name__ == "__main__":
    main()
