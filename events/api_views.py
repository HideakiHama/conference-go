from django.http import JsonResponse
from common.json import ModelEncoder
from django.views.decorators.http import require_http_methods
from .acl import get_weather, get_photo

import json
from .models import Conference, Location, State


class ConferenceListEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
    ]


@require_http_methods(["GET","POST"])
def api_list_conferences(request):

    if request.method == "GET":
        conferences = Conference.objects.all()
        return JsonResponse({"conferences": conferences},
                            encoder=ConferenceListEncoder)

    else:
        content = json.loads(request.body)

        # Get the Location object and put it in the content dict
        try:         #get id of ForeignKey from the Parent (Location)
            location = Location.objects.get(id=content["location"])
            content["location"] = location
        except Location.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid location id"},
                status=400,
            )
        conference = Conference.objects.create(**content)
        return JsonResponse(
            conference,
            encoder=ConferenceDetailEncoder,
            safe=False,
        )


class LocationListEncoder(ModelEncoder):
    model = Location
    properties = ["name"]

    def get_extra_data(self, o):
        return {"state": o.state.abbreviation}


class ConferenceDetailEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
        "description",
        "max_presentations",
        "max_attendees",
        "starts",
        "ends",
        "created",
        "updated",
        "location",
    ]

    #Tells ModelEncoder that we want to use that specific
    #encoder for the "location" property in the CongerenceDetailEncoder
    encoders = {
        "location": LocationListEncoder(),
    }

# conferences/<int:pk>/
@require_http_methods(["GET","DELETE","PUT"])
def api_show_conference(request, pk):
    if request.method == "GET":
        conference = Conference.objects.get(id=pk)
        state = conference.location.state.abbreviation
        # print(state)
        weather = get_weather(state)
        # print(weather)
        return JsonResponse({"conference": conference, "weather": weather},
                            encoder=ConferenceDetailEncoder,
                            safe=False)

    elif request.method == "DELETE":
        count, _ = Conference.objects.filter(id=pk).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        content = json.loads(request.body)
        try:
            if "location" in content:
                location = Location.objects.get(id=content["location"])
                content["location"] = location
        except Location.DoesNotExist:
            JsonResponse({"message": "Location does not exist"})

    Conference.objects.filter(id=pk).update(**content)
    conference = Conference.objects.get(id=pk)

    return JsonResponse(
        conference,
        ConferenceDetailEncoder,
        safe=False,
    )

# locations/
@require_http_methods(["GET", "POST"])
def api_list_locations(request):
    if request.method == "GET":
        locations = Location.objects.all()
        return JsonResponse({"location": locations},
                            encoder=LocationListEncoder)
    else:
        content = json.loads(request.body)

        # Error handeling
        try:
            # Get the State object and put it in the content dic
            #abbreviation equal to the value of the key "state"
            state = State.objects.get(abbreviation=content["state"])
            content["state"] = state
        except State.DoesNotExist:
            return JsonResponse({"messgae": "Invalid state abbreviation"},
                                status=400)

        photo = get_photo(content["city"], content["state"])
        # print(photo)
        content.update(**photo)  #check

        locations = Location.objects.create(**content)
        return JsonResponse(locations, encoder=LocationDetailEncoder,
                            safe=False)



class LocationDetailEncoder(ModelEncoder):
    model = Location
    properties = [
        "name",
        "city",
        "room_count",
        "created",
        "updated",
        "picture_url"
    ]

    def get_extra_data(self, o):
        return {"state": o.state.abbreviation}

# locations/<int:pk>/
@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_location(request, pk):
    if request.method == "GET":
        location = Location.objects.get(id=pk)
        return JsonResponse(location,
                            encoder=LocationDetailEncoder,
                            safe=False)
    elif request.method == "DELETE":
        count, _ = Location.objects.filter(id=pk).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        content = json.loads(request.body)
        try:
            if "state" in content:
                state = State.objects.get(abbreviation=content["state"])
                content["state"] = state
        except State.DoesNotExist:
            return JsonResponse({"message": "Invalid state abbreviation"},
                                status=400,)

        Location.objects.filter(id=pk).update(**content)

        location = Location.objects.get(id=pk)
        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False,
        )
