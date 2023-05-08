import requests
import sys
import subprocess
import json
import os
import dotenv

dotenv.load_dotenv("/root/browsertrix/configs/config.env")
admin_user=os.environ.get("SUPERUSER_EMAIL")
admin_password=os.environ.get("SUPERUSER_PASSWORD")

config_path="/root/.integrity/"
base_url = "/mnt/integrity_store/starling/internal"

#def get_users():
#    cli = "kubectl exec -it local-mongo-0 -- /usr/bin/mongosh -u root -p example --eval 'use browsertrixcloud' --eval 'EJSON.stringify(db.users.find().toArray(),null,2, { relaxed: false })' --quiet"
#    r=subprocess.check_output(cli, shell=True, text=True)
#    y=r.split("\n")
#    y[0]="["
#    r="\n".join(y)
#    a=json.loads(r)
#    return a

def get_token(email,password,server):
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


def get_me(header,server):
    URL=f"https://{server}/api/users/me"
    r = requests.get(URL, headers=header)
    return r.json()

def change_password(header,userid,password,server):
    URL=f"https://{server}/api/users/{userid}"
    d= {"password": password}
    r = requests.patch(URL, headers=header, json=d)
    return r.json()  
def create_org(header,org_name,server):
    URL=f"https://{server}/api/orgs/create"
    d= {"name": org_name}
    r = requests.post(URL, headers=header, json=d)
    return r.json()
def get_org(header,org_name,server):
    URL=f"https://{server}/api/orgs"
    d= {"name": org_name}
    r = requests.get(URL, headers=header)
    res= r.json()
    for o in res["items"]:
        if o["name"]==org_name:
            return o
def create_user(header,email,name,oid,server):
    URL=f"https://{server}/api/orgs/{oid}/add-user"
    d= {
        "email": email,
        "role": 100,
        "password": "test123",
        "name": name
        }
    r = requests.post(URL, headers=header, json=d)
    return r.json()  
def invite_user_to_org(header,email,oid,server):
    URL=f"https://{server}/api/orgs/{oid}/invite"
    d= {
        "email": email,
        "role": 100
        }
    r = requests.post(URL, headers=header, json=d)
    return r.json()
def get_invites(header,oid,server):
    URL=f"https://{server}/api/orgs/{oid}/invites"
    r = requests.get(URL, headers=header)
    return r.json()

### Change super user password
email="admin@example.com"
password="testing123"
header=get_token(email,password)

##password="PASSW0RD!"
#me=get_me(header)
#change_password(header,me['id'],"testing123")

## Create Strling Org
#print(create_org(header,"Starling Lab"))

data = {}

with open(f"{config_path}preprocessor-browsertrix-collections.json","r") as f:
    data = json.load(f)

result = { "collections": {}}
for item_data in data:
    server = item_data["server"]
    archive_name = item_data["orgID"] + "_" +  item_data["collectionID"]
    if "suffix" in item_data:
      archive_name = archive_name + "_" + item_data['suffix']
    aid = ""
    org = get_org(header,archive_name,server)
    if org is None:
        print (f"Creating {archive_name}")
        res = create_org(header, archive_name,server)
#        invite_user_to_org(header,"integrity@starlinglab.org",org["id"])
        org = get_org(header,archive_name,server)
    print(org["id"])
    author = None
    if "author" in item_data:
      author = item_data['author']
    col = item_data["collectionID"]
    org =item_data["orgID"]
    result["collections"][aid] =    {
            "collectionID": col,
            "target_path": f"{base_url}/{org}/{col}/",
            "author": author,
            "server": server
        }
    
#    print(get_invites(header,org["id"]))
    #print(archive_name)
#f = open(config_dir, 'w')
#json.dump(result,f,indent=2)
#config_dir =  os.environ.get("CONFIG_FILE")