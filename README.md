# Purpose:

Python module to plot DWD (german weather service) radar data on a map. Data source is the currently freely available RADOLAN data from DWD.


# Requirements

- wradlib (and requirements for wradlib)
- numpy
- matplotlib
- basemap

Tested with Python 3.7.7


# Install:

TODO -> setup.py (in progress)



# Usage:

- Plot current radar reflectivities for germany

e.g. start IPython in the folder where the library is cloned to

    import create_current_rx_plot
    # define a tmp-file where the downloaded data is stored to
    tmp_file='/path/to/latest.ry'
    # define a fig-filename where the radar plot is stored
    fig_filename='/path/to/tmp/radar/latest.png'
    # run the download of data and creation of plot
    create_current_rx_plot.process(tmp_file,fig_filename)


# Example plot:

![](https://www.meteo-blog.net/images/radar_sample_rx_20200610.png)
