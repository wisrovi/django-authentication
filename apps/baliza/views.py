from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt

from django.contrib import messages

import baliza.Util as BALIZ
from baliza.Form import PackBracelet, SignUpForm
from baliza.models import Bracelet, HistorialBraceletSensors, Baliza, UsuarioRol, RolUsuario

from django.contrib.auth.forms import UserCreationForm


# Create your views here.

# @login_required
@csrf_exempt
def getPackStringBaliza(request):
    form = PackBracelet()
    if request.method == 'POST':
        form = PackBracelet(request.POST)
        if form.is_valid():
            objetos = BALIZ.UnZipPackBracelets()
            string_data = form.cleaned_data['string_pack']
            key = form.cleaned_data['key']
            if key:
                if key == "ESP32":

                    if string_data:
                        # vamos a procesar los datos recibidos

                        # listamos los correos de los usuario con rol de server
                        # y se toman los correos para enviar los mensajes si algo sale mal en el proceso siguiente
                        rolBuscar = 'Server'
                        listaCorreosDestinatarios = list()
                        for rol in RolUsuario.objects.all():
                            if rol.rolUsuario.find(rolBuscar) > 0:
                                for usuarioRevisar in UsuarioRol.objects.all():
                                    if usuarioRevisar.rolUsuario == rol:
                                        listaCorreosDestinatarios.append(usuarioRevisar.usuario.email)

                        # Paso 1:
                        # Leer todos los datos de los sensores
                        listBracelets = objetos.setString(string_data)
                        listBracelets = listBracelets[::-1]

                        todasPulserasRegistradas = Bracelet.objects.all()
                        macEncontradasPaquete = list()
                        print("*****************", end="")
                        from time import gmtime, strftime
                        showtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                        print(showtime, end="")
                        print("*****************")
                        print("Procesando datos de los sensores")

                        import json
                        baliza = json.loads(string_data)['baliza']
                        balizaEncontrada = None
                        for baliz in Baliza.objects.all():
                            if baliz.macDispositivoBaliza == baliza:
                                balizaEncontrada = baliz
                                break

                        if balizaEncontrada is not None:
                            for bracelet in listBracelets:
                                # Procesando cada bracelet por separado del paquete recibido
                                macPulsera_complete = bracelet.MAC[0:2] \
                                                      + ":" + bracelet.MAC[2:4] \
                                                      + ":" + bracelet.MAC[4:6] \
                                                      + ":" + bracelet.MAC[6:8] \
                                                      + ":" + bracelet.MAC[8:10] \
                                                      + ":" + bracelet.MAC[10:12]

                                distancia = dict()
                                distancia["rssi"] = bracelet.RSI

                                # print("*****************************************************")
                                if macPulsera_complete in macEncontradasPaquete:
                                    pass
                                else:
                                    # Se confirma que no se este procesando un bracelet repetido para este paquete
                                    macEncontradasPaquete.append(macPulsera_complete)

                                    sensores = dict()
                                    sensores["temperatura"] = bracelet.TEM
                                    sensores["ppm"] = bracelet.PPM
                                    sensores["caidas"] = bracelet.CAI
                                    sensores["proximidad"] = bracelet.PRO
                                    otrosDatosPulsera = dict()
                                    otrosDatosPulsera["bat"] = bracelet.BAT
                                    otrosDatosPulsera["semilla"] = bracelet.SED

                                    pulseraEncontrada = None
                                    for i in todasPulserasRegistradas:
                                        if i.macDispositivo == macPulsera_complete:
                                            pulseraEncontrada = i
                                            break

                                    if pulseraEncontrada is not None:

                                        # Paso 1: Procesar datos de  RSSI para determinar la ubicación de los sensores

                                        # Paso 2: Procesar datos de los sensores del bracelet que se reportó en este escaner

                                        dato_ppm_int = int(sensores["ppm"])
                                        dato_caida_bool = bool(sensores["caidas"])
                                        dato_proximidad_bool = bool(sensores["proximidad"])
                                        dato_bateria_int = int(otrosDatosPulsera["bat"])
                                        dato_temperatura_int = int(sensores["temperatura"])
                                        dato_rssi_int = int(distancia["rssi"])

                                        if dato_bateria_int > 0 \
                                                and dato_ppm_int > 0 \
                                                and dato_temperatura_int > 0 \
                                                and dato_rssi_int > 0:

                                            if bracelet.CAI == "1":
                                                diccionarioDatos = dict()
                                                diccionarioDatos['ADMIN'] = str('Admin Server')
                                                diccionarioDatos['BALIZA'] = str(baliza)
                                                diccionarioDatos['MAC'] = str(macPulsera_complete)
                                                diccionarioDatos['PROJECT'] = str('Hospital Smart Bracelet')
                                                diccionarioDatos['FIRMA'] = str('WISROVI')
                                                html_message = render_to_string(
                                                    'email/bracelet_alerta_persona_caida.html',
                                                    diccionarioDatos)
                                                asunto = "Alerta, persona caida (" + macPulsera_complete + ")"
                                                firmaResumenRemitente = "Hospital Smart Bracelet"
                                                send_mail(
                                                    asunto,
                                                    strip_tags(html_message),
                                                    firmaResumenRemitente,
                                                    listaCorreosDestinatarios,
                                                    fail_silently=False,
                                                    html_message=html_message
                                                )
                                                print(macPulsera_complete + " - Persona caida")

                                            if not bracelet.PRO == "1":
                                                diccionarioDatos = dict()
                                                diccionarioDatos['ADMIN'] = str('Admin Server')
                                                diccionarioDatos['BALIZA'] = str(baliza)
                                                diccionarioDatos['MAC'] = str(macPulsera_complete)
                                                diccionarioDatos['PROJECT'] = str('Hospital Smart Bracelet')
                                                diccionarioDatos['FIRMA'] = str('WISROVI')
                                                html_message = render_to_string(
                                                    'email/bracelet_alerta_persona_seQuitoPulsera.html',
                                                    diccionarioDatos)
                                                asunto = "Alerta, persona se quitó el bracelet (" + macPulsera_complete + ")"
                                                firmaResumenRemitente = "Hospital Smart Bracelet"
                                                send_mail(
                                                    asunto,
                                                    strip_tags(html_message),
                                                    firmaResumenRemitente,
                                                    listaCorreosDestinatarios,
                                                    fail_silently=False,
                                                    html_message=html_message
                                                )
                                                print(macPulsera_complete + " - Persona se quitó el bracelet")

                                            histBraceSensors = HistorialBraceletSensors()
                                            histBraceSensors.bracelet = pulseraEncontrada
                                            histBraceSensors.ppm_sensor = dato_ppm_int
                                            histBraceSensors.caida_sensor = dato_caida_bool
                                            histBraceSensors.proximidad_sensor = dato_proximidad_bool
                                            histBraceSensors.nivel_bateria = dato_bateria_int
                                            histBraceSensors.temperatura_sensor = dato_temperatura_int
                                            histBraceSensors.rssi_signal = dato_rssi_int
                                            histBraceSensors.baliza = balizaEncontrada

                                            todosRegistros = HistorialBraceletSensors.objects.filter(
                                                bracelet=pulseraEncontrada.id).order_by('-id')
                                            print(pulseraEncontrada, end=" ( id=")
                                            if todosRegistros.count() > 0:
                                                for esteRegistro in todosRegistros:
                                                    print(esteRegistro.id, "): ", end="")
                                                    if histBraceSensors.bracelet == esteRegistro.bracelet \
                                                            and histBraceSensors.rssi_signal == esteRegistro.rssi_signal \
                                                            and histBraceSensors.ppm_sensor == esteRegistro.ppm_sensor \
                                                            and histBraceSensors.caida_sensor == esteRegistro.caida_sensor \
                                                            and histBraceSensors.temperatura_sensor == esteRegistro.temperatura_sensor \
                                                            and histBraceSensors.proximidad_sensor == esteRegistro.proximidad_sensor \
                                                            and histBraceSensors.nivel_bateria == esteRegistro.nivel_bateria:
                                                        print("Ya existe el registro")
                                                    else:
                                                        print("Registro no existe...", end="")
                                                        histBraceSensors.save()
                                                        print("Registro Guardado")
                                                    break
                                            else:
                                                print("No existen registros para este bracelet...", end="")
                                                histBraceSensors.save()
                                                print("Primer Registro Guardado")
                                                break
                                        else:
                                            # Datos invalidos, se reporta en correo de que el bracelet esta enviando datos invalidos

                                            diccionarioDatos = dict()
                                            diccionarioDatos['ADMIN'] = str('Admin Server')
                                            diccionarioDatos['BALIZA'] = str(baliza)
                                            diccionarioDatos['MAC'] = str(macPulsera_complete)
                                            diccionarioDatos['PROJECT'] = str('Hospital Smart Bracelet')
                                            diccionarioDatos['FIRMA'] = str('WISROVI')
                                            html_message = render_to_string('email/bracelet_report_bad_sensors.html',
                                                                            diccionarioDatos)
                                            asunto = "Nuevo Bracelet por registrar (" + macPulsera_complete + ")"
                                            firmaResumenRemitente = "Hospital Smart Bracelet"
                                            send_mail(
                                                asunto,
                                                strip_tags(html_message),
                                                firmaResumenRemitente,
                                                listaCorreosDestinatarios,
                                                fail_silently=False,
                                                html_message=html_message
                                            )
                                    else:
                                        print(macPulsera_complete, "- No existe el Bracelet")

                                        # como no existe la pulsera, entonces se envia un correo usando una plantilla
                                        # donde se reemplazan los datos en la plantilla y con esto se envia el correo
                                        # a los correos destinatarios y el asunto estipulado

                                        diccionarioDatos = dict()
                                        diccionarioDatos['ADMIN'] = str('Admin Server')
                                        diccionarioDatos['BALIZA'] = str(baliza)
                                        diccionarioDatos['MAC'] = str(macPulsera_complete)
                                        diccionarioDatos['PROJECT'] = str('Hospital Smart Bracelet')
                                        diccionarioDatos['FIRMA'] = str('WISROVI')
                                        html_message = render_to_string('email/nuevo_bracelet_encontrado.html',
                                                                        diccionarioDatos)
                                        asunto = "Nuevo Bracelet por registrar (" + macPulsera_complete + ")"
                                        firmaResumenRemitente = "Hospital Smart Bracelet"
                                        send_mail(
                                            asunto,
                                            strip_tags(html_message),
                                            firmaResumenRemitente,
                                            listaCorreosDestinatarios,
                                            fail_silently=False,
                                            html_message=html_message
                                        )

                            print("*****************************************************")
                            return HttpResponseRedirect('../receivedOK')
                        else:
                            diccionarioDatos = dict()
                            diccionarioDatos['ADMIN'] = str('Admin Server')
                            diccionarioDatos['BALIZA'] = str(baliza)
                            diccionarioDatos['PROJECT'] = str('Hospital Smart Bracelet')
                            diccionarioDatos['FIRMA'] = str('WISROVI')
                            html_message = render_to_string('email/nuevo_baliza_encontrada.html',
                                                            diccionarioDatos)
                            asunto = "Nueva Baliza por registrar (" + baliza + ")"
                            firmaResumenRemitente = "Hospital Smart Bracelet"
                            send_mail(
                                asunto,
                                strip_tags(html_message),
                                firmaResumenRemitente,
                                listaCorreosDestinatarios,
                                fail_silently=False,
                                html_message=html_message
                            )
                            print(baliza + " - Nueva Baliza por registrar")
                        # Entregar respuesta final

    return render(request, "receivedBaliza.html", {'form': form})

def signup_view(request):
    form = SignUpForm()
    if request.method == 'POST':
        pass
        messages.success(request, 'Account created successfully')
        # form = UserCreationForm(request.POST)
        # if form.is_valid():
        #     #form.save()
        #     messages.success(request, 'Account created successfully')
    return render(request, 'FORM.html', {'form': form})


def setReceivedOK(request):
    return render(request, 'receivedOK.html', {})
