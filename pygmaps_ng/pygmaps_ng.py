#!/usr/bin/python
from csv import DictReader
from os import path, listdir
import re

import bs4
from jsmin import jsmin
    
BASE_DIR = path.dirname(path.abspath(__file__))

'''

Example of building the json object to give to gmm-up.

build_data produces a json object of markers and lines from a directory
  tree of csv files

build_page compiles this json data, javascript, css and html into one
 stand alone html file (google maps still requires an internet connection)

In writing your own json objects, use this to debug broken data:

    In [0]: type(json_obj)	#a list of all apps
    Out[0]: list
    In [1]: [[key, type(value)] for key, value in json_obj[0].items()
    Out[1]: [['dataset_1', dict],  ['id', str],  ['title', str]]
    In [2]: [[key, type(value)] for key, value in json_obj[0]['group_3'].items()]
    Out[2]: 
[['color', str], 
 ['markers', list], 
 ['lines', list],
 ['polygons', list],
 ['title', str]]

    In [3]: [[key, type(value)] for key, value in json_obj[0]['dataset1']['markers'][0].items()]
    Out[3]: [['lat', str], ['color', str], ['lon', str], ['text', str]]

    In [4]: [[key, type(value)] for key, value in json_obj[0]['dataset1']['lines'][0].items()]  #oddly, v3 shouldn't support the editable keyword, but it sometimes does
    Out[4]: [[path, list], ['color', str], ['editable',str]]

    #path = [[pt1x,pt1y],[pt2x,pt2y],...]

    In [5]: [[key, type(value)] for key, value in json_obj[0]['dataset1']['polygons'][0].items()]
    Out[5]:
[['strokeColor', str],
 ['fillOpacity', float],
 ['polygon', list],
 ['fillColor', str]]

    #polygon = [ [ [ [pt1x,pt1y] , ... ], [[hole1x,hole1y],...] ] ]
    #hole verticies must be wound opposite (clockwise vs counter clockwise)

'''

gmmup_loc = path.join(BASE_DIR,'gmmup/')  #location of gmm-up (contains static.html, javascripts/, etc.)

class Map(object):
    def __init__(self):
        self.apps = list()

    def data(self):
        result = [] 
        for app in self.apps:
          tmp = {'id':app.id,'title':app.title}
          tmp.update(app.data())
          result.append(tmp)
        return result   

    def build_page(self,center=[30.320000, -97.770000],zoom=5,outfile='output.html'):
        '''
        Compile stylesheets, javascript, html, and generated data into one html file
        data is a dictionary. See definition in main.js'''
        global gmmup_loc

        def path_join(f):
          return path.join(gmmup_loc,f)

        soup = bs4.BeautifulSoup(open(path_join('static.html')).read())
        stylesheets = soup.findAll("link", {"rel": "stylesheet"})
        for s in stylesheets:
    	  t = soup.new_tag('style')
    	  c = bs4.element.NavigableString(open(path_join(s["href"])).read())
    	  t.insert(0,c)
    	  t['type'] = 'text/css'
    	  s.replaceWith(t)
    
        #insert data into javascript file
        jsonMarker ='/* INSERT JSON DATA HERE */' 

        data = self.data()
        #print "data: ",data
        jsonData = str(data)[1:-1]	#strip the outer {} because it is being inserted into {}
        #print jsonData
     
        javascripts = soup.findAll("script")
        for s in javascripts:
    	  t = soup.new_tag('script')
    	  #print s['src']
    	  if s['src'][:4] != 'http':
    	    c = bs4.element.NavigableString(open(path_join(s["src"])).read().replace(jsonMarker,jsonData))
            #print "navstring ",c
    	    t.insert(0,c)
    	    t['type'] = 'text/javascript'
    	    s.replaceWith(t)
    
        #the compiled page:
        page = str(soup.prettify(formatter=None))
        
        #use tags in that javascript to insert the map options
        options_tag = re.compile(r'/\* OPTIONS TAG START \*/((.|\n)*)/\* OPTIONS TAG END \*/')
        options = '''
        var centerlatlng = new google.maps.LatLng(%s, %s);
        var myOptions = {
        zoom: %s,
        center: centerlatlng,
        mapTypeId: google.maps.MapTypeId.ROADMAP
        };''' % (center[0],center[1],zoom)
        
    
    
        open(outfile, "w").write(jsmin(re.sub(options_tag,options,page)))



class App(object):
    def __init__(self,id, title="No Title"):
        '''id must be html safe (no spaces or anything fancy)'''
        self.id = id
        self.title = title
        self.datasets = []

    def data(self):
        result = {'id':self.id,'title':self.title}
        for d in self.datasets:
          result[d.id] = d.data()
        return result

