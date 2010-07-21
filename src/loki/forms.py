from django.forms.models import modelformset_factory

from loki.models import Config, ConfigParam, Step, StepParam

ConfigParamFormSet = modelformset_factory(ConfigParam)
StepParamFormSet = modelformset_factory(StepParam)
