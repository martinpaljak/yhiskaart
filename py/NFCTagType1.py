#!/usr/bin/python

#
# Copyright: Collin Mulliner <collin@mulliner.org>
# Web: http://www.mulliner.org/nfc/
#
# License: GPLv2
#

import Utils

def padd_data(data, padding_size = 16):
	out = data
	if padding_size > 0 and len(out) % padding_size > 0:
		pad = padding_size - (len(out) % padding_size)
		for i in range(0, pad):
			out = out + chr(0x00)
	return out

# not working yet!
class LockTLV:
	def __init__(self) : 
		# bpp = 16, bpl = 16, sib = 16):
		#self.__bytes_per_page = bpp
		#self.__bytes_locked_per_bit = bpl
		#self.__size_in_bits = 0
		pass
		
	def parse(self, data):
		if len(data) == 3:
			# Page Control
			n = data[2] & 0x0f
			self.__bytes_per_page = 2
			for i in range(1, n):
				self.__bytes_per_page = self.__bytes_per_page * 2
			self.__bytes_locked_per_bit = 2
			n = data[2] >> 4
			for i in range(1, n):
				self.__bytes_locked_per_bit = self.__bytes_locked_per_bit * 2
			# Size
			self.__size_in_bits = data[1]
			# Position
			self.__page_addr = data[0] >> 4
			self.__offset = data[0] & 0x0f
			#
			self.__byte_addr = self.__page_addr * self.__bytes_per_page + self.__offset
			#
			print "Bytes per Page: " + str(self.__bytes_per_page)
			print "Bytes Locked per Bit: " + str(self.__bytes_locked_per_bit)
			print "Size in Bits: " + str(self.__size_in_bits)
			print "Page Addr: " + str(self.__page_addr)
			print "Page Offset: " + str(self.__offset)
			print "Byte addr: " + str(self.__byte_addr)
			
		else:
			print "Lock TLV data invalid"

def NFCTagSectorize(data, sec_size = 16, is_hex = 1):
	i = 0
	if is_hex == 1:
		sec_size = sec_size * 2
	while i < len(data):
		print data[i:i+sec_size]
		i = i + sec_size

class NFCTagType1:
	def __init__(self):
		self.__ndef_tlv = 0x03
		self.__terminator_tlv = 0xFE
		self.__ndef_data = []
		self.__length = 0
		self.__raw_data = []
		self.__raw_length = 0
		
	def setNDEF(self, raw_data, raw_is_hex = 1):
		if raw_is_hex == 1:
			self.__ndef_data = Utils.hex2bin(raw_data)
		else:
			self.__ndef_data = raw_data
		self.__length = len(self.__ndef_data)
			
	def fromRawData(self, raw_data, raw_is_hex = 1):
		if raw_is_hex == 1:
			self.__raw_data = Utils.hex2bin(raw_data)
		else:
			self.__raw_data = raw_data
		self.__raw_length = len(self.__raw_data)
		if self.__raw_data[0] == self.__ndef_tlv:
			if self.__raw_data[1] == 0xFF:
				self.__ndef_length = self.__raw_data[2] << 8 | self.__raw_data[3]
				pos = 4
			else:
				self.__ndef_length = self.__raw_data[1]
				pos = 2
			for i in range(0, self.__ndef_length):
				self.__ndef_data.append(self.__raw_data[pos+i])
			#if self.__raw_data[pos + self.__ndef_length] == self.__terminator_tlv:
			#	print "terminator found"
			#else:
			#	print "terminator not found!"
		
	def getNDEF(self):
		return self.__ndef_data
		
	def setLength(self, length):
		self.__length = length
		
	def getLength(self):
		return self.__length
		
	def getTag(self, in_hex = 1, padding_size = 16):
		out = []
		out.append(self.__ndef_tlv)
		length = self.__length
		if length <= 0xFE:
			out.append(length & 0xFF)
		else:
			out.append(0xFF)
			out.append((length >> 8) & 0xFF)
			out.append(length & 0xFF)
		for i in range(0, len(self.__ndef_data)):
			out.append(self.__ndef_data[i])
		out.append(self.__terminator_tlv)
		if padding_size > 0 and len(out) % padding_size > 0:
			pad = padding_size - (len(out) % padding_size)
			for i in range(0, pad):
				out.append(0x00)
		if in_hex != 0:
			return Utils.bin2hex(out, 1)
		else:
			ho = ""
			for i in range(0, len(out)):
				ho = ho + chr(out[i])
			return ho
	
if __name__ == "__main__":
	import NDEFUri
	import os
	u = NDEFUri.NDEFUri()
	#u.setUri("http://www.mulliner.org/collin/")
	u.setUri("http://AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
	t = NFCTagType1()
	t.setNDEF(u.getNDEFRecord().getHex())
	td = t.getTag(0)
	#d = ""
	#for i in range(0, len(td)):
	#	d = d + chr(td[i])
	fp = open(os.sys.argv[1], 'wb')
	fp.write(td)
	fp.close()
	#print t.getTag(1)
	#NFCTagSectorize(t.getTag())
	#l = LockTLV()
	#d = []
	##d.append(0xf0)
	#d.append(0x10)
	#d.append(0x33)
	#l.parse(d)
