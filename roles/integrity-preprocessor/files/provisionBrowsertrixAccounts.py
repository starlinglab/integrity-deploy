#!/usr/bin/python3
import json
import requests
import sys
import subprocess
import dotenv
import os

dotenv.load_dotenv("/root/browsertrix/configs/config.env")
admin_user=os.environ.get("SUPERUSER_EMAIL")
admin_password=os.environ.get("SUPERUSER_PASSWORD")

mongo_user = os.environ.get("MONGO_INITDB_ROOT_USERNAME")
mongo_password=os.environ.get("MONGO_INITDB_ROOT_PASSWORD")

dotenv.load_dotenv("/root/integrity-preprocessor/browsertrix/.env")
master_user=os.environ.get("BROWSERTRIX_USERNAME")
master_password=os.environ.get("BROWSERTRIX_PASSWORD")
config_dir =  os.environ.get("CONFIG_FILE")

base_url = "/mnt/integrity_store/starling/internal"
data = [
    {
    "collectionID": "bosnia-investigation-remote",
    "orgID": "starling-lab"
    },
    {
    "collectionID": "tracked-series-web-archives",
    "orgID": "associated-press"
    }
]


result = {
    "collections": {
    }
}



def get_token(username,password):
    URL = "http://127.0.0.1:9871/api/auth/jwt/login"
    auth = {"username": username, "password": password}
    resp = requests.post(URL, data=auth)
    response_json = resp.json()
    if "access_token" in response_json:
        access_token = response_json["access_token"]
        headers = {"Authorization": "Bearer " + access_token}
        return headers
def create_account(email,password,archive_name):
    URL = "http://127.0.0.1:9871/api/auth/register"
    body = {
        "email": email,
        "password": password,
        "name": archive_name,
        "newArchive": True,
        "newArchiveName": archive_name
    }
    response = requests.post(URL, json=body)

    headers =  get_token(email,password)
    # get AID
    URL = "http://127.0.0.1:9871/api/archives"
    r = requests.get(URL, headers=headers)
    res = r.json()
    aid = res["archives"][0]["id"]
    return aid

def invite_user(email,password,aid):
    headers =  get_token(email,password)
    d={ "email": "tools@starlinglab.org", "role":40 }
    URL = f"http://127.0.0.1:9871/api/archives/{aid}/invite/"
    r = requests.post(URL, headers=headers, json=d)
    res = r.json()
    # Process Invite
    ID = get_users()
    for a in ID:
        if "id" in a:
            if a['email'] == "tools@starlinglab.org":
                for token in a['invites']:
                    URL = f"http://127.0.0.1:9871/api/archives/invite-accept/{token}"
                    r = requests.post(URL, headers=master_token)
    return aid

def get_users():
    cli = f"mongo --eval \"db.users.find()\" -u {mongo_user} -p {mongo_password} browsertrixcloud"

    cli = "docker exec -it browsertrix-mongo-1 sh -c \"echo 'use browsertrixcloud\\ndb.users.find()' | mongo -u root -p example --quiet\""
    r=subprocess.check_output(cli, shell=True, text=True)
    r = r.replace("ObjectId(","")
    r = r.replace("UUID(","")
    r = r.replace("ISODate(","")
    r = r.replace(")","")
    r2=r.split("\n")
    r2.pop(0)  
    r3=",".join(r2)
    r3 = "[" + r3 + "{} ]"

    a=json.loads(r3)
    return a



admin_token=get_token(admin_user,admin_password)
master_token=get_token(master_user,master_password)


URL = "http://127.0.0.1:9871/api/archives"
response = requests.get(URL,headers=admin_token)
archives = response.json()

for item_data in data:
    archive_name = item_data["orgID"] + "-" +  item_data["collectionID"]
    aid = ""
    for a in archives['archives']:
        if a['name'] == archive_name:
            aid = a['id']
            break
    u="tools+" + archive_name + "@starlinglab.org"
    p = master_password
    # Archive does not exist, create it
    if (aid == ""):
        print (f"Creating {archive_name}")
        aid = create_account(u,p,archive_name)
        invite_user(u,p,aid)

    print(archive_name)
    col = item_data["collectionID"]
    org =item_data["orgID"]
    result["collections"][aid] =    {
            "collectionID": col,
            "target_path": f"{base_url}/{org}/{col}/"
        }

f = open(config_dir, 'w')
json.dump(result,f,indent=2)
