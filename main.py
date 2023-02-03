# This is a sample Python script.
import json
import os
import time
from datetime import datetime

from hb.learn.video import Video
from hb.models.record import Scenario
from hb.record.recorder import Recorder


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.
    recorder = Recorder()
    #recorder.start()
    #input('Stop')
    #print('Scenario lasts: {0}'.format(end-start))
    #recorder.stop()
    with open(os.path.join(recorder.config.folder,'60cbec7b-4aa1-4a1d-89e9-8b8cab34f85d/events.json'),'r') as f:
        scenario = Scenario.parse_obj(json.load(f))
        fpath = os.path.join(os.getcwd(), recorder.config.folder)
        video = Video(fpath,scenario)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
