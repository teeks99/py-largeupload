import json, sys, fcntl, cPickle, string, hashlib
import cgitb
cgitb.enable()

def output_json_header():
	print "Content-Type: application/json"     # HTML is following
	print                               # blank line, end of headers

def chunk_upload():
	status = "OK"
	post_data = sys.stdin.read()

	start = "START_JS"
	end = "END_JS"
	startPoint = len(start) 
	endPoint = string.find(post_data, end)
	chunk_data = json.loads(post_data[startPoint:endPoint])
	data = post_data[endPoint+len(end):]
	if not len(data) == chunk_data['chunkSize']:
		status = "INVALID_DATA"
		pass #TODO throw invalid data exception

	uploadId = chunk_data['uploadId']

	p = open("tmp_resource/"+uploadId+".pickle", 'r+')
	fcntl.lockf(p,fcntl.LOCK_EX)

	local_info = cPickle.load(p)
	if not local_info['chunks_rcvd'] == chunk_data['sequenceNum']:
		status = "OUT_OF_ORDER"
		pass #TODO throw out of order exception

	if not hashlib.sha256(data).hexdigest() == chunk_data['sha256']:
		status = "INVALID_DATA"
		pass #TODO throw invalid data exception

	f = open("tmp_file/"+uploadId+".hfile",'ab')
	f.write(data)
	f.close()

	local_info['bytes_rcvd'] = local_info['bytes_rcvd'] + len(data)
	local_info['chunks_rcvd'] = local_info['chunks_rcvd'] + 1
	local_info['chunk_hash'] = chunk_data['sha256']
	
	if (local_info['chunks_rcvd'] == local_info['chunks_expected']) and (local_info['bytes_rcvd'] == local_info['size']):
		local_info['complete'] = True
		status = "COMPLETE"

	cPickle.dump(local_info,p)
	fcntl.lockf(p,fcntl.LOCK_UN)
	p.close()

	response = {}
	response['status'] = status
	response['bytes_rcvd'] = local_info['bytes_rcvd']
	output_json_header()
	print json.dumps(response)

if __name__ == '__main__':
	chunk_upload()
