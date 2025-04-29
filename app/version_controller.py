from json import dump, load
import hashlib
from os import walk
from os.path import exists

## DEFAULT CFG
"""
        {
            "fullpath": "",
            "MD5": "",
            "SHA1": "",
            "SHA256": ""
        }
"""
DEFAULT_CFG_PATH = "py_factory.json"
CFG = {
    "excluded_paths" : [".\\data\\logs",
                        "__pycache__",
                        DEFAULT_CFG_PATH,
                        "version_controller.py",
                        "tokens.json"],
    "files": [

    ]
}

class VersCFG:

    @staticmethod
    def create_cfg() -> dict:
        with open(DEFAULT_CFG_PATH, "w") as f:
            dump(CFG, f)
        return CFG.copy()

    @staticmethod
    def load():
        if not exists(DEFAULT_CFG_PATH):
            return VersCFG.create_cfg()
        try:
            with open(DEFAULT_CFG_PATH, "r") as f:
                return load(f)
        except IOError as _:
            print("[ERROR] Cant load cfg file => Using default cfg")
            return VersCFG.create_cfg()

    @staticmethod
    def dump(cfg: dict):
        with open(DEFAULT_CFG_PATH, "w") as f:
            return dump(cfg, f, indent=2)



class VersController:
    def __init__(self):
        self._cfg = VersCFG().load()
        self._package_info_getters = {
            "py": self.get_pack_info_py,
            "json": self.get_pack_info_json
        }

    @staticmethod
    def file_checksums(filepath) -> dict:
        """
        filepath - Fullpath to file
        Returns:
            MD5, SH1, SHA256 FILE CHECKSUMS
        """
        hash_md5 = hashlib.md5()
        hash_sha1 = hashlib.sha1()
        hash_sha256 = hashlib.sha256()
        with open(filepath, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                hash_md5.update(chunk)
                hash_sha1.update(chunk)
                hash_sha256.update(chunk)
        return {
            "MD5": hash_md5.hexdigest(),
            "SHA1": hash_sha1.hexdigest(),
            "SHA256": hash_sha256.hexdigest()
        }

    @staticmethod
    def is_excluded_path(path: str) -> bool:
        for excluded_path in CFG["excluded_paths"]:
            if path.find(excluded_path) != -1:
                return True
        return False

    @staticmethod
    def get_pack_info_py(path: str) -> dict | None:
        with open(path, "r", encoding="utf-8") as f:

            content = f.read()
        index = content.find("__pyfactory_package__")
        if index == -1:
            return None
        index += 21
        dict_parse_index = 0
        brackets = 0
        result = ""
        for i in range(index, len(content)):
            if dict_parse_index and (not brackets):
                result = content[dict_parse_index:i]
                break
            if content[i] == "{":
                if not brackets:
                    dict_parse_index = i
                brackets += 1
            elif content[i] == "}":
                brackets -=1
        if not result:
            return None

        try:
            return eval(result)
        except IOError as _:
            return None

    @staticmethod
    def get_pack_info_json(path: str) -> dict | None:
        with open(path, "r", encoding="utf-8") as f:
            try:
                content = load(f)
            except IOError as _:
                return None

        return content.get("__pyfactory_package__")

    @staticmethod
    def compare_versions(now_ver: str, need_ver: str) -> bool:
        nov = now_ver.split(".")
        lnov = len(nov)
        nev = need_ver.split(".")

        for inev in range(len(nev)):
            if nev[inev] == "*":
                return True
            if lnov == inev:
                return True
            if int(nov[inev]) > int(nev[inev]):
                return False
        return True


    def dir_walk(self) -> (str, str):
        for (dirpath, dirnames, filenames) in walk("."):
            if self.is_excluded_path(dirpath):
                continue
            for file in filenames:
                if self.is_excluded_path(file):
                    continue
                yield dirpath, file

    def save_all_file_checksums(self):
        self._cfg["files"] = []
        for dirpath, file in self.dir_walk():
            fullpath = dirpath + "\\" + file
            file_info = {
                "fullpath": fullpath
            }
            file_info.update(
                self.file_checksums(fullpath)
            )
            self._cfg["files"].append(file_info)
        VersCFG.dump(self._cfg)

    def validate_file_checksums(self):
        all_files = len(self._cfg['files'])
        raised_files = 0
        output = "File Validation ALL ({all_files}) PASSED ({passed}) RAISED ({raised})"
        for file in self._cfg["files"]:
            fullpath = file["fullpath"]
            del file["fullpath"]

            if self.file_checksums(fullpath) != file:
                raised_files += 1
                output += f"\n[WARN] {fullpath} checksums are difference"

        print(output
                .format(
                all_files=all_files,
                raised=raised_files,
                passed=all_files-raised_files
                )
              )

    def validate_package_versions(self):
        output = "Package version control PACKAGES ({packages})"
        packages = []
        package_versions = {}
        for dirpath, file in self.dir_walk():
            extension = file.split(".")[-1]
            info_getter = self._package_info_getters.get(extension)
            if not info_getter:
                continue
            package_info = info_getter(dirpath + "\\" + file)
            if not package_info:
                continue

            packages.append(package_info)
            package_versions[package_info["name"]] = package_info["version"]
        output += f"\n({' '.join([package['name'] + '==' + package['version'] for package in packages])})"
        for package in packages:
            dependencies = package.get("dependencies")
            if not dependencies:
                continue
            for dependency_name, dependency_version in dependencies.items():
                now_version = package_versions.get(dependency_name)
                if not now_version:
                    output += f"\n[ERROR] Can't find {dependency_name} (any version) for {package['name']}"
                    continue
                elif not self.compare_versions(now_version, dependency_version):
                    output += (f"\n[WARN] Wrong version of package {dependency_name} for {package['name']}" +
                        f" NOW({now_version}) NEED({dependency_version})")

        output = output.format(packages=len(packages))
        print(output)

vs = VersController()
vs.save_all_file_checksums()
vs.validate_file_checksums()
vs.validate_package_versions()