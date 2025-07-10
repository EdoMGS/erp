from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, DetailView, ListView

from .models import Employee, RadnaEvaluacija
from .services import EvaluacijaService


class ZaposlenikEvaluacijaListView(LoginRequiredMixin, ListView):
    model = RadnaEvaluacija
    template_name = 'ljudski_resursi/evaluacije/lista_evaluacija.html'
    
    def get_queryset(self):
        return RadnaEvaluacija.objects.select_related(
            'employee', 
            'evaluator'
        ).filter(
            employee_id=self.kwargs.get('employee_id')
        ).order_by('-datum_evaluacije')

class KreirajEvaluacijuView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = RadnaEvaluacija
    template_name = 'ljudski_resursi/evaluacija/kreiranje_evaluacije.html'
    
    def form_valid(self, form):
        employee = form.cleaned_data['employee']
        period = form.cleaned_data['period']
        
        # Use service to create evaluation
        evaluacija = EvaluacijaService.kreiraj_evaluaciju(
            employee=employee,
            evaluator=self.request.user.employee,
            period=period,
            efikasnost=form.cleaned_data['efikasnost'],
            kvaliteta_rada=form.cleaned_data['kvaliteta_rada'],
            timski_rad=form.cleaned_data['timski_rad'],
            inicijativa=form.cleaned_data['inicijativa'],
            komentar=form.cleaned_data['komentar']
        )
        
        return redirect(evaluacija.get_absolute_url())
