
import json, os, hashlib, urllib2, sys

class File:
	def __init__(self):
		self.status = "NOT_STARTED"
		self.chunkHash = []
		self.chunksUploaded = 0
		self.bytesSent = 0
		self.bytesReceivedRemote = 0
		self.prefix = ""
		self.verbose = False

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
			if self.verbose:
				print "Chunk " + str(c+1) + "/" + str(self.totalChunks()) +" uploaded"

		# This is how other programs can access the file
		return self.uploadId

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
		# If we're on the last chunk allow it to have a smaller chunk size
		if len(chunk) < chunkSize:
			if c == self.totalChunks()-1:
				chunkSize = len(chunk)
		self.bytesSent = self.bytesSent + chunkSize
		sha256 = hashlib.sha256(chunk).hexdigest()
		self.chunkHash.append(sha256)
		header = {'uploadId':self.uploadId, 'sequenceNum':c, 'sha256':sha256, 'chunkSize':chunkSize}
		jsHeader = json.dumps(header)
		return "START_JS" + jsHeader + "END_JS" + chunk

	def unpackChunkResponse(self, response):
		print response
		sys.stdout.flush()

		status = True
		data = json.loads(response)
		self.bytesReceivedRemote = data['bytes_rcvd']
		if not ( (data['status'] == "OK") or (data['status'] == "COMPLETE") ):
			status = False
		return status

	def totalChunks(self):
		chunks = self.size / self.chunkSize
		if self.size % self.chunkSize:
			chunks = chunks + 1
		return chunks

if __name__ == '__main__':
	f = File()
	f.prefix = "dh-"
	f.verbose = True
	f.upload('http://teeks99.com/py-largeupload/','RedEyeExample.jpg')
