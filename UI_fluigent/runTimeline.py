"""

This code runs pressure timeline. It must be connected to fluigent devices.


"""



# Packages requirement
# --------------------------------------------------------------------------

import time

import numpy as np
import pandas as pd

import Fluigent.SDK as fgt_sdk

# Functions definition
# --------------------------------------------------------------------------

def EndingProcedure():
    # close each channel after setting pressure at 0
    if fluigent_is_plugged:
        print("\n\n... Pressure set at zero and closure")
        for i in range(fgt_sdk.fgt_get_pressureChannelCount()):
            fgt_sdk.fgt_set_pressure(i, 0.)
        fgt_sdk.fgt_close()
    print("--------------- Procedure terminated ---------------")
#

def PrintTiming(t_current, t_total):
    if t_current<t_total:
        print(f"... Elapsed time: {t_current:.2f}s ---- {t_current*100./t_total:.2f}% of total duration")
    else:
        print(f"... 100% of total duration ---- Experiment done")
#

def ReadPressure(channel, counters, timeline):
    
    # read in the dataframe pressure to assign 
    pressure = timeline[channel].iloc[counters[channel]]

    if pd.isna(pressure):  # if we read a NaN, we we go back to the beginning of the cycle
        counters[channel]=0
        pressure = timeline[channel].iloc[counters[channel]]
    #

    return pressure
#

def ReadAllPressure(counters, timeline, N):
    current={}
    
    for channel in timeline.columns:  # pressure is read channel by channel
        current[channel]=ReadPressure(channel, counters, timeline)
        counters[channel] = (counters[channel] + 1) % N   # if we get to the end of the cycle, we go back to the beginning of the cycle
    #

    return current
#

def RunMultichannelTimeline(timeline, metadata):
    
    timeline.drop("Frame", axis=1, inplace=True)
    nb_of_points=len(timeline)
    total_duration=metadata["total_duration"][0]
    dt=metadata["time_reso"][0]
    
    print("\n--------------- Run Timeline Procedure ---------------")
    if fluigent_is_plugged:
        print("... Initializing SDK Fluigent")
        fgt_sdk.fgt_init()

        nb_devices = fgt_sdk.fgt_get_pressureChannelCount()
        print("... Number of detected channels:", str(nb_devices))

        print("... Initializing Channel Pressure")
        initial_pressure=timeline.iloc[0]
        for i in range(fgt_sdk.fgt_get_pressureChannelCount()):
            fgt_sdk.fgt_set_pressure(i, float(initial_pressure[i]))
        
        # wait to ensure pression reach inital value
        time.sleep(10.)
    #

    print("\n\n... Beginning of the Timeline")
    t_start = time.time()
    active = True          # this boolean controls wether the cycles are finished or not
    
    
    counters = {channel: 0 for channel in timeline.columns}
    while active:
        t_now = time.time() - t_start
        active = False

        PrintTiming(t_now, total_duration)

        if t_now<total_duration:
            active = True
            current_pressure = ReadAllPressure(counters, timeline, nb_of_points)
            
            # pressure is pushed in the channels
            if fluigent_is_plugged:
                for channel, pressure in current_pressure.items():
                    fgt_sdk.fgt_set_pressure(int(channel), pressure)
            #

            time.sleep(dt)
        #
    #
#



# User interface
# --------------------------------------------------------------------------

# If you want to test the code without be connected to fluigent
fluigent_is_plugged=False


# Main
# --------------------------------------------------------------------------

if __name__ == "__main__":

    timelines = pd.read_csv(r"assets\\Timeline.csv")
    metadata  = pd.read_csv(r"assets\\Timeline_Metadata.csv")

    try:
        RunMultichannelTimeline(timelines, metadata)
    finally:
        EndingProcedure()
#