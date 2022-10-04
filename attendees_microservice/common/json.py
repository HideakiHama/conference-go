from json import JSONEncoder
from datetime import datetime
from django.db.models import QuerySet


# Object of type datetime is not JSON serializable
class DateEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        else:
            return super().default(o)


# Object of type QuerySet is not JSON serializable
class QuerySetEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, QuerySet):
            return list(o)
        else:
            return super().default(o)


class ModelEncoder(DateEncoder, QuerySetEncoder, JSONEncoder):
            # empty encoder dictionary is for some CustomEncoder we created
            # in View don't have a encoders variable
            # LocationDetailEncoder doesnt have encodervariable
            # ConferenceDetailEncoder have a encoder variable
            #otherwise without encoder={} the ModelEncoder wont able to run
    encoders = {}

    def default(self, o):
        if isinstance(o, self.model):

            d = {}
            if hasattr(o, "get_api_url"):
                d["href"] = o.get_api_url()
            for property in self.properties:
                value = getattr(o, property)
                if property in self.encoders:
                    #for the location encoder
                    encoder = self.encoders[property]
                    value = encoder.default(value)
                d[property] = value
            d.update(self.get_extra_data(o))
            return d
        else:
            return super().default(o)

    def get_extra_data(self, o):
        return {}
