from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, ValidationError
from django.utils.translation import gettext_lazy as _


class CustomUser(User):
    class Meta:
        proxy = True

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name()


class Patient(models.Model):
    national_id = models.CharField(
        max_length=10,
        default='1234567890',
        unique=True,
        verbose_name='National ID',
        validators=[
            RegexValidator(r'^\d{10}$', message='Only digits(10) are allowed.')
        ]
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    sickness = models.CharField(max_length=50)
    watchful_name = models.CharField(max_length=50)
    age = models.IntegerField(default=0)
    height = models.IntegerField(default=0, verbose_name='Height (cm)')
    weight = models.IntegerField(default=0, verbose_name='Weight (kg)')
    phone_number = models.CharField(
        max_length=13,
        default='+989120000000',
        validators=[
            RegexValidator(r'^\+989\d{9}$', message='Enter valid phone number.(+989)')
        ]
    )
    insurances = [
        ('0', 'ٔNo Insurance'),
        ('1', 'General Health'),
        ('2', 'Social Supply'),
        ('3', 'ٔNomads Health'),
    ]
    insurance_type = models.CharField(max_length=10, choices=insurances, default='0')
    address = models.CharField(max_length=250)
    blood_types = [
        ('0', 'A+'),
        ('1', 'A-'),
        ('2', 'B+'),
        ('3', 'B-'),
        ('4', 'O+'),
        ('5', 'O-'),
        ('6', 'AB+'),
        ('7', 'AB-'),
    ]
    blood_type = models.CharField(max_length=10, choices=blood_types)
    doctor_order = models.TextField(blank=True)
    nurse_report = models.TextField(blank=True)
    doctor = models.ForeignKey(
        CustomUser,
        models.CASCADE,
        null=True,
        blank=True,
        limit_choices_to={'groups__name': 'Doctors'},
        related_name='doctor'
    )
    nurse = models.ForeignKey(
        CustomUser,
        models.CASCADE,
        null=True,
        blank=True,
        limit_choices_to={'groups__name': 'Nurses'},
        related_name='nurse'
    )
    login_at = models.DateTimeField(auto_now_add=True)
    is_hospitalized = models.BooleanField(default=True, verbose_name='Present')
    discharge_date = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if not self.is_hospitalized:
            payments = Payment.objects.filter(patient=self)
            if [payment for payment in payments if not payment.is_paid]:
                raise ValidationError(_('The payments not made!'))

    class Meta:
        unique_together = ('is_hospitalized', 'national_id')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Bed(models.Model):
    floors = [
        (0, 'ICU'),
        (1, '1'),
        (2, '2'),
    ]
    floor = models.IntegerField(default=1, verbose_name='Floor (0 for ICU)', choices=floors)
    rooms = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
    ]
    room = models.IntegerField(default=1, choices=rooms)
    beds = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
    ]
    bed = models.IntegerField(default=1, choices=beds)
    patient = models.OneToOneField(Patient, models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.floor}{self.room}{self.bed}'


class Medicine(models.Model):
    patient = models.ForeignKey(Patient, models.CASCADE)
    name = models.CharField(max_length=50)
    order = models.TextField()

    def __str__(self):
        return self.name


class Payment(models.Model):
    patient = models.ForeignKey(Patient, models.CASCADE)
    title = models.CharField(max_length=50)
    cost = models.BigIntegerField(default=0)
    paid = models.BigIntegerField(default=0)

    def clean(self):
        if self.paid > self.cost:
            raise ValidationError(_('Can not pay more than cost!'))

    def __str__(self):
        return self.title
