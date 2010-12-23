
import json, sys, fcntl, cPickle

# 1MB Chunk
#chunk_size = 1048576

# 1KB Chunk
chunk_size = 1024

def unpack_header(post_data):
	data = json.loads(post_data)

def output_json_header():
	print "Content-Type: application/json"     # HTML is following
	print                               # blank line, end of headers

def start_upload():
	post_data = sys.stdin.read()
	file_info = unpack_header(post_data)

	local_info = {}
	local_info['uploadId'] = file_info['sha256']
	local_info['given_name'] = file_info['filename']
	local_info['size'] = file_info['size']
	local_info['sha256'] = file_info['sha256']
	local_info['chunks_rcvd'] = 0
	local_info['chunk_hash'] = []

	f = open("tmp_resource/"+file_info['sha256']+".pickle",'w')
	fcntl.lockf(f,fcntl.LOCK_EX)
	cPickle.dump(local_info,f)
	fcntl.lockf(f,fcntl.LOCK_UN)
	f.close()

	output = {}
	output['uploadId'] = file_info['sha256']
	output['echoSha256Sum'] = file_info['sha256']
	output['chunkSize'] = chunk_size
	output['status'] = True

	output_json_header()
	print json.dumps(output)

if __name__ == '__main__':
	start_upload()


