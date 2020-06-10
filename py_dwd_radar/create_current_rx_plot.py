from radolan_plots import RadolanPlot 


def process(tmp_file,fig_filename):

    settings = dict()
    settings['product'] = 'rx'
    settings['latest'] = True
    settings['tmp_filename'] = tmp_file
    settings['fig_filename'] = fig_filename
    settings['output_units'] = 'rainrate' # dBZ or rainrate

    rObj = RadolanPlot(settings)
    rObj.download_radar_data()
    rObj.set_radar_locations()
    rObj.load_radolan_file()
    rObj.set_grid()
    rObj.mask_data()
    rObj.create_radar_fig()

    return
