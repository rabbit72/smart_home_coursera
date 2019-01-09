from django.urls import reverse_lazy
from django.views.generic import FormView

from .models import Setting
from .form import ControllerForm


class ControllerView(FormView):
    form_class = ControllerForm
    template_name = 'core/control.html'
    success_url = reverse_lazy('form')

    def get_context_data(self, **kwargs):
        context = super(ControllerView, self).get_context_data()
        context['data'] = {"light": "Off"}
        return context

    def get_initial(self):
        return {
            "bedroom_target_temperature": 22,
            "hot_water_target_temperature": 88,
            "bedroom_light": True,
            "bathroom_light": True,
        }

    def form_valid(self, form):
        return super(ControllerView, self).form_valid(form)