class DataSet(object):
    '''Object for adding markers, lines and polygons to an app.
    latlon = True means the coordinates are [lat, lon].
    latlon = False reverses the coordinate order'''

    def __init__(self, id, title="No Title",key_color="#888888",latlon = True):
        self.id = id
        self.title = title
        self.key_color = key_color
        self.latlon = latlon
        self.markers = []
        self.lines = []
        self.polygons = []

    def add_marker(self,pt,color='#000088',title=None,text=None):
        '''pt = (lat, lon)'''
        try:
          #check type and shape of pt
          pt = [float(x) for x in pt[:3]]
          if len(pt) != 2:
            raise ValueError
        except ValueError:
          print "Expected pt to be [float, float] but got",type(pt),pt
          raise
        if not self.latlon:
            pt.reverse()

        color = color.strip('#') #the one time we dont want '#'
        result = {'lat':str(pt[0]),'lon':str(pt[1]),'color':color}
        if title:
         result['title'] = title
        if text:
         result['text'] = text
        self.markers.append(result)

    def add_line(self,pts,color="#880000"):
        '''input is a list of lists, 
        the inner list being [lat,lon]'''

        try:
           if not len([[float(x),float(y)] for x,y in pts]) > 1:
             raise ValueError
        except ValueError:
          print "Bad LineString.  Got ",pts
          raise
        #We need a string that could be a float
        if self.latlon:
          pts = [[str(x),str(y)] for x,y in pts]
        else:
          pts = [[str(y),str(x)] for x,y in pts]

        result = {'path':pts,'color':color}
        self.lines.append(result)

    def add_polygon(self,pts,fillColor="#880088",
                    fillOpacity=.8,strokeColor="#000000"):
        ''' pts = [[[[pt1x,pt1y],[pt2x,p2y],...],
                    [[hole1x,hole1y],...]
                  ]]
            holes (inner polgons) must be oppositely wound, 
             (CW vs CCW) '''
        try:
          #pressure the data for errors.  Better know now than
          # wonder why the javascript doesn't work
          polygon = list(pts)
          for complex_poly in polygon:
            complex_poly = list(complex_poly)
            for simple_poly in complex_poly:
              simple_poly = list(simple_poly)
              for valpair in simple_poly:
                valpair = [str(float(valpair[0])), 
                             str(float(valpair[1]))]
                if not self.latlon:
                   valpair.reverse()
        except ValueError:
           print "did not get a good data structure for polygon"
           raise
                        
        result = {'polygon':pts,'fillColor':fillColor,
           'fillOpacity':fillOpacity,'strokeColor':strokeColor}
        self.polygons.append(result)

    def data(self):
        '''return data'''
        result = {'color':self.key_color, 'title':self.title}
        for p in self.markers:
          #if no markers, markers key isn't created  
          result.setdefault('markers',[]).append(p)
        for l in self.lines:
          result.setdefault('lines',[]).append(l)
        for p in self.polygons:
          result.setdefault('polygons',[]).append(p)
        return result


def csv2markers(infile,default_color='#000088'):
    '''takes a filename and returns a list lists where 
       inner list is [pt, color,title,text] '''
    with open(infile, 'rb') as f:
      reader = DictReader(f, delimiter='\t')
      result = []
      color = default_color
      for i,row in enumerate(reader):

    	try:
    	    pt = [row['lat'],row['lon']]
    	except KeyError:
    	    print '%s was malformed. needs "lat" and "lon" columns.' % filename
    	    break
    
    	try:
    	    color = str(row['color'].replace('','')) #replace is to trigger error for None
    	except AttributeError:
    	    #if only one point has a color, those after it will have the same color
    	    pass
    	except KeyError:
    	    #if only one point has a color, those after it will have the same color
    	    pass
    
    	try:
    	    title = row['title']
    	except KeyError:
            title = None
    
    	try:
    	    text = row['text']
    	except KeyError:
            text = None
        
    	result.append([pt,color,title,text])
    return result

def csv2lines(infile, default_color = '#000000'):
    '''takes a filename and returns a list of dictionaries with keys 'path':[[lat, lng],], 
	'color', and optionally, 'editable' '''
    with open(infile, 'rb') as f:
      reader = DictReader(f, delimiter='\t')
      color = default_color
      path = []
      result = []
      for row in reader:
        try:
          path.append([row['lat'], row['lon']])
          if not lng or not lat:
            raise KeyError
        except KeyError:
          #blank or malformed line.  Time to start a new path
          #if you start with a blank line, you DESERVE a bug
          #BUG: an empty row is IGNORED by DictReader.
          #	 row must have something in it to trigger this error!
          result.append([path,color])
          path = []
        else:
          path.append([lat,lng])
          try:
            if not row['color']:
              #print "Called"
              raise KeyError
            else:
              color = '#'+row['color']
          except AttributeError:
            #if only one point has a color, those after it will have the same color
            pass
          except KeyError:
            #if only one point has a color, those after it will have the same color
            pass
            
    #one more push to put whatever is left into the result
    result.append([path,color])
    return result


def map_from_csvs(data_dir = './example_data'):
    '''
	Builds applications from directory tree of .csv's
     
        data_dir/
          App1/
            dataset1/
              markers.csv
            dataset2/
              markers.csv
          App2/
            ...
    '''
    color = "#FFFFFF"
    mymap = Map()
    x = path.join	    #shorthand later
    #first directory level is app names
    appnames = [y for y in listdir(data_dir) if path.isdir(x(data_dir,y))]
    appnames.sort()
    for appname in appnames:
        app = App(appname,title=appname.replace('_',' ').capitalize())
        mymap.apps.append(app)
        #second level is data-group name
        datanames = [y for y in listdir(x(data_dir,appname)) if path.isdir(x(data_dir, x(appname, y)))]
        datanames.sort()
        for datasetname in datanames:
            dataset = DataSet(datasetname, title=" ".join([xxx.capitalize()for xxx in datasetname.split("_")]))
            app.datasets.append(dataset)
            #last level is primitive name
            primnames = [y[:-4] for y in listdir(x(data_dir,x(appname,datasetname))) if y[-4:] == '.csv']
            for primname in primnames:
                if primname == 'markers':
                    for marker in csv2markers(x(data_dir,x(appname, x(datasetname, x('%s.csv' % primname))))):
                        pt, color, title, text = marker
                        dataset.add_marker(pt,color=color,title=title,text=text)
                if primname == 'lines':
                     for line in csv2lines(x(data_dir,x(appname, x(datasetname, x('%s.csv' % primitive))))):
                        pts, color = line
                        dataset.add_line(pts,color=color)
                if color[0] != '#':
                  color = '#'+color
                dataset.key_color = color
    return mymap



