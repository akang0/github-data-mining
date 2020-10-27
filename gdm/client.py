import argparse
from pymongo import MongoClient

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--database', type=str, required=True)
parser.add_argument('-c', '--collections', type=str, required=True)

args = parser.parse_args()
print("database:", args.database)
print("collections:", args.collections)

# connect to local mongo db
client = MongoClient()
db = client[args.database]

# print the given collection
if args.collections == "repos":
    for repo in db.repos.find():
        print(repo)
elif args.collections == "repos.pulls":
    for pull in db.repos.pulls.find():
        print(pull)
else:
    print("no such collection in db: ", args.collections)
    exit(1)

print(args.collections, "count:", db[args.collections].count_documents({}))
