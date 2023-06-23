from django.test import TestCase
from .models import CustomUser, Patient, Bed, Medicine, Payment


class CustomUserModelTest(TestCase):
    def test_full_name(self):
        user = CustomUser(first_name='John', last_name='Doe')
        self.assertEqual(user.full_name(), 'John Doe')

    def test_str(self):
        user = CustomUser(first_name='John', last_name='Doe')
        self.assertEqual(str(user), 'John Doe')


class PatientTest(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(
            national_id='1234567890',
            first_name='John',
            last_name='Doe',
            sickness='Fever',
            watchful_name='Jane',
            age=30,
            height=180,
            weight=75,
            phone_number='+989120000000',
            insurance_type='1',
            address='123 Main St',
            blood_type='0',
            doctor_order='Take medicine',
            nurse_report='Patient is stable',
            doctor=None,
            nurse=None,
            login_at='2022-01-01T00:00:00Z',
            is_hospitalized=True,
            discharge_date=None,
        )


class PatientModelTest(PatientTest):
    def setUp(self):
        self.patient = Patient.objects.create(
            national_id='1234567890',
            first_name='John',
            last_name='Doe',
            sickness='Fever',
            watchful_name='Jane',
            age=30,
            height=180,
            weight=75,
            phone_number='+989120000000',
            insurance_type='1',
            address='123 Main St',
            blood_type='0',
            doctor_order='Take medicine',
            nurse_report='Patient is stable',
            doctor=None,
            nurse=None,
            login_at='2022-01-01T00:00:00Z',
            is_hospitalized=True,
            discharge_date=None,
        )

    def test_str(self):
        self.assertEqual(str(self.patient), 'John Doe')

    def test_unique_together_constraint(self):
        with self.assertRaises(Exception):
            Patient.objects.create(
                national_id='1234567890',
                first_name='Jane',
                last_name='Doe',
                sickness='Headache',
                watchful_name='John',
                age=25,
                height=170,
                weight=60,
                phone_number='+989120000001',
                insurance_type='2',
                address='456 Main St',
                blood_type='1',
                doctor_order='',
                nurse_report='',
                doctor=None,
                nurse=None,
                login_at='2022-01-02T00:00:00Z',
                is_hospitalized=True,
                discharge_date=None,
            )


class BedModelTest(PatientTest):
    def setUp(self):
        self.patient = Patient.objects.create(
            national_id='1234567890',
            first_name='John',
            last_name='Doe',
            sickness='Fever',
            watchful_name='Jane',
            age=30,
            height=180,
            weight=75,
            phone_number='+989120000000',
            insurance_type='1',
            address='123 Main St',
            blood_type='0',
            doctor_order='Take medicine',
            nurse_report='Patient is stable',
            doctor=None,
            nurse=None,
            login_at='2022-01-01T00:00:00Z',
            is_hospitalized=True,
            discharge_date=None,
        )

        self.bed = Bed.objects.create(
            floor=1,
            room=1,
            bed=1,
            patient=self.patient,
        )

    def test_str(self):
        self.assertEqual(str(self.bed), '111')


class MedicineModelTest(PatientTest):
    def setUp(self):
        self.patient = Patient.objects.create(
            national_id='1234567890',
            first_name='John',
            last_name='Doe',
            sickness='Fever',
            watchful_name='Jane',
            age=30,
            height=180,
            weight=75,
            phone_number='+989120000000',
            insurance_type='1',
            address='123 Main St',
            blood_type='0',
            doctor_order='Take medicine',
            nurse_report='Patient is stable',
            doctor=None,
            nurse=None,
            login_at='2022-01-01T00:00:00Z',
            is_hospitalized=True,
            discharge_date=None,
        )

        self.medicine = Medicine.objects.create(
            patient=self.patient,
            name='Paracetamol',
            order='Take 2 tablets every 8 hours',
        )

    def test_str(self):
        self.assertEqual(str(self.medicine), 'Paracetamol')


class PaymentModelTest(PatientTest):
    def setUp(self):
        self.patient = Patient.objects.create(
            national_id='1234567890',
            first_name='John',
            last_name='Doe',
            sickness='Fever',
            watchful_name='Jane',
            age=30,
            height=180,
            weight=75,
            phone_number='+989120000000',
            insurance_type='1',
            address='123 Main St',
            blood_type='0',
            doctor_order='Take medicine',
            nurse_report='Patient is stable',
            doctor=None,
            nurse=None,
            login_at='2022-01-01T00:00:00Z',
            is_hospitalized=True,
            discharge_date=None,
        )

        self.payment = Payment.objects.create(
            patient=self.patient,
            title='Hospital fee',
            cost=500000,
            is_paid=False,
        )

    def test_str(self):
        self.assertEqual(str(self.payment), 'Hospital fee')
