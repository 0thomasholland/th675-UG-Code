# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown] id="KyoC1gMmotr3"
# # Practical 2: Ambient noise data processing
#
# The goal of this practical is to introduce you to a variety of signal analysis tools that can be used for processing ambient noise data. The test dataset comes from Iceland, where the Cambridge volcano seismology group has been running portable arrays of broadband seismic stations for the last few decades.
#
# The first step of the practical requires you to have obspy installed. Obspy is a powerful module that provides a python framework for processing and manipulating seismic data. If you installed Jupyter Notebook via Anaconda, you can install obspy using a command sequence like
#
# ```conda config --add channels conda-forge
# conda create -n obspy python=3.7
# conda activate obspy
# conda install obspy
# ```
#
# If you are running on colab, execute the cell below - make sure you have the required `prac_data.zip` file on your drive, and `prac_path` reflects its location. If you are running locally, run the notebook in the same folder as unzipped prac_data, and skip this cell.
#

# %% id="OWyZDkXmpJ9-"
# !pip install -q obspy

# %% id="u3UojKFOotr6"
# This cell contains some custom functions that will be used later.
# You can run it (shift + enter) and skip to the next part

# %%
import json
import pickle

import matplotlib.pyplot as plt
import numpy as np
import obspy  # obspy is a module for processing seismic data
from scipy.signal import correlate
from scipy.stats.mstats import winsorize


def plot_data(st, title=""):
    try:
        data_to_plot = st[0].data
        times = st[0].times()
    except:
        data_to_plot = st.data
        times = st.times()
    times = times - max(times) / 2
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.plot(times, data_to_plot, "k-")
    ax.set_xlabel("Time, s", size=14)
    ax.set_ylabel("Norm. Amplitude", size=14)
    plt.title(title)
    plt.show()


def stack_days(folder, start_date, end_date):
    from obspy import UTCDateTime

    assert UTCDateTime(end_date) > UTCDateTime(start_date)
    date = UTCDateTime(start_date)
    datas = []
    while UTCDateTime(date) < UTCDateTime(end_date):
        date = date + 24 * 60 * 60
        file_name = str(date)[:10] + ".SAC"
        file_path = os.path.join(folder_name, file_name)
        try:
            tr0 = obspy.read(file_path)[0]
            datas.append(tr0.data)
        except:
            print(f"file does not exist: {file_name}")
    print(f"found {len(datas)} files\n")
    if len(datas) > 0:
        tr_out = tr0.copy()
        tr_out.data = np.mean(datas, axis=0)
        return tr_out


from math import asin, cos, radians, sin, sqrt


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles
    return c * r


def correlation(tr1, tr2):
    tr0 = tr1.copy()
    cc = correlate(tr1_slice.data, tr2_slice.data, mode="same")
    tr0.data = cc
    return tr0


def get_stations_dist(s1, s2):
    stations_dict = json.load(open("./prac_data/station_locations_dict.json"))
    lat1 = stations_dict[s1]["lat"]
    lat2 = stations_dict[s2]["lat"]
    lon1 = stations_dict[s1]["lon"]
    lon2 = stations_dict[s2]["lon"]
    return haversine(lon1, lat1, lon2, lat2)


def move_out_plot(station_name, folder_name):
    fig, ax = plt.subplots(figsize=(12, 6))

    ls = os.listdir(folder_name)
    for file_name in ls:
        s1s2 = file_name.split(".")[0]
        s1, s2 = s1s2.split("_")
        if station_name == s1:
            file_path = os.path.join(folder_name, file_name)
            dist = get_stations_dist(s1, s2)
            tr = obspy.read(file_path)[0]
            times = tr.times()
            times = times - max(times) / 2
            data = 7 * tr.data / tr.data.max()
            ax.plot(times, data + dist, c="k")
    ax.set_xlabel("Time, s", size=14)
    ax.set_ylabel("Distance, km/s", size=14)


