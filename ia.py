#!python
import sys
import re
from PIL import Image
from modules import steg

func_map = {}

test_pipelines = [
    ("open(file1, file2) | xor | save(file3) ",
        [("open", ("file1", "file2")), ("xor", ()), ("save", ("file3",))]
    ),
    ("open(infile1, infile2) | xor | scatter | save(outfile1, outfile2) ",
        [("open", ("infile1", "infile2")), ("xor", ()), ("scatter", ()), ("save", ("outfile1", "outfile2"))]
    ),
    ("open(infile1, infile2) | xor | scatter(parts=3,bg=0 0 0 255) | save(outfile1, outfile2) ",
        [("open", ("infile1", "infile2")), ("xor", ()), ("scatter", ("parts=3","bg=0 0 0 255",)), ("save", ("outfile1", "outfile2"))]
    )
]

def register_module(name, function):
    global func_map
    func_map[name] = function

def is_valid_module(name):
    return name in func_map

def get_module(name):
    return func_map[name]

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

def init_default_modules():
    register_module("open", x_open)
    register_module("open_right", x_open)
    register_module("open_left", x_open_left)
    register_module("xor", x_xor)
    register_module("xor_color", x_xor_color)
    register_module("save", x_save)
    register_module("scatter", x_scatter)
    register_module("display", x_display)
    register_module("extract", x_extract)
    register_module("scale", x_scale)
    register_module("fill", x_fill)
    register_module("noisify", x_noisify)
    register_module("duplicate", x_duplicate)
    register_module("steg", steg.steg)
    register_module("isteg", steg.isteg)

# Rules:
# First argument of all functions should be a tuple containing return-values of the previous functions in the pipeline
# Second argument of all functinons should be a tuple containing the string arguments as defined by pipeline
#    TODO: Implement support for named parameters?
# All modules shall return a tuple of PIL Images


def x_open(piped, passed):
    """
    Opens files from passed paths, and returns PIL Images
    Any images eventually piped to this will be passed through (at beginning
    of returned set), making it possible to open new files mid-pipeline.
    """

    result = []
    result.extend(piped)
    if not passed:
        raise "InvalidArguments"

    for i in passed:
        result.append(Image.open(i))

    return tuple(result)

def x_open_left(piped, passed):
    """
    Opens files from passed paths, and returns PIL Images
    Any images eventually piped to this will be passed through (at end
    of returned set), making it possible to open new files mid-pipeline.
    """

    result = []
    result.extend(piped)
    if not passed:
        raise "InvalidArguments"

    for i in passed:
        result.insert(0, Image.open(i))

    return tuple(result)


def x_xor(piped, __):
    """
    Takes two (or more) input images, returns an image that's the pixelwise
    XOR of them.

    TODO: Determine what to in case of alpha channel
    """
    assert( len(piped) >= 2 )
    def _txor(v1, v2):
        return (v1[0] ^ v2[0], v1[1] ^ v2[1], v1[2] ^ v2[2])

    pxs = []
    for img in piped:
        pxs.append(img.load())

    for (i,__) in enumerate(pxs[1:]):
        for y in xrange(piped[0].size[0]):
            for x in xrange(piped[0].size[1]):
                pxs[0][x, y] = _txor(pxs[0][x, y], pxs[i+1][x, y])

    return (piped[0],)

def x_xor_color(piped, passed):
    """
    XORs a flat color on the passed image(s).
    Default: color=255 255 255, index=0 (space-separated list)

    TODO: Determine what to in case of alpha channel
    """
    assert( len(piped) >= 1 )

    passed_keyvals = keyvals_to_dict(passed)
    color = (255, 255, 255)
    if "color" in passed_keyvals:
        color = tuple(map(int, passed_keyvals["color"].split(" ")))

    indexes = [0]
    if "index" in passed_keyvals:
        indexes = map(int, passed_keyvals["index"].split(" "))

    def _txor(v1, v2):
        return (v1[0] ^ v2[0], v1[1] ^ v2[1], v1[2] ^ v2[2])

    pxs = []
    for img in piped:
        pxs.append(img.load())

    for index in indexes:
        for y in xrange(piped[index].size[0]):
            for x in xrange(piped[index].size[1]):
                pxs[index][x, y] = _txor(pxs[index][x, y], color)

    return piped

