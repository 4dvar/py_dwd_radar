#!/usr/bin/env python

import tempfile
import sys
import os
import urllib
import numpy as np
import wradlib as wrl
import matplotlib as mpl

mpl.rcParams['font.family'] = 'sans-serif' 
mpl.rcParams['font.monospace'] = 'Arial Unicode MS'
mpl.rcParams['font.sans-serif'] = 'Arial Unicode MS' 
mpl.rcParams['font.serif'] = 'Arial Unicode MS' 

import matplotlib.pyplot as pl
from mpl_toolkits.basemap import Basemap
from osgeo import osr

# module libs
import r_colormaps


"""
more details on radolan and wradlib
https://docs.wradlib.org/en/stable/notebooks/radolan/radolan_showcase.html
"""


###########################################################
###########################################################



class RadolanPlot(object):
    """

    INFO Radolan Products:

    ID  INT     avail   Description
    RX/WX   5 min   5 min   original radardata in qualitative RVP6-units (1 byte coded)
    RZ  5 min   5 min   radardata after correction of PBB converted to rainrate with improved Z-R-relation
    RY  5 min   5 min   radardata after correction with Quality-composit (QY)
    RH  1 h     5 min   1 h summation of RZ-composit
    RB  1 h     hh:50   1 h summation with preadjustment
    RW  1 h     hh:50   1 h summation with standard adjustment “best of two”
    RL  1 h     hh:50   1 h summation with adjustment by Merging
    RU  1 h     hh:50   1 h summation with standard and merging adjustment “best of three”
    SQ  6 h     hh:50   6 h summation of RW
    SH  12 h    hh:50   12 h summation of RW
    SF  24 h    hh:50   24 h summation of RW
    W1  7 d     05:50   7 d summation of RW
    W2  14 d    05:50   14 d summation of RW
    W3  21 d    05:50   21 d summation of RW
    W4  30 d    05:50   30 d summation of RW

    """


    def __init__(self,settings):

        # init

        if 'product' in settings.keys():
            self.product = settings['product']
        else:
            self.product = 'rx' # standard value


        if 'latest' in settings.keys():
            self.latest = settings['latest']
        else:
            self.latest = True # standard value

        if 'ddate' in settings.keys() and self.latest==False:
            self.ddate = settings['ddate']
        else:
            self.ddate = ''

        if 'dtime' in settings.keys() and self.latest==False:
            self.dtime = settings['dtime']
        else:
            self.dtime = ''

        if 'tmp_filename' in settings.keys():
            self.tmp_filename = settings['tmp_filename']
        else:
            self.tmp_filename = os.path.join(tempfile.mkdtemp(), 'dwd_radar_data.bin')
        
        if 'fig_filename' in settings.keys():
            self.fig_filename = settings['fig_filename']
        else:
            self.fig_filename = os.path.join(tempfile.mkdtemp(), 'radar_plot.png')

        if 'output_units' in settings.keys():
            self.output_units = settings['output_units']
        else:
            sys.exit('ERROR: no units given for plot')

        return


    ###########################################################
    ###########################################################


    def download_radar_data(self):
        """
        OPTIONS:
            * latest: get the latest data
            * ddate: yymmdd (only available if latest=False)
            * dtime: hhmm (UTC, i.e. -2h or -1h winter time)
            * ry_tmp_file: store the downloaded data to this file
        """

        print('... download radar data')

        if self.latest==True:
            print(' ... latest')
        else:
            print('... for specific date:' + self.ddate + ' ' + self.dtime)
        
        url = self.create_dwd_url(self.product)
        print('... url: '+url)
        urllib.request.urlretrieve(url,self.tmp_filename)
        print('... download successful')
        print('... local file: '+self.tmp_filename)

        return


    ###########################################################
    ###########################################################


    def create_dwd_url(self,product='rx'):
        """
        PURPOSE:
            depending on product build the download url on dwd opendata server
        INPUT:
            * product: e.g. rx, ry

        SAMPLE URLS:
        https://opendata.dwd.de/weather/radar/radolan/rw/raa01-rw_10000-latest-dwd---bin
        https://opendata.dwd.de/weather/radar/radolan/rw/raa01-rw_10000-'+ddate+dtime+'-dwd---bin
        """


        if self.latest == True:
            url_part2 = '-latest-dwd---bin'
        else:
            if self.ddate != '' and self.dtime != '':
                url_part2 = '-'+self.ddate+self.dtime+'-dwd---bin'
            else:
                sys.exit('ERROR: no ddate and dtime specified.')


        if product == 'rw':
            dwd_base_url = 'https://opendata.dwd.de/weather/radar/radolan/rw/raa01-rw_10000'
        elif product == 'rx':
            dwd_base_url = 'https://opendata.dwd.de/weather/radar/composit/rx/raa01-rx_10000'
        elif product == 'wx':
            dwd_base_url = 'https://opendata.dwd.de/weather/radar/composit/wx/raa01-wx_10000'
        else:
            sys.exit('Product '+self.product+' not supported')

        dwd_url = dwd_base_url + url_part2

        return dwd_url



    ###########################################################
    ###########################################################



    def set_radar_locations(self):
        """
        PURPOSE:
            define the location information for the DWD radar stations
        """

        self.radars = {}

        radar = {'name': 'ASB Borkum', 'wmo': 10103, 'lon': 6.748292,
                 'lat': 53.564011, 'alt': 261}
        self.radars['ASB'] = radar

        radar = {'name': 'ASR Dresden', 'wmo': 10487, 'lon': 13.76347,
                 'lat': 51.12404, 'alt': 261}
        self.radars['ASD'] = radar

        radar = {'name': 'Boostedt', 'wmo': 10132, 'lon': 10.04687,
                 'lat': 54.00438, 'alt': 124.56}
        self.radars['BOO'] = radar

        radar = {'name': 'Dresden', 'wmo': 10488, 'lon': 13.76865, 'lat': 51.12465,
                 'alt': 263.36}
        self.radars['DRS'] = radar

        radar = {'name': 'Eisberg', 'wmo': 10780, 'lon': 12.40278, 'lat': 49.54066,
                 'alt': 798.79}
        self.radars['EIS'] = radar

        radar = {'name': 'Emden', 'wmo': 10204, 'lon': 7.02377, 'lat': 53.33872,
                 'alt': 58}
        self.radars['EMD'] = radar

        radar = {'name': 'Essen', 'wmo': 10410, 'lon': 6.96712, 'lat': 51.40563,
                 'alt': 185.10}
        self.radars['ESS'] = radar

        radar = {'name': 'Feldberg', 'wmo': 10908, 'lon': 8.00361, 'lat': 47.87361,
                 'alt': 1516.10}
        self.radars['FBG'] = radar

        radar = {'name': 'Flechtdorf', 'wmo': 10440, 'lon': 8.802, 'lat': 51.3112,
                 'alt': 627.88}
        self.radars['FLD'] = radar

        radar = {'name': 'Hannover', 'wmo': 10339, 'lon': 9.69452, 'lat': 52.46008,
                 'alt': 97.66}
        self.radars['HNR'] = radar

        radar = {'name': 'Neuhaus', 'wmo': 10557, 'lon': 11.13504, 'lat': 50.50012,
                 'alt': 878.04}
        self.radars['NEU'] = radar

        radar = {'name': 'Neuheilenbach', 'wmo': 10605, 'lon': 6.54853,
                 'lat': 50.10965, 'alt': 585.84}
        self.radars['NHB'] = radar

        radar = {'name': 'Offenthal', 'wmo': 10629, 'lon': 8.71293, 'lat': 49.9847,
                 'alt': 245.80}
        self.radars['OFT'] = radar

        radar = {'name': 'Proetzel', 'wmo': 10392, 'lon': 13.85821,
                 'lat': 52.64867, 'alt': 193.92}
        self.radars['PRO'] = radar

        radar = {'name': 'Memmingen', 'wmo': 10950, 'lon': 10.21924,
                 'lat': 48.04214, 'alt': 724.40}
        self.radars['MEM'] = radar

        radar = {'name': 'Rostock', 'wmo': 10169, 'lon': 12.05808, 'lat': 54.17566,
                 'alt': 37}
        self.radars['ROS'] = radar

        radar = {'name': 'Isen', 'wmo': 10873, 'lon': 12.10177, 'lat': 48.1747,
                 'alt': 677.77}
        self.radars['ISN'] = radar

        radar = {'name': 'Tuerkheim', 'wmo': 10832, 'lon': 9.78278,
                 'lat': 48.58528, 'alt': 767.62}
        self.radars['TUR'] = radar

        radar = {'name': 'Ummendorf', 'wmo': 10356, 'lon': 11.17609,
                 'lat': 52.16009, 'alt': 183}
        self.radars['UMM'] = radar

        return


    ###########################################################
    ###########################################################


    def load_radolan_file(self):

        # load radolan file
        self.r_data, self.r_attrs = wrl.io.read_radolan_composite(self.tmp_filename)

        # print the available attributes
        print("R_ Attributes:", self.r_attrs)

        return


    ###########################################################
    ###########################################################


    def set_grid(self):

        # create radolan projection object
        self.proj_stereo = wrl.georef.create_osr("dwd-radolan")


        # create wgs84 projection object
        self.proj_wgs = osr.SpatialReference()
        self.proj_wgs.ImportFromEPSG(4326)

        # get radolan grid
        self.radolan_grid_xy = wrl.georef.get_radolan_grid(900, 900)
        self.x1 = self.radolan_grid_xy[:, :, 0]
        self.y1 = self.radolan_grid_xy[:, :, 1]

        # convert to lonlat
        self.radolan_grid_ll = wrl.georef.reproject(self.radolan_grid_xy,projection_source=self.proj_stereo,projection_target=self.proj_wgs)
        self.lon1 = self.radolan_grid_ll[:, :, 0]
        self.lat1 = self.radolan_grid_ll[:, :, 1]

        return


    ###########################################################
    ###########################################################



    def plot_radar_station(self,radar,bmap):

        site = (radar['lon'], radar['lat'], radar['alt'] )

        # plot radar location and information text
        x, y = bmap(radar['lon'], radar['lat'])
        pl.plot(x,y,'k+')
        pl.text(x+10000,y+10000,str(radar['name']), color='k',fontsize=7.)

        return


    ###########################################################
    ###########################################################


    def create_radar_fig(self):

        pl.clf()

        bmap = Basemap(projection='merc',lon_0=9.5,lat_0=42.0,
        llcrnrlon=5.0,llcrnrlat=47.0,
        urcrnrlon=16.0,urcrnrlat=55.0,
        resolution='i')

        blon,blat = bmap(self.lon1,self.lat1)


        fig1 = pl.figure(figsize=(8,8))
        ax1 = pl.gca()

        # plot the actual radar data and map
        bmap.drawcountries(linewidth=0.5, color='#000000')
        bmap.drawcoastlines(linewidth=0.6, color='#000000')


        cmaplist = r_colormaps.get_blue_green_yellow_red_violett_range()
        # force the first color entry to be grey
        cmaplist[0] = '#fffffe'

        # create the new map
        cmap = mpl.colors.LinearSegmentedColormap.from_list('CRadar',cmaplist,len(cmaplist))

        # output actual data depending on output units
        if self.output_units == 'dBZ':
            self.rpv6_to_dBZ()
            # define the bins and normalize
            bounds = list(np.arange(6.0,18.0,2.0)) + list(np.arange(18.0,30.0,2.0)) + list(np.arange(30.0,42.0,2.0)) + list(np.arange(42.0,56.0,2.0)) + list(np.arange(56.0,80.0,4.0))
            norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
            pm = bmap.pcolormesh(blon, blat, self.dBZ, cmap=cmap, norm=norm)
        elif self.output_units == 'rainrate':
            bounds = list(np.linspace(0.01,0.5,6)) + list(np.linspace(0.5,5.0,6)) + list(np.linspace(6,30,6)) + list(np.linspace(31,150,6)) + list(np.linspace(151,500,6))
            norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
            self.rpv6_to_dBZ()
            self.dBZ_to_rainrate()
            pm = bmap.pcolormesh(blon, blat, self.rainrate, cmap=cmap, norm=norm)


        cb = fig1.colorbar(pm, shrink=0.6)
        cb.set_label("mm/h")
        pl.title('RADOLAN '+self.product.upper()+'\n' + self.r_attrs['datetime'].isoformat())

        # plot the radar stations
        for radar_id in self.r_attrs['radarlocations']:
            # get radar coords etc from dict
            # repair Ummendorf ID
            if radar_id == 'umd':
                radar_id = 'umm'
            radar = self.radars[radar_id.upper()]
            self.plot_radar_station(radar, bmap)


        pl.text(0.7,-0.025,'www.meteo-blog.net',transform=pl.gca().transAxes,fontsize=9)
        pl.text(0.7,-0.045,'Data from opendata.dwd.de',transform=pl.gca().transAxes,fontsize=9)
        pl.tight_layout()
        pl.savefig(self.fig_filename,dpi=150)

        return


    ###########################################################
    ###########################################################


    def mask_data(self):
        self.r_data = np.ma.masked_equal(self.r_data,self.r_attrs["nodataflag"])
        return


    ###########################################################
    ###########################################################


    def draw_poly(self,lats,lons,m):
        x, y = m( lons, lats )
        xy = zip(x,y)
        poly = mpl.patches.Polygon( list(xy),edgecolor='#888888',facecolor=None, linewidth=0.4, fill=False )
        pl.gca().add_patch(poly)
        return


    ###########################################################
    ###########################################################


    def rpv6_to_dBZ(self):
        self.dBZ = self.r_data / 2. - 32.5
        return



    ###########################################################
    ###########################################################


    def dBZ_to_rainrate(self):
        """
        using standard RADLON formula: Z = 256 * rainrate**1.42
        """
        # dbZ to mm6/m3
        Z=10.0**(1/10. * self.dBZ)
        self.rainrate = (Z/256.)**(1/1.42) # as mm/h
        return




###########################################################
###########################################################



if __name__ == '__main__':
    process()
