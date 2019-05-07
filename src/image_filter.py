"""
This class represents an instance of a set of filtering parameters for a given 
video/set of videos of a single object under controlled conditions.
"""

import os.path
import cv2
import numpy as np

__author__ = 'Nick'

class ImageFilter:

    # TODO: add some basic validation and related exception handling (?)
    def __init__(self, filters):
        self.filters = filters

    # generate aggregate extractive mask for supplied frame of video
    # returns extractive mask
    def get_aggregate_mask(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
        height, width, _ = img.shape
            
        masks = {}
            
        # get all masks for later combination
        for key, (lower,upper) in self.filters.iteritems():
            masks[key] = cv2.inRange(hsv, lower, upper)

        # get aggregate mask
        masks['combined'] = 0
        masks['combined'] = self._combine_masks(masks)

        return masks['combined']
    
    # combine arbitrary number of binary masks into one
    def _combine_masks(self, masks):
        combined_mask = []
        for key, mask in masks.iteritems():
            # initialize result mask to be first mask in dict if it doesn't already have a value
            # TODO: find a good solution to get rid of this ugly garbage solution
            if combined_mask == []:
                combined_mask = mask
                continue
            combined_mask = cv2.bitwise_or(combined_mask, mask)
        return combined_mask
