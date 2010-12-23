
import json, sys, fcntl, cPickle, random, hashlib
import cgitb
cgitb.enable()

# 1MB Chunk
#chunk_size = 1048576

# 1KB Chunk
chunk_size = 1024

def output_json_header():
	print "Content-Type: application/json"     # HTML is following
	print                               # blank line, end of headers

def start_upload():
	post_data = sys.stdin.read()

	file_info = json.loads(post_data)

	uploadId = hashlib.sha256(file_info['sha256'] + hex(random.getrandbits(256))[2:]).hexdigest()
	#TODO: Check to make sure these files don't exist (that's a lot of randomness though)

	local_info = {}
	local_info['uploadId'] = uploadId
	local_info['given_name'] = file_info['filename']
	local_info['size'] = file_info['size']
	local_info['sha256'] = file_info['sha256']
	local_info['chunks_rcvd'] = 0
	local_info['bytes_rcvd'] = 0
	local_info['chunks_expected'] = 0
	local_info['chunk_hash'] = []
	local_info['complete'] = False

	p = open("tmp_resource/"+uploadId+".pickle",'w')
	fcntl.lockf(p,fcntl.LOCK_EX)

	cPickle.dump(local_info,p)
	f = open("tmp_file/"+uploadId+".hfile",'wb')
	f.close()

	fcntl.lockf(p,fcntl.LOCK_UN)
	p.close()

	output = {}
	output['uploadId'] = uploadId
	output['echoSha256Sum'] = file_info['sha256']
	output['chunkSize'] = chunk_size
	output['status'] = True

	output_json_header()
	print json.dumps(output)

if __name__ == '__main__':
	start_upload()


