from django.conf import settings
from django.db import models
from django.utils import timezone

class Establishment(models.Model):
    CATEGORY_CHOICES = [
        ("hopital", "Hôpital"),
        ("banque", "Banque"),
        ("administration", "Administration"),
        ("autre", "Autre service"),
    ]
    name = models.CharField("Nom", max_length=150)
    category = models.CharField("Catégorie", max_length=30, choices=CATEGORY_CHOICES, default="autre")
    city = models.CharField("Ville", max_length=100)
    address = models.CharField("Adresse", max_length=255, blank=True)
    description = models.TextField("Description", blank=True)
    is_active = models.BooleanField("Actif", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Établissement"
        verbose_name_plural = "Établissements"

    def __str__(self):
        return f"{self.name} — {self.city}"

class Ticket(models.Model):
    STATUS_CHOICES = [
        ("en_attente", "En attente"),
        ("appele", "Appelé"),
        ("termine", "Terminé"),
        ("annule", "Annulé"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tickets")
    establishment = models.ForeignKey(Establishment, on_delete=models.CASCADE, related_name="tickets")
    number = models.PositiveIntegerField("Numéro du ticket")
    status = models.CharField("Statut", max_length=20, choices=STATUS_CHOICES, default="en_attente")
    created_at = models.DateTimeField("Créé le", default=timezone.now)
    called_at = models.DateTimeField("Appelé le", null=True, blank=True)

    class Meta:
        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(fields=["establishment", "number"], name="unique_ticket_number_per_establishment")
        ]
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"

    def __str__(self):
        return f"{self.establishment.name} — T{self.number:03d}"

    @property
    def position(self):
        if self.status != "en_attente":
            return 0
        return Ticket.objects.filter(
            establishment=self.establishment,
            status="en_attente",
            created_at__lt=self.created_at
        ).count() + 1


class RendezVous(models.Model):
    STATUT_CHOICES = [
        ("confirme", "Confirmé"),
        ("en_route", "En route"),
        ("retard", "En retard"),
        ("arrive", "Arrivé"),
        ("termine", "Terminé"),
        ("annule", "Annulé"),
    ]

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rendez_vous"
    )

    establishment = models.ForeignKey(
        Establishment,
        on_delete=models.CASCADE,
        related_name="rendez_vous"
    )

    date_heure = models.DateTimeField("Date et heure du rendez-vous")

    statut = models.CharField(
        "Statut",
        max_length=20,
        choices=STATUT_CHOICES,
        default="confirme"
    )

    message_retard = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date_heure"]
        verbose_name = "Rendez-vous"
        verbose_name_plural = "Rendez-vous"

    def __str__(self):
        return (
            f"{self.patient.username} - "
            f"{self.establishment.name} - "
            f"{self.date_heure}"
        )



   