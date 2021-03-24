import argparse
from pymongo import MongoClient
from github import Github
from datetime import datetime

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

today = datetime.today()

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
    print("upserting.... ", repo_json)
    db["repos"].update_one({"id": repo.id}, repo_json_set, upsert=True)
    print("done upsert: ", repo_json)

    if repo.name=="backlog":
        # get all the prs under the repo and upsert to the db.repos_pulls
        for pr in repo.get_pulls(state="all"):
            pr_json = {
                "repoId": repo.id,
                "repoName": repo.name,
                "id": pr.id,
                "title": pr.title,
                "state": pr.state,
                "createdAt": pr.created_at.strftime("%Y-%m-%d"),
            }

            if pr.closed_at is None:
                age = (today - pr.created_at).days
                if age < 0:
                    age = 0
                pr_json["age"] = age
            else:
                pr_json["closedAt"] = pr.closed_at.strftime("%Y-%m-%d")
                daysToClose = (pr.closed_at - pr.created_at).days
                if daysToClose < 0:
                    daysToClose = 0
                pr_json["daysToClose"] = daysToClose
                pr_json["age"] = pr_json["daysToClose"]

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
            labels = ""
            milestone = None
            for label in issue.get_labels():
                labels = labels + ","
                labels = labels + label.name
            if issue.milestone:
                milestone = issue.milestone.title
            issue_json = {
                "repoId": repo.id,
                "repoName": repo.name,
                "id": issue.id,
                "number": issue.number,
                "createdBy": issue.user.login,
                "title": issue.title,
                "body": issue.body,
                "state": issue.state,
                "createdAt": issue.created_at.strftime("%Y-%m-%d"),
                "labels": labels,
                "milestone": milestone
            }

            if issue.closed_at is not None:
                issue_json["closedAt"] = issue.closed_at.strftime("%Y-%m-%d")
                issue_json["daysToClose"] = (issue.closed_at - issue.created_at).days

            issue_set = {"$set": issue_json}
            print("upserting... ", issue_json)
            db["repos_issues"].update_one(
                {"id": issue.id},
                issue_set,
                upsert=True,
            )
            print("done upsert: ", issue_json)
