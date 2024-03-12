from importlib import import_module
from os import system


path_to_reg = "data\\sys\\req.txt"
path_to_reg_temp = "data\\sys\\req_temp.txt"
req = ""


print("""[$] UPDATE MANAGER VER 0.1.0
[$] Scanning requirements
[$] Status: starting...""")

with open(path_to_reg, "r") as file:
    for lib_name_ver in file.read().split("\n"):
        c = 0
        l_n_v = lib_name_ver.split("==")
        try:
            import_module(l_n_v[0].replace("python-", ""))
        except ImportError:
            req += f"{lib_name_ver}\n"

print("[$] Status: complete!")
if not req:
    print("[$] All ok!")
    print("[$] Stopping update manager...")
    exit(0)


print(f"""[!] Program couldn't found these modules or modules was broken:\n
{req}
[$] Install needed modules ?""")

response = input("[?] answer [y/n] > ")

if response != "y":
    print("[$] Stopping update manager...")
    exit(1)

print("""[$] Installing requirements
[$] Status: starting...""")
with open(path_to_reg_temp, "w") as file:
    file.write(req)

system(f"pip install -r {path_to_reg_temp}")
print("""[$] Status: complete!
[!] Restarting...
[$] Stopping update manager...""")

exit(2)
