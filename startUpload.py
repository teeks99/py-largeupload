
import json
import sys

# 1MB Chunk
#chunk_size = 1048576

# 1KB Chunk
chunk_size = 1024

def unpack_header(post_data):
	data = json.loads(post_data)

def basic_output():
	print "Content-Type: text/html"     # HTML is following
	print                               # blank line, end of headers
	print ""	

def start_upload():
	post_data = sys.stdin.read()
	file_info = unpack_header(post_data)

	basic_output()

if __name__ == '__main__':
	start_upload()


