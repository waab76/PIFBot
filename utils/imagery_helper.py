'''
Created on Apr 1, 2020

@author: rcurtis
'''

import logging
import os

from PIL import Image

from .file_system_helper import get_files_in_desc_order

def generate_thumbnail(source_dir, source_file, max_dimensions):
    source_file_path = os.path.join(source_dir, source_file)
    thumbnail_image = Image.open(source_file_path)
    thumbnail_image.thumbnail(max_dimensions)
    return thumbnail_image

def generate_thumbnail_file(source_dir, source_file, target_file, max_dimensions):
    thumbnail_image = generate_thumbnail(source_dir, source_file, max_dimensions)
    thumbnail_image.save(os.path.join(source_dir, target_file))

def generate_banner_image(source_dir, banner_image_name, banner_dimensions):
    banner_image = Image.new('RGB', banner_dimensions)
    start_pixel = 0
    skipped_latest = 0
    src_file_list = get_files_in_desc_order(source_dir)
    
    for source_file in src_file_list:
        if skipped_latest < 2:
            skipped_latest += 1
            continue
        
        if start_pixel < banner_dimensions[0]:
            reduced_image = generate_thumbnail(source_dir, source_file, banner_dimensions)
        
            crop_box = (0, 0, reduced_image.size[0], reduced_image.size[1])
            region = reduced_image.crop(crop_box)
        
            paste_box = (start_pixel, 0, start_pixel + reduced_image.size[0], banner_dimensions[1])
            banner_image.paste(region, paste_box)
        
            start_pixel += reduced_image.size[0]
        else:
            logging.info('Probably need to delete [%s]', source_file)
        
    banner_image.save(os.path.join(source_dir, banner_image_name))