def x_scale(piped, passed):
    """
    """
    assert(len(passed) == 2)
    width = passed[0]
    height = passed[1]

    result = []

    for (i, img) in enumerate(piped):
        result.append(img.resize((int(width), int(height)), Image.NEAREST))

    return tuple(result)


def x_extract(piped, passed):
    """
    Input: a source image to extract from, an image with pattern to extract
    Output: an image with the pixels specified by the pattern extracted from the source image

    Example pipeline:

    TODO: Make support for transparancy
    """

    def _is_black(argb):
        return argb[0] == 0 and argb[1] == 0 and argb[2] == 0
    img = piped[0]
    imgpx = img.load()
    patternimg = piped[1]
    patternpx = patternimg.load()

    dest1 = Image.new("RGB", img.size, (0, 0, 0))
    dpx1 = dest1.load()

    for y in xrange(img.size[0]):
        for x in xrange(img.size[1]):
            if not _is_black(patternpx[x, y]):
                dpx1[x, y] = imgpx[x,y]

    return (dest1,)


def x_save(piped, passed):
    """
    Saves each piped picture by mapping them to file paths specified by passed
    pipeline arguments. Number of passed paths may be less than the number of
    piped images; in such case only the n first images will be saved.

    Example pipeline:
        "open(file1.png, file2.png) | save(file1_copy.png, file2_copy.png)"
    """
    assert(len(piped) >= len(passed))
    for (i, __) in enumerate(passed):
        piped[i].save(passed[i])

    return piped

def x_scatter(piped, passed):
    """
    Input: source image
    Output: two images which together contains all the pixels of the source.
        Each pixel has a even probability to end in either destination image

    TODO: Allow input: types of scattering

    Example pipeline:
    """
    assert(len(piped) == 1)
    import random

    # Determine parameters
    num_outs = 2
    background = (0, 0, 0, 255)

    passed_keyvals = keyvals_to_dict(passed)
    if "num" in passed_keyvals:
        num_outs = int(passed_keyvals["num"])

    if "bg" in passed_keyvals:
        # RGBA, separated by spaces (e.g. bg=255 255 255 0)
        background = tuple(map(int, passed_keyvals["bg"].split(" ")))

    # Process
    img = piped[0]
    px = img.load()

    dests = []
    dpxs = []

    for i in xrange(0, num_outs):
        dests.append(Image.new("RGBA", img.size, background))
        dpxs.append(dests[i].load())

    for y in xrange(img.size[0]):
        for x in xrange(img.size[1]):
            out = random.randint(0, num_outs-1)
            dpxs[out][x, y] = px[x, y]

    return tuple(dests)


def x_display(piped, passed):
    """
    Will attempt to preview all the piped images.
    Can be used mid-pipeline, and by passing "pause" it will require the user
    to "Press Enter to continue."

    Example pipeline:
        "open(file1.png, file2.png) | display"
    """
    try:
        input = raw_input
    except:
        pass

    for img in piped:
        img.show()

    if "pause" in passed:
        __ = input("Press Enter to continue...")

    return (piped)

