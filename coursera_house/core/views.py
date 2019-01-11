from django.urls import reverse_lazy
from django.views.generic import FormView

from .models import Setting
from .form import ControllerForm
from .utils import fetch_controller_data, send_command_to_controller, normalize_data


class ControllerView(FormView):
    form_class = ControllerForm
    template_name = "core/control.html"
    success_url = reverse_lazy("form")

    def __init__(self):
        self.controller_data = normalize_data(fetch_controller_data())
        super(ControllerView, self).__init__()

    def get_context_data(self, **kwargs):
        context = super(ControllerView, self).get_context_data()
        context["data"] = {
            name.replace("_", " ").capitalize(): value
            for name, value in self.controller_data.items()
        }
        return context

    def get_initial(self):
        bedroom_target_temperature = Setting.objects.get(
            controller_name="bedroom_target_temperature"
        ).value
        hot_water_target_temperature = Setting.objects.get(
            controller_name="hot_water_target_temperature"
        ).value
        return {
            "bedroom_target_temperature": bedroom_target_temperature,
            "hot_water_target_temperature": hot_water_target_temperature,
            "bedroom_light": self.controller_data["bedroom_light"],
            "bathroom_light": self.controller_data["bathroom_light"],
        }

    def form_valid(self, form):
        bedroom_target_temperature = form.cleaned_data["bedroom_target_temperature"]
        hot_water_target_temperature = form.cleaned_data["hot_water_target_temperature"]
        Setting.objects.filter(controller_name="bedroom_target_temperature").update(
            value=bedroom_target_temperature
        )
        Setting.objects.filter(controller_name="hot_water_target_temperature").update(
            value=hot_water_target_temperature
        )

        command_for_controller = {}
        bedroom_target_light = form.cleaned_data["bedroom_light"]
        bathroom_target_light = form.cleaned_data["bathroom_light"]
        bedroom_light = self.controller_data["bedroom_light"]
        bathroom_light = self.controller_data["bathroom_light"]
        if bedroom_target_light != bedroom_light:
            command_for_controller.update({"bedroom_light": bedroom_target_light})
        if bathroom_target_light != bathroom_light:
            command_for_controller.update({"bathroom_light": bathroom_target_light})
        send_command_to_controller(command_for_controller)
        return super(ControllerView, self).form_valid(form)
