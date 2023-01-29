'''
Questions
1. How to store edge data?
    In an mxn grid, there are (m-1)n + (n-1)m orthogonal edges
    There are 2(m-1)(n-1) diagonal edges
    Total = 4(m-1)(n-1) + m + n - 2
          = 2mn - 2n - 2m + 2 + mn - n + mn - m
          = 4mn - 3m - 3n + 2
          = (2m - 3/2)(2n - 3/2) - 1/4
2. How to split roads up? Need to have each piece be intersection-free
'''

import numpy as np
import pandas as pd

from pyproj import Transformer
import geopandas as gpd

from bokeh.io import show
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, GeoJSONDataSource, Span
from bokeh.models.tools import HoverTool,TapTool
from bokeh.tile_providers import get_provider, Vendors


def grid_path(path_x, path_y, grid_x, grid_y):
    # Interpolate path onto grid nodes
    assert len(path_x) == len(path_y)
    path_length = len(path_x)
    grid_path_x = []
    grid_path_y = []

    # Start at nearest grid node to path start
    start_node_x, start_node_y = nearest_grid_node(path_x[0], path_y[0], grid_x, grid_y)
    grid_path_x.append(start_node_x)
    grid_path_y.append(start_node_y)
    i_path = 1

    # Find the intersection of the path and a 2x2 box around the node
    # while i_path < path_length:



def nearest_grid_node(x, y, grid_x, grid_y):
    # Find closest grid node to (x, y)
    return None


## From play.ipynb
def make_colorado_map():
    colo_lon = (-109.05, -102.05)
    colo_lat = (37., 41.)
    south, north = colo_lat
    west, east = colo_lon

    transformer = Transformer.from_crs('epsg:4326', 'epsg:3857')
    colo_lons_web, colo_lats_web = transformer.transform(colo_lat, colo_lon)

    tile_provider = get_provider(Vendors.CARTODBPOSITRON)
    #tile_provider = get_provider(Vendors.ESRI_IMAGERY)
    #tile_provider = get_provider(Vendors.STAMEN_TERRAIN)
    #tile_provider = get_provider(Vendors.STAMEN_TONER)


    highways_shp = gpd.read_file(
        "data/tl_2015_08_prisecroads/tl_2015_08_prisecroads.shp")

    highways_web = highways_shp.to_crs(epsg=3857)
    highways_gds = GeoJSONDataSource(geojson=highways_web.to_json())

    cities_shp = gpd.read_file(
        "data/Colorado_City_Boundaries/Colorado_City_Boundaries.shp")

    cities_web = cities_shp.to_crs(epsg=3857)
    cities_web['FULLNAME'] = cities_web['NAME10']
    # Convert GeoDataFrames into GeoJSONDataSource objects (similar to ColumnDataSource)
    cities_gds = GeoJSONDataSource(geojson=cities_web.to_json())


    p = figure(title='CO cities',
               x_range=colo_lons_web,
               y_range=colo_lats_web,
               x_axis_type="mercator", 
               y_axis_type="mercator")

    p.add_tile(tile_provider)
    p.multi_line(xs='xs',
                 ys='ys',
                 source=highways_gds, color='grey',
                 legend_label='Highways'
                )
    p.patches('xs', 'ys', source=cities_gds, fill_color='green', fill_alpha=0.5,
              line_color='green',
              legend_label='Cities'
             )


    span_lons = np.linspace(colo_lons_web[0], colo_lons_web[1], 37)
    # span_lats = np.linspace(colo_lats_web[0], colo_lats_web[1], 37)
    # let's make latitude grid lines have the same spacing, and center them on the center of the state
    lon_center = sum(colo_lons_web)/2
    lat_center = sum(colo_lats_web)/2
    span_lats = span_lons - lon_center + lat_center


    for span_lon in span_lons:
        vertical_span = Span(location=span_lon, name='{}'.format(span_lon),
                             dimension='height', line_color='blue',
                             #line_dash='dashed', 
                             line_width=1)
        p.add_layout(vertical_span)
        

    for span_lat in span_lats:
        horizontal_span = Span(location=span_lat,
                               dimension='width', line_color='blue',
                               #line_dash='dashed', 
                               line_width=1)
        p.add_layout(horizontal_span)


    span_lon_centers = (span_lons[:-1] + span_lons[1:])/2
    span_lat_centers = (span_lats[:-1] + span_lats[1:])/2


    grid_x, grid_y = np.meshgrid(span_lon_centers, span_lat_centers)
    grid_i, grid_j = np.meshgrid(np.arange(6, 42), np.arange(6, 42)[::-1])
    grid_df = pd.DataFrame({'x': grid_x.flatten(),
                            'y': grid_y.flatten(),
                            'i': grid_i.flatten(),
                            'j': grid_j.flatten()
                           })
    grid_cdf = ColumnDataSource(grid_df)
    p.circle(source=grid_cdf, color='brown', legend_label='Grid centers')


    p.legend.click_policy="hide"
    #p.add_tools(HoverTool(tooltips=[("name", "@FULLNAME"), ("x, y", "($x, $y)")]), TapTool())#, BoxSelectTool())
    p.add_tools(HoverTool(tooltips=[("name", "@FULLNAME"), ("grid", "(@i, @j)")]), TapTool())#, BoxSelectTool())


    show(p)
