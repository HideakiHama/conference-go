from django.http import JsonResponse
from common.json import ModelEncoder
from django.views.decorators.http import require_http_methods
import json

from .models import Presentation, Status
from events.models import Conference


class PresentationListEncoder(ModelEncoder):
    model = Presentation
    properties = ["title"]

    def get_extra_data(self, o):
        return {"status": o.status.name}

@require_http_methods(["GET","POST"])
def api_list_presentations(request, conference_id):
    if request.method == "GET":
        presentations = Presentation.objects.filter(conference=conference_id)
        return JsonResponse({"presentations": presentations},
                            encoder=PresentationListEncoder)

    else:
        content = json.loads(request.body)
        try:
            if "status" in content:
                status = Status.objects.get(id=conference_id)
                print(status)
                content["status"] = status

        except Status.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid Status id"},
                status=400,
            )
        presentation = Presentation.create(**content)

        return JsonResponse(presentation,
                            encoder=PresentationDetailEncoder,
                            safe=False
                            )




class PresentationDetailEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "presenter_name",
        "company_name",
        "presenter_email",
        "title",
        "synopsis",
        "created",
    ]

    def get_extra_data(self, o):
        return {"status": o.status.name}

@require_http_methods(["GET","DELETE","PUT"])
def api_show_presentation(request, pk):
    if request.method == "GET":
        presentation = Presentation.objects.get(id=pk)
        return JsonResponse(presentation,
                            encoder=PresentationDetailEncoder,
                            safe=False)
    elif request.method == "DELETE":
        count, _ = Presentation.objects.get(id=pk).delete()
        return JsonResponse({"deleted": count > 0})
    else:
        content = json.loads(request.body)
        try:
            if "conference" in content:
                conference = Conference.objects.get(id=content["conference"])
                content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse({"message":"conference does not exist"},
                                status=400)

        Presentation.objects.filter(id=pk).update(**content)
        presentation = Presentation.objects.get(id=pk)

        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )
