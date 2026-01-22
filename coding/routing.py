from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/coding/(?P<problem_id>\d+)/$', consumers.CodingConsumer.as_asgi()),
]