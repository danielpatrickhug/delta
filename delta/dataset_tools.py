#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __BEGIN_LICENSE__
#  Copyright (c) 2009-2013, United States Government as represented by the
#  Administrator of the National Aeronautics and Space Administration. All
#  rights reserved.
#
#  The NGT platform is licensed under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance with the
#  License. You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# __END_LICENSE__

"""
Tools for loading data into the TensorFlow Dataset class.
"""
import sys
import os
import math

import numpy as np

import image_reader
import utilities



def get_roi_horiz_band_split(image_size, region, num_splits):
    """Return the ROI of an image to load given the region.
       Each region represents one horizontal band of the image.
    """

    assert region < num_splits, 'Input region ' + str(region) \
           + ' is greater than num_splits: ' + str(num_splits)

    min_x = 0
    max_x = image_size[0]

    # Fractional height here is fine
    band_height = image_size[1] / num_splits

    # TODO: Check boundary conditions!
    min_y = math.floor(band_height*region)
    max_y = math.floor(band_height*(region+1.0))

    return utilities.Rectangle(min_x, min_y, max_x, max_y)


def get_roi_tile_split(image_size, region, num_splits):
    """Return the ROI of an image to load given the region.
       Each region represents one tile in a grid split.
    """
    num_tiles = num_splits*num_splits
    assert region < num_tiles, 'Input region ' + str(region) \
           + ' is greater than num_tiles: ' + str(num_tiles)

    tile_row = math.floor(region / num_splits)
    tile_col = region % num_splits

    # Fractional sizes are fine here
    tile_width  = floor(image_size[0] / side)
    tile_height = floor(image_size[1] / side)

    # TODO: Check boundary conditions!
    min_x = math.floor(tile_width  * tile_col)
    max_x = math.floor(tile_width  * (tile_col+1.0))
    min_y = math.floor(tile_height * tile_row)
    max_y = math.floor(tile_height * (tile_row+1.0))

    return utilities.Rectangle(min_x, min_y, max_x, max_y)


def load_image_region(path, region, roi_function, chunk_size, chunk_overlap, num_threads):
    """Load all image chunks for a given region of the image.
       The provided function converts the region to the image ROI.
    """

    # Set up the input image handle
    input_paths  = [path]
    input_reader = image_reader.MultiTiffFileReader()
    input_reader.load_images(input_paths)
    image_size = input_reader.image_size()

    # Call the provided function to get the ROI to load
    roi = roi_function(image_size, region)

    # Until we are ready to do a larger test, just return a short vector
    return np.array([roi.min_x, roi.min_y, roi.max_x, roi.max_y], dtype=np.int32) # DEBUG

    # Load the chunks from inside the ROI
    chunk_data = input_reader.parallel_load_chunks(roi, chunk_size, chunk_overlap, num_threads)

    return chunk_data


def prep_input_pairs(image_file_list, num_regions):
    """For each image generate a pair with each region"""

    image_out  = []
    region_out = []
    for i in image_file_list:
        for r in range(0,num_regions):
            image_out.append(i)
            region_out.append(r)

    return (image_out, region_out)