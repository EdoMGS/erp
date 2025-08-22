-from prodaja.api import (
+from prodaja.api import (
     QuoteCreateView,
     QuoteDetailView,
     QuoteAcceptView,
     QuoteSendView,
-    QuoteToWorkOrderView,
+    QuoteRevisionView,   # <- dodaj ovo
 )
 
 urlpatterns = [
     path("quotes", QuoteCreateView.as_view()),
     path("quotes/<int:pk>", QuoteDetailView.as_view()),
     path("quotes/<int:pk>/send", QuoteSendView.as_view()),
     path("quotes/<int:pk>/accept", QuoteAcceptView.as_view()),
-    path("quotes/<int:pk>/to-wo", QuoteToWorkOrderView.as_view()),
+    path("quotes/<int:pk>/revision", QuoteRevisionView.as_view()),  # <- i ovo
 ]
