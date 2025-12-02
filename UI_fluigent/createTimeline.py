"""

This code generates pressure timeline. It results a .csv table containing Nc+1 columns with Nc the number of channels involved.


"""



# Packages requirement
# --------------------------------------------------------------------------

import numpy as np
import pandas as pd

# Functions definition
# --------------------------------------------------------------------------
def AddLinearTimeline(p_start, p_end, dt=.1, nb_points=np.nan, ramp_speed=np.nan):
    """
    Compute the transition between p_start and p_end (mbar) at a certain ramp_speed in (mbar/s).
    dt (s) is the time resolution.
    Possibility to define the ramp with a number of steps (n_steps) and not a speed. 
    Be careful, nb_points includes p_start and p_end so nb_points>=2
    """

    # range of pressure
    delta_p = abs(p_end - p_start)

    if not np.isnan(ramp_speed):                     ## the ramp is defined with a speed (assuming dt)
        duration = delta_p / ramp_speed
        nb_points = int(max(1, int(duration / dt)))
    elif not np.isnan(nb_points):                     ## the ramp is defined by a number of steps
        duration=dt*int(nb_points-1)
        ramp_speed = delta_p / duration
    #

    ramp=np.linspace(p_start, p_end, nb_points)
    return ramp, duration, ramp_speed
#

def AddCycleTimeline(p_min, p_max, dt=.1, nb_points=np.nan, sync=True):

    # create 1/4 of a cycle (pressure increases or decreases)
    ramp, t, speed = AddLinearTimeline(p_start=p_min, p_end=p_max, nb_points=nb_points, dt=dt)
        
    # create the cycle
    if sync:
        cycle = np.concatenate([ramp, np.flip(ramp[1:-1])])
    else:  # if channels are in phase opposition
        cycle = np.concatenate([np.flip(ramp), ramp[1:-1]])

    return cycle
#

def AddTimeline(metadata_by_channel):
    list_of_timelines = []  
    for metadata in metadata_by_channel:
        # get channel infos
        channel_index   = metadata["channel"]
        evolution       = metadata["evo"]
        p_min           = metadata["p_min"]
        p_max           = metadata["p_max"]
        number_steps    = metadata["nb_points_1_ramp"]

        if evolution=="linear":
            timeline, duration, speed=AddLinearTimeline(p_min, p_max, nb_points=number_steps)
        
        if evolution=="cyclic":
            synchronization = metadata["sync"]
            timeline=AddCycleTimeline(p_min, p_max, nb_points=number_steps, sync=synchronization)
        
        list_of_timelines.append({channel_index:timeline})
    #

    # combine all timelines in a single dictionnary
    timelines={}
    for timeline in list_of_timelines:
        timelines.update(timeline)
    #

    return ConvertTimeline(timelines)
#

def ConvertTimeline(dict):
    
    # get the longuest timeline
    longuest_timeline=0
    for timeline in dict.values():
        L=len(timeline)
        if L>longuest_timeline:
            longuest_timeline=L
    #

    # fill short timeline with nan
    for channel, timeline in dict.items():
        L=len(timeline)
        if L<longuest_timeline:
            dict[channel]=np.concatenate((timeline, (longuest_timeline-L)*[np.nan]))
    #

    df=pd.DataFrame(dict)
    df.reset_index(inplace=True, drop=False, names="Frame")

    return df
#

def ExportMetadata(metadata):
    return pd.DataFrame(metadata, index=np.arange(1))
#


# User interface
# --------------------------------------------------------------------------

# pressure in fluidic (mbar)
p_fluidic=300.

# pressure in valves (mbar)
delta_p=200.
p_min=p_fluidic - delta_p
p_max=p_fluidic + delta_p

# timeline pressure resolution
nb_points=10

# timeline time resolution
dt=.1

channels = [
    {"channel": 0, "evo":"linear", "p_min": p_fluidic, "p_max": p_fluidic, "nb_points_1_ramp": nb_points},
    {"channel": 1, "evo":"cyclic", "p_min": p_min, "p_max": p_max, "nb_points_1_ramp": nb_points, "sync":True},
    {"channel": 2, "evo":"cyclic", "p_min": p_min, "p_max": p_max, "nb_points_1_ramp": nb_points, "sync":False}
    ]

metadata={"p_fluidic":p_fluidic,
          "delta_p+":delta_p,
          "delta_p-":delta_p,
          "p_min":p_min,
          "p_max":p_max,
          "pressure_reso":nb_points,
          "time_reso":dt,
          "total_duration":10.,
          "nb_of_channels":len(channels)
          }
#



# Main
# --------------------------------------------------------------------------

AddTimeline(channels).to_csv(r"assets\Timeline.csv", index=False)
ExportMetadata(metadata).to_csv(r"assets\Timeline_Metadata.csv", index=False)
