import argparse
from pymongo import MongoClient

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--database", type=str, required=True)

args = parser.parse_args()
print("database:", args.database)

# connect to local mongo db
client = MongoClient()
db = client[args.database]

# calculates the average days to close for pull requests per repo
avgDaysToClose = list(
    db.repos_pulls.aggregate(
        [{"$group": {"_id": "$repoId", "avgDaysToClose": {"$avg": "$daysToClose"}}}]
    )
)

for repo in db["repos"].find():
    for averageDay in avgDaysToClose:
        if averageDay["_id"] == repo["id"]:
            repo_json = {"avgPullDaysToClose": averageDay["avgDaysToClose"]}
            pr_repo_set = {"$set": repo_json}
            print("upserting... ", repo_json)
            db["repos"].update_one({"id": repo["id"]}, pr_repo_set, upsert=True)
            print("done upsert: ", repo_json)

# calculates the average age for pull requests per repo
avgAge = list(
    db.repos_pulls.aggregate(
        [{"$group": {"_id": "$repoId", "avgAge": {"$avg": "$age"}}}]
    )
)

for repo in db["repos"].find():
    for aAge in avgAge:
        if aAge["_id"] == repo["id"]:
            repo_json = {"avgAge": aAge["avgAge"]}
            pr_repo_set = {"$set": repo_json}
            print("upserting... ", repo_json)
            db["repos"].update_one({"id": repo["id"]}, pr_repo_set, upsert=True)
            print("done upsert: ", repo_json)

# Sort out labels of issue from github raw data
qe_member = ["quchangl-github", "drkho", "thuyn-581", "laisongls", "akang0", "dhrpatel4", "evelinec"]
for issue in db["repos_issues"].find():
    labels = issue["labels"]
    labelsArray = labels.split(',')
    # Add bug label
    if 'bug' in labelsArray:
        issue["isBug"] = "True"
    # Add squad label
    if any('squad' in s for s in labelsArray):
        squadMatching = [s for s in labelsArray if 'squad' in s]
        if len(squadMatching) == 1:
            issue["squad"] = squadMatching[0]
    # Add QE created label
    creator = issue["createdBy"]
    if creator in qe_member:
        issue["QEcreated"] = "QE"
    else:
        issue["QEcreated"] = "Non-QE"
    # Add priority label
    if 'blocker (P0)' in labelsArray:
        issue["priority"] = 'Priority/P0'
    elif any('Priority' in s for s in labelsArray):
        priorityMatching = [s for s in labelsArray if 'Priority' in s]
        issue["priority"] = priorityMatching[0]
    # Update DB
    issue_set = {"$set": issue}
    print("upserting... ", issue)
    db["repos_issues"].update_one(
        {"id": issue["id"]},
        issue_set,
        upsert=True,
    )
    print("done upsert: ", issue)