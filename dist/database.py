class Database:
    def __init__(self, database):
        self.database = database
        self.db = self.load(database)
        self.numbersets = None
        self.intervalrest = None
        self.setsrest = None

    def load(self, database):
        try:
            data = open(database).readlines()
            data = [activity.rstrip('\n') for activity in data]
            data = [activity.split(', ') for activity in data]
            data = [[activityname, int(activityduration)] for activityname, activityduration in data]
            return data
        except Exception as error:
            print(error)
    
    def add(self, activityname, newactivityduration):
        self.db.append([activityname, newactivityduration])
        
    def remove(self, index):
        self.db.pop(index)
    
    def move(self, activityname, newindex):
        i = -1
        for x in self.db:
            i += 1
            if activityname == x[0]:
                self.db.insert(newindex, self.db.pop(i))
                break
            else:
                continue
    
    def edit(self, activityname, editactivityname, editduration):
        i = -1
        for activity in self.db:
            i += 1
            if activityname == activity[0]:
                self.db.pop(i)
                self.db.insert(i, [editactivityname, editduration])
                break
            else:
                continue
            
    def clearall(self):
        self.db = []
    
    def save(self):
        data = open(self.database, 'w')
        for x in self.db:
            data.write(f"{x[0]}, {x[1]}\n")
        data.close()