def plot_dc(s1, s2):
    dcs = pickle.load(open("./prac_data/Iceland.pick", "rb"), encoding="latin1")
    if f"{s1}_{s2}" in dcs:
        p, v, _, _ = dcs[f"{s1}_{s2}"]
    elif f"{s2}_{s1}" in dcs:
        p, v, _, _ = dcs[f"{s2}_{s1}"]
    else:
        print("No data found for this pair")
        return
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(p, v, c="k")
    ax.set_xlabel("Period, s", size=14)
    ax.set_ylabel("Velocity, km/s", size=14)


# %% [markdown] id="Ztyc1GeCotr9"
# ## Part 1: Preprocessing and cross-correlation
#
# In this first part of the practical, we will investigate how signal can be extracted from ambient noise data by using cross-correlation.
#
# The link below shows a map of seismic stations in Iceland from an experiment called HOTSPOT which we will use in this practical:
#
# https://www.google.com/maps/d/u/0/edit?mid=1rrAuB2VrM7N4ecT7xhTO6qbwNrlx2Piu&usp=sharing
#

# %% [markdown] id="elfIoWU6otr-"
# The first step reads in data for two of the Icelandic stations (BORG and HOT19 - find them on the map) for the entire day of 10th January 1997. In this case, we will just look at the vertical component seismogram, which will ultimately yild EGFs that correspond to band-limited EGFs.

# %% id="FFOYvFZjotr_"
tr1 = obspy.read("./prac_data/raw_data/II.BORG.10.BHZ.D.1997.010")[
    0
]  # tr1 now holds the data for station BORG
tr2 = obspy.read("./prac_data/raw_data/XD.HOT19..BHZ.D.1997.010")[
    0
]  # tr2 now holds the data for station HOT19

# %% [markdown] id="vhkcgglNotsA"
# Our goal is to cross correlate the signals from the two stations, but first some preproccsing is required.
# The steps are:
# 1. Cut the data into shorter chunks
# 2. Reduce the sampling rate
# 3. Normalize and taper the signals
#
# To start, we will look at the raw data for one station and check the sampling rate.

# %% id="edxGtx4HotsB"
print("Raw data:")
plot_data(tr1)
print("The sampling rate is:", int(tr1.stats.sampling_rate), "samples per second")

# %% [markdown] id="6MIVlKrfotsC"
# We see we have 24 hours of data at 40 samples per second.
# First we need to cut the data into shorter chunks and reduce the sampling rate
#
# Why do you think this might be useful?
#
# We will now take the first half an hour of data:

# %% id="D361DCUzotsD"
starttime = tr1.stats.starttime
endtime = starttime + 60 * 30  # half an hour in seconds
tr1_slice = tr1.copy().slice(starttime, endtime)
print("Half an hour of raw data:")
plot_data(tr1_slice)

# %% [markdown] id="RHgl2EFqotsE"
# Now we remove any trends from the data and remove the mean so that it is centred around zero.

# %% id="OaM5uI3KotsF"
print("Mean and trend removed:")
tr1_slice.detrend("linear")
plot_data(tr1_slice)

# %% [markdown] id="aFQZXdGRotsG"
# Next we want to decimate the data to 1 sample per second.
# To do this we must first filter the data with a lowpass filter at 0.5 Hz.
# To avoid edge effects when filtering, we first apply a 5% taper to the data

# %% id="omSzq5nuotsG"
print("Tapering:")
tr1_slice.taper(0.05)
plot_data(tr1_slice)
print("Filtering and decimating:")
tr1_slice.filter(type="lowpass", freq=0.5, zerophase=True)
# To get a sampling rate of 1 samples per second we need to decimate our signal by a factor of 40
# We decimate in two steps since obspy does not let you decimate using a number greater than 10
tr1_slice.decimate(10)
tr1_slice.decimate(4)
plot_data(tr1_slice)
print(
    "The new sampling rate is:",
    int(tr1_slice.stats.sampling_rate),
    "samples per second",
)


