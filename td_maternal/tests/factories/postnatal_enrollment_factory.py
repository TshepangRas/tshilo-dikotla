import factory

from datetime import datetime
from django.utils import timezone

from edc_registration.tests.factories import RegisteredSubjectFactory
from edc_constants.choices import YES, NO, POS, NEG, NOT_APPLICABLE

from td_maternal.models import PostnatalEnrollment
from tshilo_dikotla.constants import LIVE, STILL_BIRTH

from ..factories import MaternalConsentFactory, MaternalOffStudyFactory


class PostnatalEnrollmentFactory(factory.DjangoModelFactory):

    class Meta:
        model = PostnatalEnrollment

    report_datetime = timezone.datetime.now()
    consent_model = MaternalConsentFactory
    off_study_model = MaternalOffStudyFactory
    postpartum_days = 1
    vaginal_delivery = YES
    gestation_wks_delivered = timezone.datetime.date(datetime.today())
    delivery_status = LIVE
    live_infants = 1
    weeks_base_field = gestation_wks_delivered
