from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


# Create your models here.

class RequestStatus(models.TextChoices):
    NEW = 'NEW', _('Neu')
    ACCEPTED = 'ACP', _('Genehmigt')
    DENIED = 'DEN', _('Abgelehnt')


class Request(models.Model):
    id = models.BigAutoField(primary_key=True)

    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requests")
    acknowledged_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name="acknowledged_requests")

    start_date = models.DateField(blank=False, null=False)
    end_date = models.DateField(blank=False, null=False)

    request_status = models.CharField(max_length=3, choices=RequestStatus.choices, default=RequestStatus.NEW)

    # Eine Funktion der Klasse models.Model wird überschrieben --> self Zugriff auf das aktuelle Objekt
    # Beispiel: Wir wollen das Startdatum nicht einfach als String anzeigen, sondern holen uns das Datum vom Objekt selbst
    def __str__(self):
        return '%s | %s | %s | %s | %s' % (self.requested_by.get_full_name(), self.start_date, self.end_date, self.acknowledged_by, self.request_status)
