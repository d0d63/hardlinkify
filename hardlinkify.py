#!/usr/bin/python
# $dodge: hardlinkify.py,v 1.1 2010/06/13 18:25:43 dodge Exp $
# vim: shiftwidth=8 nocindent noai smartindent 

# Find all the files in sys.argv, find the duplicates, and hard link them to
# conserve space

import sys
import hashlib
import os
import stat

hashes = {}

def get_hash (filename):
	try:
		descriptor = open(filename)
	except:
		print("get_hash -- Can't open " + filename)
		return

	hash_object = hashlib.md5()
	file_size = os.stat(filename).st_size
	bytes_read = 0
	while (bytes_read < file_size):
		buf = descriptor.read()
		hash_object.update(buf)
		bytes_read = bytes_read + len(buf)

	print("get_hash -- returning " + hash_object.hexdigest())
	return hash_object.hexdigest()

class file_info():
	name = None
	hash = None
	inode = None

	def __init__ (self, filename):
		self.name = filename
		self.inode = os.stat(filename).st_ino
		try:
			print("file_info __init__ -- " + str(os.stat(filename).st_size) + " bytes -- attempting to get hash")
			self.hash = get_hash(filename)
		except:
			self.name = None
			self.hash = None
			self.inode = None

def recurse (path):
	print("recurse -- path:" + path)
	for new_path in os.listdir(path):
		print("recurse -- Will check_path " + path + "/" + new_path)
		check_path(path + "/" + new_path)

def check_file (filename):
	print("check_file -- number " + str(1 + len(hashes)) + " -- filename:" + filename + " -- " + str(os.stat(filename).st_size) + " bytes")

	this = file_info(filename)
	if (this.hash == None):
		print("check_file -- no hash")
		return

	print("check_file -- name:" + this.name + " -- hash:" + this.hash + " -- inode:" + str(this.inode))

	try:
		old = hashes[this.hash]
	except:
		print("check_file -- this is new")
		hashes[this.hash] = this;
		return

	if (old.inode == this.inode):
		print("check_file -- already linked")
		return

	print("check_file -- " + this.name + " and " + old.name + " have the same contents, hard link them")
	os.unlink(this.name)
	os.link(old.name, this.name)

def check_path ( path ) :
	print("checking path " + path);

	try:
		mode = os.stat(path).st_mode
	except:
		print("Can't find " + path)
		return

	if (stat.S_ISDIR(os.stat(path).st_mode)):
		recurse(path)
	elif(stat.S_ISREG(os.stat(path).st_mode)):
		check_file(path)

for path in sys.argv[1:]:
	check_path(path)

