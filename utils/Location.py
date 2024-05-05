class Location:
    def __init__(self, address):
        self.address = address
        self.url = 'https://nominatim.openstreetmap.org/search?q=' + self.address +'&format=json'
        self.line = (0.04276, 1, -108.93376)
    def parse_to_json(self):
        response_API = requests.get(self.url)
        data = response_API.text[1:-1].split("},{")
        if (data!=['']):
            if (len(data) > 1):
                data = data[0] + "}"
            else:
                data = data[0]
            return json.loads(data)
        else: 
            return None
    def get_lat(self):
        data = self.parse_to_json()
        if (data):
            latitude = float(data["lat"])
        else:
            latitude = 0
        return latitude
    def get_long(self):
        data = self.parse_to_json()
        if data:
            longitude = float(data["lon"])
        else:
            longitude = 0
        return longitude