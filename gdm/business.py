import argparse
from pymongo import MongoClient

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--database", type=str, required=True)

args = parser.parse_args()
print("database:", args.database)

# connect to local mongo db
client = MongoClient()
db = client[args.database]

# calculates the average age of pull requests
averageDays = list(
    db.repos_pulls.aggregate(
        [{"$group": {"_id": "$repo_id", "avgAge": {"$avg": "$days_to_close"}}}]
    )
)

for repo in db["repos"].find():
    for averageDay in averageDays:
        if averageDay["_id"] == repo["id"]:
            repo_json = {"avgPullAge": averageDay["avgAge"]}
            pr_repo_set = {"$set": repo_json}
            print("upserting... ", repo_json)
            db["repos"].update_one({"id": repo["id"]}, pr_repo_set, upsert=True)
            print("done upsert: ", repo_json)
