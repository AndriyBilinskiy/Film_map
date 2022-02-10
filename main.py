"""
This module adds locations where the films were shot and then find the 
closest to given locations.
"""
import json
import folium 
from geopy.geocoders import Nominatim
import argparse
import haversine


def parse():
    """
    Parsing the arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('year', type=int)
    parser.add_argument('latitude', type=float)
    parser.add_argument('longtitude', type=float)
    parser.add_argument('path', type=str)
    return parser.parse_args()


def parse_text(path: str):
    """
    Parse the text in the file.
    """
    with open(path, 'r') as file:
        strings = file.readlines()
    new_strings = []
    for string in strings:
        if '{' in string:
            start = string.find('{')
            end = string.find('}')
            string = string[:start] + string[end+1:]
        i = -1
        string = string.strip()
        if string[i] == ')':
            while string[i] != '(':
                string = string[:-1]
        string = string.replace('(',')')
        string = string.split(')')
        string = ','.join(string)
        string = string.split(',')
        string = [i.strip() for i in string]
        if '' in string:
            string.remove('')
        new_strings.append([string[0],string[1],string[2:]])
    return new_strings


def convert_location_to_coordinates(location):
    """
    this function converts text location to coordinates
    >>> convert_location_to_coordinates('Atlanta, Georgia, USA')
    (33.7489924 -84.3902644)
    """
    try:
        geoloc = Nominatim(user_agent="main.py")
        location_cord = geoloc.geocode(location)
        longitude = location_cord.longitude
        latitude = location_cord.latitude
    except:
        return(0,0)
    return(latitude, longitude)


def create_map(all_data, specific_year, start):
    """
    creates map
    """
    map = folium.Map(location=[start[0],start[1]],
    zoom_start=10)
    all_fg = folium.FeatureGroup(name='Films Including all years')
    specific = folium.FeatureGroup(name='Films shot the specific year')
    for film in all_data:
        print(film[4])
        description = film[0] + ' (' + film[1] + ')'
        all_fg.add_child(folium.Marker([film[3][0],film[3][1]], popup=description))
    for film in specific_year:
        description = film[0] + ' (' + film[1] + ')'
        specific.add_child(folium.Marker([film[3][0], film[3][1]], popup=description))
    map.add_child(specific)
    map.add_child(all_fg)
    folium.TileLayer('Stamen Terrain').add_to(map)
    map.add_child(folium.LayerControl())
    map.save('Map.html')


def main():
    """
    The main function.
    """
    args = parse()
    data = parse_text(args.path)
    start = (args.latitude, args.longtitude)
    prev_loc = ''
    prev_value = (0,0)
    year = args.year
    specific_data = []
    for i in range(len(data)):
        film = data[i]
        loc = ','.join(film[2])
        if loc == prev_loc:
            coords = prev_value
        else:
            coords = convert_location_to_coordinates(loc)
            if coords == (0,0):
                loc  = ','.join(film[2][1:])
            prev_value = coords
            prev_loc = loc
        film.append(coords)
        film.append(haversine.haversine(start,coords))
        print(film[1])
        if film[1] == str(year):
            specific_data.append(film)
    create_map(sorted(data, key = lambda x: x[4])[:10],sorted(specific_data, key = lambda x: x[4])[:10], start)


if __name__ == "__main__":
    main()
