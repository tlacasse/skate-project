import cv2

def iterate_image(img):
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            yield (i, j)

class AutoCropper:
    
    def __init__(self, color_lower, color_upper, threshold=225, padding=10, pre_crop=10):
        """
        'color_lower' and 'color_upper' are arrays of [H, S, V]
        """
        self.color_lower = color_lower
        self.color_upper = color_upper
        self.threshold = threshold
        self.padding = padding
        self.pre_crop = pre_crop
        self.CROP_FAILURE_THRESHOLD = 10
        
    def _isolate_colors(self, hsv_frame, lower_colors, upper_colors):
        mask = cv2.inRange(hsv_frame, lower_colors[0], upper_colors[0])
        for i in range(1, len(lower_colors)):
            mask = cv2.bitwise_or(mask, 
                     cv2.inRange(hsv_frame, lower_colors[i], upper_colors[i]))
        return mask
    
    def _prepare_mask(self, mask):
        # reduce noise
        mask = cv2.resize(mask, None, fx = 0.5, fy = 0.5, interpolation = cv2.INTER_CUBIC)
        mask = cv2.GaussianBlur(mask, (9, 9), 500)
        mask = cv2.resize(mask, None, fx = 2, fy = 2, interpolation = cv2.INTER_CUBIC)
        # remove colors other than the object of interest
        mask = cv2.cvtColor(mask, cv2.COLOR_BGR2HSV)
        mask = self._isolate_colors(mask, self.color_lower, self.color_upper)
        # blur out some noise below "white" threshold
        mask = cv2.GaussianBlur(mask, (17, 17), 1500)
        return mask
    
    def crop(self, img):
        # crop flat amound around edge
        img = img[self.pre_crop:-self.pre_crop, self.pre_crop:-self.pre_crop]
        src = img
        mask = self._prepare_mask(img)
        
        bounds_min = [mask.shape[i] for i in [0, 1]]
        bounds_max = [0, 0]
        
        for i, j in iterate_image(mask):
            # isolate_colors() returns B&W, W is object of interest
            if (mask[i, j] > self.threshold):
                bounds_min[0] = min(bounds_min[0], i)
                bounds_max[0] = max(bounds_max[0], i)
                bounds_min[1] = min(bounds_min[1], j)
                bounds_max[1] = max(bounds_max[1], j)
                
        for i in [0, 1]:
            bounds_min[i] = max(bounds_min[i] - self.padding, 0)
            bounds_max[i] = min(bounds_max[i] + self.padding, mask.shape[i] - 1)
        
        if (bounds_max[0] - bounds_min[0] < self.CROP_FAILURE_THRESHOLD
                or bounds_max[1] - bounds_min[1] < self.CROP_FAILURE_THRESHOLD):
            return None
        
        return src[bounds_min[0]:bounds_max[0], bounds_min[1]:bounds_max[1]]
