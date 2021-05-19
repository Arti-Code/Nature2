class DataBox():

    def __init__(self):
        self.data = {}

    def add_category(self, name: str):
        self.data[name] = []

    def add_value(self, category: str, value: any):
        self.data[category].append(value)

    def get_category(self, category: str):
        return self.data[category]
    
    def reset(self, categoories: list=None):
        self.data = {}
        if categoories != None:
            for category in categoories:
                self.add_category(category)
