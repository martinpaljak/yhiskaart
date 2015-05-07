#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import hashlib
import binascii
import tempfile
import urllib
import urllib2 
import re

import Mifare
import NFCTagType1
import NDEFMessage

import pilet as piletee

# Issuer X509 -> nice name
issuers = {
  'http://pilet.ee/crt/30864900-0001.crt': 'Ühiskaart',
  'http://pilet.ee/crt/92337316-0001.crt': 'Ülikool',
  'http://pilet.ee/crt/92337331-0001.crt': 'SEB',
}

issuer_certs = {
  'http://pilet.ee/crt/30864900-0001.crt': 'live_30864900-0001.txt',
  'http://pilet.ee/crt/92337316-0001.crt': 'isic_ut_fixed_92337316-0001.txt',
  'http://pilet.ee/crt/92337331-0001.crt': 'seb_ut_fixed_92337331-0001.txt',
}

def verify_signature(signature_bin, signature_issuer):
  with tempfile.NamedTemporaryFile() as sigfile, tempfile.NamedTemporaryFile() as hashfile:
    sigfile.write(signature_bin)
    sigfile.flush()
    cmd =  "openssl rsautl -verify -certin -in %s -inkey %s -out %s 2>/dev/null" %(sigfile.name, issuer_certs[signature_issuer], hashfile.name)
    if os.system(cmd) == 0:
      sigvalue = hashfile.read()
      signature_hash = binascii.hexlify(sigvalue[-20:])
      print "Allkirja SHA1:      " + signature_hash
      return True
    else:
      print "Allkiri EI VERIFITSEERU!"
      return False
  return False

def xml2hexdump(filename):
  s = subprocess.check_output(["xsltproc", "xml2hexdump.xslt", filename])
  # replace - with 0x00
  return s.replace("-", "0")

def chunks(l, n):
  for i in xrange(0, len(l), n):
    yield l[i:i+n]

def dump2data(dumpchunks):
  datablocks = [1,2,4,5,6,8,9,10,12,13,14,16,17,18,20,21,22,24,25,26]
  return [dumpchunks[i] for i in datablocks]

def swapHexBytes(hstr):
  return ''.join(sum([(c,d,a,b) for a,b,c,d in zip(*[iter(hstr)]*4)], ()))

if __name__ == "__main__":
  print "Ühiskaardi analüsaator. info: martin@martinpaljak.net"
  print "Androidi NFC TagInfo rakenduse salvestatav XML või hexdump sisendiks!"
  print

  if len(sys.argv) < 2:
    print "validaator.py <fail>"
    sys.exit(1)

  tagfile = sys.argv[1]
  if tagfile.endswith(".xml"):
    dump = xml2hexdump(tagfile)
  elif tagfile.endswith(".mfd"):
    dump = open(sys.argv[1]).read()
    dump = binascii.hexlify(dump)
# WTF FUCK some libnfc come swapped, some not.    
#    dump = swapHexBytes(dump)  
  elif tagfile.endswith(".hex"):
    dump = open(sys.argv[1]).read()
    dump = dump.replace("\n", "").replace(" ", "").lower()
  
  if len(sys.argv)>2 and sys.argv[2] == "-d":
    for piece in list(chunks(dump, 32))[:64]:
      print piece
    print  

  m = Mifare.Mifare(dump)
  nt = NFCTagType1.NFCTagType1()
  nt.fromRawData(m.getData(), 0)
  ndef = NDEFMessage.NDEFMessage()
  ndef.fromRawData(nt.getNDEF(), 0)
  
  pilet = ndef.getRecord(0)
  allkiri = ndef.getRecord(1)
  
  # pileti metainfo
  pilet_pan = pilet.getPayload()[31:50]
  pilet_nr = pilet.getPayload()[39:50]
  mifare_uid = dump[:8]
  pilet_uid = binascii.hexlify(pilet.getPayload())[-8:]

  # allkiri
  sigdata_bin = pilet.getType() + pilet.getPayload()
  signature_bin = allkiri.getPayload()[4:132]
  signature_issuer = allkiri.getPayload()[135:]
  # compare UID-s

  print "Viipekaardi tüüp:   " + issuers[signature_issuer]
  print "Viipkeaardi sisu:   " + piletee.fetch_card_content(pilet_nr)
  print
  print "Pileti NR:          " + pilet_nr
  print "Pileti PAN: " + pilet_pan

  print "Mifare UID:         " + mifare_uid
  print "pilet.ee UID:       " + pilet_uid
  if mifare_uid == pilet_uid:
    print "UID klapib."
  else:
    print "UID EI KLAPI!"

  print "Allkirjastaja:      " + signature_issuer
  print "Andmete SHA1:       " + hashlib.sha1(sigdata_bin).hexdigest()
  #print "Allkiri (hex): " + binascii.hexlify(signature_bin)
  # Verify signature
  verify_signature(signature_bin, signature_issuer)
      
    
  
  
  


  
  
  
