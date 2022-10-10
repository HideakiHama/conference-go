from django.http import JsonResponse
from common.json import ModelEncoder
from django.views.decorators.http import require_http_methods
import json
import pika

from .models import Presentation, Status
from events.models import Conference
from events.api_views import ConferenceListEncoder


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
            conference = Conference.objects.get(id=conference_id)
            content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"messgae": "Invalid conference id"},
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

    encoders = {
        "conference": ConferenceListEncoder(),
    }

    def get_extra_data(self, o):
        return {"status": o.status.name}

@require_http_methods(["GET","DELETE","PUT"])
def api_show_presentation(request, pk):
    if request.method == "GET":
        try:
            presentation = Presentation.objects.get(id=pk)
        except Presentation.DoesNotExist:
            return JsonResponse({"message": "presentation does not exist"},
                                status=400)
        return JsonResponse(presentation,
                            encoder=PresentationDetailEncoder,
                            safe=False)
    elif request.method == "DELETE":
        count, _ = Presentation.objects.filter(id=pk).delete()
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

@require_http_methods(["PUT"])
def api_approve_presentation(request, pk):
    presentation = Presentation.objects.get(id=pk)
    presentation.approve()

    parameters = pika.ConnectionParameters(host="rabbitmq")
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue="presentation_approvals")  #queue "presentation_approvals"
    # routing_key is associated with 'task' channel
    channel.basic_publish(
        exchange="",
        routing_key="presentation_approvals",
    # "Data from producer"
        body=json.dumps({
                "presenter_name": presentation.presenter_name,
                "presenter_email": presentation.presenter_email,
                "title": presentation.title,
                       })
    )
    connection.close()

    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False,
    )

@require_http_methods(["PUT"])
def api_reject_presentation(request, pk):
    presentation = Presentation.objects.get(id=pk)
    presentation.reject()

    parameters = pika.ConnectionParameters(host="rabbitmq")
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue="presentation_rejections")     #queue "presentation_rejections"
    channel.basic_publish(
        exchange="",
        routing_key="presentation_rejections",
        body=json.dumps({
            "presenter_name": presentation.presenter_name,
            "presneter_email": presentation.presenter_email,
            "title": presentation.title,
            }),
    )
    connection.close()


    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False,
    )