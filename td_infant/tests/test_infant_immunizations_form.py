from dateutil.relativedelta import relativedelta
from datetime import datetime, date
from django.utils import timezone

from edc_constants.constants import SCREENED
from edc_registration.models import RegisteredSubject
from edc_identifier.models import SubjectIdentifier
from edc_constants.constants import FAILED_ELIGIBILITY, OFF_STUDY, SCHEDULED, POS, YES, NO, NOT_APPLICABLE, UNKNOWN
from edc_appointment.models import Appointment

from tshilo_dikotla.constants import MODIFIED, NO_MODIFICATIONS, DISCONTINUED, NEVER_STARTED
from td_maternal.models import MaternalVisit

from td_maternal.tests import BaseTestCase
from td_maternal.tests.factories import (MaternalUltraSoundIniFactory, MaternalEligibilityFactory,
                                         MaternalConsentFactory, AntenatalEnrollmentFactory,
                                         AntenatalVisitMembershipFactory, MaternalLabourDelFactory,
                                         MaternalVisitFactory)
from td_infant.forms import InfantFuImmunizationsForm, VaccinesReceivedForm, VaccinesMissedForm
from .factories import (InfantBirthFactory, InfantVisitFactory, InfantArvProphFactory, InfantBirthArvFactory,
                        InfantFuImmunizationsFactory)


