#!python
import sys
import re
from PIL import Image

func_map = {}

test_pipelines = [
    ("open(file1, file2) | xor | save(file3) ",
        [("open", ("file1", "file2")), ("xor", ()), ("save", ("file3",))]
    ),
    ("open(infile1, infile2) | xor | scatter | save(outfile1, outfile2) ",
        [("open", ("infile1", "infile2")), ("xor", ()), ("scatter", ()), ("save", ("outfile1", "outfile2"))]
    )
]

def register_module(name, function):
    global func_map
    func_map[name] = function

def is_valid_module(name):
    return name in func_map

def get_module(name):
    return func_map[name]


def init_default_modules():
    register_module("open", x_open)
    register_module("xor", x_xor)
    register_module("save", x_save)
    register_module("scatter", x_scatter)
    register_module("display", x_display)
    register_module("extract", x_extract)
    register_module("scale", x_scale)

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


def x_xor(piped, __):
    """
    Takes two (or more) input images, returns an image that's the pixelwise
    XOR of them.
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
    assert(len(piped) == len(passed))
    for (i, __) in enumerate(passed):
        piped[i].save(passed[i])

    return piped

def x_scatter(piped, passed):
    """
    Input: source image
    Output: two images which together contains all the pixels of the source.
        Each pixel has a even probability to end in either destination image

    Example pipeline:
    """
    assert(len(piped) == 1)
    import random
    # TODO: Allow input: background color, types of scattering
    img = piped[0]
    px = img.load()

    dests = []
    dpxs = []
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

    return (dest1, dest2)


def x_display(piped, passed):
    """
    Will attempt to preview all the piped images.
    Can be used mid-pipeline, and by passing "pause" it will require the user
    to press Enter to continue.

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
        print result == tc[1]

if __name__ == "__main__":
    from pprint import pprint
    if len(sys.argv) <= 1:
        print("error: No pipeline given; running tests");
        test()
        exit(-1)

    parsed = parse_pipeline(sys.argv[1])
    result = process_pipeline(parsed)
