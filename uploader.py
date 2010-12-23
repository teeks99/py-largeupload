
import json, os, hashlib, urllib2, sys

verbose = True

class File:
	def __init__(self):
		self.status = "NOT_STARTED"
		self.chunkHash = []
		self.chunksUploaded = 0
		self.prefix = ""

	def upload(self, dir_url, local_file):
		self.status = "PROCESSING_FILE"

		self.url_base = dir_url
		self.filename = local_file
		
		self.size = os.path.getsize(self.filename)		
		self.file = open(self.filename, "rb")

		self.sha256 = hashlib.sha256(self.file.read()).hexdigest()		
		self.file.seek(0)

		data = self.createJsStart()

		self.status = "CONTACTING_SERVER"
		response = urllib2.urlopen(self.url_base + self.prefix + 'startUpload.py', data)
		self.status = "PROCESSING_RESPONSE"
		if not self.unpackJsResponse(response.read()):
			pass #TODO: Throw exception

		self.status = "UPLOADING"
		for c in range(self.totalChunks()):
			data = self.createCgiChunk(c)
			try_counter = 0
			while True:
				try_counter = try_counter + 1
				response = urllib2.urlopen(self.url_base + self.prefix + 'chunkUpload.py', data)
				if self.unpackChunkResponse(response.read()) or (try_counter > 10):
					break # this is a python do-while loop equliavan
			if verbose:
				print "Chunk " + str(c) " uploaded"

	def createJsStart(self):
		data = {}
		data['filename'] = self.filename #TODO Strip off path
		data['size'] = self.size
		data['sha256'] = self.sha256

		jdata = json.dumps(data)
		return jdata

	def unpackJsResponse(self, response):
		status = True
		data = json.loads(response)
		self.uploadId = data['uploadId']
		self.chunkSize = data['chunkSize']
		if not data['echoSha256Sum'] == self.sha256:
			status = False
		if not data['status']:
			status = False
		return status

	def createCgiChunk(self, c):
		chunk = self.file.read(self.chunkSize)
		chunkSize = self.chunkSize
		#TODO test chunk len, accpetable to be shorter for last one
		sha256 = hashlib.sha256(chunk).hexdigest()
		self.chunkHash.append(sha256)
		header = {'uploadId':self.uploadId, 'sequenceNum':c, 'sha256':sha256, 'chunkSize':chunkSize}
		jsHeader = json.dumps(header)
		return "START_JS" + jsHeader + "END_JS" + chunk

	def unpackChunkResponse(self, response):
		status = True
		data = json.loads(response)
		if not ( (data['status'] == "OK") or (data['status'] == "COMPLETE") ):
			status = False

	def totalChunks(self):
		chunks = self.size / self.chunkSize
		if self.size % self.chunkSize:
			chunks = chunks + 1
		return chunks

if __name__ == '__main__':
	f = File()
	f.prefix = "dh-"
	f.upload('http://teeks99.com/py-largeupload/','README')
