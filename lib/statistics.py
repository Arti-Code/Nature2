

class Statistics():

    def __init__(self):
        self.data = {}

    def add_collection(self, collection_name: str, named_rows: list):
        collection = {}
        for row in named_rows:
            collection[row] = []
        self.data[collection_name] = collection

    def add_data(self, collection_name: str, data: dict):
        for data_key in data:
            self.data[collection_name][data_key].append(data[data_key])