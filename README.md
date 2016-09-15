Idea
=========
Two images contains each half of some code
XORing those images together shall manifest this code (graphically, probably)

To achieve this a thought process may be:
1) Construct a bitmap symbol that you want to hide. Preferable grayscale?
2) Split this symbol into two partial images, each with approx 50% of the pixels
- this split can either be random, checkerboard or e.g. split vertically or horizontally.
Assumption: a pure split are more likely to produce recognizable artifacts, increasing the suspicion of the observers.
This may, or may not, be a flaw.

3) Then XOR each of those two images into each of the base images


Thoughts
--------
Instead of XORing the white pixels of the code image, it may be necessary to XOR
the corresponding images of the other picture.

Image formats: bitmap (no transparency?)
XORing with black should not change anything. Code image should thus be white on black

Definitions:
------------
IMGcode - the image containing the code
IMG1 - the one part of the code
IMG2 - the other part of the code
BASE1 - one of the base images
BASE2 - the other of the base images

DEST1 = BASE1 XOR IMG1
DEST2 = BASE2 XOR IMG2

RESULT = DEST1 XOR DEST2
- which is suspected to produce a visual representation on top of random artifacts generated by each



Scripts to make:
----------------
1) xor.py inputimg1 inputimg2 outputimg
2) scatter.py imgcode <type> outputimg1 outputimg2
3)


TODO
========
Superimpose XORed pixels from the other image



Try:
Create the XORed image of BASE1 and BASE2, then use the white pixels of IMGcode to extract the relevant pixels from this.
Then XOR this code onto BASE1 and BASE2 (perhaps splitted by scatter.py)