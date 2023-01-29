"""
TODO: hook divs to on_select

New concept:
Focus on names places as nodes
Don't worry about ways (roads or buidings), just points

GAME:
Choose a base node
Gather resources from nearby nodes (producer nodes?)
Scout nodes
Expand to new base nodes
Trade between nodes (send resources)
Upgrade:
- Base node
    - Number of simultaneous producers
    - Amount you can store
    - Amount your base node collects from producers
    - Collection radius
    - Kinds of resources your base node specializes in
        - Encourage specializing for more trade
- Producers
    - Rate of production
    - What they produce
        - Specialized advanced products
        - Change what they produce
    - Probability of sudden windfalls
- Trade routes
    - Exponetially higher cost with longer distance
    - String bases together
    - Warehouses? Hubs?
    - Possibility of losing resources during transit
    - Speed of trade
    - Schedule recurring trades?
        - At time intervals
        - Over threshold
- Expansion: Scavengers
    - Fill production gaps
- Other players? (Later expansion)
    - Adversarial base nodes 
        - Diminish producers
        - Diminish enemy bases
        - Take over enemy bases
    - Interceptors
        - Steal enemy trades
        - Fight other interceptors
        - Lay siege
    - Defenses
        - Increase cost of producer -> base conversion
        - Escort trades
        - Faster trades
        - More routing options
        - Resilience to adversarial bases

Resources:
- Basic:
    - People
    - Money
    - Food
- Advances:
    - Gas
    - Home goods
    - Lumber
    - Metal
    - Electronics

Base node:
- Start with one producer slot
- Have to toggle between producers at first to obtain a range of goods
- 

"""

import os
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

