from pygmaps_ng import Map, App, DataSet, map_from_csvs
import WhereWeMeet as App3

'''
Run to build the example pages of pymaps-ng
'''
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

app_id = 'wherewemeet'
contour_app = App(app_id,title="Composite Drive Time")

for i,d in enumerate(App3.data()):
    this = DataSet('%s%s'%(app_id,i),title = d['keyValue'])
    this.add_polygon(d['polygon'],fillColor=d['fillColor'],strokeColor=d['strokeColor'],fillOpacity=d['fillOpacity'])
    this.key_color = d['fillColor']
    print d['fillColor']
    contour_app.datasets.append(this)
    
    


if __name__ == '__main__':
  Austin = [30.320000, -97.770000]
  mymap = map_from_csvs(data_dir = './example_data')
  mymap.build_page(center=Austin,zoom=5,outfile='from_csv_example.html')
  mymap.apps.append(contour_app)
  mymap.build_page(center=Austin,zoom=9,outfile='two_apps.html')
