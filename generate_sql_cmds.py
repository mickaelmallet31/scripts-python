#!/usr/bin/env python

print "Name of the image file root:"
#input image_file_root
image_file_root = 'barcelona_'

print "Number of photos for this new list:"
#input nb_photos
nb_photos = 29

print "Last ID used for the photos:"
#input last_ID_used
last_ID_used = 681

print "ID of the gallery to be used:"
#input id_gallery
id_gallery = 26

print "\nTo be added at the end of fichierimage table:"
for id in range(last_ID_used+1, last_ID_used+1+nb_photos):
	print "({}, {}),".format(id, id_gallery)

print "\nTo be added at the end of image table:"
for id in range(1, nb_photos+1):
	print "({}, '{}{:02}', ''),".format(last_ID_used+id, image_file_root, id)
