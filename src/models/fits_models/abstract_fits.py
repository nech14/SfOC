from datetime import datetime


class FitsInfoAbstract:
    def __init__(self, info):
        self.EXPOTIME = info[0]

    def get_time(self):
        return str(self.EXPOTIME)[-6:]

    def get_norm_time(self):
        time = self.get_time()
        return time[:2] + ':' + time[2:4] + ':' + time[4:]

    def get_datetime(self):
        date = str(self.EXPOTIME)
        return datetime(int(date[:4]), int(date[4: 6]), int(date[6: 8]),
                                 int(date[8: 10]), int(date[10: 12]), int(date[12: 14]))