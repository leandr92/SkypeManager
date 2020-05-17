import json
import datetime
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import login, authenticate, logout
from .forms import RegistrationFrom, AccountAuthenticationForm, AccountUpdateForm
from .models import Account, Contact
from django.http import HttpResponse
from skpy import Skype
from skpy import SkypeCallMsg
from skpy import SkypeUser
from skpy import SkypeAuthException
from skpy import SkypeApiException

from django.template import loader


def registration_view(request):
    context= {}
    if request.POST:
        form = RegistrationFrom(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            account = authenticate(email = email, password = raw_password)
            login(request, account)

            return redirect('index')
        else:
            context['registration_form'] = form
    else:
        form = RegistrationFrom()
        context['registration_form'] = form
    return render(request, 'register.html', context)

def logout_view(request):
    logout(request)
    return redirect('index')

def login_view(request):

    context= {}

    user = request.user

    if user.is_authenticated:
        return redirect('index')
    if request.POST:
        form = AccountAuthenticationForm(request.POST)

        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)

            if user:
                login(request, user)
                return redirect('index')
    else:
        form = AccountAuthenticationForm()

    context['login_form'] = form
    return render(request, 'login.html', context)

def account_view(request):   
    if not request.user.is_authenticated:
        return redirect('login')
    context = {}

    if request.POST:
        form = AccountUpdateForm(request.POST, instance=request.user)

        if form.is_valid():
            form.initial ={
                "email": request.POST['email'],
                "username": request.POST['username'],
                "skype_login": request.POST['skype_login'],
                "skype_password": request.POST['skype_password'],
            }
            form.save()
            context['success_message'] = "Сохранено"
    else:
        form = AccountUpdateForm(
                initial={
                    "email": request.user.email,
                    "username": request.user.username,
                    "skype_login": request.user.skype_login,
                    "skype_password": request.user.skype_password,
                }
            )

    context['account_form'] = form
    return render(request, 'account.html', context)

def skype_login(request):

    template = loader.get_template('skypeLogin.html')
    context = {
        'contact_list': contacts,
    }
    return HttpResponse(template.render(context, request))

def index(request):

    if not request.user.is_authenticated:
        template = loader.get_template('login.html')
        context = {
        'error_message': "Пользователь не найден"
        }
        return HttpResponse(template.render(context, request))

    # HttpHead = "<HEAD></HEAD>"

    # HttpBody = "<body>Hello, world. You're at the polls index.</body>"

    # HttpPattern = "<HTML>" + HttpHead + HttpBody + "</HTML>"

    return redirect('calls')

def contacts_view(request):

    user = request.user

    if not user.is_authenticated:
        return redirect('login')

    login       = ""
    password    = ""
    skype_auth  = True
    skype_auth_error = ""

    if request.method == "POST":
        login = request.POST['login']
        password = request.POST['pass']

    # sk = Skype("mingaliev.e", "123jkpvdvxh123")
    sk = Skype(connect=False)

    sk.conn.setTokenFile(user.email + ".tokens-app")

    try:
        sk.conn.readToken()
    except SkypeAuthException:
        
        if not login or not password:
           skype_auth = False
           skype_auth_error = "Имя пользователя и пароль должны быть заполнены"

        if skype_auth: 

            sk.conn.setUserPwd(login, password)
            
            try:
                sk.conn.getSkypeToken()
            except SkypeAuthException as authEx:
                skype_auth = False
                skype_auth_error = authEx.args[0]

    try:
        sk.conn
    except SkypeAuthException as authEx:
        skype_auth = False
        skype_auth_error = authEx.args[0]

    if not skype_auth:
        return  HttpResponse(render(request, 'skypeLogin.html', {
            'error_message': "Аутентификация Skype не пройдена. Причина: " + skype_auth_error}))

    def GetContactInfo(contactName, id, used):

        contactInfo = {"name": "", "id": id, "used": used}

        if isinstance(contactName, SkypeUser.Name):
            contactInfo["name"] = str(contactName.first or '') + \
                " " + str(contactName.last or '')
        else:
            contactInfo["name"] = str(contactName or '')

        if contactInfo["name"].strip() == "":
            contactInfo["name"] = id

        return contactInfo

    contacts = []

    for contact in sk.contacts:

        used = False

        try:
            contact_data = Contact.objects.get(owner = user, contactId = contact.id)
            used = True

        except Contact.DoesNotExist:
            used = False

        contactInfo = GetContactInfo(contact.name, contact.id, used)
        contacts.append(contactInfo)

    template = loader.get_template('contacts.html')
    context = {
        'contact_list': contacts,
    }
    return HttpResponse(template.render(context, request))

def contacts_update(request):

    user = request.user

    if not user.is_authenticated:
        return redirect('login')

    if request.POST:
        
        contacts_json_data = request.POST.get('contacts', False);
        contacts_data = json.loads(contacts_json_data)

        if contacts_data:
           
            Contact.objects.filter(owner=user).delete()
            
            for contact_data in contacts_data:
                contact = Contact(owner = user, contactId=contact_data)
                contact.save()



    context = {"c_d":contacts_data}
    template = loader.get_template('contacts.html')

    return HttpResponse(contacts_data)

def calls(request):
    
    def GetContactInfo(contactName, id):

        contactInfo = {"name": "", "id": id, "duration": "", "duration_view": ""}

        if isinstance(contactName, SkypeUser.Name):
            contactInfo["name"] = str(contactName.first or '') + \
                " " + str(contactName.last or '')
        else:
            contactInfo["name"] = str(contactName or '')

        return contactInfo

    user = request.user
    skype_auth = True

    if not user.is_authenticated:
        return redirect('login')
  
    sk = Skype(connect=False)

    sk.conn.setTokenFile(user.email + ".tokens-app")

    try:
        sk.conn.readToken()
    except SkypeAuthException:
        
        if skype_auth: 
            
            try:
                sk.conn.getSkypeToken()
            except SkypeAuthException as authEx:
                skype_auth = False
                skype_auth_error = authEx.args[0]

    try:
        sk.conn
    except SkypeAuthException as authEx:
        skype_auth = False
        skype_auth_error = authEx.args[0]

    if not skype_auth:
        return  HttpResponse(render(request, 'skypeLogin.html', {
            'error_message': "Аутентификация Skype не пройдена. Причина: "}))

    used_contacts = Contact.objects.filter(owner = user)
    
    contacts = []

    for used_contact in used_contacts:

        contact = sk.contacts[used_contact.contactId]
        contacts.append(contact)
    
    calls = []

    for contact in contacts:

        contactInfo = GetContactInfo(contact.name, contact.id)

        msgs = []

        callFinded = False
        duration = ""

        while not callFinded:
            for msg in msgs:
                if isinstance(msg, SkypeCallMsg):
                    callFinded = True
                    
                    now = datetime.datetime.now()
                    days = ""
                
                    then = msg.time
                    
                    delta = now - then

                    days = delta.days
                    
                    duration = days 

                    break
            
            if duration:
                contactInfo["duration"] = duration
                contactInfo["duration_view"] = str(duration) + " д. назад"
           
            try:
                msgs = contact.chat.getMsgs()
            except SkypeApiException:
                callFinded = True

            if not len(msgs):
                callFinded = True
                contactInfo["duration_view"] = "Более 30 д. назад, или звонков небыло"

        calls.append(contactInfo)
   
    template = loader.get_template('calls.html')
    context = {"calls": calls}
    return HttpResponse(template.render(context, request))
