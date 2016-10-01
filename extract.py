#!/usr/bin/python
import sys
from PIL import Image, ImageFilter

def is_black(argb):
    return argb[0] == 0 and argb[1] == 0 and argb[2] == 0

def extract(sourcepath, patternpath, destpath):
    img = Image.open( sourcepath )
    imgpx = img.load()
    patternimg = Image.open( patternpath )
    patternpx = patternimg.load()

    dest1 = Image.new("RGB", img.size, (0, 0, 0))
    dpx1 = dest1.load()

    for y in xrange(img.size[0]):
        for x in xrange(img.size[1]):
            if not is_black(patternpx[x, y]):
                dpx1[x, y] = imgpx[x,y]

    dest1.save(destpath)



if __name__ == "__main__":
    extract(sys.argv[1], sys.argv[2], sys.argv[3])
