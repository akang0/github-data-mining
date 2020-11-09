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
