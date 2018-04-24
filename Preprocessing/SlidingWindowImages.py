#
# created by
# Antonio Garcia-Uceda Juarez
# PhD student
# Medical Informatics
#
# created on 09/02/2018
# Last update: 09/02/2018
########################################################################################

import numpy as np


class SlidingWindowImages(object):

    def __init__(self, num_images, size_image):
        self.num_images = num_images
        self.size_image = size_image

    @staticmethod
    def get_num_images_1d(size_total, size_image, prop_overlap):

        return int(np.floor((size_total - prop_overlap*size_image) /(1-prop_overlap) /size_image))

    @staticmethod
    def get_limits_image_1d(index, size_image, prop_overlap):

        coord_n    = int(index * (1.0-prop_overlap) * size_image)
        coord_npl1 = coord_n + size_image
        return (coord_n, coord_npl1)

    def get_num_images_total(self):
        return self.num_images

    def get_num_channels_array(self, in_array_shape):
        if len(in_array_shape) == len(self.size_image):
            return 1
        else:
            return in_array_shape[-1]

    def get_shape_out_array(self, num_images, num_channels=1):
        if num_channels == 1:
            return [num_images] + list(self.size_image)
        else:
            return [num_images] + list(self.size_image) + [num_channels]

    def get_image_cropped(self, images_array, index):
        pass

    def get_image_array(self, images_array, index):

        return self.get_image_cropped(images_array, index)

    def compute_images_array_all(self, images_array):

        out_array_shape = self.get_shape_out_array(images_array.shape[0], num_channels=self.get_num_channels_array(images_array.shape))

        out_images_array = np.ndarray(out_array_shape, dtype=images_array.dtype)

        for index in range(self.num_images):
            out_images_array[index] = self.get_image_cropped(index, images_array)
        #endfor

        return out_images_array


class SlidingWindowImages2D(SlidingWindowImages):

    def __init__(self, size_total, size_image, prop_overlap):

        (self.size_total_x,   self.size_total_y  ) = size_total
        (self.size_image_x,   self.size_image_y  ) = size_image
        (self.prop_overlap_x, self.prop_overlap_y) = prop_overlap
        (self.num_images_x,   self.num_images_y  ) = self.get_num_images()
        self.num_images_total = self.num_images_x * self.num_images_y

        super(SlidingWindowImages2D, self).__init__(self.num_images_total, size_image)

    def get_indexes_local(self, index):

        index_y  = index // self.num_images_x
        index_x  = index % self.num_images_x
        return (index_x, index_y)

    def get_num_images(self):

        num_images_x = self.get_num_images_1d(self.size_total_x, self.size_image_x, self.prop_overlap_x)
        num_images_y = self.get_num_images_1d(self.size_total_y, self.size_image_y, self.prop_overlap_y)

        return (num_images_x, num_images_y)

    def get_limits_image(self, index):

        (index_x, index_y) = self.get_indexes_local(index)

        (x_left, x_right) = self.get_limits_image_1d(index_x, self.size_image_x, self.prop_overlap_x)
        (y_down, y_up   ) = self.get_limits_image_1d(index_y, self.size_image_y, self.prop_overlap_y)

        return (x_left, x_right, y_down, y_up)

    def get_image_cropped(self, images_array, index):

        (x_left, x_right, y_down, y_up) = self.get_limits_image(index)

        return images_array[x_left:x_right, y_down:y_up, ...]


class SlidingWindowImages3D(SlidingWindowImages):

    def __init__(self, size_total, size_image, prop_overlap):

        (self.size_total_z,   self.size_total_x,   self.size_total_y  ) = size_total
        (self.size_image_z,   self.size_image_x,   self.size_image_y  ) = size_image
        (self.prop_overlap_z, self.prop_overlap_x, self.prop_overlap_y) = prop_overlap
        (self.num_images_z,   self.num_images_x,   self.num_images_y  ) = self.get_num_images()
        self.num_images_total = self.num_images_x * self.num_images_y * self.num_images_z

        super(SlidingWindowImages3D, self).__init__(self.num_images_total, size_image)

    def get_indexes_local(self, index):

        num_images_xy = self.num_images_x * self.num_images_y
        index_z  = index // (num_images_xy)
        index_xy = index % (num_images_xy)
        index_y  = index_xy // self.num_images_x
        index_x  = index_xy % self.num_images_x
        return (index_z, index_x, index_y)

    def get_num_images(self):

        num_images_x = self.get_num_images_1d(self.size_total_x, self.size_image_x, self.prop_overlap_x)
        num_images_y = self.get_num_images_1d(self.size_total_y, self.size_image_y, self.prop_overlap_y)
        num_images_z = self.get_num_images_1d(self.size_total_z, self.size_image_z, self.prop_overlap_z)

        return (num_images_z, num_images_x, num_images_y)

    def get_limits_image(self, index):

        (index_z, index_x, index_y) = self.get_indexes_local(index)

        (x_left, x_right) = self.get_limits_image_1d(index_x, self.size_image_x, self.prop_overlap_x)
        (y_down, y_up   ) = self.get_limits_image_1d(index_y, self.size_image_y, self.prop_overlap_y)
        (z_back, z_front) = self.get_limits_image_1d(index_z, self.size_image_z, self.prop_overlap_z)

        return (z_back, z_front, x_left, x_right, y_down, y_up)

    def get_image_cropped(self, images_array, index):

        (z_back, z_front, x_left, x_right, y_down, y_up) = self.get_limits_image(index)

        return images_array[z_back:z_front, x_left:x_right, y_down:y_up, ...]


class SlicingImages2D(SlidingWindowImages2D):

    def __init__(self, size_total, size_image):
        super(SlicingImages2D, self).__init__(size_total, size_image, (0.0, 0.0))

class SlicingImages3D(SlidingWindowImages3D):

    def __init__(self, size_total, size_image):
        super(SlicingImages3D, self).__init__(size_total, size_image, (0.0, 0.0, 0.0))