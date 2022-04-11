# TODO:
# Support both RGB and ARGB
# Make <bits>-configuration matter.

import sys
from PIL import Image

def keyvals_to_dict(keyvals):
    """
    Takes a tuple of arbitrary length, expecting each item to be "<key>=<value>"
    Create and return a corresponding dict.

    TODO: Consider to do this directly in the block-parser
    """
    result = {}

    for keyval in keyvals:
        tmp = keyval.split("=")
        result[tmp[0]] = tmp[1]

    return result

def steg(piped, passed):
    # encode / embed
    assert(len(piped) == 2)
    passed_keyvals = keyvals_to_dict(passed)
    bits = 4
    if "bits" in passed_keyvals:
        bits = int(passed_keyvals["bits"])

    dpx = [
            piped[0].load(),
            piped[1].load()
        ]


    # take <bits> most significant bits of px2, insert at <bits> least
    # significant bits of px1
    # assume 8bit pr pixel
    def embed(px1, px2, bits):
        low_mask = 0xff>>(8-bits)
        high_mask = 0xff^low_mask

        px2_0 = (px2[0] >> (8-bits)) & low_mask
        px2_1 = (px2[1] >> (8-bits)) & low_mask
        px2_2 = (px2[2] >> (8-bits)) & low_mask

        return ((px1[0] & high_mask) | px2_0,
                (px1[1] & high_mask) | px2_1,
                (px1[2] & high_mask) | px2_2
            )

    for x in range(piped[0].size[0]):
        for y in range(piped[0].size[1]):
            dpx[0][x,y] = embed(dpx[0][x,y], dpx[1][x,y], bits)

    return (piped[0],)

def isteg(piped, passed):
    # inverse / extract
    assert(len(piped) == 1)
    passed_keyvals = keyvals_to_dict(passed)
    bits = 4
    if "bits" in passed_keyvals:
        bits = int(passed_keyvals["bits"])

    dest = Image.new("RGB", piped[0].size, (0, 0, 0))
    dpx = [
            piped[0].load(),
            dest.load()
        ]

    def extract(px, bits):
        
        low_mask = 0xff>>(8-bits)
        rest_mask = 0xff<<(bits)
        high_mask = 0xff^low_mask
        return ((px[0] & low_mask) << (8-bits),
                (px[1] & low_mask) << (8-bits),
                (px[2] & low_mask) << (8-bits)
            )
        # return ((px[0] & rest_mask),
        #         (px[1] & rest_mask),
        #         (px[2] & rest_mask)
        #     )

    for x in range(piped[0].size[0]):
        for y in range(piped[0].size[1]):
            dpx[1][x,y] = extract(dpx[0][x,y], bits)

    return (dest,)