def x_fill(piped, passed):
    # Replace all instances of a given color with either a randomly generated
    # color, or the corresponding pixel from another image source
    import random

    passed_keyvals = keyvals_to_dict(passed)
    # Default: visible black
    background = (0, 0, 0, 255)

    if "bg" in passed_keyvals:
        # RGBA, separated by spaces (e.g. bg=255 255 255 0)
        background = tuple(map(int, passed_keyvals["bg"].split(" ")))

    if "source" in passed_keyvals:
        source_img = Image.open(passed_keyvals["source"])

    # Process
    img = piped[0]
    px = img.load()


    if source_img:
        pxsrc = source_img.load()
        for y in xrange(img.size[0]):
            # print px[0, y]
            for x in xrange(img.size[1]):
                # TODO: Verify color comparison integrity,
                # E.g. now comparing an RGB with an RGBA will always fail.
                if px[x, y] == background:
                    px[x, y] = pxsrc[x, y]
    else:
        for y in xrange(img.size[0]):
            # print px[0, y]
            for x in xrange(img.size[1]):
                # TODO: Verify color comparison integrity,
                # E.g. now comparing an RGB with an RGBA will always fail.
                if px[x, y] == background:
                    px[x, y] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    return piped

def x_duplicate(piped, passed):
    # Assuming a single image piped, then duplicate this the passed 'num'
    # number of times.
    # Defaults: num=2
    passed_keyvals = keyvals_to_dict(passed)
    copies = 2
    if "num" in passed_keyvals:
        copies = int(passed_keyvals["num"])

    results = []

    for i in xrange(0, copies):
        results.append(piped[0].copy())

    return tuple(results)

def x_noise(piped, passed):
    # Generate an image. If an image is piped or passed, it will use this as the
    # palette. Otherwise it will create an evenly distributed RGB image
    return piped

def x_noisify(piped, passed):
    # Generate an image. If an image is piped or passed, it will use this as the
    # palette. Otherwise it will create an evenly distributed RGB image
    # Currently identifying every unique color, and evenly distribute them.
    #   Consider keeping the original distribution ratio
    import random

    passed_keyvals = keyvals_to_dict(passed)
    img_index = 0
    if "index" in passed_keyvals:
        img_index = int(passed_keyvals["index"])

    img = piped[img_index]
    px = img.load()

    palette_tmp = {}

    for y in xrange(img.size[0]):
        for x in xrange(img.size[1]):
            palette_tmp[px[x, y]] = 1

    palette = palette_tmp.keys()
    palette_size = len(palette)

    for y in xrange(img.size[0]):
        for x in xrange(img.size[1]):
            px[x, y] = palette[random.randint(0, palette_size-1)]

    return piped


def parse_block(block):
    """
    Excepts a string in format "<command>(<arg1>[,<arg2>,....])"
    Returns a two-element tuple: (<command>, [arg0, ... argn])
    """
    block = block.strip()
    pattern = "(\w+)" + "(\((.+)\))?"
    func = ""
    args = ()

    result = re.search(pattern, block)
    if not result:
        raise "InvalidBlock"

    func = result.group(1)

    if result.group(3):
        args = tuple(map(str.strip, result.group(3).split(",")))

    return (func, args)

def parse_pipeline(pipeline_raw):
    """
    Input: string representation of pipeline
    Output: internal pipeline representation
    """
    result = []
    for block in pipeline_raw.split("|"):
        result.append(parse_block(block))

    return result

def process_pipeline(pipeline):
    """
    Input: internal pipeline representation, as e.g. returned by parse_pipeline
    Output: nothing (apart from what's specified by the pipeline)
    """
    results = ()

    while len(pipeline) > 0:
        (current_func_name, current_passed_args) = pipeline.pop(0)
        current_func = get_module(current_func_name)

        results = current_func(results, current_passed_args)

init_default_modules()


def test():
    for tc in test_pipelines:
        result = parse_pipeline(tc[0])
        print "Testing   : {}".format(tc[0])
        print "Expecting : {}".format(tc[1])
        print "Got       : {}".format(result)
        print "Conclusion: {}".format(result == tc[1])

if __name__ == "__main__":
    from pprint import pprint
    if len(sys.argv) <= 1:
        print("error: No pipeline given; running tests");
        test()
        exit(-1)

    parsed = parse_pipeline(sys.argv[1])
    result = process_pipeline(parsed)
