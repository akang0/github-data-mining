import argparse
from pymongo import MongoClient
from github import Github

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--database", type=str, required=True)
parser.add_argument("-o", "--organization", type=str, required=True)
parser.add_argument("-g", "--github-api-key", type=str, required=True)

args = parser.parse_args()
print("database:", args.database)
print("organization:", args.organization)
print("github-api-key: *************")

# connect to local mongo and create github db
client = MongoClient()
db = client[args.database]

# create repos, pulls, and issues collections
repos_col = db["repos"]
repos_pulls_col = db["repos_pulls"]
repos_issues_col = db["repos_issues"]

# connect to github
g = Github(args.github_api_key)

# get all the repos under the given org and upsert to the db.repos
org = g.get_organization(args.organization)
for repo in org.get_repos():
    repo_json = {
        "id": repo.id,
        "name": repo.name,
        "organization": repo.organization.name,
    }
    if repo.private:
        repo_json["type"] = "private"
    else:
        repo_json["type"] = "public"

    repo_json_set = {"$set": repo_json}
    print("upserting... ", repo_json)
    db["repos"].update_one({"id": repo.id}, repo_json_set, upsert=True)
    print("done upsert: ", repo_json)

    # get all the prs under the repo and upsert to the db.repos_pulls
    for pr in repo.get_pulls(state="all"):
        pr_json = {
            "repo_id": repo.id,
            "repo_name": repo.name,
            "id": pr.id,
            "title": pr.title,
            "state": pr.state,
            "created_at": pr.created_at.strftime("%Y-%m-%d"),
        }

        if pr.closed_at is not None:
            pr_json["closed_at"] = pr.closed_at.strftime("%Y-%m-%d")
            pr_json["days_to_close"] = (pr.closed_at - pr.created_at).days

        pr_json_set = {"$set": pr_json}
        print("upserting... ", pr_json)
        db["repos_pulls"].update_one(
            {"id": pr.id},
            pr_json_set,
            upsert=True,
        )
        print("done upsert: ", pr_json)

    # get all the issues under the repo and upsert to the db.repos_issues
    for issue in repo.get_issues(state="all"):
        issue_json = {
            "repo_id": repo.id,
            "repo_name": repo.name,
            "id": issue.id,
            "number": issue.number,
            "title": issue.title,
            "body": issue.body,
            "state": issue.state,
            "created_at": issue.created_at.strftime("%Y-%m-%d"),
        }

        if issue.closed_at is not None:
            issue_json["closed_at"] = issue.closed_at.strftime("%Y-%m-%d")
            issue_json["days_to_close"] = (issue.closed_at - issue.created_at).days

        issue_set = {"$set": issue_json}
        print("upserting... ", issue_json)
        db["repos_issues"].update_one(
            {"id": issue.id},
            issue_set,
            upsert=True,
        )
        print("done upsert: ", issue_json)
