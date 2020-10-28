import argparse
from pymongo import MongoClient

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--database', type=str, required=True)

args = parser.parse_args()
print("database:", args.database)

# connect to local mongo db
client = MongoClient()
db = client[args.database]


for pull in db.repos.pulls.find({"days_to_close": 0}):
    print(pull)

for pull in db.repos.pulls.find({"days_to_close": 1}):
    print(pull)

for pull in db.repos.pulls.find({"days_to_close": 2}):
    print(pull)
