from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

from OpenEXRDirectory import OpenEXRDirectory

class OpenEXRDirectories:

  def __init__(self, base_directory, number_of_sources_per_example):
    self.base_directory = base_directory
    self.number_of_sources_per_example = number_of_sources_per_example
    self.samples_per_pixel_to_exr_directories = {}
    subdirectories = OpenEXRDirectories._subdirectories(self.base_directory)
    for subdirectory in subdirectories:
      exr_directory = OpenEXRDirectory(subdirectory)
      samples_per_pixel = exr_directory.samples_per_pixel
      if not samples_per_pixel in self.samples_per_pixel_to_exr_directories:
        exr_directories = [exr_directory]
        self.samples_per_pixel_to_exr_directories[samples_per_pixel] = exr_directories
      else:
        exr_directories = self.samples_per_pixel_to_exr_directories[samples_per_pixel]
        exr_directories.append(exr_directory)
        exr_directories.sort()

  def required_files_exist(self, samples_per_pixel, render_passes_usage):
    result = True
    if samples_per_pixel in self.samples_per_pixel_to_exr_directories:
      exr_directories = self.samples_per_pixel_to_exr_directories[samples_per_pixel]
      for index, exr_directory in enumerate(exr_directories):
        if index < self.number_of_sources_per_example:
          result = exr_directory.required_files_exist(render_passes_usage)
          if not result:
            break
        else:
          break
    return result

  def load_images(self, samples_per_pixel, render_passes_usage):
    if samples_per_pixel in self.samples_per_pixel_to_exr_directories:
      exr_directories = self.samples_per_pixel_to_exr_directories[samples_per_pixel]
      for index, exr_directory in enumerate(exr_directories):
        if index < self.number_of_sources_per_example:
          exr_directory.load_images(render_passes_usage)
  
  def size_of_loaded_images(self):
    height = 0
    width = 0
    done = False
    for samples_per_pixel in self.samples_per_pixel_to_exr_directories:
      exr_directories = self.samples_per_pixel_to_exr_directories[samples_per_pixel]
      for exr_directory in exr_directories:
        if exr_directory.is_loaded():
          height, width = exr_directory.size_of_loaded_images()
          done = True
          break
      if done:
        break
    return height, width
  
  def have_loaded_images_identical_sizes(self):
    result = True
    height, width = self.size_of_loaded_images()
    for samples_per_pixel in self.samples_per_pixel_to_exr_directories:
      exr_directories = self.samples_per_pixel_to_exr_directories[samples_per_pixel]
      for index, exr_directory in enumerate(exr_directories):
        if index < self.number_of_sources_per_example:
          result = exr_directory.have_loaded_images_size(height, width)
          if not result:
            break
        else:
          break
      if not result:
        break
    return result
  
  def unload_images(self):
    for samples_per_pixel in self.samples_per_pixel_to_exr_directories:
      exr_directories = self.samples_per_pixel_to_exr_directories[samples_per_pixel]
      for exr_directory in exr_directories:
        exr_directory.unload_images()
  
  def ground_truth_samples_per_pixel(self):
    result = 0
    for samples_per_pixel in self.samples_per_pixel_to_exr_directories:
      if result < samples_per_pixel:
        result = samples_per_pixel
    return result
  
  @staticmethod
  def _subdirectories(directory):
    return filter(os.path.isdir, [os.path.join(directory, subdirectory) for subdirectory in os.listdir(directory)])