class Game:

    _message = ''
    _income = 0
    # initialize date
    # date = datetime.date(2000,1,1)
    # day = datetime.timedelta(days=1)
    # month = datetime.timedelta(months=1)
    _date = 2000
    _one_year = 1
    # initialize money
    _money = 1500
    _money = 10000
    # initialize message box
    _message = ''

    _top_div_height = 20
    _date_div = Div(text="Date: "+str(_date),width=200,height=_top_div_height)
    _money_div = Div(text="Money: ${:0,.2f}".format(_money).replace('$-','-$'),width=200,height=_top_div_height)
    _income_div = Div(text="Income: ${:0,.2f}".format(_money).replace('$-','-$'),width=200,height=_top_div_height)
    _message_div = Div(text=_message,width=800,height=100)
    _table_id = TextInput(value='', title='OSM ID')
    _table_name = TextInput(value='', title='Name')
    _table_tag = TextInput(value='', title='Tag')
    _table_area = TextInput(value='',title='Area')
    _table_length = TextInput(value='',title='Length')
    _table_nearest_node = TextInput(value='',title='Nearest street node ID')

    def __init__(self):


        self._tile_provider = get_provider(Vendors.CARTODBPOSITRON)
        transformer = Transformer.from_crs('epsg:4326', 'epsg:3857')

        # get nodes in wide box to complete ways
        print('Reading node data')
        nodes_filename = '7820_Raleigh.nodes'
        if os.path.isfile(nodes_filename):
            with open(nodes_filename,'r') as nodes_file:
                response_text = nodes_file.read()

        # node_result = api.query(overpass_node_query)
        # node_result = api.parse_json(response_text)
        # # combine ways and nodes results
        # result.expand(node_result)
        # Or just use nodes
        print('Parsing node data')
        api = overpy.Overpass()
        result = api.parse_json(response_text)

        print('Organizing node data')
        node_indices = [n.id for n in result.nodes]
        lons = [float(n.lon) for n in result.nodes]
        lats = [float(n.lat) for n in result.nodes]
        # lons_web,lats_web=transform(Proj('epsg:4326'), Proj('epsg:3857'), lons,lats)
        lons_web, lats_web = transformer.transform(lats, lons)
        tags = [str(n.tags) for n in result.nodes]
        names = [n.tags['name'] if 'name' in n.tags.keys() else '' for n in result.nodes]
        # is_tagged = [tag!='{}' for tag in tags]
        is_named = [n != '' for n in names]
        # all_node_data = {'id':node_indices,
        #                 'lon':lons_web,
        #                 'lat':lats_web,
        #                 'name':names,
        #                 'tag':tags
        #                 # 'bought':[False]*len(node_indices)
        #                }
        named_node_data = {'id':list(compress(node_indices,is_named)),
                           'lon':list(compress(lons_web,is_named)),
                           'lat':list(compress(lats_web,is_named)),
                           'name':list(compress(names,is_named)),
                           'tag':list(compress(tags,is_named))
                          }
        # tagged_node_data = {'id':list(compress(node_indices,is_tagged)),
        #                     'lon':list(compress(lons_web,is_tagged)),
        #                     'lat':list(compress(lats_web,is_tagged)),
        #                     'name':list(compress(names,is_tagged)),
        #                     'tag':list(compress(tags,is_tagged))
        #                    }
        node_data = named_node_data
        self.node_cdf = ColumnDataSource(data=node_data)

        print('Plotting')
        # point_data = {'id':[0],
        #               'lon':[lon_web],
        #               'lat':[lat_web],
        #               'name':['Nearest node'],
        #               'tag':[''],
        #               'line_alpha':[0],
        #               'fill_alpha':[0]
        #              }
        # point_cdf = ColumnDataSource(data=point_data)
        # p.circle(x='lon',
        #          y='lat',
        #          source=point_cdf,
        #          color='red',
        #          line_alpha='line_alpha',
        #          fill_alpha='fill_alpha')

        # min_lon = min([min(l) for l in street_data['lon']])
        # max_lon = max([max(l) for l in street_data['lon']])
        min_lon = min(node_data['lon'])
        max_lon = max(node_data['lon'])
        lon_range = max_lon-min_lon
        lon_pad = .001+.05*lon_range
        # min_lat = min([min(l) for l in street_data['lat']])
        # max_lat = max([max(l) for l in street_data['lat']])
        min_lat = min(node_data['lat'])
        max_lat = max(node_data['lat'])
        lat_range = max_lat-min_lat
        lat_pad = .001+.05*lat_range
        self._min_lon_plot = min_lon - lon_pad
        self._max_lon_plot = max_lon + lon_pad
        self._min_lat_plot = min_lat - lat_pad
        self._max_lat_plot = max_lat + lat_pad

    # I need a way to return functions that can update the object (divs)
    # and that can be passed to on_change()
    def node_select(self,attr,old,new):
        _message = ''
        if len(self.node_cdf.selected.indices)>0:
            selected_index = self.node_cdf.selected.indices[0]
            #_table_name.value = str(self.node_cdf.data['name'][new])
            self._table_id.value = str(self.node_cdf.data['id'][selected_index])
            self._table_name.value = str(self.node_cdf.data['name'][selected_index])
            self._table_tag.value = str(self.node_cdf.data['tag'][selected_index])
            self._table_area.value = ''
            self._table_length.value = ''
        # else:
        #     _table_name.value = ''
        self.update()

    def update(self):
        _date_div.text = "Date: "+str(self._date)
        _money_div.text = "Money: ${:0,.2f}".format(self._money).replace('$-','-$')
        _message_div.text = self._message
        # Check for base nodes
        # num_base_nodes = len(base_node_data)
        # print('{} base nodes'.format(num_base_nodes))
        # print(bought_node_ids)

        # for i_base_node in range(num_base_nodes):
        #     # get base_node center
        #     x = base_node_data['lon'][i_base_node]
        #     y = base_node_data['lat'][i_base_node]
        #     cx,cy = mean_center(x,y)
        #     i_nearest_node = nearest_node(cx,cy,street_nodes_lon,street_nodes_lat)
        #     id_nearest_node = street_nodes_ids[i_nearest_node]
        #     base_node_owned = (id_nearest_node in bought_node_ids)
        #     if base_node_owned:
        #         base_node_data['color'][i_base_node] = base_node_colors[True]
        #         area = PolyArea(x,y)
        #         income += profit_per_sq_m * area
        #     else:
        #         base_node_data['color'][i_base_node] = base_node_colors[False]
        # _income_div.text = "Income: ${:0,.2f}".format(income).replace('$-','-$')
        # base_node_cdf.data = base_node_data

    @property
    def panel(self):
        p = figure(title='OSM nodes',
                   x_range=(self._min_lon_plot, self._max_lon_plot),
                   y_range=(self._min_lat_plot, self._max_lat_plot),
                   x_axis_type="mercator", 
                   y_axis_type="mercator")
        p.add_tile(self._tile_provider)
        p.circle(x='lon', y='lat', source=self.node_cdf, color='brown')
        p.add_tools(HoverTool(tooltips=[("name", "@name")]), TapTool(), BoxSelectTool())
        p = pn.Column(
            pn.Row(self._date_div,self._money_div,self._income_div),
            pn.Row(#pn.Column(p, pn.Row(buy_button,end_button)),
                   pn.Column(p),
                   pn.Column(self._table_id,
                             self._table_name, 
                             self._table_tag, 
                             self._table_length, 
                             self._table_area, 
                             self._table_nearest_node)),
            self._message_div)
        return p



# p = figure(title='OSM ways and nodes',
#            x_range=(min_lon-lon_pad,max_lon+lon_pad),
#            y_range=(min_lat-lat_pad,max_lat+lat_pad),
#            x_axis_type="mercator", 
#            y_axis_type="mercator")
# p.add_tile(tile_provider)
# p.circle(x='lon', y='lat', source=node_cdf, color='brown')
# p.add_tools(HoverTool(tooltips=[("name", "@name")]), TapTool(), BoxSelectTool())
# # show(p)

g = Game()
# p = g.panel
print('Serving')
pn.Row(g.panel).servable()

# pn.Column(pn.Row(date_div,money_div,income_div),
#           pn.Row(pn.Column(p,
#                            pn.Row(buy_button,end_button)), 
#                  pn.Column(table_id, 
#                            table_name, 
#                            table_tag, 
#                            table_length, 
#                            table_area, 
#                            table_nearest_node)), 
#           message_div).servable()

