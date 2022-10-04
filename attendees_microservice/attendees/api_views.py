from django.http import JsonResponse
from common.json import ModelEncoder
from django.views.decorators.http import require_http_methods
import json

from .models import Attendee, ConferenceVO



class ConferenceVODetailEncoder(ModelEncoder):
    model = ConferenceVO
    properties = ["name", "import_href"]

class AttendeeListEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "name"
    ]


@require_http_methods({"GET","POST"})
def api_list_attendees(request, conference_vo_id=None):
    if request.method == "GET":
        attendees = Attendee.objects.filter(conference=conference_vo_id)
        return JsonResponse({"attendees": attendees},
                            encoder=AttendeeListEncoder)
    else:
        content = json.loads(request.body)

        # Get the COnference object and put it in the content dict
        try:
            conference_href = f'/api/conferences/{conference_vo_id}/'
            conference = ConferenceVO.objects.get(import_hrref=conference_href)
            content["conference"] = conference
        except ConferenceVO.DoesNotExist:
            return JsonResponse(
                {"messgae": "Invalid conference id"},
                status=400,
            )

        attendee = Attendee.objects.create(**content)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )



class AttendeeDetailEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "email",
        "name",
        "company_name",
        "created",

    ]

@require_http_methods(["GET","DELETE","PUT"])
def api_show_attendee(request, pk):
    if request.method == "GET":
        attendee = Attendee.objects.get(id=pk)
        return JsonResponse(attendee,
                            encoder=AttendeeDetailEncoder,
                            safe=False)
    elif request.method == "DELETE":
        count, _ = Attendee.objects.filter(id=pk).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        content = json.loads(request.body)
        try:
            if "conference" in content:
                conference = ConferenceVO.objects.get(id=content["conference"])
                content["conference"] = conference
        except ConferenceVO.DoesNotExist:
            return JsonResponse({"message":"conference does not exist"},
                                status=400)

        Attendee.objects.filter(id=pk).update(**content)
        attendees = Attendee.objects.get(id=pk)

        return JsonResponse(
            attendees,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )
