import requests
import sys
import subprocess
import json
import os
import dotenv

dotenv.load_dotenv("/root/integrity-preprocessor/browsertrix/.env")
admin_user = os.environ.get("SUPERUSER_EMAIL")
admin_password = os.environ.get("SUPERUSER_PASSWORD")
config_dir = os.environ.get("CONFIG_FILE")

BROWSERTRIX_CREDENTIALS = os.environ.get("BROWSERTRIX_CREDENTIALS")


config_path = "/root/.integrity/"
base_url = "/mnt/integrity_store/starling/internal"

# def get_users():
#    cli = "kubectl exec -it local-mongo-0 -- /usr/bin/mongosh -u root -p example --eval 'use browsertrixcloud' --eval 'EJSON.stringify(db.users.find().toArray(),null,2, { relaxed: false })' --quiet"
#    r=subprocess.check_output(cli, shell=True, text=True)
#    y=r.split("\n")
#    y[0]="["
#    r="\n".join(y)
#    a=json.loads(r)
#    return a


def get_token_bypass(email, password, server):
    # AUTH
    auth = {"username": email, "password": password}
    URL = f"https://{server}/api/auth/jwt/login"
    access_token = ""
    resp = requests.post(URL, data=auth)
    response_json = resp.json()
    if "access_token" not in response_json:
        raise Exception("Access Token Failed")
    access_token = response_json["access_token"]

    return {"Authorization": "Bearer " + access_token}


# password="PASSW0RD!"
if os.path.exists(BROWSERTRIX_CREDENTIALS):
    with open(BROWSERTRIX_CREDENTIALS, "r") as f:
        SERVERS = json.load(f)


def get_token(server):
    email = SERVERS[server]["login"]
    password = SERVERS[server]["password"]
    if "headers" not in SERVERS[server]:
        SERVERS[server]["headers"] = ""
    if SERVERS[server]["headers"] == "":
        SERVERS[server]["headers"] = get_token_bypass(email, password, server)
    return SERVERS[server]["headers"]


def get_me(server):
    header = get_token(server)
    URL = f"https://{server}/api/users/me"
    r = requests.get(URL, headers=header)
    return r.json()


def change_password(userid, password, server):
    header = get_token(server)
    URL = f"https://{server}/api/users/{userid}"
    d = {"password": password}
    r = requests.patch(URL, headers=header, json=d)
    return r.json()


def create_org(org_name, server):
    header = get_token(server)
    URL = f"https://{server}/api/orgs/create"
    d = {"name": org_name}
    r = requests.post(URL, headers=header, json=d)
    return r.json()


def get_org(org_name, server):
    header = get_token(server)
    URL = f"https://{server}/api/orgs"
    d = {"name": org_name}
    r = requests.get(URL, headers=header)
    res = r.json()
    for o in res["items"]:
        if o["name"] == org_name:
            return o


def create_user(email, name, oid, server):
    header = get_token(server)
    URL = f"https://{server}/api/orgs/{oid}/add-user"
    d = {
        "email": email,
        "role": 100,
        "password": "test123",
        "name": name
    }
    r = requests.post(URL, headers=header, json=d)
    return r.json()


def invite_user_to_org(email, oid, server):
    header = get_token(server)
    URL = f"https://{server}/api/orgs/{oid}/invite"
    d = {
        "email": email,
        "role": 100
    }
    r = requests.post(URL, headers=header, json=d)
    return r.json()


def get_invites(oid, server):
    header = get_token(server)
    URL = f"https://{server}/api/orgs/{oid}/invites"
    r = requests.get(URL, headers=header)
    return r.json()


# Change super user password
email = "admin@example.com"
password = "testing123"

# password="PASSW0RD!"
# me=get_me(header)
# change_password(header,me['id'],"testing123")

# Create Strling Org
# print(create_org(header,"Starling Lab"))

data = {}

with open(f"{config_path}preprocessor-browsertrix-collections.json", "r") as f:
    data = json.load(f)

result = {"collections": {}}
for item_data in data:
    server = item_data["server"]
    archive_name = item_data["orgID"] + "_" + item_data["collectionID"]
    if "suffix" in item_data:
        archive_name = archive_name + "_" + item_data['suffix']
    aid = ""
    btrx_org = get_org(archive_name, server)
    if btrx_org is None:
        print(f"Creating {archive_name}")
        res = create_org(archive_name, server)
#        invite_user_to_org(header,"integrity@starlinglab.org",org["id"])
        btrx_org = get_org(archive_name, server)
    author = None
    if "author" in item_data:
        author = item_data['author']
    col = item_data["collectionID"]
    org = item_data["orgID"]
    orgid = btrx_org["id"]
    print(item_data)
    result["collections"][orgid] = {
        "collectionID": col,
        "organizationID":org,
        "target_path": f"{base_url}/{org}/{col}/",
        "author": author,
        "server": server
    }

#    print(get_invites(header,org["id"]))
    # print(archive_name)
print(config_dir)
f = open(config_dir, 'w')
json.dump(result, f, indent=2)
