from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty, NumericProperty
from kivy.uix.recycleview import RecycleView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.recycleview.views import RecycleDataViewBehavior, RecycleDataAdapter
from database import Database
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.clock import Clock
from datetime import datetime, timedelta
from kivy.uix.button import Button
import winsound
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior


def validateduration(activityhour, activityminute, activitysecond):
    if activityhour.text.isnumeric() and activityminute.text.isnumeric() and activitysecond.text.isnumeric():
        if int(activityminute.text) <= 60 and int(activitysecond.text) <= 60:
            return True
        else:
            return False
    else:
        return False

def convert_to_seconds(hour, minute, second):
    duration = (int(hour.text)*3600) + (int(minute.text)*60) + int(second.text)
    return duration
    
def convert_to_hms(duration):
    hours, remainder = divmod(duration, 3600)
    minutes, seconds = divmod(remainder, 60)
    hmsformat = f"{hours:02}:{minutes:02}:{seconds:02}"
    return hmsformat

def notify():
    winsound.PlaySound("sound/trimmed alarm.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)

db = Database('database.txt')


class WindowManager(ScreenManager):
    pass


class ActivityWindow(Screen):
    running = BooleanProperty(False)
    i = None
    activitydurationlist = None
    activitylist = None
    activityduration = None
    activitylistlen = None
    

    def initDynamic(self):
        self.i = 0
        self.initActivitySets()
        self.updateactivity()
        self.pauseresumebtn = Button(text= 'Pause', size_hint= (0.2, 0.05), pos_hint= {"center_x": 0.2, "y": 0.05})
        self.pauseresumebtn.bind(on_release=self.pauseresume)
    
    def initActivitySets(self):
        self.activitydurationlist = [x[1] for x in db.db]
        self.activitylist = [x[0] for x in db.db]
        for i in range(1, len(self.activitylist)+len(self.activitylist)-2, 2):
            self.activitydurationlist.insert(i, db.intervalrest)
            self.activitylist.insert(i, "Interval Rest")
        self.activitylistlen = len(self.activitylist)
        if db.numbersets >= 2:
            self.activitylist *= db.numbersets
            self.activitydurationlist *= db.numbersets
            for i in range(self.activitylistlen, len(self.activitylist)+db.numbersets-1, self.activitylistlen+1):
                self.activitydurationlist.insert(i, db.setsrest)
                self.activitylist.insert(i, "Set Rest")


    def updateactivity(self):
        self.activityduration = self.activitydurationlist[self.i]
        self.ids.currentactivity.text = str(self.activitylist[self.i])
        if len(self.activitylist)-1 >= self.i+1:
            self.ids.nextactivity.text = str(self.activitylist[self.i+1])
        else:
            self.ids.nextactivity.text = "Finishing"

    def start(self):
        if len(db.db)>0:
            self.running = True
            self.initDynamic()
            self.add_widget(self.pauseresumebtn)
            self.ids.startstop.text = "Stop"
            if self.running:
                Clock.schedule_interval(self.countdown, 1)

    def countdown(self, *args):
        self.ids.countdown.text = str(convert_to_hms(self.activityduration))
        self.activityduration -= 1
        if self.activityduration == 0:
            notify()
        if self.activityduration == -1:
            self.i += 1
            if len(self.activitydurationlist)-1 >= self.i:
                self.updateactivity()
            else:
                self.stop()

    def back(self):
        if self.running:
            self.stop()

    def stop(self):
        self.running = False
        Clock.unschedule(self.countdown)
        self.remove_widget(self.pauseresumebtn)
        self.ids.startstop.text = "Start"
        self.initDynamic()
        self.ids.countdown.text = str(convert_to_hms(self.activitydurationlist[self.i]))
    
    def startstop(self):
        if not self.running:
            self.start()
        elif self.running:
            self.stop()
    
    def pauseresume(self, pauseresumebtn):
        if self.pauseresumebtn.text == 'Pause':
            self.pauseresumebtn.text = "Resume"
            Clock.unschedule(self.countdown)
        elif self.pauseresumebtn.text == 'Resume':
            self.pauseresumebtn.text = "Pause"
            Clock.schedule_interval(self.countdown, 1)


class ActivityEditWindow(FloatLayout):
    indexnum = ObjectProperty(None)
    activityname = ObjectProperty(None)
    activityhour = ObjectProperty(None)
    activityminute = ObjectProperty(None)
    activitysecond = ObjectProperty(None)

    def cancel(self):
        MainWindow.dismiss_editpop()
        self.activityname.text = ''
        self.activityhour.text = '0'
        self.activityminute.text = '0'
        self.activitysecond.text = '15'
    
    def remove(self):
        if self.indexnum.text.isnumeric():
            index = int(self.indexnum.text)
            if index <= len(db.db):
                db.remove(index-1)
                db.save()
    
    def edit(self):
        if self.indexnum.text.isnumeric():
            index = int(self.indexnum.text)
            if index <= len(db.db):
                if validateduration(self.activityhour, self.activityminute, self.activitysecond):
                    db.db[index-1] = self.activityname.text, convert_to_seconds(self.activityhour, self.activityminute, self.activitysecond)
            db.save()
            

class ActivityInputWindow(FloatLayout):
    activityname = ObjectProperty(None)
    newactivityhour = ObjectProperty(None)
    newactivityminute = ObjectProperty(None)
    newactivitysecond = ObjectProperty(None)

    def saving(self):
        if validateduration(self.newactivityhour, self.newactivityminute, self.newactivitysecond):
            dt = timedelta(hours=int(self.newactivityhour.text), minutes= int(self.newactivityminute.text), seconds=int(self.newactivitysecond.text))
            db.add(self.activityname.text, dt.seconds)
            db.save()

    def cancel(self):
        MainWindow.dismiss_inputpop()
        self.activityname.text = ''
        self.newactivityhour.text = '0'
        self.newactivityminute.text = '0'
        self.newactivitysecond.text = '15'


class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = [{'text': str(index+1) + '    ' + str(activity[0]) + '     ' + str(convert_to_hms(activity[1]))} for index, activity in enumerate(db.db)]
        Clock.schedule_interval(self.refreshData, 1)

    def refreshData(self, nothing):
        self.data = [{'text': str(index+1) + '    ' + str(activity[0]) + '     ' + str(convert_to_hms(activity[1]))} for index, activity in enumerate(db.db)]


class MainWindow(Screen):
    numbersets = ObjectProperty(None)
    intervalresthour = ObjectProperty(None)
    intervalrestminute = ObjectProperty(None)
    intervalrestsecond = ObjectProperty(None)
    setsresthour = ObjectProperty(None)
    setsrestminute = ObjectProperty(None)
    setsrestsecond = ObjectProperty(None)

    def show_inputpop(self):
        inputpopupWindow.open()

    def dismiss_inputpop():
        inputpopupWindow.dismiss()

    def show_editpop(self):
        editpopupWindow.open()

    def dismiss_editpop():
        editpopupWindow.dismiss()

    def updatedatabase(self):
        if validateduration(self.intervalresthour, self.intervalrestminute, self.intervalrestsecond) and validateduration(self.setsresthour, self.setsrestminute, self.setsrestsecond):
            db.numbersets = int(self.numbersets.text)
            db.intervalrest = convert_to_seconds(self.intervalresthour, self.intervalrestminute, self.intervalrestsecond)
            db.setsrest = convert_to_seconds(self.setsresthour, self.setsrestminute, self.setsrestsecond)

   
class WorkoutTimerApp(App):
    def build(self):
        Window.size = (360, 750) 
        return sm





kv = Builder.load_file("workouttimer.kv")

sm = WindowManager()

screens = [MainWindow(name="main"), ActivityWindow(name="activity")]
for screen in screens:
    sm.add_widget(screen)


editpopupWindow = Popup(title="Edit Activity", content=ActivityEditWindow(), size_hint=(0.8, 0.5))


inputpopupWindow = Popup(title="New Activity", content=ActivityInputWindow(), size_hint=(0.8, 0.5))


if __name__ == "__main__":
    WorkoutTimerApp().run()