from django.forms import ModelForm
from django.forms.models import modelformset_factory

from loki.models import Builder, ConfigParam, StepParam

ConfigParamFormSet = modelformset_factory(ConfigParam)
StepParamFormSet = modelformset_factory(StepParam)

class BuilderForm(ModelForm):
    class Meta:
        model = Builder
