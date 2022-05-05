#!/usr/bin/python3
import json
import requests
import sys

if len(sys.argv) < 4:
    print (f"usage: {sys.argv[0]} username@domain.com password name_of_archive [invite_user")
    sys.exit(-1)

email = sys.argv[1]
password = sys.argv[2]
archive_name = sys.argv[3]

invite=""
if len(sys.argv) == 5:
    invite = sys.argv[4]

URL = "http://127.0.0.1:9871/api/auth/register"
body = {
    "email": email,
    "password": password,
    "name": archive_name,
    "newArchive": True,
    "newArchiveName": archive_name
}
response = requests.post(URL, json=body)

# AUTH
auth = {"username": email, "password": password}
URL = "http://127.0.0.1:9871/api/auth/jwt/login"
access_token = ""
resp = requests.post(URL, data=auth)
response_json = resp.json()
if "access_token" not in response_json:
    raise Exception("Access Token Failed")
access_token = response_json["access_token"]
headers = {"Authorization": "Bearer " + access_token}

# get AID
URL = "http://127.0.0.1:9871/api/archives"
r = requests.get(URL, headers=headers)
res = r.json()
aid = res["archives"][0]["id"]

if (invite !=""):
    d={ "email": invite, "role":10 }
    # get AID
    URL = f"http://127.0.0.1:9871/api/archives/{aid}/invite/"
    r = requests.post(URL, headers=headers, json=d)
    res = r.json()

echo aid
