# VolumeTracker
Image annotation tool to keep track of movements of a meniscus during injections using small capillaries.

## Rationale

Getting precise small volume injections can be challenging. At the end, what really tells you how much liquid was injected is the displacement of the meniscus (oil-water interface). The movement of the meniscus can be hard to notice visually, even with conventional stereomicroscopes (and especially for small volumes). The proposed solution is to track the movement of the meniscus using a small USB microscope.

> For the companion files to 3D print the USB microscope holder, check https://github.com/teamnbc/USBCameraHolder

This Python code uses the OpenCV library to annotate the live image of the capillary and (knowing its diameter) to provide a graduation in order to track the exact volume injected.

## Usage

The code takes a number of arguments:
  - `-s` or `--scale`: image resizing factor in % of original image; default value is 200%.
  - `-v` or `--volume`:  list of volumes indicated on graduation (in microL); default value is `[20,40,60,80,100]`.
  - `-od` or `--outer_diameter`: capillary outer diameter in mm; default is 1 mm.
  - `-id` or `--inner_diameter`: capillary outer diameter in mm; default is 0.5 mm.

Example:

`python3 main.py -s 250 -v 25,50,75,100 -od 1.2 -id 0.6`
