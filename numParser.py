# -*- coding: UTF-8 -*-
import os

locale = os.getenv('LANG', u'en_US.utf8')

# Define local dicts
arabic = {u'0': u'0', u'1': u'1', u'2': u'2', u'3': u'3', u'4': u'4', u'5': u'5', u'6': u'6', u'7': u'7', u'8': u'8', u'9': u'9'}
indic = {u'۰': u'0', u'۱': u'1', u'۲': u'2', u'۳': u'3', u'۴': u'4', u'۵': u'5', u'۶': u'6', u'۷': u'7', u'۸': u'8', u'۹': u'9'}
tamil = {u'௦': u'0', u'௧': u'1', u'௨': u'2', u'௩': u'3', u'௪': u'4', u'௫': u'5', u'௬': u'6', u'௭': u'7', u'௮': u'8', u'௯': u'9'}
devanagari = {u'०': u'0', u'१': u'1', u'२': u'2', u'३': u'3', u'४': u'4', u'५': u'5', u'६': u'6', u'७': u'7', u'८': u'8', u'९': u'9'}
kannada = {u'0': u'0', u'౧': u'1', u'౨': u'2', u'౩': u'3', u'౪': u'4', u'౫': u'5', u'౬': u'6', u'౭': u'7', u'౮': u'8', u'౯': u'9'}
malayam = {u'൦': u'0', u'൧': u'1', u'൨': u'2', u'൩': u'3', u'൪': u'4', u'൫': u'5', u'൬': u'6', u'൭': u'7', u'൮': u'8', u'൯': u'9'}

if locale in ['ar_SA.utf8', 'ar_YE.utf8', 'ar_AE.utf8', 'ar_SY.utf8', 'ar_OM.utf8', 'ar_JO.utf8', 'ar_IQ.utf8', 'ar_KW.utf8', 'ar_LB.utf8', 'ar_IQ.utf8', 'ar_SD.utf8', 'ar_EG.utf8', 'fa_IR.utf8']:
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

standardDic = {v: k for k, v in localDic.items()}


def local(standardString):
    result = u''
    for c in standardString:
        if c.encode('utf-8') in standardDic:
            result = result + standardDic[c]
        else:
            result = result + c
    return result


def standard(localString):
    localString = localString.decode('utf-8')
    result = u''
    for c in localString:
        if c in localDic:
            result = result + localDic[c]
        else:
            result = result + c
    return result
