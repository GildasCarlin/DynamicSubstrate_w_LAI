# ================================================================================================================
# ================================================================================================================
#                                                    packages importation
# ================================================================================================================
# ================================================================================================================

import time
import numpy as np

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pkg_resources")

import Fluigent.SDK as fgt_sdk


# ================================================================================================================
# ================================================================================================================
#                                                    intermediate functions
# ================================================================================================================
# ================================================================================================================

def add_ramp(p_start, p_end, dt=.1, n_values=np.nan, ramp_speed=np.nan):
    """
    Compute the transition between p_start and p_end (mbar) at a certain ramp_speed in (mbar/s).
    dt (s) is the time resolution.
    Possibility to define the ramp with a number of steps (n_steps) and not a speed. 
    Be careful, n_values includes p_start and p_end so n_values>=2
    """

    # range of pressure
    delta_p = abs(p_end - p_start)

    ## the ramp is defined by a speed (assuming dt)
    if not np.isnan(ramp_speed):
        duration = delta_p / ramp_speed
        n_values = int(max(1, int(duration / dt)))
    ## the ramp is defined by a number of steps
    elif not np.isnan(n_values):
        duration=dt*int(n_values-1)
        ramp_speed = delta_p / duration
    #

    ramp=np.linspace(p_start, p_end, n_values)
    return ramp, duration, ramp_speed
#

def run_timeline_multichannel_sync(params_list, dt=.1):
    """
    Multiple channels are running simultaneously

    params_list = [
        {"channel": 0, "p_min": 0, "p_max": 100, "ramp_speed": 40},
        {"channel": 1, "p_min": 50, "p_max": 200, "ramp_speed": 30},
        ...
    ]
    dt : time resolution (s)
    """

    print("Initializing SDK Fluigent...")
    fgt_sdk.fgt_init()

    # Créer les rampes individuelles (montée + descente)
    channel_data = []
    for params in params_list:
        channel_index=params["channel"]
        p_min, p_max = params["p_min"], params["p_max"]
        number_steps = params["n_values"]
        total_duration = params["total_duration"]

        ramp_up, t_up, speed_up = add_ramp(p_start=0., p_end=p_max, n_values=number_steps, dt=dt)
        ramp_down, t_down, speed_down = add_ramp(p_start=0., p_end=p_min, n_values=number_steps, dt=dt)
        cycle = np.concatenate([ramp_up, np.flip(ramp_up), ramp_down, np.flip(ramp_down)])
        cycle_duration = 2.*t_up + 2.*t_down

        ### les deux valves sont en opposition de phase
        if not params["sync"]:   
            cycle=np.flip(cycle)
        #

        channel_data.append({
            "channel": channel_index,
            "cycle": cycle,
            "cycle_duration": cycle_duration,
            "total_duration": total_duration
        })

        print(f"[Canal {params['channel']}] cycle = {cycle_duration:.2f}s ({len(cycle)} points)")

    # Synchronisation stricte : boucle principale
    print("\nBeginning of the Timeline...")
    t_start = time.time()
    active = True

    while active:
        t_now = time.time() - t_start
        active = False  # on arrêtera si tous les canaux ont fini

        for data in channel_data:
            ch = data["channel"]
            cycle = data["cycle"]
            cycle_dur = data["cycle_duration"]
            total_dur = data["total_duration"]

            if t_now < total_dur:
                active = True
                # Where in the cycle
                cycle_pos = (t_now % cycle_dur) / cycle_dur
                idx = int(cycle_pos * (len(cycle) - 1))
                pressure = float(cycle[idx])
                fgt_sdk.fgt_set_pressure(ch, pressure)
            #
        #
            
        time.sleep(dt)
    #

    print("\n... Timeline over for each channel")
#





# ================================================================================================================
# ================================================================================================================
#                                                  User interface
# ================================================================================================================
# ================================================================================================================

channels = [
        {"channel": 0, "p_min": -100., "p_max": 100., "n_values": 100, "total_duration": 60, "sync":True},
        {"channel": 1, "p_min": -100., "p_max": 100., "n_values": 100, "total_duration": 60, "sync":False}
    ]


# ================================================================================================================
# ================================================================================================================
#                                                    MAIN function
# ================================================================================================================
# ================================================================================================================


if __name__ == "__main__":
    print("Initialisation Fluigent SDK...")
    #fgt_sdk.fgt_init()

    nb_devices = fgt_sdk.fgt_get_pressureChannelCount()
    print("\n... Number of detected channels: {nb_devices}\n")
    
    try:
        print("\n... Run timeline")
        run_timeline_multichannel_sync(channels, dt=.1)
    finally:
        ## close each channel after setting pressure at 0
        print("Pressure set at zero and closure...")
        for i in range(fgt_sdk.fgt_get_pressureChannelCount()):
            fgt_sdk.fgt_set_pressure(i, 0)
        fgt_sdk.fgt_close()
    #
#


