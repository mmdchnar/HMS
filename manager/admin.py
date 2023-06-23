from django.contrib import admin
from django.utils.html import format_html
from .models import Patient, Bed, Medicine, Payment
from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.forms import CheckboxInput
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.conf import settings
from pytz import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F


class MedicineInline(admin.TabularInline):
    model = Medicine
    extra = 0

    def has_add_permission(self, request, obj=None):
        if obj and request.user != obj.doctor and not request.user.is_superuser:
            return False
        return super().has_add_permission(request, obj)

    has_change_permission = has_add_permission
    has_delete_permission = has_add_permission


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


class CustomCheckboxInput(CheckboxInput):
    def __init__(self, note=None, **kwargs):
        self.note = note
        super().__init__(**kwargs)

    def render(self, name, value, attrs=None, renderer=None):
        checkbox_html = super().render(name, value, attrs, renderer)
        if self.note:
            note_html = f'<span style="color:red;">{self.note}</span>'
            return f'{note_html}  {checkbox_html}'
        return checkbox_html


class BedInline(admin.TabularInline):
    model = Bed
    extra = 0


class PatientAdmin(admin.ModelAdmin):
    search_fields = ('first_name', "last_name")
    list_display = [
        '__str__',
        'sickness',
        'doctor',
        'nurse',
        'debt',
        'paid',
        'custom_login_at',
        'custom_discharge_date',
        'bed',
        'is_hospitalized',
    ]
    fields = [
        'is_hospitalized',
        'first_name',
        'last_name',
        'sickness',
        'age',
        'height',
        'weight',
        'blood_type',
        'insurance_type',
        'national_id',
        'phone_number',
        'address',
        'watchful_name',
        'nurse',
        'nurse_report',
        'doctor',
        'doctor_order',
    ]

    def custom_login_at(self, obj):
        return obj.login_at.strftime('%y/%m/%d %H:%M')

    custom_login_at.short_description = 'Login'

    def custom_discharge_date(self, obj):
        if obj.discharge_date:
            return obj.discharge_date.strftime('%y/%m/%d %H:%M')
        else:
            return '-'

    custom_discharge_date.short_description = 'Discharge'

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)

        if db_field.name == 'is_hospitalized':
            formfield.widget = CustomCheckboxInput(
                note='This action cannot be undone.     <br><br>')

        return formfield

    def save_model(self, request, obj, form, change):
        if change:
            if not obj.is_hospitalized:
                try:
                    obj.bed.delete()
                except ObjectDoesNotExist:
                    pass
                obj.discharge_date = datetime.now(tz=timezone(settings.TIME_ZONE))
            elif obj.is_hospitalized:
                obj.discharge_date = None
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        if obj and not obj.is_hospitalized and not request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)

    def get_list_display(self, request, obj=None):
        if request.user.groups.filter(name__in=['Doctors', 'Nurses']):
            return [display for display in self.list_display
                    if display not in ['debt', 'paid', 'login_at', 'discharge_date']]
        else:
            return self.list_display

    def get_fields(self, request, obj=None):
        if request.user.groups.filter(name__in=['Doctors', 'Nurses']):
            self.fields = [field for field in self.fields if field not in ['national_id', 'phone_number', 'address']]

        return super(PatientAdmin, self).get_fields(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['first_name',
                           'last_name',
                           'insurance_type',
                           'doctor_order',
                           'nurse_report',
                           'watchful_name',
                           'age',
                           'sickness',
                           'blood_type',
                           'height',
                           'weight',
                           'doctor',
                           'nurse',
                           'is_hospitalized',
                           'discharge_date',
                           ]
        if request.user.is_superuser:
            return []
        else:
            user_groups = request.user.groups.values_list('name', flat=True)
            if 'Doctors' in user_groups or 'Nurses' in user_groups:
                readonly_fields.remove('sickness')
                readonly_fields.remove('blood_type')
                readonly_fields.remove('height')
                readonly_fields.remove('weight')
            if 'Doctors' in user_groups:
                readonly_fields.remove('doctor_order')
                if request.user != obj.doctor:
                    readonly_fields = self.fields
            elif 'Nurses' in user_groups:
                readonly_fields.remove('nurse_report')
                if request.user != obj.nurse:
                    readonly_fields = self.fields
            elif 'Managers' in user_groups:
                readonly_fields = [
                    field for field in readonly_fields
                    if field not in [
                        'first_name',
                        'last_name',
                        'insurance_type',
                        'watchful_name',
                        'age',
                        'doctor',
                        'nurse',
                        'is_hospitalized',
                        'discharge_date',
                    ]]
        return readonly_fields

    inlines = [
        MedicineInline,
        PaymentInline,
        BedInline,
    ]

    def debt(self, obj):
        unpaid_payments = obj.payment_set.filter(cost__gt=F('paid'))
        total_amount = sum((payment.cost - payment.paid) for payment in unpaid_payments)
        return format_html(f'<a href="/invoice/{obj.national_id}"><u style="color: red">${total_amount}</u></a>')

    debt.short_description = 'Debt'
    debt.allow_tag = True

    def paid(self, obj):
        paid_payments = obj.payment_set.all()
        total_amount = sum(payment.paid for payment in paid_payments)
        return format_html(f'<a href="/invoice/{obj.national_id}"><u style="color: green">${total_amount}</u></a>')

    paid.short_description = 'Paid'
    paid.allow_tag = True


class IsFilledFilter(admin.SimpleListFilter):
    title = _('Is Filled?')
    parameter_name = 'is_filled'

    def lookups(self, request, model_admin):
        return (
            ('1', _('Filled beds')),
            ('0', _('Empty beds')),)

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(patient__isnull=False)
        elif self.value() == '0':
            return queryset.filter(patient__isnull=True)
        else:
            return queryset


class BedAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Bed:', {"fields": [
            'floor',
            'room',
            'bed',
            'patient',
        ], }),)

    def is_filled(self, obj):
        return bool(obj.patient)

    is_filled.boolean = True
    is_filled.short_doctor_order = 'Filled?'

    def is_filled_order(self, obj):
        return bool(obj.patient)

    @staticmethod
    def name(obj):
        return obj.patient or '--------------------'

    is_filled_order.admin_order_field = 'is_filled_field'

    list_display = ('name', 'floor', 'room', 'bed', 'is_filled')
    list_display_links = ('name', 'floor', 'room', 'bed', 'is_filled')
    list_filter = (IsFilledFilter,)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'patient':
            kwargs['queryset'] = Patient.objects.filter(bed__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class PaymentAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Payment:', {"fields": [
            'patient',
            'title',
            'cost',
            'paid',
        ], }),)

    list_display = ('patient', 'title', 'cost', 'paid')


class CustomUserAdmin(UserAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(id=request.user.id)
        return qs

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = [
            'group_permissions',
            'groups',
            'last_login',
            'date_joined',
            'is_superuser',
            'is_active',
            'is_staff',
            'user_permissions',
        ]
        if request.user.is_superuser:
            return []
        elif request.user.groups.filter(name='Managers'):
            readonly_fields.remove('is_active')
            readonly_fields.remove('groups')
        return readonly_fields

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Bed, BedAdmin)
admin.site.register(Patient, PatientAdmin)
