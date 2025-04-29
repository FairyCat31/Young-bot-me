# import hashlib
# from json import dumps
#
# import requests
# from datetime import datetime
#
# connect_url = "http://127.0.0.1:8080/"
# json_goyda = {
#   "auth_token": "B0PAOxO8ATlFFQ6tAq283qVIFzkrMl7VyLRaoQ2wVdhAzWfwtGQppjamGR61jiGBG3Rc2Awt",
#   "reset_cookie": "M5DWm6pCjBFdKixt4IpTy3enIznCCQ7LXkKIKyburMIoU3h9jYBzZQfIbJjggeYldxuKqinhCerj5sndeB4ZIYIMgEsl3QeH2M0nge01LLA6K1uxMd0Ak6oPGGVvs9fd",
#   "tid": "unimice_test"
# }
#
#
# print("1")
# sss = requests.post(connect_url + f"v1/auth?tid={json_goyda['tid']}&auth_token={json_goyda['auth_token']}",
#                     verify=False)
# print("2")
# json = sss.json()
# print(json)
# print("3")
# headers = {"Authorization": f"Bearer {json['access_token']}"}
# content = {"exp": int(datetime.now().timestamp()+30), "easy": "Hello world"}
# content["signature"] = hashlib.pbkdf2_hmac("SHA256", dumps(content).encode("latin1"), json["salt"].encode("latin1"), 100).decode("latin1")
#
# print(connect_url+f"v1/{json['sid']}/test")
# ddd = requests.post(connect_url+f"v1/{json['sid']}/test", headers=headers, json=content)
# print(ddd.text)
# # json = ddd.json()
# # headers = {"Authorization": f"Bearer {json['refresh_token']}"}
# # ddd = requests.post(connect_url+f"v1/{json['sid']}/close_session", headers=headers)
# # print(ddd.text)
#
#
#
# #print(sss.headers)
#

d = "daaddddddd"
print(d.find("aa"))
