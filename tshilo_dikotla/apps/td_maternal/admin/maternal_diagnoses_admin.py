from django.contrib import admin

from ..forms import MaternalDiagnosesForm
from ..models import MaternalDiagnoses
from .base_maternal_model_admin import BaseMaternalModelAdmin


class MaternalDiagnosesAdmin(BaseMaternalModelAdmin):

    form = MaternalDiagnosesForm
    list_display = ('maternal_visit', 'instructions_given', 'diagnoses', 'has_who_dx')
    list_filter = ('instructions_given', 'diagnoses', 'has_who_dx')
    radio_fields = {'instructions_given': admin.VERTICAL,
                    'diagnoses': admin.VERTICAL,
                    'has_who_dx': admin.VERTICAL}
    filter_horizontal = ('who', )

admin.site.register(MaternalDiagnoses, MaternalDiagnosesAdmin)
