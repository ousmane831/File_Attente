from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Count, Max, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import RegisterForm
from .models import Establishment, RendezVous, Ticket


def envoyer_notification_email(utilisateur, sujet, message):
    if not utilisateur.email:
        return False

    send_mail(
        subject=sujet,
        message=message,
        from_email=None,
        recipient_list=[utilisateur.email],
        fail_silently=False,
    )

    return True


def etablissements_actifs():
    """Établissements actifs annotés avec le nombre de tickets en attente."""
    return Establishment.objects.filter(is_active=True).annotate(
        waiting_now=Count("tickets", filter=Q(tickets__status="en_attente"))
    )


def home(request):
    context = {
        "establishments": etablissements_actifs()[:6],
        "establishment_count": Establishment.objects.filter(is_active=True).count(),
        "waiting_count": Ticket.objects.filter(status="en_attente").count(),
        "categories": Establishment.CATEGORY_CHOICES,
    }
    return render(request, "queueapp/home.html", context)


def establishment_list(request):
    establishments = etablissements_actifs()

    category = request.GET.get("categorie", "").strip()
    city = request.GET.get("ville", "").strip()

    if category:
        establishments = establishments.filter(category=category)

    if city:
        establishments = establishments.filter(city__icontains=city)

    context = {
        "establishments": establishments,
        "categories": Establishment.CATEGORY_CHOICES,
        "selected_category": category,
        "city": city,
    }

    return render(request, "queueapp/establishment_list.html", context)


def establishment_detail(request, pk):
    establishment = get_object_or_404(Establishment, pk=pk, is_active=True)

    waiting = establishment.tickets.filter(status="en_attente").count()

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.info(request, "Connectez-vous pour prendre un ticket.")
            return redirect(f"{reverse('login')}?next={request.path}")

        last_number = establishment.tickets.aggregate(
            max_number=Max("number")
        )["max_number"] or 0

        # Créer le ticket
        ticket = Ticket.objects.create(
            user=request.user,
            establishment=establishment,
            number=last_number + 1,
        )

        # Envoyer la notification par e-mail
        envoyer_notification_email(
            utilisateur=request.user,
            sujet="Confirmation de votre ticket - SmartQueue Sénégal",
            message=(
                f"Bonjour {request.user.username},\n\n"
                f"Votre ticket T{ticket.number:03d} a été créé avec succès.\n"
                f"Établissement : {establishment.name}\n"
                "Veuillez patienter et consulter votre espace SmartQueue "
                "pour suivre votre tour.\n\n"
                "Merci d'utiliser SmartQueue Sénégal."
            ),
        )

        messages.success(request, f"Votre ticket T{ticket.number:03d} a été créé.")

        return redirect("ticket_detail", pk=ticket.pk)

    return render(
        request,
        "queueapp/establishment_detail.html",
        {"establishment": establishment, "waiting": waiting},
    )


@login_required
def my_tickets(request):
    tickets = list(
        Ticket.objects.filter(user=request.user)
        .select_related("establishment")
        .order_by("-created_at")
    )
    actifs = [t for t in tickets if t.status in ("en_attente", "appele")]
    passes = [t for t in tickets if t.status not in ("en_attente", "appele")]
    return render(
        request,
        "queueapp/my_tickets.html",
        {"tickets": tickets, "active_tickets": actifs, "past_tickets": passes},
    )


@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(
        Ticket.objects.select_related("establishment", "user"), pk=pk, user=request.user
    )
    return render(request, "queueapp/ticket_detail.html", {"ticket": ticket})


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Votre compte a été créé avec succès.")
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


@staff_member_required
def gestion_file(request):
    etablissements = Establishment.objects.all().order_by("name")

    etablissement_id = (
        request.POST.get("establishment_id")
        or request.GET.get("etablissement")
    )

    if not etablissement_id or etablissement_id == "None":
        etablissement_id = None

    tickets_attente = Ticket.objects.filter(
        status="en_attente"
    ).select_related("user", "establishment").order_by("created_at")

    tickets_appeles = Ticket.objects.filter(
        status="appele"
    ).select_related("user", "establishment").order_by("called_at")

    if etablissement_id:
        tickets_attente = tickets_attente.filter(establishment_id=etablissement_id)
        tickets_appeles = tickets_appeles.filter(establishment_id=etablissement_id)

    if request.method == "POST":
        if not etablissement_id:
            messages.error(request, "Veuillez choisir un établissement.")
            return redirect(request.path)

        action = request.POST.get("action")
        ticket_id = request.POST.get("ticket_id")

        if action == "appeler":
            ticket = tickets_attente.first()

            if ticket:
                ticket.status = "appele"
                ticket.called_at = timezone.now()
                ticket.save()
                messages.success(request, f"Le ticket T{ticket.number:03d} a été appelé.")
            else:
                messages.info(request, "Aucun ticket en attente dans cet établissement.")

        elif action in ("terminer", "annuler") and ticket_id:
            ticket = get_object_or_404(tickets_appeles, pk=ticket_id)

            if action == "terminer":
                ticket.status = "termine"
                messages.success(request, "Le passage est terminé.")
            else:
                ticket.status = "annule"
                messages.success(request, "Le ticket a été annulé.")

            ticket.save()

        return redirect(f"{request.path}?etablissement={etablissement_id}")

    statistiques = {"total": 0, "en_attente": 0, "appeles": 0, "termines": 0}
    repartition = []
    etablissement_courant = None

    if etablissement_id:
        etablissement_courant = Establishment.objects.filter(pk=etablissement_id).first()
        tickets_etablissement = Ticket.objects.filter(establishment_id=etablissement_id)

        statistiques = {
            "total": tickets_etablissement.count(),
            "en_attente": tickets_etablissement.filter(status="en_attente").count(),
            "appeles": tickets_etablissement.filter(status="appele").count(),
            "termines": tickets_etablissement.filter(status="termine").count(),
        }

        total = statistiques["total"]
        if total:
            annules = total - statistiques["en_attente"] - statistiques["appeles"] - statistiques["termines"]
            segments = [
                ("en_attente", "En attente", statistiques["en_attente"]),
                ("appele", "Appelés", statistiques["appeles"]),
                ("termine", "Terminés", statistiques["termines"]),
                ("annule", "Annulés", annules),
            ]
            repartition = [
                {"key": k, "label": label, "count": n, "pct": round(n * 100 / total)}
                for k, label, n in segments
            ]

    return render(
        request,
        "queueapp/gestion_file.html",
        {
            "etablissements": etablissements,
            "etablissement_id": etablissement_id,
            "etablissement_courant": etablissement_courant,
            "tickets_attente": tickets_attente,
            "tickets_appeles": tickets_appeles,
            "prochain": tickets_attente.first() if etablissement_id else None,
            "dernier_appele": tickets_appeles.last() if etablissement_id else None,
            "statistiques": statistiques,
            "repartition": repartition,
        },
    )


@login_required
def mes_rendez_vous(request):
    rendez_vous = RendezVous.objects.filter(
        patient=request.user
    ).select_related("establishment")

    return render(request, "queueapp/mes_rendez_vous.html", {"rendez_vous": rendez_vous})
