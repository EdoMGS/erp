from django.urls import path

from .api import (
    EstimateView,
    QuoteAcceptView,
    QuoteCreateView,
    QuoteDetailView,
    QuoteRevisionView,
    QuoteSendView,
    QuoteToWOView,
)

urlpatterns = [
    path("quotes/estimate", EstimateView.as_view()),
    path("quotes", QuoteCreateView.as_view()),
    path("quotes/<int:pk>", QuoteDetailView.as_view()),
    path("quotes/<int:pk>/send", QuoteSendView.as_view()),
    path("quotes/<int:pk>/accept", QuoteAcceptView.as_view()),
    path("quotes/<int:pk>/to-wo", QuoteToWOView.as_view()),
    path("quotes/<int:pk>/revision", QuoteRevisionView.as_view()),
]
