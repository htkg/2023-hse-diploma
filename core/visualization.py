import folium
from folium.plugins import MarkerCluster
from core.utils import get_prefecture

def plot_map(json_obj):
    # Create a base map centered around Japan
    japan_map = folium.Map(location=[36.2048, 138.2529], zoom_start=5)

    # Create a dictionary to store marker clusters per prefecture
    prefecture_clusters = {}
    prefecture_stats = {}
    
    for location in json_obj.values():
        if location is not None and 'geometry' in location and 'location' in location['geometry']:
            latitude = location['geometry']['location']['lat']
            longitude = location['geometry']['location']['lng']
            name = location['formatted_address']

            # Extract the prefecture from the address_components
            prefecture = get_prefecture(location)
            if prefecture is None:
                continue
            
            if prefecture not in prefecture_stats:
                prefecture_stats[prefecture] = 0
            prefecture_stats[prefecture] += 1
            
            # If the prefecture does not already have a marker cluster, create one
            if prefecture not in prefecture_clusters:
                marker_cluster = MarkerCluster().add_to(japan_map)
                prefecture_clusters[prefecture] = marker_cluster

            marker = folium.Marker([latitude, longitude], popup=name)
            marker.add_to(prefecture_clusters[prefecture])
        else:
            None
    
    return japan_map, prefecture_stats

def count_tweets_per_prefecture(prefecture_stats):
    for prefecture, count in prefecture_stats.items():
        print(f'{prefecture}: {count}')