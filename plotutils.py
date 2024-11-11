import matplotlib.pyplot as plt
import numpy as np
from cartopy import crs as ccrs, feature as cfeature
import matplotlib.ticker as mticker
from matplotlib import colors, cm
import math 

def make_basic_plot():
    # setting up the initial "canvas" we'll put the figure on
    fig = plt.figure(figsize=(9,6)) # figsize specifies shape of figure
    # what type of globe projection we want and where we want it centered:
    ax = plt.axes(projection=ccrs.Robinson(central_longitude=-103)) 

    # configure gridlines across the map
    gl = ax.gridlines(linewidth=0.1, color='black')
    # Set the interval for longitude and latitude gridlines
    gl.xlocator = mticker.FixedLocator(range(-180, 181, 10))  # Longitude every 10 degrees
    gl.ylocator = mticker.FixedLocator(range(-90, 91, 10))    # Latitude every 10 degrees

    ax.coastlines() # coastlines
    return fig, ax

COLOR_PRESETS = {
    'temperature': 
        ('#323897', # dark blue
         '#FFFEBE', # light yellow
         '#A60026'  # dark red
        ),
    'humidity': 
        ('#FF9D35',
         '#ffffff',
         '#CB77FF'),
    'precipitation': # colors from https://unidata.github.io/python-gallery/examples/Precipitation_Map.html
        [(1.0, 1.0, 1.0),
        (0.3137255012989044, 0.8156862854957581, 0.8156862854957581),
        (0.0, 1.0, 1.0),
        (0.0, 0.8784313797950745, 0.501960813999176),
        (0.0, 0.7529411911964417, 0.0),
        (0.501960813999176, 0.8784313797950745, 0.0),
        (1.0, 1.0, 0.0),
        (1.0, 0.6274510025978088, 0.0),
        (1.0, 0.0, 0.0),
        (1.0, 0.125490203499794, 0.501960813999176),
        (0.9411764740943909, 0.250980406999588, 1.0),
        (0.501960813999176, 0.125490203499794, 1.0),
        (0.250980406999588, 0.250980406999588, 1.0),
        (0.125490203499794, 0.125490203499794, 0.501960813999176),
        (0.125490203499794, 0.125490203499794, 0.125490203499794),
        (0.501960813999176, 0.501960813999176, 0.501960813999176),
        (0.8784313797950745, 0.8784313797950745, 0.8784313797950745),
        (0.9333333373069763, 0.8313725590705872, 0.7372549176216125),
        (0.8549019694328308, 0.6509804129600525, 0.47058823704719543),
        (0.6274510025978088, 0.42352941632270813, 0.23529411852359772),
        (0.4000000059604645, 0.20000000298023224, 0.0)]
}

def interpolation_sigmoid(x):
    # designed to take vals between 0 and 1, and make them more squished towards 0 or 1
    return 1 / (1 + math.exp(32-64*x))

def interpolate_hex_colors(color1, color2, n, anomaly=False):
    # Parse the hex colors into RGB components
    r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
    r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
    
    # Create a list to store the interpolated colors
    colors = []
    
    for i in range(n):
        # Calculate the interpolation factor
        t = i / (n - 1)
        if anomaly:
            t = interpolation_sigmoid(t)
        
        # Interpolate each color component
        r = round(r1 + (r2 - r1) * t)
        g = round(g1 + (g2 - g1) * t)
        b = round(b1 + (b2 - b1) * t)
        
        # Format the interpolated color as a hex string and add to the list
        interpolated_color = f"#{r:02X}{g:02X}{b:02X}"
        colors.append(interpolated_color)
    
    return colors

def make_custom_colormap(min, max, n, task='temperature', anomaly=False):
    if task not in COLOR_PRESETS.keys():
        raise ValueError(f'Incorrect task for custom_colormap. task must be one of {COLOR_PRESETS.keys()}')
    if task == 'precipitation':
        colorlist = COLOR_PRESETS[task]
    else:
        edge_colors = COLOR_PRESETS[task]
        
        offset = n%2 # repeat middle color if n is even 
        m = math.ceil(n/2)
        colorlist = interpolate_hex_colors(edge_colors[0], edge_colors[1], m, anomaly) + \
                interpolate_hex_colors(edge_colors[1], edge_colors[2], m, anomaly)[offset:] 
    cmap = colors.ListedColormap(colorlist)
    
    n_bins = len(colorlist)
    size_bin = (max-min)/n_bins 
    bounds = [min+i*size_bin for i in range(n_bins)]+[max]
    norm = colors.BoundaryNorm(bounds, cmap.N)
    
    return cmap, norm
