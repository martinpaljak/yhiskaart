#!/usr/bin/python

#
# Copyright: Collin Mulliner <collin@mulliner.org>
# Web: http://www.mulliner.org/nfc/
#
# License: GPLv2
#

import Utils

class NDEFMessage:
	def __init__(self):
		self.__records = []
		self.__raw_data = []
		
	def getNumRecords(self):
		return len(self.__records)

	def append(self, rec):
		self.__records.append(rec)
		self.updateRecords()
	
	def getRecord(self, index):
		if index < len(self.__records):
			return self.__records[index]
		return None
	
	# update Message Begin/End in each record
	def updateRecords(self):
		if len(self.__records) == 1:
			self.__records[0].setMB(1)
			self.__records[0].setME(1)
		elif len(self.__records) > 1:
			self.__records[0].setMB(1)
			self.__records[0].setME(0)
			for i in range(1, len(self.__records) - 1):
				self.__records[i].setMB(0)
				self.__records[i].setME(0)
			self.__records[len(self.__records) - 1].setMB(0)
			self.__records[len(self.__records) - 1].setME(1)

	def getRawBytes(self):
		res_data = []
		for i in range(0, len(self.__records)):
			data = self.__records[i].getRawBytes()
			for j in range(0, len(data)):
				res_data.append(data[j])
		return res_data
		
	def getHex(self):
		b = self.getRawBytes()
		return Utils.bin2hex(b)
		
	def __parseRaw(self):
		p = 1
		pos = 0
		while (p):
			rec = NDEFRecord()
			rec.fromRawData(self.__raw_data[pos:], 0)
			self.__records.append(rec)
			pos = pos + len(rec.getRawBytes())
			if pos >= len(self.__raw_data):
				p = 0
		
	def fromRawData(self, raw_data, raw_is_hex):
		if raw_is_hex == 1:
			self.__raw_data = Utils.hex2bin(raw_data)
		else:
			self.__raw_data = raw_data
		self.__parseRaw()
		self.__raw_data = []

