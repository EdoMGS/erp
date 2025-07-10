from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Projekt
from .forms import ProjektForm

class ListaProjekataView(LoginRequiredMixin, ListView):
    model = Projekt
    template_name = 'nalozi/lista_projekata.html'
    context_object_name = 'projekti'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_active=True).order_by('-created_at')
        for projekt in queryset:
            projekt.azuriraj_status()  # Ažuriranje statusa
        return queryset

class DetaljiProjektaView(LoginRequiredMixin, DetailView):
    model = Projekt
    template_name = 'detalji_projekta.html'
    context_object_name = 'projekt'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projekt = self.get_object()
        context.update({
            'radni_nalozi': projekt.radni_nalozi.filter(is_active=True),
            'dokumentacija': projekt.dokumentacija.all(),
            'tip_projekta_info': projekt.tip_projekta,
            'tip_vozila_info': projekt.tip_vozila,
        })
        return context

class KreirajProjektView(LoginRequiredMixin, CreateView):
    model = Projekt
    form_class = ProjektForm
    template_name = 'nalozi/dodaj_uredi_projekt.html'
    success_url = reverse_lazy('lista_projekata')

    
        
            def form_valid(self, form):
                instance = form.save(commit=False)
                instance.save()  # Sprema instancu kako bi dobila ID
                form.save_m2m()  # Sada možemo raditi s ManyToMany poljima
                messages.success(self.request, "Uspješno ažurirano!")
                return super().form_valid(form)
            instance.save()  # Sprema instancu kako bi dobila ID
            form.save_m2m()  # Sada možemo raditi s ManyToMany poljima
            messages.success(self.request, "Uspješno ažurirano!")
            return super().form_valid(form)
            projekt = form.save(commit=False)
            projekt.save()
            form.save_m2m()

            messages.success(self.request, "Projekt uspješno kreiran!")
            return super().form_valid(form)
        except Exception as e:
            print(f"Greška prilikom kreiranja projekta: {e}")
            messages.error(self.request, "Došlo je do greške. Provjerite podatke.")
            return self.form_invalid(form)

class AzurirajProjektView(LoginRequiredMixin, UpdateView):
    model = Projekt
    form_class = ProjektForm
    template_name = 'nalozi/dodaj_uredi_projekt.html'
    success_url = reverse_lazy('lista_projekata')

    
        
            def form_valid(self, form):
                instance = form.save(commit=False)
                instance.save()  # Sprema instancu kako bi dobila ID
                form.save_m2m()  # Sada možemo raditi s ManyToMany poljima
                messages.success(self.request, "Uspješno ažurirano!")
                return super().form_valid(form)
            instance.save()  # Sprema instancu kako bi dobila ID
            form.save_m2m()  # Sada možemo raditi s ManyToMany poljima
            messages.success(self.request, "Uspješno ažurirano!")
            return super().form_valid(form)
            projekt = form.save(commit=False)
            projekt.save()
            form.save_m2m()

            messages.success(self.request, "Projekt uspješno ažuriran!")
            return super().form_valid(form)
        except Exception as e:
            print(f"Greška prilikom ažuriranja projekta: {e}")
            messages.error(self.request, "Došlo je do greške. Provjerite podatke.")
            return self.form_invalid(form)

class ObrisiProjektView(LoginRequiredMixin, DeleteView):
    model = Projekt
    template_name = 'obrisi_projekt.html'
    success_url = reverse_lazy('lista_projekata')

    def delete(self, request, *args, **kwargs):
        projekt = self.get_object()
        if projekt.radni_nalozi.filter(is_active=True).exists():
            messages.error(request, "Projekt se ne može obrisati jer ima aktivne radne naloge.")
            return redirect('detalji_projekta', pk=projekt.pk)

        projekt.is_active = False
        projekt.save()

        messages.success(request, "Projekt uspješno obrisan!")
        return redirect(self.success_url)
