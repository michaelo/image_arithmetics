#!python
import sys
import re
from PIL import Image, ImageFilter

# "open(file1, file2) | xor | save(file3) "
# "open(infile1, infile2) | xor | scatter | save(outfile1, outfile2) "
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

# Rules:
# First argument of all functions should be a tuple containing return-values of the previous functions in the pipeline
# Second argument of all functinons should be a tuple containing the string arguments as defined by pipeline

def x_open(piped, passed):
    """Ignores first argument for now. Expects tuple of filenames (through "passed")"""
    result = []
    if not passed:
        raise "InvalidArguments"

    for i in passed:
        result.append(Image.open(i))

    return tuple(result)


def x_xor(piped, __):
    assert( len(piped) == 2 )
    def _txor(v1, v2):
        return (v1[0] ^ v2[0], v1[1] ^ v2[1], v1[2] ^ v2[2])

    # TODO: XOR arbitrary number of images
    px1 = piped[0].load()
    px2 = piped[1].load()

    for y in xrange(piped[0].size[0]):
        for x in xrange(piped[0].size[1]):
            px1[x, y] = _txor(px1[x, y], px2[x, y])

    return (piped[0],)

def x_save(piped, passed):
    assert(len(piped) == len(passed))
    for (i, __) in enumerate(piped):
        piped[i].save(passed[i])

def x_scatter(piped, passed):
    assert(len(piped) == 1)
    import random
    # TODO: Allow input: background color, types of scattering
    img = piped[0]
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

    return (dest1, dest2)


def x_display(piped, passed):
    # TODO: Argument to pause before continuing
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
    """ Excepts a string in format "<command>(<arg1>[,<arg2>,....])" """
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

def parse_pipeline(pipeline):
    result = []
    for block in pipeline.split("|"):
        result.append(parse_block(block))

    return result

def process_pipeline(pipeline):
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
        # print("error: No pipeline");
        test()
        exit(-1)

    parsed = parse_pipeline(sys.argv[1])
    result = process_pipeline(parsed)
    #
    # pprint(parse(sys.argv[1]))
