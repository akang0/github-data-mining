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

# create repos, prs, collection
repos_col = db["repos"]
repos_pulls_col = db["repos_pulls"]

# connect to github
g = Github(args.github_api_key)

# get all the repos under the given org and upsert to the db.repos
org = g.get_organization(args.organization)
for repo in org.get_repos():
    repo_json = {
        "name": repo.name,
        "id": repo.id,
        "organization": repo.organization.name,
    }
    repo_json_set = {"$set": repo_json}
    print("upserting... ", repo_json)
    db["repos"].update_one(repo_json, repo_json_set, upsert=True)
    print("done upsert: ", repo_json)

    # get all the prs under the repo and upsert to the db.repos_pulls
    for pr in repo.get_pulls(state="all"):
        pr_json = {
            "repo_id": repo.id,
            "repo_name": repo.name,
            "name": pr.title,
            "state": pr.state,
            "created_at": pr.created_at.strftime("%Y-%m-%d"),
        }

        if pr.closed_at is not None:
            pr_json["closed_at"] = pr.closed_at.strftime("%Y-%m-%d")
            pr_json["days_to_close"] = (pr.closed_at - pr.created_at).days

        pr_json_set = {"$set": pr_json}
        print("upserting... ", pr_json)
        db["repos_pulls"].update_one(
            {"repo_name": repo.name, "repo_id": repo.id, "name": pr.title},
            pr_json_set,
            upsert=True,
        )
        print("done upsert: ", pr_json)
