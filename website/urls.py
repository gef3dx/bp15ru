from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "website"
urlpatterns = [
    path("", views.page, name="home"),
    path("index.html", RedirectView.as_view(pattern_name="website:home", permanent=True)),
    path("inquiries/submit/", views.inquiry_submit, name="inquiry_submit"),
    path("success.html", views.success, name="success"),
    path("success/", RedirectView.as_view(pattern_name="website:success", permanent=True)),
    path("robots.txt", views.robots, name="robots"),
    path("sitemap.xml", views.sitemap, name="sitemap"),
]
for slug in ("bureau", "ossetia", "dmc-mice", "programs", "exclusive", "contacts"):
    urlpatterns.append(path(f"{slug}/", views.page, {"page_name": slug}, name=slug))
    urlpatterns.append(path(f"{slug}/index.html", RedirectView.as_view(pattern_name=f"website:{slug}", permanent=True)))
