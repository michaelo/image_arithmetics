Image arithmetic toolset
========================
Author: Michael Odden

A pipeline-based approach to chaining image-based operations:

Examples:

> python ia.py "open(file1.png, file2.png) | scale(200, 200) | xor | save(xored_and_scaled.png)"


Usage
-----
You define your desired operation(s) as a set of actions you want to perform, formulated as a string-encoded pipeline.

The pipeline string is passed to the ia.py entry point, which will parse it and execute it.

Basix syntax of pipeline:
> module1[(argument,key=value)] [| module2... [| moduleN]]

Supported modules
-----------
* open
* open_left
* save
* display
* xor
* xor_color
* scatter
* duplicate
* extract
* scale
* fill
* noisify


Installation / Prerequisites
------------
* Python 2.7
* Python module "PIL" or "Pillow"


TODO
----
* Bundled description of the supported modules / blocks
* Make consistent, intuitive, support for RGB and ARGB
* Make/consider support for arbitrary number of input for as many modules as possible
* Logging: Implement support for --debug flag
* Error handling: helpful output
* Consider possibility to support parallel lines (tee), or make index-choice part of all relevant modules
* Consider supporting other image libraries than PIL/Pillow
