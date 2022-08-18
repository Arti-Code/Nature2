class Diary():

    def __init__(self, sim_name: str):
        self.simulation = sim_name
        self.file = open("saves/" + self.simulation + ".txt", "w")