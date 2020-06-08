# from django.core.mail import send_mail
# EXAMPLE 1:
# send_mail(
#     "asunto prueba",
#     "Hola mundo",
#     "WISROVI",
#     ["wisrovi.rodriguez@gmail.com"],
#     fail_silently=False,
# )


# ESAMPLE 2:
# listaCorreosDestinatarios = list()
# listaCorreosDestinatarios.append("wisrovi.rodriguez@gmail.com")
# diccionarioDatos = dict()
# diccionarioDatos['ADMIN'] = "ejemplo de datos del diccionario"
# html_message = render_to_string('template_email.html', diccionarioDatos)
# asunto = "asunto del correo"
# firmaResumenRemitente = "firma del remitente"
# send_mail(
#     asunto,
#     strip_tags(html_message),
#     firmaResumenRemitente,
#     listaCorreosDestinatarios,
#     fail_silently=False,
#     html_message=html_message
# )

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'wisrovi.rodriguez@gmail.com'
EMAIL_HOST_PASSWORD = 'FC5JB6EM'
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