class NDEFRecord:
	def __init__(self):
		self.__recInit()
		
	def fromRawData(self, raw_data, raw_is_hex):
		self.__recInit()
		if raw_is_hex == 1:
			self.__raw_data = Utils.hex2bin(raw_data)
		else:
			self.__raw_data = raw_data
		self.__parseRaw()
		#print "b " + str(self.__rec_payload)
		self.__raw_data = []
		
	def fromTypeAndPayload(self, tnf, rtype, payload):
		self.__rec_tnf = tnf
		self.__rec_type_len = len(rtype)
		self.__rec_type = rtype
		self.__rec_payload_len = len(payload)
		self.__rec_payload = payload
		if len(payload) <= 255:
			self.__rec_sr = 1
		else:
			self.__rec_sr = 0
	
	def getCopy(self):
		return NDEFRecord(self.__rec_tnf, self.__rec_type, self.__rec_payload)

	def getTnf(self):
		return self.__rec_tnf
		
	def setTnf(self, tnf):
		self.__rec_tnf = int(tnf)

	def getMB(self):
		return self.__rec_mb

	def setMB(self, mb):
		self.__rec_mb = int(mb)
		
	def getME(self):
		return self.__rec_me

	def setME(self, me):
		self.__rec_me = int(me)
		
	def getSR(self):
		return self.__rec_sr
		
	def setSR(self, sr):
		self.__rec_sr = int(sr)
		
	def getCF(self):
		return self.__rec_cf
		
	def setCF(self, cf):
		self.__rec_cf = int(cf)
	
	def setID(self, rec_id):
		if len(rec_id) > 0:
			self.__rec_id = rec_id
			self.__rec_id_len = len(rec_id)
			self.__rec_il = 1
		else:
			self.__rec_il = 0
			self.__rec_id = None
			self.__rec_id_len = 0
	
	def getID(self):
		return self.__rec_id
	
	def setIDLen(self, idlen):
		self.__rec_id_len = idlen
		
	def getIDLen(self):
		return self.__rec_id_len
	
	def setPayload(self, payload):
		self.__rec_payload = payload
		self.__rec_payload_len = len(payload)
		if len(payload) <= 255:
			self.__rec_sr = 1
		else:
			self.__rec_sr = 0
			
	def setPayloadRaw(self, payload):
		self.__rec_payload = payload
	
	def getPayload(self):
		p = ""
		for i in range(0, len(self.__rec_payload)):
			p = p + chr(self.__rec_payload[i])
		return p
	
	def getPayloadRaw(self):
		return self.__rec_payload
	
	def getPayloadLen(self):
		return self.__rec_payload_len
	
	def setPayloadLen(self, payload_len):
		self.__rec_payload_len = int(payload_len)
		
	def getTypeRaw(self):
		return self.__rec_type
		
	def getType(self):
		t = ""
		for i in range(0, len(self.__rec_type)):
			t = t + self.__rec_type[i]
		return t
		
	def setType(self, rtype):
		self.__rec_type = rtype
		self.__rec_type_len = len(rtype)
	
	def setTypeRaw(self, rtype):
		self.__rec_type = rtype
		
	def setTypeLenRaw(self, rtype_len):
		self.__rec_type_len = int(rtype_len)
	
	def getRawBytes(self):
		self.__raw_data = []
		pos = 0
		raw_data_len = 3 + self.__rec_payload_len + self.__rec_type_len + self.__rec_id_len
		if self.__rec_sr == 0:
			raw_data_len = raw_data_len + 3
		if self.__rec_il == 1:
			raw_data_len = raw_data_len + 1
		#print str(raw_data_len)
		#self.__raw_data = [raw_data_len]
		self.__raw_data.append(self.__rec_mb << 7)
		self.__raw_data[0] = self.__raw_data[0] | self.__rec_me << 6
		self.__raw_data[0] = self.__raw_data[0] | self.__rec_cf << 5
		self.__raw_data[0] = self.__raw_data[0] | self.__rec_sr << 4
		self.__raw_data[0] = self.__raw_data[0] | self.__rec_il << 3
		self.__raw_data[0] = self.__raw_data[0] | (self.__rec_tnf & 7)
		self.__raw_data.append(self.__rec_type_len)
		pos = 2
		if self.__rec_sr == 1:
			self.__raw_data.append(self.__rec_payload_len & 0xFF)
		else:
			self.__raw_data.append((self.__rec_payload_len >> 24) & 0xFF)
			pos = pos + 1
			self.__raw_data.append((self.__rec_payload_len >> 16) & 0xFF)
			pos = pos + 1
			self.__raw_data.append((self.__rec_payload_len >> 8) & 0xFF)
			pos = pos + 1
			self.__raw_data.append(self.__rec_payload_len & 0xFF)
			pos = pos + 1
		if self.__rec_il == 1:
			self.__raw_data.append(self.__rec_id_len & 0xFF) 
		for i in range(0, len(self.__rec_type)):
			self.__raw_data.append(ord(self.__rec_type[i]))
			pos = pos + 1
		if self.__rec_il == 1:
			for i in range(0, len(self.__rec_id)):
				self.__raw_data.append(ord(self.__rec_id[i]))
				pos = pos + 1
		if self.__rec_payload != None:
			for i in range(0, len(self.__rec_payload)):
				# ugly hack
				if type(self.__rec_payload[i]) == int:
					self.__raw_data.append(self.__rec_payload[i])
				else:
					self.__raw_data.append(ord(self.__rec_payload[i]))
				pos = pos + 1
		return self.__raw_data
		
	def __parseRaw(self):
		#print str(len(self.__raw_data))
		#print type(self.__raw_data[0])
		self.__rec_mb = (self.__raw_data[0] >> 7) & 1
		self.__rec_me = (self.__raw_data[0] >> 6) & 1
		self.__rec_cf = (self.__raw_data[0] >> 5) & 1
		self.__rec_sr = (self.__raw_data[0] >> 4) & 1
		self.__rec_il = (self.__raw_data[0] >> 3) & 1
		self.__rec_tnf = self.__raw_data[0] & 7
		self.__rec_type_len = self.__raw_data[1]
		if self.__rec_sr == 1:
			self.__rec_payload_len = self.__raw_data[2]
			pos = 3
		else:
			self.__rec_payload_len = self.__raw_data[2] << 24 | self.__raw_data[3] << 16 | self.__raw_data[4] << 8 | self.__raw_data[5];
			pos = 6
		if self.__rec_il == 1:
			self.__rec_id_len = self.__raw_data[pos]
			pos = pos + 1
		self.__rec_type = []
		for i in range(0, self.__rec_type_len):
			self.__rec_type.append(chr(self.__raw_data[pos]))
			pos = pos + 1
		if self.__rec_il == 1:
			self.__rec_id = []
			for i in range(0, self.__rec_id_len):
				self.__rec_id.append(self.__raw_data[pos])
				pos = pos + 1
		self.__rec_payload = []
		#print "* " + str(self.__raw_data)
		if pos < len(self.__raw_data):
			for i in range(0, self.__rec_payload_len):
				self.__rec_payload.append(int(self.__raw_data[pos]))
				pos = pos + 1
		
	def getHex(self):
		d = self.getRawBytes()
		return Utils.bin2hex(d)
		
	def __recInit(self):
		self.__raw_data = []
		self.__rec_mb = 1
		self.__rec_me = 1
		self.__rec_cf = 0
		self.__rec_sr = 0
		self.__rec_il = 0
		self.__rec_tnf = 0
		self.__rec_payload = None
		self.__rec_payload_len = 0
		self.__rec_type = None
		self.__rec_type_len = 0
		self.__rec_id = None
		self.__rec_id_len = 0
		

# for testing
if __name__ == "__main__":
	bla = NDEFRecord()
	bla.fromTypeAndPayload(0x01, 'U', "\0http://www.mulliner.org/nfc")
	print bla.getHex()
	bla2 = NDEFRecord()
	bla2.fromRawData(bla.getHex(), 1)
	print bla2.getHex()
	if bla2.getHex() == bla.getHex():
		print "test passed"
	else:
		print "test failed"
