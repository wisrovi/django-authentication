from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags

import authentication.PREFERENCES as Preferences

from .forms import LoginForm, RegistrationForm


def signin(request):
    forms = LoginForm()
    if request.method == 'POST':
        forms = LoginForm(request.POST)
        if forms.is_valid():
            username = forms.cleaned_data['username']
            password = forms.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')
    context = {
        'form': forms
    }
    return render(request, 'signin.html', context)

def signup_confirm_email(request):
    forms = RegistrationForm()
    code_verification = ""
    if request.method == 'POST':
        parametros = request.POST
        if len(parametros) == 7:
            data = dict()
            if len(parametros['code_verification']) > 0 \
                    and len(parametros['code']) > 0:
                if parametros['code_verification'] == parametros['code']:
                    print('OK')
                    return redirect('signup')
                    # No esta redireccionando a la siguiente vista
                data['Value_button'] = 'VALIDAR CODIGO'
                print('hola mundo')
            else:
                print(parametros['firstname'])
                print(parametros['lastname'])
                print(parametros['email'])

                if len(parametros['code_verification']) < 1:
                    from random import randint
                    code_verification = str(randint(1000, 9999))
                    data['code_verification'] = code_verification
                else:
                    data['code_verification'] = parametros['code_verification']
                data['Value_button'] = 'VALIDAR CODIGO'
            return JsonResponse(data, safe=False)
        else:
            data = dict()
            data['error'] = 'Datos invalidos'
            return JsonResponse(data, safe=False)
    context = {
        'form': forms,
        'Value_button': 'VALIDAR EMAIL',
        'code_verification': code_verification
    }
    return render(request, 'signup_confim_email.html', context)



def signup(request):
    forms = RegistrationForm()
    pasoFinal = False
    value_button = 'Validar Email'
    code_verification = ""
    if request.method == 'POST':
        parametros = request.POST
        print(parametros['email'])
        if len(parametros) == 6:
            print(parametros['firstname'])
            print(parametros['lastname'])
            print(parametros['email'])
            from random import randint
            code_verification = str(randint(1000, 9999))
            data = dict()
            data['code_verification'] = code_verification
            data['value_button'] = "Validar Code"
            data['paso'] = "pasoFinal"
            return JsonResponse(data, safe=False)
        else:
            forms = RegistrationForm(parametros)
            print(forms.is_valid())
            if forms.is_valid():
                firstname = forms.cleaned_data['firstname']
                lastname = forms.cleaned_data['lastname']
                email = forms.cleaned_data['email']
                username = forms.cleaned_data['username']
                password = forms.cleaned_data['password']
                confirm_password = forms.cleaned_data['confirm_password']
                if password == confirm_password:
                    try:
                        from datetime import datetime
                        now = datetime.now()
                        tiempoAhora = dict()
                        tiempoAhora['year'] = now.year
                        tiempoAhora['month'] = now.month
                        tiempoAhora['day'] = now.day
                        tiempoAhora['hour'] = now.hour
                        tiempoAhora['minute'] = now.minute + 15
                        tiempoAhora['second'] = now.second
                        tiempoAhora['firstname'] = firstname
                        tiempoAhora['lastname'] = lastname
                        tiempoAhora['email'] = email
                        tiempoAhora['username'] = username
                        tiempoAhora['password'] = password

                        import base64
                        import json
                        import gzip
                        comprimido = base64.b64encode(bytes(json.dumps(tiempoAhora), 'utf-8'))
                        comprimido_codificado = gzip.compress(comprimido)

                        diccionarioDatos = dict()
                        diccionarioDatos['USERNAME'] = username
                        diccionarioDatos['NAME'] = firstname
                        diccionarioDatos['LASTNAME'] = lastname
                        diccionarioDatos['EMAIL'] = email
                        diccionarioDatos['TOKEN'] = comprimido_codificado

                        decodificado_comprimido = gzip.decompress(comprimido_codificado)
                        descomprimido = base64.b64decode(decodificado_comprimido)
                        print(decodificado_comprimido)
                        print(descomprimido)

                        listaCorreosDestinatarios = list()
                        listaCorreosDestinatarios.append(email)
                        html_message = render_to_string('email_user_create.html', diccionarioDatos)
                        asunto = "Bienvenido, falta confirmar correo"
                        firmaResumenRemitente = Preferences.NAME_APP
                        send_mail(
                            asunto,
                            strip_tags(html_message),
                            firmaResumenRemitente,
                            listaCorreosDestinatarios,
                            fail_silently=False,
                            html_message=html_message
                        )

                        pasoFinal = False
                        value_button = 'Crear'

                        # User.objects.create_user(username=username, password=password, email=email, first_name=firstname,
                        #                          last_name=lastname)
                        return redirect('signin')
                    except:
                        context = {
                            'form': forms,
                            'error': 'This Username Already exists!'
                        }
                        return render(request, 'signup.html', context)
    context = {
        'form': forms,
        'paso': pasoFinal,
        'Value_button': value_button,
        'code_verification': code_verification
    }
    return render(request, 'signup.html', context)


def signout(request):
    logout(request)
    return redirect('signin')
