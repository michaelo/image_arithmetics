import sys
import random
from PIL import Image, ImageFilter

def scatter(source, destpath1, destpath2):
    img = Image.open( source )
    px = img.load()

    dest1 = Image.new("RGB", img.size, (0, 0, 0))
    dest2 = Image.new("RGB", img.size, (0, 0, 0))
    dpx1 = dest1.load()
    dpx2 = dest2.load()

    for y in xrange(img.size[0]):
        for x in xrange(img.size[1]):
            if(random.randint(0,1) == 0):
                dpx1[x, y] = px[x, y]
            else:
                dpx2[x, y] = px[x, y]
            # px1[x, y] = txor(px1[x, y], px2[x, y])

    dest1.save(destpath1)
    dest2.save(destpath2)


if __name__ == "__main__":
    scatter(sys.argv[1], sys.argv[2], sys.argv[3])
