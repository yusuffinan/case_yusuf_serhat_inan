from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static


urlpatterns = [
    path("", views.index, name="index"),
    path("show_history", views.show_history, name="show_history"),
    path("past_fifty", views.past_fifty, name="past_fifty"),
    path("result_graphic", views.result_graphic, name="result_graphic"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
