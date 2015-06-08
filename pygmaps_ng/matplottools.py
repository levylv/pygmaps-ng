'''
Tools for outputting pyplot objects as data for pygmaps-ng
'''

from matplotlib import use
use("AGG")  #turn off graphical backends
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from numpy import linspace,array

def uniform_grid(X,Y,Z,grid_shape=(300,300),method='linear'):

    #http://wiki.scipy.org/Cookbook/Matplotlib/Gridding_irregularly_spaced_data
    # define grid.
    X,Y,Z = map(array,(X,Y,Z))  #tuples, lists no good 
    xi = linspace(X.min(),X.max(),grid_shape[0])
    yi = linspace(Y.min(),Y.max(),grid_shape[1])
    zi = griddata((X, Y), Z, (xi[None,:], yi[:,None]), method=method)
    return xi,yi,zi

def mplcolor2hex(mplcolor):
    ''' take (r,g,b,a) and return hex representation '''
    return '#%02X%02X%02X' % tuple([x*255 for x in mplcolor[:3]])

def get_contour_paths(X,Y,Z,n,grid_shape=(300,300),**kwargs):
    '''
    use like matplotlib.pyplot.contourf to return contour paths, colors and values.
    Assumes non-uniform data (not on a grid) and interpolates to a grid
    Assumes lowest value is within lowest level
    '''
    X,Y,Z = uniform_grid(X,Y,Z,grid_shape=grid_shape)
    C = plt.contourf(X,Y,Z,n,**kwargs)
    #plt.show()
    levels = []
    for collection in C.collections:
    #/print "type: {}".format(type(collection))
        #colors.append(collection.get_color())
        ps = []
        for p in collection.get_paths():
          #if p.codes:
          #  print ':: {}\n'.format(p.codes)
          ps.append(list(map(list,p.vertices)))
        levels.append(ps)
    #paths, colors of paths, and values represented by paths
    return levels,[mplcolor2hex(color[0]) for color in C.tcolors],C.levels

def polys_from_contour_paths(paths):
    '''
    takes output from get_contour_paths and creates complex polygons with holes
    defined by poygons with oppositely wound verticies, as google maps requires
    to render them properly
    '''
    
    for i in range(len(paths)):
      tmp=list()
      for n,path in enumerate(paths[i]):
        p =  map(list,path)
        #ugh, gotta break up the path where it meets itself to get
        # distinct polygons
        old = set()
        poly = list()
        for vert in p:
          if str(vert) not in old:
            old.add(str(vert))
            poly.append(vert)
          else:
            #sever
            old.clear()
            tmp.append(poly)
            poly = list()
        '''if i != 0:
          #cut out the hole for the layer before it also
          for n,path in enumerate(paths[i-1]):
            p =  map(list,path)
            p.reverse()
            tmp.append(p)'''
      yield tmp

if __name__ == "__main__":
   from numpy.random import uniform,seed
   from numpy import vectorize
   from pygmaps_ng import *
   almostblack = '#262626'  
   seed(1234)
   npts =  300
   nlevels = 10
   lat = uniform(30.1,30.5,npts)
   lon = uniform(-97.8,-97.4,npts)
   def metric(lat,lon):
       '''quick, arbitrary values to contour around'''
       x = (lat-30.1)/(30.5-30.1)+uniform(-.03,.03)
       y = (lon+97.8)/(97.8-97.4)+uniform(-.03,.03)
       return (x-.5)**2+(y-.5)**2

   v = vectorize(metric)
   z = v(lat,lon)
   paths,colors,keyval = get_contour_paths(lat,lon,z,nlevels)
   poly_generator = polys_from_contour_paths(paths)
   mymap = Map()
   thisapp = App('app1',title="Random Contours")
   mymap.apps.append(thisapp)
   for i,path in enumerate(poly_generator):
     dset = DataSet(str(i),title=str(keyval[i]),key_color=colors[i])
     thisapp.datasets.append(dset)
     dset.add_polygon([path],fillColor=colors[i],strokeColor=almostblack)
   mymap.build_page(center=(30.3,-97.6),zoom=14,outfile="contour_test.html")
