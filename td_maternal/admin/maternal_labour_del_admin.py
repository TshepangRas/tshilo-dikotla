from django.contrib import admin

from edc_registration.models import RegisteredSubject

from tshilo_dikotla.base_model_admin import MembershipBaseModelAdmin

from ..forms import MaternalLabourDelForm, MaternalHivInterimHxForm
from ..models import MaternalLabourDel, MaternalHivInterimHx

from .base_maternal_model_admin import BaseMaternalModelAdmin


class MaternalLabourDelAdmin(MembershipBaseModelAdmin):

    form = MaternalLabourDelForm

    list_display = ('registered_subject',
                    'delivery_datetime',
                    'labour_hrs',
                    'delivery_hospital',
                    'valid_regiment_duration')

    list_filter = ('delivery_hospital',
                   'valid_regiment_duration')

    search_fields = ('registered_subject__subject_identifier', )
    readonly_fields = ('live_infants_to_register',)

    radio_fields = {'delivery_time_estimated': admin.VERTICAL,
                    'delivery_hospital': admin.VERTICAL,
                    'valid_regiment_duration': admin.VERTICAL,
                    'mode_delivery': admin.VERTICAL,
                    'csection_reason': admin.VERTICAL,
                    'csection_reason': admin.VERTICAL, }
    filter_horizontal = ('delivery_complications',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "registered_subject":
            if request.GET.get('registered_subject'):
                kwargs["queryset"] = RegisteredSubject.objects.filter(
                    id__exact=request.GET.get('registered_subject', 0))
            else:
                self.readonly_fields = list(self.readonly_fields)
                try:
                    self.readonly_fields.index('registered_subject')
                except ValueError:
                    self.readonly_fields.append('registered_subject')
        return super(MaternalLabourDelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(MaternalLabourDel, MaternalLabourDelAdmin)


class MaternalHivInterimHxAdmin(BaseMaternalModelAdmin):

    form = MaternalHivInterimHxForm

    radio_fields = {'has_cd4': admin.VERTICAL,
                    'has_vl': admin.VERTICAL,
                    'vl_detectable': admin.VERTICAL}

admin.site.register(MaternalHivInterimHx, MaternalHivInterimHxAdmin)
