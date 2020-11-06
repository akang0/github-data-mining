# github-data-mining

Data mining on GitHub

# Prerequisites

- https://docs.mongodb.com/manual/administration/install-community/
- https://www.python.org/downloads/
- https://github.com/PyGithub/PyGithub
- https://api.mongodb.com/python/current/installation.html

# Getting started

```
$ python gdm/mine.py -d _database_name_ -o _github_organization_ -g _github_api_key_
$ python gdm/client.py -d _database_name_ -c repos
$ python gdm/client.py -d _database_name_ -c repos.pulls
```

Run business.py to add additional calculations, which includes

- average age for all pull requests

```
$ python gdm/business.py -d _database_name_
```
