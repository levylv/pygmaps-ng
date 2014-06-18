pygmaps-ng
======

Create stand alone google maps data visualizations.

Data is grouped into datasets of points, lines and complex polygons, which are grouped into Apps.  Visibility of data sets and groups of data sets (apps) can be toggled.

example:

    from pygmaps_ng import *
    
    mymap = Map()
    app1 = App('test1',title="Test #1")
    mymap.apps.append(app1)

    dataset1 = DataSet('data1', title="Point test" ,key_color='FF0088')
    app1.datasets.append(dataset1)

    pt = [40.7,-74.0]
    dataset1.add_marker(pt ,title="click me",color="000000",text="<a href='http://en.wikipedia.org/wiki/New_York'>New York!</a>")

    mymap.build_page(center=pt,zoom=14,outfile="NYC.html")
