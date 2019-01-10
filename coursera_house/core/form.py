from django import forms


class ControllerForm(forms.Form):
    bedroom_target_temperature = forms.IntegerField(
        max_value=50, min_value=16, initial=21
    )
    hot_water_target_temperature = forms.IntegerField(
        max_value=90, min_value=24, initial=80
    )
    bedroom_light = forms.BooleanField(required=False)
    bathroom_light = forms.BooleanField(required=False)
