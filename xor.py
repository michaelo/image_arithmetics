#!/usr/bin/python
import sys
from PIL import Image, ImageFilter

def txor(v1, v2):
    return (v1[0] ^ v2[0], v1[1] ^ v2[1], v1[2] ^ v2[2])

def xor(path1, path2, destpath):
    img1 = Image.open( path1 )
    img2 = Image.open( path2 )

    px1 = img1.load()
    px2 = img2.load()

    for y in xrange(img1.size[0]):
        for x in xrange(img1.size[1]):
            px1[x, y] = txor(px1[x, y], px2[x, y])

    if destpath:
        img1.save(destpath)
    else:
        img1.show()


if __name__ == "__main__":
    if len(sys.argv) > 3:
        xor(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        xor(sys.argv[1], sys.argv[2], None)
