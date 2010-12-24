import json, sys, fcntl, cPickle, string, hashlib
import cgitb
cgitb.enable()

class InvalidData(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class OutOfOrder(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

def output_json_header():
	print "Content-Type: application/json"     # HTML is following
	print                               # blank line, end of headers

def chunk_upload():
	status = "OK"
	fail = ""
	response = {}
	try:
		post_data = sys.stdin.read()

		start = "START_JS"
		end = "END_JS"
		startPoint = len(start) 
		endPoint = string.find(post_data, end)
		chunk_data = json.loads(post_data[startPoint:endPoint])
		data = post_data[endPoint+len(end):]
		if not len(data) == chunk_data['chunkSize']:
			status = "INVALID_DATA"
			raise InvalidData("chunk size: " + str(chunk_data['chunkSize']) + " data size: " + str(len(data)))

		uploadId = chunk_data['uploadId']

		p = open("tmp_resource/"+uploadId+".pickle", 'r+')
		fcntl.lockf(p,fcntl.LOCK_EX)
	
		local_info = cPickle.load(p)
		if not local_info['chunks_rcvd'] == chunk_data['sequenceNum']:
			status = "OUT_OF_ORDER"
			raise OutOfOrder("Already received: " + str(local_info['chunks_rcvd']) + " sequence num: " + str(chunk_data['sequenceNum']))

		if not hashlib.sha256(data).hexdigest() == chunk_data['sha256']:
			status = "INVALID_DATA"
			raise InvalidData("chunk hash: " + chunk_data['sha256'] + " data hash: " + hashlib.sha256(data).hexdigest())
	
		f = open("tmp_file/"+uploadId+".hfile",'ab')
		f.write(data)
		f.close()

		local_info['bytes_rcvd'] = local_info['bytes_rcvd'] + len(data)
		local_info['chunks_rcvd'] = local_info['chunks_rcvd'] + 1
		local_info['chunk_hash'].append(chunk_data['sha256'])
	
		if (local_info['chunks_rcvd'] == local_info['chunks_expected']) and (local_info['bytes_rcvd'] == local_info['size']):
			local_info['complete'] = True
			status = "COMPLETE"

		p.seek(0)
		cPickle.dump(local_info,p)
		fcntl.lockf(p,fcntl.LOCK_UN)
		p.close()

		response['bytes_rcvd'] = local_info['bytes_rcvd']

	except InvalidData as invld:
		fail = invld.value
	except OutOfOrder as outofodr:
		fail = outofodr.value

	response['status'] = status
	if fail:
		response['failure'] = fail
	output_json_header()
	print json.dumps(response)

if __name__ == '__main__':
	chunk_upload()
