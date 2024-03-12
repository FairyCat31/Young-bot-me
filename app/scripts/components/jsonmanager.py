from json import dump, load

cfg = "data/json/json_conf.json"



class JsonManager():
    def __init__(self):
        self.name = ""
        self.loadCode = 0
        self.replics = {}
        self.buffer = {}
        self.load_cfg(cfg)
        self.pjson = self.buffer["pjson"]
        self.pro_keys = {"bots_properties.json": self.procedure_for_bots}

    def __str__(self):
        return self.name

    def load_cfg(self, path):
        with open(path, "r") as f:
            self.name = path.split("/")[-1]
            try:
                self.buffer = load(f)
            except Exception as e:
                self.name = ""
                self.loadCode = 0
                print(e)
            else:
                self.loadCode = 1

    def procedure_for_bots(self, bot_name: str):
        self.replics = self.buffer[bot_name]["replics"]

    def dload_cfg(self, short_name):
        self.load_cfg(self.pjson + short_name)

