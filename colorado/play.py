'''
TODO:

GRAPHICS
    Draw buildings as patches
    Color owned buildings 
    Color buildings when nearest road is selected
    Color roads with buildings differently
    Write building names on map
    Write areas/lengths on map, or on hover tooltip

DATA
    Set up better data structures
        Less memory (no unnecessary tags)
        Easy to search
        Easy to append to
    Allow queries at larger scale
        Only include certain highways, nodes, etc
        May need to pay based on nodes, not buildings
    Name buildings based on nodes they contain
    Convert buildings into nodes?
    Use address to choose nearest street node intelligently
    Explore by performing another query
    Assign road speeds
    Allow purchases of pieces of road
    Assign building resource based on building type

GAMEPLAY
    Tune road costs and building income
    Add road maintenance
        Cost per turn, OR
        # turns before road needs repair
    Account for road speed
    Add different resources
        Choose which resource a given road/building produces
    Add things to buy
        trucks/buses
        drivers
        mechanics
        employees
    Add tech tree/upgrades
        faster trucks
        increase income per building
        decrease road maintenance costs
        decrease time per turn
        decrease cost per truck
    Add losing roads
    Add selling roads
    Add depots
'''

from game import Game

'''
import os
# import pickle
import requests
import json
from itertools import compress
import math

import numpy as np
# from pyproj import Proj, transform
from pyproj import Transformer
# import pandas as pd
# import geopandas as gpd
# import geoviews as gv
# from cartopy import crs
import overpy

from bokeh.io.doc import curdoc
from bokeh.io import show, output_file
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, GraphRenderer, StaticLayoutProvider, Oval, GeoJSONDataSource, Div
from bokeh.events import ButtonClick
from bokeh.palettes import Spectral8
from bokeh.models.tools import HoverTool,TapTool,BoxSelectTool
from bokeh.tile_providers import get_provider, Vendors
from bokeh.models.widgets import TextInput, Button
from bokeh.layouts import widgetbox, row, column, gridplot
import panel as pn
# import param

# gv.extension('bokeh')

def get_ip_data():
    """  Function To Print GeoIP Latitude & Longitude """
    ip_request = requests.get('https://get.geojs.io/v1/ip.json')
    my_ip = ip_request.json()['ip']
    geo_request = requests.get('https://get.geojs.io/v1/ip/geo/' +my_ip + '.json')
    geo_data = geo_request.json()
    return geo_data

def PolyArea(x,y):
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

def PolyLength(x,y):
    return np.sum(np.sqrt(np.diff(x)**2+np.diff(y)**2))

def mean_center(x,y):
    return (np.mean(x),np.mean(y))

def nearest_node(xp,yp,x,y):
    # print(type(xp), type(yp), type(x), type(y))
    xn = x-xp
    yn = y-yp
    # xn = np.array(x) - xp
    # yn = np.array(y) - yp
    d = np.sqrt(xn**2+yn**2)
    return np.argmin(d)

street_highways = [
    'motorway',
    'trunk',
    'primary',
    'secondary',
    'tertiary',
    'motorway_link',
    'trunk_link',
    'primary_link',
    'secondary_link',
    'tertiary_link',
    'unclassified',
    'residential',
    'living_street',
    'service'#,
    # 'track',
    # 'pedestrian'
]

def get_streets(ways):
    way_streets = []
    for w in ways:
        if 'highway' in w.tags:
            if w.tags['highway'] in street_highways:
                way_streets.append(w)
    return way_streets

# ip_data = get_ip_data()
# lon = float(ip_data['longitude'])
# lat = float(ip_data['latitude'])

#lon = ip_data['longitude']
#lat = ip_data['latitude']

# my address
lon = -105.2201
lat = 39.75345
# ip_lonlat = gv.Points((lon,lat))

dlon = .02
dlat = .02
south = lat-dlat/2
north = lat+dlat/2
west = lon-dlon/2
east = lon+dlon/2

overpass_url = "http://overpass-api.de/api/interpreter"
ways_filename = '811_14th.ways'
if os.path.isfile(ways_filename):
    with open(ways_filename,'r') as ways_file:
        response_text = ways_file.read()
else:
    overpass_query = ("""
    [out:json][bbox:"""+str(south)+""","""+str(west)+""","""+str(north)+""","""+str(east)+"""];
    (way;);
    out;
    """)
    print('Querying Overpass for ways...')
    response = requests.get(overpass_url,
                            params={'data': overpass_query})
    response_text = response.text
    with open(ways_filename,'w') as ways_file:
        ways_file.write(response_text)

api = overpy.Overpass()
result = api.parse_json(response_text)
# with open(ways_filename,'wb') as ways_file:
    # pickle.dump(result,ways_file)

# get nodes in wide box to complete ways
nodes_filename = '811_14th.nodes'
if os.path.isfile(nodes_filename):
    with open(nodes_filename,'r') as nodes_file:
        response_text = nodes_file.read()
else:
    # dnode = 0.5
    dnode = 0.1
    overpass_node_query = ("""
    [out:json][bbox:"""+str(south-dnode)+""","""+str(west-dnode)+""","""+str(north+dnode)+""","""+str(east+dnode)+"""];
    (node;);
    out;
    """)
    print('Querying Overpass for nodes...')
    response = requests.get(overpass_url,
                            params={'data': overpass_node_query})
    response_text = response.text
    with open(nodes_filename,'w') as nodes_file:
        nodes_file.write(response_text)

# node_result = api.query(overpass_node_query)
node_result = api.parse_json(response_text)
# combine ways and nodes results
result.expand(node_result)

# set prices
cost_per_m = 1
profit_per_sq_m = 1

# initialize date
# date = datetime.date(2000,1,1)
# day = datetime.timedelta(days=1)
# month = datetime.timedelta(months=1)
date = 2000
one_year = 1
# initialize money
money = 1500
money = 10000
# initialize message box
message = ''




# Plot only named nodes
print('Loading node data...')
tile_provider = get_provider(Vendors.CARTODBPOSITRON)
transformer = Transformer.from_crs('epsg:4326', 'epsg:3857')

node_indices = [n.id for n in result.nodes]
lons = [float(n.lon) for n in result.nodes]
lats = [float(n.lat) for n in result.nodes]
# lons_web,lats_web=transform(Proj('epsg:4326'), Proj('epsg:3857'), lons,lats)
lons_web, lats_web = transformer.transform(lats, lons)
tags = [str(n.tags) for n in result.nodes]
names = [n.tags['name'] if 'name' in n.tags.keys() else '' for n in result.nodes]
is_tagged = [tag!='{}' for tag in tags]
is_named = [n != '' for n in names]
all_node_data = {'id':node_indices,
                'lon':lons_web,
                'lat':lats_web,
                'name':names,
                'tag':tags
                # 'bought':[False]*len(node_indices)
               }
named_node_data = {'id':list(compress(node_indices,is_named)),
                   'lon':list(compress(lons_web,is_named)),
                   'lat':list(compress(lats_web,is_named)),
                   'name':list(compress(names,is_named)),
                   'tag':list(compress(tags,is_named))
                  }
tagged_node_data = {'id':list(compress(node_indices,is_tagged)),
                    'lon':list(compress(lons_web,is_tagged)),
                    'lat':list(compress(lats_web,is_tagged)),
                    'name':list(compress(names,is_tagged)),
                    'tag':list(compress(tags,is_tagged))
                   }
node_data = named_node_data
node_cdf = ColumnDataSource(data=node_data)

# Plot only ways that are buildings
print('Loading way data...')
# is_building = ['building' in w.tags.keys() for w in result.ways]
buildings = [w for w in result.ways if 'building' in w.tags.keys()]

# lats and lons are now lists of lists
lons_web = []
lats_web = []
complete_buildings = []
buildings_incomplete_data = 0
for w in buildings:
    # lons_way = [float(n.lon) for n in w.get_nodes(resolve_missing=True)]
    # lats_way = [float(n.lat) for n in w.get_nodes(resolve_missing=True)]
    try:
        lons_way = [float(n.lon) for n in w.nodes]
        lats_way = [float(n.lat) for n in w.nodes]
        # lons_web_way, lats_web_way = transform(Proj('epsg:4326'),
        #                                        Proj('epsg:3857'),
        #                                        lons_way,lats_way)
        lons_web_way, lats_web_way = transformer.transform(lats_way, lons_way)
        lons_web.append(lons_web_way)
        lats_web.append(lats_web_way)
        complete_buildings.append(w)
        if len(lons_web)%1000==0:
            print(str(len(complete_buildings))+' of '+str(len(buildings)))
    except overpy.exception.DataIncomplete:
        buildings_incomplete_data += 1
print(str(buildings_incomplete_data)+' buildings with missing nodes')

building_colors = ['grey','green']
building_ids = [w.id for w in complete_buildings]
tags = [str(w.tags) for w in complete_buildings]
names = [w.tags['name'] if 'name' in w.tags.keys() else '' for w in complete_buildings]
colors = [building_colors[False] for w in complete_buildings]
is_tagged = [tag!='{}' for tag in tags]
is_named = [n != '' for n in names]
named_way_data = {'id':list(compress(building_ids,is_named)),
                   'lon':list(compress(lons_web,is_named)),
                   'lat':list(compress(lats_web,is_named)),
                   'name':list(compress(names,is_named)),
                   'tag':list(compress(tags,is_named)),
                   'color':list(compress(colors,is_named))
                  }
all_way_data = {'id':building_ids,
                'lon':lons_web,
                'lat':lats_web,
                'name':names,
                'tag':tags,
                'color':colors
               }

building_data = all_way_data
building_cdf = ColumnDataSource(data=building_data)

# Plot ways that are streets
print('Loading way data...')
# is_building = ['building' in w.tags.keys() for w in result.ways]
# streets = [w for w in result.ways if 'highway' in w.tags.keys()]
streets = get_streets(result.ways)

# lats and lons are now lists of lists
lons_web = []
lats_web = []
complete_streets = []
streets_incomplete_data = 0
for w in streets:
    # lons_way = [float(n.lon) for n in w.get_nodes(resolve_missing=True)]
    # lats_way = [float(n.lat) for n in w.get_nodes(resolve_missing=True)]
    try:
        lons_way = [float(n.lon) for n in w.nodes]
        lats_way = [float(n.lat) for n in w.nodes]
        # lons_web_way, lats_web_way = transform(Proj('epsg:4326'),
        #                                        Proj('epsg:3857'),
        #                                        lons_way,lats_way)
        lons_web_way, lats_web_way = transformer.transform(lats_way, lons_way)
        lons_web.append(lons_web_way)
        lats_web.append(lats_web_way)
        complete_streets.append(w)
        if len(lons_web)%1000==0:
            print(str(len(complete_streets))+' of '+str(len(streets)))
    except overpy.exception.DataIncomplete:
        streets_incomplete_data += 1
print(str(streets_incomplete_data)+' streets with missing nodes')

street_colors = ['tan','blue']
# nonselection_street_colors = ['grey','yellow']
street_ids = [w.id for w in complete_streets]
street_node_ids = [[n.id for n in w.nodes] for w in complete_streets]
tags = [str(w.tags) for w in complete_streets]
names = [w.tags['name'] if 'name' in w.tags.keys() else '' for w in complete_streets]
colors = [street_colors[False] for w in complete_streets]
# nonselection_colors = [nonselection_street_colors[False] for w in complete_streets]
is_tagged = [tag!='{}' for tag in tags]
is_named = [n != '' for n in names]
named_way_data = {'id':list(compress(street_ids,is_named)),
                  'node_ids':list(compress(street_node_ids,is_named)),
                  'lon':list(compress(lons_web,is_named)),
                  'lat':list(compress(lats_web,is_named)),
                  'name':list(compress(names,is_named)),
                  'tag':list(compress(tags,is_named)),
                  'color':list(compress(colors,is_named))
                  # 'nonselection_color':list(compress(nonselection_colors,is_named))
                  }
all_way_data = {'id':street_ids,
                'node_ids':street_node_ids,
                'lon':lons_web,
                'lat':lats_web,
                'name':names,
                'tag':tags,
                'color':colors
                # 'nonselection_color':nonselection_colors
               }

street_data = all_way_data
street_cdf = ColumnDataSource(data=street_data)

# lon_web,lat_web=transform(Proj('epsg:4326'), Proj('epsg:3857'), lon,lat)
lon_web,lat_web = transformer.transform(lat, lon)
point_data = {'id':[0],
              'lon':[lon_web],
              'lat':[lat_web],
              'name':['Nearest node'],
              'tag':[''],
              'line_alpha':[0],
              'fill_alpha':[0]
             }
point_cdf = ColumnDataSource(data=point_data)

# set first bought way
bought_way_ids = [581208335]
first_way = next(w for w in result.ways if w.id in bought_way_ids)
# initialize bought list with nodes
bought_node_ids = [n.id for n in first_way.nodes]
way_index = street_data['id'].index(bought_way_ids[0])
street_data['color'][way_index] = street_colors[True]
# street_data['nonselection_color'][way_index] = nonselection_street_colors[True]
street_cdf.data = street_data

min_lon = min([min(l) for l in street_data['lon']])
max_lon = max([max(l) for l in street_data['lon']])
lon_range = max_lon-min_lon
lon_pad = .001+.05*lon_range

min_lat = min([min(l) for l in street_data['lat']])
max_lat = max([max(l) for l in street_data['lat']])
lat_range = max_lat-min_lat
lat_pad = .001+.05*lat_range

p = figure(title='OSM ways and nodes',
           x_range=(min_lon-lon_pad,max_lon+lon_pad),
           y_range=(min_lat-lat_pad,max_lat+lat_pad),
           x_axis_type="mercator", 
           y_axis_type="mercator")
p.add_tile(tile_provider)
p.multi_line(xs='lon',
             ys='lat',
             source=street_cdf,
             line_color='color',
             nonselection_line_color='color',
             nonselection_line_alpha=0.35)
p.multi_line(xs='lon',
             ys='lat',
             source=building_cdf,
             line_color='color',
             nonselection_line_color='color',
             nonselection_line_alpha=0.35)
# p.circle(x='lon', y='lat', source=node_cdf, color='brown')
p.circle(x='lon',
         y='lat',
         source=point_cdf,
         color='red',
         line_alpha='line_alpha',
         fill_alpha='fill_alpha')
p.add_tools(HoverTool(tooltips=[("name", "@name")]), TapTool(), BoxSelectTool())
# show(p)

top_div_height = 20
date_div = Div(text="Date: "+str(date),width=200,height=top_div_height)
money_div = Div(text="Money: ${:0,.2f}".format(money).replace('$-','-$'),width=200,height=top_div_height)
income_div = Div(text="Income: ${:0,.2f}".format(money).replace('$-','-$'),width=200,height=top_div_height)
message_div = Div(text=message,width=800,height=100)
table_id = TextInput(value='', title='OSM ID')
table_name = TextInput(value='', title='Name')
table_tag = TextInput(value='', title='Tag')
table_area = TextInput(value='',title='Area')
table_length = TextInput(value='',title='Length')
table_nearest_node = TextInput(value='',title='Nearest street node ID')

def Update():
    global income
    income = 0
    date_div.text = "Date: "+str(date)
    money_div.text = "Money: ${:0,.2f}".format(money).replace('$-','-$')
    message_div.text = message
    # Check for owned buildings
    num_buildings = len(building_data[next(iter(building_data))])
    # print('{} buildings'.format(num_buildings))
    # print(bought_node_ids)
    # print(bought_way_ids)
    street_nodes_lon = [l for li in street_cdf.data['lon'] for l in li]
    street_nodes_lat = [l for li in street_cdf.data['lat'] for l in li]
    street_nodes_id = [id for id,li in zip(street_cdf.data['id'],
                                           street_cdf.data['lon']) for l in li]
    # street_nodes_ids = [n.id for id,li in zip(street_cdf.data['id'], 
                                              # street_cdf.data['lon']) for l in li]
    street_nodes_ids = [i for li in street_cdf.data['node_ids'] for i in li]

            # street_id = street_cdf.data['id'][selected_index]
            # way = next(w for w in complete_streets if w.id==street_id)
            # shares_bought_node = any(n.id in bought_node_ids for n in way.nodes)


    for i_building in range(num_buildings):
        # get building center
        x = building_data['lon'][i_building]
        y = building_data['lat'][i_building]
        cx,cy = mean_center(x,y)
        i_nearest_node = nearest_node(cx,cy,street_nodes_lon,street_nodes_lat)
        id_nearest_node = street_nodes_ids[i_nearest_node]
        building_owned = (id_nearest_node in bought_node_ids)
        if building_owned:
            building_data['color'][i_building] = building_colors[True]
            area = PolyArea(x,y)
            income += profit_per_sq_m * area
        else:
            building_data['color'][i_building] = building_colors[False]
    income_div.text = "Income: ${:0,.2f}".format(income).replace('$-','-$')
    building_cdf.data = building_data



def node_select(attr,old,new):
    global message
    message = ''
    if len(node_cdf.selected.indices)>0:
        selected_index = node_cdf.selected.indices[0]
        #table_name.value = str(node_cdf.data['name'][new])
        table_id.value = str(node_cdf.data['id'][selected_index])
        table_name.value = str(node_cdf.data['name'][selected_index])
        table_tag.value = str(node_cdf.data['tag'][selected_index])
        table_area.value = ''
        table_length.value = ''
    # else:
    #     table_name.value = ''
    Update()

def building_select(attr,old,new):
    global message
    message = ''
    if len(building_cdf.selected.indices)>0:
        selected_index = building_cdf.selected.indices[0]
        table_id.value = str(building_cdf.data['id'][selected_index])
        table_name.value = str(building_cdf.data['name'][selected_index])
        table_tag.value = str(building_cdf.data['tag'][selected_index])
        x = building_cdf.data['lon'][selected_index]
        y = building_cdf.data['lat'][selected_index]
        table_area.value = str(int(round(PolyArea(x,y))))
        table_length.value = str(0)
        building_center_x,building_center_y = mean_center(x,y)
        street_nodes_lon = [l for li in street_cdf.data['lon'] for l in li]
        street_nodes_lat = [l for li in street_cdf.data['lat'] for l in li]
        i_nearest_node = nearest_node(building_center_x,
                                      building_center_y,
                                      street_nodes_lon,
                                      street_nodes_lat)
        street_nodes_id = [id for id,li in zip(street_cdf.data['id'],
                                                street_cdf.data['lon']) for l in li]
        table_nearest_node.value = str(street_nodes_id[i_nearest_node])
        point_cdf.data['lon']=[street_nodes_lon[i_nearest_node]]
        point_cdf.data['lat']=[street_nodes_lat[i_nearest_node]]
        point_cdf.data['fill_alpha']=[1]
    else:
        point_cdf.data['fill_alpha']=[0]
    #     table_name.value = ''
    Update()

def street_select(attr,old,new):
    global message
    message = ''
    if len(street_cdf.selected.indices)>0:
        selected_index = street_cdf.selected.indices[0]
        table_id.value = str(street_cdf.data['id'][selected_index])
        table_name.value = str(street_cdf.data['name'][selected_index])
        table_tag.value = str(street_cdf.data['tag'][selected_index])
        x = street_cdf.data['lon'][selected_index]
        y = street_cdf.data['lat'][selected_index]
        table_area.value = str(0)
        table_length.value = str(int(round(PolyLength(x,y))))
    # else:
    #     table_name.value = ''
    Update()

def buy(event):
    global bought_node_ids
    global money
    global message
    message = ''
    # Check if a street is selected
    if len(street_cdf.selected.indices)>0:
        selected_index = street_cdf.selected.indices[0]
        # TODO: Track bought ways better
        if street_data['color'][selected_index] == street_colors[False]:
            # Check if it shared a node with a way that's already bought
            # first, get way from index
            street_id = street_cdf.data['id'][selected_index]
            way = next(w for w in complete_streets if w.id==street_id)
            shares_bought_node = any(n.id in bought_node_ids for n in way.nodes)
            if shares_bought_node:
                # Check if we can afford it
                x = street_cdf.data['lon'][selected_index]
                y = street_cdf.data['lat'][selected_index]
                way_length = PolyLength(x,y)
                cost = way_length*cost_per_m
                if money >= cost:
                    # Buy it!
                    money -= cost
                    street_data['color'][selected_index] = street_colors[True]
                    # street_data['nonselection_color'][selected_index] = nonselection_street_colors[True]
                    street_cdf.data = street_data
                    # add nodes to bought list
                    bought_node_ids += [n.id for n in way.nodes]
                else:
                    message = 'Cannot afford to buy'
            else:
                message = 'Must buy adjoining street first'
        else:
            message = 'Street already purchased'
    else:
        message = 'No street selected'
    Update()

def end_turn(event):
    global date
    global money
    global income
    global message
    date += one_year
    money += income
    message = 'New turn'
    Update()



buy_button = Button(label="Buy", button_type="success")
end_button = Button(label="End turn", button_type="primary")

buy_button.on_event(ButtonClick,buy)
end_button.on_event(ButtonClick,end_turn)
node_cdf.selected.on_change('indices', node_select)
building_cdf.selected.on_change('indices', building_select)
street_cdf.selected.on_change('indices', street_select)

Update()

pn.Column(pn.Row(date_div,money_div,income_div),
          pn.Row(pn.Column(p,
                           pn.Row(buy_button,end_button)), 
                 pn.Column(table_id, 
                           table_name, 
                           table_tag, 
                           table_length, 
                           table_area, 
                           table_nearest_node)), 
          message_div).servable()

# layout = row(p,table_name)
# curdoc().add_root(layout)
# output_notebook()
# show(p)
'''



