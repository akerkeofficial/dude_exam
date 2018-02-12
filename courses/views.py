from django.shortcuts import render, render_to_response, redirect
from django.utils import timezone
from django.http import Http404, HttpResponse
from .models import Professor, Exam, Course
from .forms import ExamForm
from django.contrib.auth.decorators import login_required
from accounts.forms import LoginForm, SignUpForm
from django.contrib.auth import login, logout, authenticate

from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from accounts.tokens import account_activation_token
from django.contrib.sites.shortcuts import get_current_site



def home_page(request):
    context = {}
    if request.method=='POST' and request.POST['action'] == 'Login':
        login_form=LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('/main')

    elif request.method=='POST' and request.POST['action'] == 'Signup':
        signup_form = SignUpForm(request.POST)
        if signup_form.is_valid():
            user = signup_form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            subject = 'Activate Your SDUDE Account'
            message = render_to_string('accounts/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return redirect('/signup/account_activation_sent')

    else:
        login_form = LoginForm()
        signup_form = SignUpForm()
        context['login_form'] = login_form
        context['signup_form'] = signup_form
        return render(request, "index.html", context)

@login_required(login_url='/')
def main_page(request):
    course_list = Course.objects.all()
    prof_list = Professor.objects.all()
    exam_list = Exam.objects.all()

    context = {
        "course_list": course_list,
        "prof_list": prof_list,
        "exam_list": exam_list,
        "title": "Main Page"
    }

    if request.method == 'POST':
        exam_form = ExamForm(request.POST, request.FILES)
        if exam_form.is_valid():
            ins = exam_form.save(commit=False)
            ins.created_by = request.user
            ins.save()
            return redirect('/')
    else:
        exam_form = ExamForm()
        context['form'] = exam_form
    return render(request, "main.html", context)
