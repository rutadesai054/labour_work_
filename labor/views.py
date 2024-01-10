from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
import random
from django.conf import settings
from .models import labor_register
from parties.models import parties_detail, task


def labor_id_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        labor_id = request.session.get('labor_id', None)
        if not labor_id:
            return redirect('login_view')
        else:
            try:
                get_labor_data = labor_register.objects.get(
                    labor_id=request.session.get('labor_id'))
            except labor_register.DoesNotExist:
                print("User does not exist.")
            else:
                request.session['first_name'] = get_labor_data.first_name
                request.session['last_name'] = get_labor_data.last_name
                request.session['email'] = get_labor_data.email
                request.session['mobile'] = get_labor_data.mobile

                return view_func(request, *args, **kwargs)
    return _wrapped_view


def login_view(request):
    if request.method == 'POST':
        labor_id_ = request.POST['labor_id']
        password_ = request.POST['password']

        try:
            check_user = labor_register.objects.get(labor_id=labor_id_)
        except labor_register.DoesNotExist:
            print("User does not exist.")
        else:
            if check_user:
                if check_user.password == password_:
                    request.session['labor_id'] = labor_id_
                    print("Now you are logged in.")
                    return redirect('dashboard_view')
                else:
                    print("Labor_id or Password doesn't match.")

    return render(request, 'login.html')


def register_request_view(request):
    return render(request, 'register-request.html')


def forgot_password_view(request):
    if request.method == 'POST':
        email_ = request.POST['email']
        try:
            check_user = labor_register.objects.get(email=email_)
        except labor_register.DoesNotExist:
            print("User does not exist.")
        else:
            if check_user:
                otp_ = random.randint(111111, 999999)

                subject = 'OTP Verification | WORK-DIARY'
                message = f"Your otp is : {otp_}"
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [f'{email_}']

                print(subject, message, from_email, recipient_list)
                send_mail(subject, message, from_email, recipient_list)
                check_user.otp = otp_
                check_user.save()
                context = {
                    'email': email_
                }

                return render(request, 'otp-verification.html', context)
    return render(request, 'forgot-password.html')


def otp_verify_view(request):
    if request.method == 'POST':
        email_ = request.POST['email']
        otp_ = request.POST['otp']
        new_password_ = request.POST['new_password']
        confirm_password_ = request.POST['confirm_password']
        try:
            check_user = labor_register.objects.get(email=email_)
        except labor_register.DoesNotExist:
            print("User does not exist.")
        else:
            if check_user:
                if check_user.otp == otp_:
                    if new_password_ == confirm_password_:
                        check_user.password = new_password_
                        check_user.save()
                        print("Password updated successfully")
                    else:
                        print("New password and Confirm password doesn't match")
                else:
                    print("Invalid otp")
    return render(request, 'otp-verification.html')


@labor_id_required
def logout(request):
    if 'labor_id' in request.session:
        # request.session.clear()
        del request.session['labor_id']
        print("Now you are logged out.")
        return redirect('login_view')
    print("You are not logged in yet.")
    return redirect('login_view')


@labor_id_required
def dashboard_view(request):
    return render(request, 'dashboard.html')


@labor_id_required
def tasks_view(request):
    labor_id_ = request.session.get('labor_id')
    parties_ = parties_detail.objects.filter(labor_id_id=labor_id_)
    tasks_ = task.objects.filter(labor_id_id=labor_id_).order_by('-created_at')
    context = {
        'parties': parties_,
        'tasks': tasks_
    }
    return render(request, 'tasks.html', context)


@labor_id_required
def update_task(request, task_id):
    get_task_details = task.objects.get(task_id=task_id)
    labor_id_ = request.session.get('labor_id')
    parties_ = parties_detail.objects.filter(labor_id=labor_id_)
    instance = get_object_or_404(task, task_id=task_id)

    context = {
        'task': get_task_details,
        'parties': parties_,
        'TASK_STATUS': instance.TASK_STATUS,
        'task_status': get_task_details.task_status
    }
    return render(request, 'update-task.html', context)


@labor_id_required
def delete_task(request, task_id):
    delete_task_ = task.objects.get(task_id=task_id)
    delete_task_.delete()
    return redirect('tasks_view')


@labor_id_required
def payment_entry(request, task_id):
    get_task_details = task.objects.get(task_id=task_id)
    if request.method == 'POST':
        payment_entry_ = request.POST['payment_entry']
        payment_date_ = request.POST['payment_date']

        # if payment_entry_ <= get_task_details.total_payment:
        #     if get_task_details.paid_payment <= get_task_details.total_payment:
        #     get_task_details.paid_payment += payment_entry_

    context = {
        'task': get_task_details,
    }
    return render(request, 'task-payment.html', context)


@labor_id_required
def parties_view(request):
    if request.method == 'POST':
        firm_name_ = request.POST['firmname']
        first_name_ = request.POST['firstname']
        last_name_ = request.POST['lastname']
        email_ = request.POST['email']
        mobile_ = request.POST['mobile']
        address_ = request.POST['address']

        new_party = parties_detail.objects.create(
            labor_id_id=request.session.get('labor_id'),
            firm_name=firm_name_,
            first_name=first_name_,
            last_name=last_name_,
            email=email_,
            mobile=mobile_,
            address=address_

        )
        new_party.save()
        print("Party added")
        return redirect('parties_view')

    parties_ = parties_detail.objects.filter(
        labor_id=request.session.get('labor_id')).order_by('-id')
    context = {
        'parties': parties_
    }
    return render(request, 'parties.html', context)


@labor_id_required
def update_party_details(request, id):
    get_party = parties_detail.objects.get(id=id)
    if request.method == 'POST':
        firm_name_ = request.POST['firmname']
        first_name_ = request.POST['firstname']
        last_name_ = request.POST['lastname']
        email_ = request.POST['email']
        mobile_ = request.POST['mobile']
        address_ = request.POST['address']
        get_party.firm_name = firm_name_
        get_party.first_name = first_name_
        get_party.last_name = last_name_
        get_party.email = email_
        get_party.mobile = mobile_
        get_party.address = address_
        get_party.save()
        print("Party details updated")
        return redirect('parties_view')

    context = {
        'get_party': get_party
    }
    return render(request, 'update-party.html', context)


@labor_id_required
def delete_party(request, id):
    get_party = parties_detail.objects.get(id=id)
    get_party.delete()
    print("Party delete")
    return redirect('parties_view')


@labor_id_required
def payments_view(request):
    return render(request, 'payments.html')


@labor_id_required
def profile_view(request):
    return render(request, 'profile.html')


def add_task(request):
    if request.method == 'POST':
        party_id_ = request.POST['firmname']
        title_ = request.POST['title']
        content_ = request.POST['content']
        total_payment_ = request.POST['total_payment']

        new_task = task.objects.create(
            labor_id_id=request.session.get('labor_id'),
            party_id_id=party_id_,
            title=title_,
            content=content_,
            total_payment=total_payment_,
        )
        new_task.save()
        print("Task added")
        return redirect('tasks_view')

        # print(party_id, title, content, total_payment)

    return render(request, 'tasks.html')
