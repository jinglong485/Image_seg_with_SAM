import cv2
import random
import numpy as np
from pathlib import Path
import os

class ArrImage():

    def __init__(self):
        self.arr_image = None
        self.masked_image = None
        self.resize_factor = None
        self.masks = []
        self.masks_name = []
        
    def loadImage(self, path):
        self.arr_image = cv2.imread(path)
        image_height, _, _ = self.arr_image.shape
        self.resize_factor = image_height/512.0
        self.image_path = path
        self.file_name = Path(self.image_path).stem
        self.maskedResizedImage()
    
    def image(self):
        return self.arr_image
    
    def resizeFactor(self):
        return self.resize_factor
    
    def mask2contours(self, mask):
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        return contours
    
    def drawContours(self, img, mask):
        contours = self.mask2contours(mask)
        color = (0,255,0)
        if self.resize_factor < 1:
            contour_thickness = 1
        else:
            contour_thickness = 3
        cv2.drawContours(img, contours,-1, color,thickness = contour_thickness)
        return img

    def maskImage(self, img, mask, random_color = False, alpha = 0.60):

        """this method is internal methos, it generates orignal size images with masks,
        it will be used for generating:
        #1:resized maksed images for visualization in canvas
        #2:resized masked images for mask candidates"""

        BGR_mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        conj_mask = 1 - BGR_mask
        if random_color:
            random_color_mask = np.stack([mask * random.randint(0,255), mask * random.randint(0,255), mask * random.randint(0,255)], axis = -1)
        else:
            random_color_mask = np.stack([mask * 247, mask * 224, mask * 69],axis = -1)
        overlayed_image = cv2.addWeighted(img* BGR_mask, 1-alpha, random_color_mask, alpha, 0) + conj_mask * img
        return overlayed_image
    
    def maskedResizedImage(self, draw_list = None):
        #this method should be rewrite to enable selective maske drawing, it requires a list of True/False
        """this method has two usages:
        #1. it update self.masked_images with original size and all masks, this is for generate new masked candidates
        #2. it return resized masked images to viewer for visualization with size 512 in height"""
        random.seed(666)
        if draw_list == None:
            overlayed_image = self.arr_image
            for mask in self.masks:
                overlayed_image = self.maskImage(overlayed_image, mask, True)
                overlayed_image = self.drawContours(overlayed_image, mask)
        else:
            assert(len(self.masks) == len(draw_list))
            overlayed_image = self.arr_image
            for i, mask in enumerate(self.masks):
                if draw_list[i] == 1:
                    overlayed_image = self.maskImage(overlayed_image, mask, True)
                    overlayed_image = self.drawContours(overlayed_image, mask)
        #to update the masked image as the newest masked image with OG dize
        self.masked_image = overlayed_image#to update the masked image as the newest masked image with OG dize
        resize_overlayed_img = cv2.resize(overlayed_image, None, fx = 1.0 /self.resize_factor, fy = 1.0 /self.resize_factor, interpolation=cv2.INTER_LINEAR)
        return resize_overlayed_img
    
    def maskedCandidatesImage(self, mask_candidates):
        """this generates the three candidates masked images
        input: mask_candidates list of three maskes returned by sam.predictor
        return: list of three maksed images with resize factor of 4* self.resize_factor and 512 images for showing in canvas"""
        candidates_512 = []
        candidates_128 = []
        assert(len(mask_candidates) == 3)
        for mask in mask_candidates:
            masked_candidate = self.maskImage(self.masked_image, mask, False, 0.7)
            resized_masked_candidate_512 = cv2.resize(masked_candidate, None, fx = 1.0 /(self.resize_factor), fy = 1.0 /(self.resize_factor), interpolation=cv2.INTER_LINEAR)
            resized_masked_candidate_128 = cv2.resize(masked_candidate, None, fx = 1.0 /(self.resize_factor*4.0), fy = 1.0 /(self.resize_factor*4.0), interpolation=cv2.INTER_LINEAR)
            candidates_512.append(resized_masked_candidate_512)
            candidates_128.append(resized_masked_candidate_128)
        return candidates_512, candidates_128
    
    def addMask(self, mask, mask_name = "Object"):
        """this method add new mask with their name to mask list self.masks and self.mask_names
        the name of mask by default is Object_xx, where xx is # of masks_name list"""
        self.masks.append(mask)
        name = "".join((mask_name,"_",str(len(self.masks_name))))
        self.masks_name.append(name)

    def exportMaskAsTiff(self, path):
        """export data as tiff
        files saved in path/tiff/file_name
        filen name scheme should be file_name.tiff, file_name_mask_name.tiff"""
        temp_path = os.path.join(path, 'tiff')
        if not os.path.exists(temp_path):
            os.mkdir(temp_path)
        temp_file_name = "".join((path,'/tiff/',self.file_name,'.tiff'))
        cv2.imwrite(temp_file_name, self.arr_image)
        for i,mask in enumerate(self.masks):
            temp_mask_name = "".join((path,'/tiff/',self.file_name,'_',self.masks_name[i],'.tiff'))
            temp_mask = cv2.cvtColor(mask *255, cv2.COLOR_GRAY2BGR)
            cv2.imwrite(temp_mask_name,temp_mask)

    def exportMaskAsArray(self, path):
        """export images as npz file, the first should be image, then masks
        the images and maskes stores in  Dict first, then converted in to npz
        the file name is file_name.npz"""
        temp_path = os.path.join(path, 'npz')
        if not os.path.exists(temp_path):
            os.mkdir(temp_path)
        temp_file_dict = {}
        temp_file_dict["image"] = self.arr_image
        for name, mask in zip(self.masks_name, self.masks):
            temp_file_dict[name] = mask
        temp_file_name = "".join((path,'/npz/',self.file_name,'.npz'))
        np.savez(temp_file_name,**temp_file_dict)


