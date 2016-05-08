from django.db import models

from edc_base.model.models import BaseUuidModel
from edc_lab.lab_profile.models import BaseProfile

#from ..managers import ProfileManager

from .aliquot_type import AliquotType


class AliquotProfile(BaseProfile, BaseUuidModel):

    aliquot_type = models.ForeignKey(
        AliquotType,
        verbose_name='Source aliquot type')

    #objects = ProfileManager()
    objects = models.Manager()

    def natural_key(self):
        return (self.name,)

    class Meta:
        app_label = 'td_lab'
        db_table = 'td_lab_profile'