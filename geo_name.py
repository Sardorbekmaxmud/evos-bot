from geopy import Nominatim


def get_location_address(location):
    latitude = location.latitude
    longitude = location.longitude
    geo_coder = Nominatim(user_agent="my_app")
    loc = geo_coder.reverse(f"{latitude},{longitude}")
    return loc.address

# print(get_location_address(41.4363944, 69.5453866))
