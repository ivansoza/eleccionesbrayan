from django.db import models

from agenda.models import Event, EventAbstract
from django.conf import settings


class EventMember(EventAbstract):
    """ Event member model """

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="events")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ["event", "user"]

    def __str__(self):
        return str(self.user)
