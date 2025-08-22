from django.urls import path

from .api import (
    EstimateView,
    QuoteAcceptView,
    QuoteCreateView,
    QuoteDetailView,
)

urlpatterns = [
    path("quotes/estimate", EstimateView.as_view()),
    path("quotes", QuoteCreateView.as_view()),
    path("quotes/<int:pk>", QuoteDetailView.as_view()),
    path("quotes/<int:pk>/send", QuoteSendView.as_view()),
    path("quotes/<int:pk>/accept", QuoteAcceptView.as_view()),
]
