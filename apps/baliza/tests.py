from django.test import TestCase

# Create your tests here.

import baliza.Util as BALIZ

EXAMPLE = '{"beacons":[{"SED":"0000","MAC":"90E202048AE9","BAT":"40","PPM":"095","CAI":"1","TEM":"328","RSI":"075","PRO":"1"},{"SED":"0000","MAC":"90E202048AE9","BAT":"40","PPM":"095","CAI":"1","TEM":"328","RSI":"075","PRO":"1"},{"SED":"0000","MAC":"90E202048AE9","BAT":"40","PPM":"095","CAI":"1","TEM":"328","RSI":"075","PRO":"1"},{"SED":"0000","MAC":"90E202048AE9","BAT":"40","PPM":"095","CAI":"1","TEM":"328","RSI":"075","PRO":"1"},{"SED":"0000","MAC":"90E202048AE9","BAT":"40","PPM":"095","CAI":"1","TEM":"328","RSI":"075","PRO":"1"}]}'

objetos = BALIZ.UnZipPackBracelets()
listBracelets = objetos.setString(EXAMPLE)
#print(listBracelets[0].MAC)
print(listBracelets)
print(objetos.convertList())