# %% [markdown] id="_bdnrOgMotsG"
# Note the effect that tapering has on the ends of the waveform.
#
# Finally, we want to suppress large amplitudes, which may be the result of earthquakes or local ground motion. This is done here through 1-bit normalisation, noting that tapering is still required.

# %% id="RJdZ1KHzotsH"
tr1_slice.data = winsorize(tr1_slice.data, 0.25)
tr1_slice.data = tr1_slice.data / tr1_slice.data.max()
plot_data(tr1_slice)

# %% [markdown] id="KEz8HXHgotsI"
# As an exercise, try repeating the above process with HOT19 (tr2) to produce the time series tr2_slice.  Note that the sampling rate might be different, so decimate by the correct amount in order to produce 1 sample per second. Enter all relevant commands in the empty cell below and execute.

# %%

print("The sampling rate is:", int(tr2.stats.sampling_rate), "samples per second")


# %% id="aMuuu1TxotsK"


starttime2 = tr2.stats.starttime
endtime2 = starttime2 + 60 * 30  # half an hour in seconds
tr2_slice = tr2.copy().slice(starttime2, endtime2)
tr2_slice.detrend("linear")
tr2_slice.taper(0.05)
tr2_slice.filter(type="lowpass", freq=0.5, zerophase=True)
tr2_slice.decimate(10)
tr2_slice.decimate(2)
tr2_slice.data = winsorize(tr2_slice.data, 0.25)
tr2_slice.data = tr2_slice.data / tr2_slice.data.max()

print("The sampling rate is:", int(tr2_slice.stats.sampling_rate), "samples per second")
cc = correlation(tr1_slice, tr2_slice)
plot_data(cc)

# %% [markdown] id="ntOkfYLyotsL"
# You will observe that there is not much in the way of a clear signal on the causal or acausal components, but this is just a small snippet of data, and the signal will emerge as more data are added.

# %% [markdown] id="yzMiV64TotsL"
# ## Part 2 : Stacking
# As you've learned, the first step in ambient noise analysis requires cross correlating the continuous seismic data for every simultaneously recording station pair. In the first part you have done this for half an hour of data. The next step is to repeat this process for the entire day, giving 48 cross correalations which are stacked (averaged) to give a daily (24 hr) cross correlation. To save time this has already been done for you for the station pair BORG and HOT19.
#
# You have been given a folder named 'prac_data' which contains another folder named 'BORG_HO19'. Each of the files in this folder is the result of cross correlating the recordings at these two stations during one day.
#
# Lets see what is in the folder.

# %% id="5BHQxjXWotsL"
import os

folder_name = "./prac_data/BORG_HOT19/"  # path to folder
file_list = sorted(
    os.listdir(folder_name)
)  # make a list of files in the folder and sort it
print(file_list)  # print the list

# %% [markdown] id="c--vnokPotsM"
# For example, the file '1996-08-03.SAC' is the result of the cross correlation for August 3rd, 1996.
#
# The extension ".SAC" signifies a type of seismic data file (binary format).
#
# Write down the first and last days of data; you will need it later.
#
# Let's have a look at this file:

# %% id="3U0n1xMBotsN"
folder_name = "./prac_data/BORG_HOT19/"
# file_name = '1997-08-03.SAC'
file_name = "1998-08-14.SAC"
file_path = os.path.join(
    folder_name, file_name
)  # join the names of folder and file to get the correct path
data_in = obspy.read(file_path)  # read the data from the file
plot_data(data_in)  # plot the data

# %% [markdown] id="pjsSDVXgotsN"
# Can you see anything meaningful in the figure? Repeat the above for a few different dates at different times of the year. Can you see any difference?

# %% [markdown] id="QsjUJ9tsotsO"
# Next we will try to stack multiple files together to get a better signal to noise ratio. Let's start with one week of data

# %% id="d8_9Q52lotsO"
start_date = "1996-07-20"
end_date = "1998-08-14"
folder_name = "./prac_data/BORG_HOT19/"
stacked_data = stack_days(folder_name, start_date, end_date)  # Stack the data
plot_data(stacked_data)  # Plot the stacked data

