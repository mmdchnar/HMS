from django.contrib import admin
from django.utils.html import format_html
from .models import Patient, Bed, Medicine, Payment
from django.utils.translation import gettext_lazy as _


class MedicineInline(admin.TabularInline):
    model = Medicine
    extra = 0


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


class PatientAdmin(admin.ModelAdmin):
    search_fields = ('first_name', "last_name")
    list_display = ['__str__', 'sickness', 'doctor', 'nurse', 'debt', 'paid', 'login_at', 'bed']
    fields = [
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

    def get_fields(self, request, obj=None):
        if request.user.groups.filter(name__in=['Doctors', 'Nurses']):
            self.fields = [field for field in self.fields if field not in ['national_id', 'phone_number', 'address']]
            self.list_display = [display for display in self.list_display if
                                 display not in ['debt', 'paid', 'login_at']]

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
            if 'Nurses' in user_groups:
                readonly_fields.remove('nurse_report')
            if 'Managers' in user_groups:
                readonly_fields = [
                    field for field in readonly_fields
                    if field not in [
                        'first_name',
                        'last_name',
                        'insurance_type',
                        'watchful_name',
                        'age',
                        'doctor',
                        'nurse']]
        return readonly_fields

    inlines = [
        MedicineInline,
        PaymentInline,
    ]

    def debt(self, obj):
        unpaid_payments = obj.payment_set.filter(is_paid=False)
        total_amount = sum(payment.cost for payment in unpaid_payments)
        return format_html(f'<b style="color: red">{total_amount or "-"}</b>')

    debt.short_description = 'Debt'
    debt.allow_tag = True

    def paid(self, obj):
        paid_payments = obj.payment_set.filter(is_paid=True)
        total_amount = sum(payment.cost for payment in paid_payments)
        return format_html(f'<b style="color: green">{total_amount or "-"}</b>')

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
        return obj.patient if obj.patient else '--------------------'

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
            'is_paid',
        ], }),)

    list_display = ('patient', 'title', 'cost', 'is_paid')


admin.site.register(Payment, PaymentAdmin)
admin.site.register(Bed, BedAdmin)
admin.site.register(Patient, PatientAdmin)
