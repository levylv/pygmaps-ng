import pygmaps_ng
import WhereWeMeet as App3

'''
Run to build the example pages of pymaps-ng
'''

This has not been updated to new pymaps_ng objects!


###
#
# A Hard coded example of a polygon with a hole from 
# stackoverflow.com/questions/7494474/google-maps-api-polygon-with-hole-in-center
#
###
center = [30.320000, -97.770000]


polygon = [[[[25.774252, -82.190262],[17.466465, -65.118292],[34.321384, -63.75737],[25.774252, -82.190262]],[[25.774252, -80.190262],[32.321384, -64.75737],[18.466465, -66.118292],[25.774252, -80.190262]]]]

bermuda_center = [(polygon[0][0][0][0] + polygon[0][0][1][0]+polygon[0][0][2][0])/3.,(polygon[0][0][0][1] + polygon[0][0][1][1]+polygon[0][0][2][1])/3.]

bermuda = {'id' : 'app2',       #used for tag names
      'title': 'Bermuda Triangle',   #used for display
      'dataset1': { 
        'color': '#0000FF', #color to display on key
	'title': 'Polygon Example',
	'polygons' : [{'polygon':polygon, 
	     'fillColor': '#0000FF',
	     'fillOpacity': 1,
	     'strokeColor':'#000000'  
	          }],
        'markers' : [{'lat':bermuda_center[0],'lon':bermuda_center[1],'color':'#FF0000','title':'Click Me!','text':'The <strong>center</strong> of the <a href="http://en.wikipedia.org/wiki/Bermuda_Triangle">Bermuda Triangle</a>!'}],
	 },
      'dataset2': { 
        'color': '#000000', #color to display on key
	'title': 'Flight Path',
	
        'lines' : [{'path':[[45.5,-69.0],[18.5,-72.333]],'color':'#000000','editable':'true'}]
         }
     }


###
#
# An example of building data from an app
#
#
###

WhereWeMeet_data = {
    'id' : 'WhereWeMeet',       #used for tag names
      'title': 'Average Drive Time',   #used for display

      }

for i,polygondict in enumerate(App3.data()):
    tmp = dict()
    tmp['polygons'] = [polygondict]
    tmp['color'] = polygondict['fillColor']
    tmp['title'] = polygondict['keyValue']
    WhereWeMeet_data['dataset%s' % i] = tmp
    
    


if __name__ == '__main__':
  ff = pygmaps_ng.build_from_csv()
  ff.append(WhereWeMeet_data)
  pygmaps_ng.build_page(ff, zoom=13,outfile='example1.html')
  pygmaps_ng.build_page([bermuda],center=center,zoom=5,outfile='example2.html')