# %% [markdown] id="7vc14A2qotsP"
# You may notice some files are missing, this probably means one of the stations did not record that day due to a malfunction

# %% [markdown] id="6j-KY_9LotsQ"
# Can you see anything meaningful in the figure? Repeat the above using longer durations: one month, 3 months, 1 year and the entire date range. Describe what you see.
#
# Is there a difference between using 3 months of data at different times of the year (i.e. winter, summer, etc.)? If so, why do you think that is?
#
# ---
#
# Find the coordinates of the two stations by filtering the relevant rows from the dataframe below and find the distance between the two using the haversine function:

# %% id="m_QNDUCj3C2B"
import pandas as pd

df = pd.read_json(
    "./prac_data/station_locations_dict.json", orient="index"
).reset_index()
df.rename(columns={"index": "station"}, inplace=True)

print(df[df["station"] == "BORG"])
print(df[df["station"] == "HOT19"])

# %% id="YNnV7nrzotsR"
lat1 = 64.747398
lon1 = -21.326799
lat2 = 64.810371
lon2 = -14.090622
dist = haversine(lon1, lat1, lon2, lat2)
print(dist, "km")

# %% [markdown] id="-Db05fR6otsR"
# Assuming surface waves travel at between 2 - 4 km/s, how long should the travel times between the two stations be? Does that agree what with you saw in the plot?

print(dist / 4, "s to", dist / 2, "s")

# %% [markdown] id="H3dnVNOFotsS"
# ## Part 3 - Comparing different station pairs
#
# The folder 'prac_data' contains another folder named 'stacked', this folder contains the  stacked cross correlations for every station pair. Let's see what is inside:

# %% id="YhFQSQyJotsS"
folder_name = "./prac_data/stacked/"  # path to folder
file_list = sorted(
    os.listdir(folder_name)
)  # make a list of files in the folder and sort it
print(file_list)  # print the list

# %% [markdown] id="D27mRXFTotsT"
# For example, the file 'BORG_HOT19.SAC' is the stacked data for the station pair used above. This is how we would read it:
#

# %% id="tws4WTj8otsT"
folder_name = "./prac_data/stacked/"
file_name = "BORG_HOT07.SAC"
file_path = os.path.join(folder_name, file_name)
data_in = obspy.read(file_path)
plot_data(data_in)

# %% [markdown] id="IqoZVDO1otsT"
# Repeat the above with different pairs at different distances, what do you notice?

# %% [markdown] id="hI6RXR6RotsU"
# ## Part 4: Move out plot
#
# Next we want to plot all the stacked cross correlations that include the station BORG.

# %% id="NhziaKexotsU"
folder_name = "./prac_data/stacked/"
station_name = "BORG"
move_out_plot(station_name, folder_name)

# %% [markdown] id="HSiceemlotsV"
# Describe what you see, and estimate the approximate velocity of the surface wave EGFs.

# %% [markdown] id="8_rt_YlYotsV"
# ## Part 5 - Dispersion
#
# We willl now investigate the dispersion characteristics of the long term cross-correlation of BORG and HOT19. This will be done as an exercise. Use obspy's bandpass filter function to create two filtered plots of the cross-correlation time series (`data_in`) that clearly demonstrate the dispersive nature of the wavetrain (i.e. choose two different frequency bands and plot the filtered cross-correlations next to each other).

# %%

# data_in = obspy.read("./prac_data/stacked/BORG_HOT19.SAC")[0]

data_in = obspy.read("./prac_data/stacked/HOT22_HOT10.SAC")[0]

plot_data(data_in)

print(data_in.stats)


# %%

for freqmin, freqmax in [(0.001, 0.1), (0.1, 0.5)]:
    tr_slice = data_in.copy()
    tr_slice.filter(type="bandpass", freqmin=freqmin, freqmax=freqmax, zerophase=True)
    plot_data(tr_slice, title=f"Bandpass: {freqmin} - {freqmax} Hz")

# %%
