from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from queueapp import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("etablissements/", views.establishment_list, name="establishment_list"),
    path("etablissements/<int:pk>/", views.establishment_detail, name="establishment_detail"),
    path("mes-tickets/", views.my_tickets, name="my_tickets"),
    path("ticket/<int:pk>/", views.ticket_detail, name="ticket_detail"),
    path("inscription/", views.register, name="register"),
    path("connexion/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("deconnexion/", auth_views.LogoutView.as_view(), name="logout"),
    
    
    path(
    "mes-rendez-vous/",
    views.mes_rendez_vous,
    name="mes_rendez_vous"
),
    path(
    "personnel/file/",
    views.gestion_file,
    name="gestion_file"
    
),
]

