# contact_book_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/',     admin.site.urls),
    path('accounts/',  include('accounts.urls')),
    path('contacts/',  include('contacts.urls')),

    # ── Root redirect ─────────────────────────────────────
    # Sends / → /contacts/ (which then checks login)
    path('', RedirectView.as_view(url='/contacts/', permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)