class TestInfantImmunizationForm(BaseTestCase):

    def setUp(self):
        super(TestInfantImmunizationForm, self).setUp()
        self.maternal_eligibility = MaternalEligibilityFactory()
        self.maternal_consent = MaternalConsentFactory(registered_subject=self.maternal_eligibility.registered_subject)
        self.registered_subject = self.maternal_consent.registered_subject

        self.assertEqual(RegisteredSubject.objects.all().count(), 1)
        options = {'registered_subject': self.registered_subject,
                   'current_hiv_status': POS,
                   'evidence_hiv_status': YES,
                   'will_get_arvs': YES,
                   'is_diabetic': NO,
                   'will_remain_onstudy': YES,
                   'rapid_test_done': NOT_APPLICABLE,
                   'last_period_date': (timezone.datetime.now() - relativedelta(weeks=25)).date()}

        self.antenatal_enrollment = AntenatalEnrollmentFactory(**options)
        self.assertTrue(self.antenatal_enrollment.is_eligible)
        self.maternal_visit = MaternalVisit.objects.get(
            appointment__registered_subject=self.registered_subject,
            reason=SCHEDULED,
            appointment__visit_definition__code='1000M')
        self.maternal_ultrasound = MaternalUltraSoundIniFactory(
            maternal_visit=self.maternal_visit, number_of_gestations=1,)
        self.maternal_visits_membership = AntenatalVisitMembershipFactory(registered_subject=self.registered_subject)
        self.maternal_labour_del = MaternalLabourDelFactory(registered_subject=self.registered_subject,
                                                            live_infants_to_register=1)
        self.antenatal_visit_1 = MaternalVisitFactory(
            appointment=Appointment.objects.get(registered_subject=options.get('registered_subject'),
                                                visit_definition__code='1010M'))
        self.antenatal_visit_2 = MaternalVisitFactory(
            appointment=Appointment.objects.get(registered_subject=options.get('registered_subject'),
                                                visit_definition__code='1020M'))
        self.maternal_visit_2000 = MaternalVisitFactory(
            appointment=Appointment.objects.get(registered_subject=options.get('registered_subject'),
                                                visit_definition__code='2000M'))

        infant_registered_subject = RegisteredSubject.objects.get(
            relative_identifier=self.registered_subject.subject_identifier,
            subject_type='infant')
        self.infant_birth = InfantBirthFactory(
            registered_subject=infant_registered_subject,
            maternal_labour_del=self.maternal_labour_del)
        self.appointment = Appointment.objects.get(
            registered_subject=infant_registered_subject,
            visit_definition__code='2000')
        self.infant_visit = InfantVisitFactory(appointment=self.appointment)
        self.infant_birth_arv = InfantBirthArvFactory(infant_visit=self.infant_visit, azt_discharge_supply=YES)
        self.appointment = Appointment.objects.get(
            registered_subject=infant_registered_subject,
            visit_definition__code='2010')
        self.infant_visit = InfantVisitFactory(appointment=self.appointment)
        self.appointment = Appointment.objects.get(
            registered_subject=infant_registered_subject,
            visit_definition__code='2020')
        self.infant_visit = InfantVisitFactory(appointment=self.appointment)
        self.options = {
            'report_datetime': timezone.now(),
            'infant_visit': self.infant_visit,
            'vaccines_received': YES,
            'vaccines_missed': NO
        }

    def test_vaccines_received_no_table_filling(self):
        """Test an infant who received vaccines but received vaccines table not filled"""
        infant_fu_immunizations_factory = InfantFuImmunizationsFactory(**self.options)
        received_inline = {'infant_fu_immunizations': infant_fu_immunizations_factory.id,
                           'received_vaccine_name': None,
                           'date_given': None,
                           'infant_age': None}
        vaccine_received_form = VaccinesReceivedForm(data=received_inline)
        self.assertIn("You mentioned that vaccines where received. Please"
                      " indicate which ones on the Received Vaccines table.",
                      vaccine_received_form.errors.get('__all__'))

    def test_vaccines_not_received_table_filled(self):
        """Test an infant who did not receive vaccines but received vaccines table is filled"""
        self.options = {
            'report_datetime': timezone.now(),
            'infant_visit': self.infant_visit,
            'vaccines_received': NO,
            'vaccines_missed': NO
        }
        infant_fu_immunizations_factory = InfantFuImmunizationsFactory(**self.options)
        received_inline = {'infant_fu_immunizations': infant_fu_immunizations_factory.id,
                           'received_vaccine_name': 'Hepatitis_B',
                           'date_given': date.today(),
                           'infant_age': '2'}
        vaccine_received_form = VaccinesReceivedForm(data=received_inline)
        self.assertIn("No vaccines received. Do not fill Received Vaccines table",
                      vaccine_received_form.errors.get('__all__'))

    def test_vaccines_missed_no_table_filling(self):
        """Test an infant who missed vaccines and missed vaccine table not filled"""
        self.options = {
            'report_datetime': timezone.now(),
            'infant_visit': self.infant_visit,
            'vaccines_received': NO,
            'vaccines_missed': YES
        }
        infant_fu_immunizations_factory = InfantFuImmunizationsFactory(**self.options)
        received_inline = {'infant_fu_immunizations': infant_fu_immunizations_factory.id,
                           'missed_vaccine_name': None,
                           'reason_missed': None,
                           'reason_missed_other': None}
        vaccine_missed_form = VaccinesMissedForm(data=received_inline)
        self.assertIn("You mentioned that the child missed some vaccines."
                      " Please indicate which ones in the Missed Vaccines "
                      "table.", vaccine_missed_form.errors.get('__all__'))

    def test_vaccines_not_missed_table_filled(self):
        """Test an infant who did not miss vaccines and missed vaccine table is filled filled"""
        self.options = {
            'report_datetime': timezone.now(),
            'infant_visit': self.infant_visit,
            'vaccines_received': NO,
            'vaccines_missed': NO
        }
        infant_fu_immunizations_factory = InfantFuImmunizationsFactory(**self.options)
        received_inline = {'infant_fu_immunizations': infant_fu_immunizations_factory.id,
                           'missed_vaccine_name': 'Vitamin_A',
                           'reason_missed': 'Was not in country',
                           'reason_missed_other': None}
        vaccine_missed_form = VaccinesMissedForm(data=received_inline)
        self.assertIn("No vaccines missed. Do not fill Missed Vaccines table", 
                      vaccine_missed_form.errors.get('__all__'))

    def test_missed_vaccine_fields(self):
        """Test that when a missed vaccine name is given that the reason should be provided"""
        self.options = {
            'report_datetime': timezone.now(),
            'infant_visit': self.infant_visit,
            'vaccines_received': NO,
            'vaccines_missed': YES
        }
        infant_fu_immunizations_factory = InfantFuImmunizationsFactory(**self.options)
        received_inline = {'infant_fu_immunizations': infant_fu_immunizations_factory.id,
                           'missed_vaccine_name': 'BCG',
                           'reason_missed': None,
                           'reason_missed_other': None}
        vaccine_missed_form = VaccinesMissedForm(data=received_inline)
        self.assertIn("You said {} vaccine was missed. Give a reason for missing this"
                      " vaccine".format(received_inline['missed_vaccine_name']), vaccine_missed_form.errors.get('__all__'))

    def test_vaccine_received_date_not_greater_than_birth(self):
        """test if the vaccine date is not greater than the birth date"""
        infant_fu_immunizations_factory = InfantFuImmunizationsFactory(**self.options)
        received_inline = {'infant_fu_immunizations': infant_fu_immunizations_factory.id,
                           'received_vaccine_name': 'BCG',
                           'date_given': (timezone.datetime.now() - relativedelta(weeks=37)).date(),
                           'infant_age': 'At Birth'}
        vaccine_received_form = VaccinesReceivedForm(data=received_inline)
        self.assertIn("Vaccine date cannot be before infant date of birth. ",
                      vaccine_received_form.errors.get('__all__'))

    def test_received_vaccine_fields_date(self):
        """Test that when a receive vaccine name is filled that a date is provided"""
        infant_fu_immunizations_factory = InfantFuImmunizationsFactory(**self.options)
        received_inline = {'infant_fu_immunizations': infant_fu_immunizations_factory.id,
                           'received_vaccine_name': 'BCG',
                           'date_given': None,
                           'infant_age': 'At Birth'}
        vaccine_received_form = VaccinesReceivedForm(data=received_inline)
        self.assertIn("You provided a vaccine name {}. What date was it given to the "
                      "infant?".format(received_inline['received_vaccine_name']), vaccine_received_form.errors.get('__all__'))

    def test_received_vaccine_fields_age(self):
        """Test that when a receive vaccine name is filled that a date is provided"""
        infant_fu_immunizations_factory = InfantFuImmunizationsFactory(**self.options)
        received_inline = {'infant_fu_immunizations': infant_fu_immunizations_factory.id,
                           'received_vaccine_name': 'BCG',
                           'date_given': (timezone.datetime.now() - relativedelta(weeks=37)).date(),
                           'infant_age': None}
        vaccine_received_form = VaccinesReceivedForm(data=received_inline)
        self.assertIn("You provided a vaccine name {}. At how many months "
                      "was it given to the infant?".format(received_inline['received_vaccine_name']), vaccine_received_form.errors.get('__all__'))

    def test_received_vaccination_at_birth_bcg(self):
        """Test that the correct vaccine is given at birth or few days after birth"""
        infant_fu_immunizations_factory = InfantFuImmunizationsFactory(**self.options)
        received_inline = {'infant_fu_immunizations': infant_fu_immunizations_factory.id,
                           'received_vaccine_name': 'BCG',
                           'date_given': date.today(),
                           'infant_age': '2'}
        vaccine_received_form = VaccinesReceivedForm(data=received_inline)
        self.assertIn("BCG vaccination is ONLY given at birth or few days after birth",
                      vaccine_received_form.errors.get('__all__'))

    def test_received_hepatitis_vaccine(self):
        """Test that the hepatitis vaccine is not given at inappropriate infant age"""
        infant_fu_immunizations_factory = InfantFuImmunizationsFactory(**self.options)
        received_inline = {'infant_fu_immunizations': infant_fu_immunizations_factory.id,
                           'received_vaccine_name': 'Hepatitis_B',
                           'date_given': date.today(),
                           'infant_age': '6-11'}
        vaccine_received_form = VaccinesReceivedForm(data=received_inline)
        self.assertIn("Hepatitis B can only be administered at birth or 2 or 3 or 4 "
                      "months of infant life", vaccine_received_form.errors.get('__all__'))

    def test_receievd_dpt_vaccine(self):
        """Test that DPT vaccine is not given at inappropriate infant age"""
        infant_fu_immunizations_factory = InfantFuImmunizationsFactory(**self.options)
        received_inline = {'infant_fu_immunizations': infant_fu_immunizations_factory.id,
                           'received_vaccine_name': 'DPT',
                           'date_given': date.today(),
                           'infant_age': '6-11'}
        vaccine_received_form = VaccinesReceivedForm(data=received_inline)
        self.assertIn("DPT. Diphtheria, Pertussis and Tetanus can only be administered at"
                      " 2 or 3 or 4 months ONLY.", vaccine_received_form.errors.get('__all__'))

    def test_received_haemophilus_vaccine(self):
        """Test that haemophilus influenza vaccine is not administered at inappropiate infant age"""
        infant_fu_immunizations_factory = InfantFuImmunizationsFactory(**self.options)
        received_inline = {'infant_fu_immunizations': infant_fu_immunizations_factory.id,
                           'received_vaccine_name': 'Haemophilus_influenza',
                           'date_given': date.today(),
                           'infant_age': '6-11'}
        vaccine_received_form = VaccinesReceivedForm(data=received_inline)
        self.assertIn("Haemophilus Influenza B vaccine can only be given at 2 or 3 or"
                      " 4 months of infant life.", vaccine_received_form.errors.get('__all__'))

    def test_received_pcv_vaccine(self):
        """Test that PCV is administered at correct age"""
        infant_fu_immunizations_factory = InfantFuImmunizationsFactory(**self.options)
        received_inline = {'infant_fu_immunizations': infant_fu_immunizations_factory.id,
                           'received_vaccine_name': 'PCV_Vaccine',
                           'date_given': date.today(),
                           'infant_age': '6-11'}
        vaccine_received_form = VaccinesReceivedForm(data=received_inline)
        self.assertIn("The PCV [Pneumonia Conjugated Vaccine], can ONLY be administered at"
                      " 2 or 3 or 4 months of infant life.", vaccine_received_form.errors.get('__all__'))

    def test_received_polio_vaccine(self):
        """Test that polio vaccine is administered at correct age"""
        infant_fu_immunizations_factory = InfantFuImmunizationsFactory(**self.options)
        received_inline = {'infant_fu_immunizations': infant_fu_immunizations_factory.id,
                           'received_vaccine_name': 'Polio',
                           'date_given': date.today(),
                           'infant_age': '6-11'}
        vaccine_received_form = VaccinesReceivedForm(data=received_inline)
        self.assertIn("Polio vaccine can only be administered at 2 or 3 or 4 or 18 "
                      "months of infant life", vaccine_received_form.errors.get('__all__'))

    def test_received_rotavirus_vaccine(self):
        """Test rotavirus administered to infant at age 4months"""
        infant_fu_immunizations_factory = InfantFuImmunizationsFactory(**self.options)
        received_inline = {'infant_fu_immunizations': infant_fu_immunizations_factory.id,
                           'received_vaccine_name': 'Rotavirus',
                           'date_given': date.today(),
                           'infant_age': '4'}
        vaccine_received_form = VaccinesReceivedForm(data=received_inline)
        self.assertIn("Rotavirus is only administered at 2 or 3 months of"
                      " infant life", vaccine_received_form.errors.get('__all__'))

    def test_received_measles_vaccine(self):
        """Test measles vaccine administered to an infant who is only a month old"""
        infant_fu_immunizations_factory = InfantFuImmunizationsFactory(**self.options)
        received_inline = {'infant_fu_immunizations': infant_fu_immunizations_factory.id,
                           'received_vaccine_name': 'Measles',
                           'date_given': date.today(),
                           'infant_age': '2'}
        vaccine_received_form = VaccinesReceivedForm(data=received_inline)
        self.assertIn("Measles vaccine is only administered at 9 or 18"
                      " months of infant life.", vaccine_received_form.errors.get('__all__'))

    def test_received_pentavalent_vaccine(self):
        """Test for Pentavalent vaccine administered at 6-11 months of infant life"""
        infant_fu_immunizations_factory = InfantFuImmunizationsFactory(**self.options)
        received_inline = {'infant_fu_immunizations': infant_fu_immunizations_factory.id,
                           'received_vaccine_name': 'Pentavalent',
                           'date_given': date.today(),
                           'infant_age': '6-11'}
        vaccine_received_form = VaccinesReceivedForm(data=received_inline)
        self.assertIn("The Pentavalent vaccine can only be administered at 2 or 3 or"
                      " 4 months of infant life.", vaccine_received_form.errors.get('__all__'))

    def test_received_vitamin_a_vaccine(self):
        """Test for Vitamin A vaccine administered earlier than 6 months"""
        infant_fu_immunizations_factory = InfantFuImmunizationsFactory(**self.options)
        received_inline = {'infant_fu_immunizations': infant_fu_immunizations_factory.id,
                           'received_vaccine_name': 'Vitamin_A',
                           'date_given': date.today(),
                           'infant_age': '2'}
        vaccine_received_form = VaccinesReceivedForm(data=received_inline)
        self.assertIn("Vitamin A is given to children between 6-11 months of"
                      " life", vaccine_received_form.errors.get('__all__'))
