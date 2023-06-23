from django.shortcuts import render
from .models import Payment


def invoice(request, national_id):
    payments = Payment.objects.filter(patient__national_id=national_id)
    context = {
        'national_id': national_id,
        'name': f'{payments.last().patient.first_name} {payments.last().patient.last_name}',
        'address': payments.last().patient.address,
        'phone_number': payments.last().patient.phone_number,
        'login_time': payments.last().patient.login_at,
        'payments': [(i+1, payments[i], payments[i].cost, payments[i].paid) for i in range(len(payments))],
        'paid': sum(payment.paid for payment in payments),
        'unpaid': sum(payment.cost - payment.paid for payment in payments),
    }
    return render(request, 'invoice.html', context=context)

