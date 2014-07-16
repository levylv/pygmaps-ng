'''
Example of loading a large shapefile of polygons and simplifying
the polygons for a faster map.
'''
from os import path
from collections import Counter
from pygmaps_ng import Map, App, DataSet
from pygmaps_ng.color_gen import int2rgb, hex2rgb, gradient
from django.contrib.gis.gdal import DataSource,SpatialReference,CoordTransform
from brewer2mpl.brewer2mpl import get_map

zoning = {'Multi Family': {'low density':['MF-1','MF-2'],'medium density':['MF-3','MF-4'],'high density':['MF-5','MF-6']},'Commercial': {'office':['GO','LO','NO'],'business':['LR','GR','CS','CS-1','CH'],'central':['CBD'],'DT mixed use':['DMU']},'Industrial':{'major':['MI'],'limited':['LI']}} 
def sanitize_id(string):
    '''make a string suitable for a css class name'''
    pieces = ['']
    for s in string.split('-'):
      for x in s.split(' '):
          pieces.append(x)
    return 'x'.join(pieces)

def zoning_dict2map(zones,translated_geoms):
    mymap = Map()
    n = len(zoning.keys())
    n = 3 if n<3 else n
    colors = get_map('Dark2','Qualitative',n).hex_colors.__iter__()
    print("building datasets")
    for appname,datasets in zoning.items():
       appcolor = colors.next()
       thisapp = App(sanitize_id(appname),title=appname)
       mymap.apps.append(thisapp)
       num_datasets = len(datasets)+3 #don't go to gradient.end
       datacoloriter = gradient(num_datasets,
                                 start=hex2rgb(appcolor))
       for dataname,zone_fields in datasets.items():
          color = datacoloriter.next()
          dset = DataSet(sanitize_id(dataname),title=dataname,
                   latlon=False,key_color=color,precision=7)
          thisapp.datasets.append(dset)
          for i,z in enumerate(zones):
            for target in zone_fields:
              if target in z:
               geom = translated_geoms[i]
               if geom.geom_name == 'POLYGON':
                 dset.add_polygon([geom.tuple],
                               threshold=.005,fillColor=color)
               elif geom.geom_name == 'MULTIPOLYGON':
                 dset.add_polygon(geom.tuple,
                               threshold=.005,fillColor=color)
    print("building map")
    mymap.build_page(zoom=11)

if __name__ == '__main__':

    #I split a lot in loops, so this is faster apparently
    split = unicode.split

    #import shpfile
    f = path.abspath('./gis_data/zoning.shp')
    try:
      d = DataSource(f)
    except NameError:
      print('''
       This demo requires GIS data from the city of Austin, TX.
       Download it from:
       ftp://ftp.ci.austin.tx.us/GIS-Data/Regional/zoning/zoning.zip
       and unzip it to ./gis_data/''')
    layer = d[0]

    #Don't know how to sort through the zone names except to group them based on name
    zones = layer.get_fields('ZONING_ZTY')
    geoms = layer.get_geoms()

    #translate all geoms to (lon,lat)
    _world_spatref = SpatialReference('WGS84')
    coord_transform = CoordTransform(geoms[0].srs,_world_spatref)
    for geom in geoms:
      geom.transform(coord_transform)

    zoning_dict2map(zones,geoms)
    
    '''
    #top level zones (keep only initial identifier)
    c = Counter()
    for z in zones:
      c.update({split(z,'-')[0]:1})
    #I have three colors to work with which is 8 colors, or
    # 7 colors plus white 
    most_common = {name for name,count in c.most_common(7)} #is a set

    #keep track of indices of geoms to plot
    # organized into apps named after the top level zone
    # and datasets named after the actual zone name
    # == a dictionary of dictionaries of lists of indices
    zone_dict = dict()
    for i, zone_name in enumerate(zones):
      top_level_name = split(zone_name,'-')[0]
      if top_level_name in most_common:
        zone_dict.setdefault(top_level_name,dict()).setdefault(zone_name,list()).append(i)

    print("building datasets")
    bigmap = Map()
    appcolor = -1 #used to generate a unique color for each app
    for app_name in zone_dict.keys():
      appcolor += 1
      this_app = App(app_name,title=app_name)
      bigmap.apps.append(this_app)
      n = len(zone_dict[app_name])+1
      colors = gradient(n,start=int2rgb(appcolor))
      for datasetname, indices in sorted(zone_dict[app_name].items(),key=lambda item: len(item[1]),reverse=True):
        color = colors.next()
        #the x is to uniqueify the dataset id from the app
        sane_name = '%sx'%'x'.join(datasetname.split('-'))
        dset = DataSet(sane_name,key_color=color,title=datasetname,latlon=False,precision=8)
        this_app.datasets.append(dset)
        for i in indices:
          geom = geoms[i]
          if geom.geom_name == 'POLYGON':
            dset.add_polygon([geom.tuple],threshold=.005,fillColor=color)
          elif geom.geom_name == 'MULTIPOLYGON':
            dset.add_polygon(geom.tuple,threshold=.005,fillColor=color)
    print("building map")
    bigmap.build_page(zoom=11)'''
