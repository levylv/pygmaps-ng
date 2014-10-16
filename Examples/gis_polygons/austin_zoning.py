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

zoning = {'Single Family':{}, 'Multi Family': {'low density':['MF-1','MF-2'],'medium density':['MF-3','MF-4'],'high density':['MF-5','MF-6']},'Commercial': {'office':['GO','LO','NO'],'business':['LR','GR','CS','CS-1','CH'],'central':['CBD'],'DT mixed use':['DMU']},'Industrial':{'major':['MI'],'limited':['LI']}} 

for x in range(5):
    sf = 'SF-%s'%(x+2)
    zoning['Single Family'][sf] = [sf]

def sanitize_id(string):
    '''make a string suitable for a css class name'''
    pieces = ['']
    for s in string.split('-'):
      for x in s.split(' '):
          pieces.append(x)
    return 'x'.join(pieces)

def zoning_dict2map(zones,translated_geoms):
    threshold = .00000005  #choose this by trial and error, or inspecting VWSimplifier.ordered_thresholds of an example polygon
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
       for dataname,zone_fields in sorted(datasets.items()):
          color = datacoloriter.next()
          dset = DataSet(sanitize_id(dataname),title=dataname,
                   latlon=False,key_color=color,precision=9)
          thisapp.datasets.append(dset)
          for i,z in enumerate(zones):
            for target in zone_fields:
              if target in z:
               geom = translated_geoms[i]
               if geom.geom_name == 'POLYGON':
                 dset.add_polygon([geom.tuple],
                           threshold=threshold,fillColor=color,
                           strokeColor=color)
               elif geom.geom_name == 'MULTIPOLYGON':
                 dset.add_polygon(geom.tuple,
                           threshold=threshold,fillColor=color,
                           strokeColor=color)
    print("building map")
    mymap.build_page(zoom=13)

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
    
