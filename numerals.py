# -*- coding: utf-8 -*-
import os

locale = os.getenv('LANG', 'en_US.utf8')

# Define local dicts
arabic = {'0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
          '5': '5', '6': '6', '7': '7', '8': '8', '9': '9'}
indic = {'۰': '0', '۱': '1', '٢': '2', '٣': '3', '۴': '4',
         '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9'}
tamil = {'௦': '0', '௧': '1', '௨': '2', '௩': '3', '௪': '4',
         '௫': '5', '௬': '6', '௭': '7', '௮': '8', '௯': '9'}
devanagari = {'०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
              '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'}
kannada = {'೦': '0', '౧': '1', '೨': '2', '೩': '3', '౪': '4',
           '೫': '5', '೬': '6', '೭': '7', '౮': '8', '౯': '9'}
malayam = {'൦': '0', '൧': '1', '൨': '2', '൩': '3', '൪': '4',
           '൫': '5', '൬': '6', '൭': '7', '൮': '8', '൯': '9'}

if locale in ['ar_SA.utf8', 'ar_YE.utf8', 'ar_AE.utf8', 'ar_SY.utf8',
              'ar_OM.utf8', 'ar_JO.utf8', 'ar_IQ.utf8', 'ar_KW.utf8',
              'ar_LB.utf8', 'ar_IQ.utf8', 'ar_SD.utf8', 'ar_EG.utf8',
              'fa_IR.utf8']:
    localDic = indic
elif locale[0:3] in {'ta_'}:
    localDic = tamil
elif locale[0:3] in {'hi_', 'bn_', 'gu_', 'mr_'}:
    localDic = devanagari
elif locale[0:3] in {'kn_'}:
    localDic = kannada
elif locale[0:3] in {'ml_'}:
    localDic = malayam
else:
    localDic = arabic

standardDic = {v: k for k, v in list(localDic.items())}


def local(standardString):
    result = ''
    for c in standardString:
        if c in standardDic:
            result = result + standardDic[c]
        else:
            result = result + c
    return result


def standard(localString):
    result = ''
    for c in localString:
        if c in localDic:
            result = result + localDic[c]
        else:
            result = result + c
    return result
