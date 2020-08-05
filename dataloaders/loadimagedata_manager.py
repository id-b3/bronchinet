
from typing import List, Tuple, Any
import numpy as np

from common.exception_manager import catch_error_exception
from common.function_util import is_exist_file
from dataloaders.imagefilereader import ImageFileReader


class LoadImageDataManager(object):

    @classmethod
    def load_1file(cls, filename: str) -> np.ndarray:
        if not is_exist_file(filename):
            message = 'input file does not exist: \'%s\'' % (filename)
            catch_error_exception(message)

        return ImageFileReader.get_image(filename)

    @classmethod
    def load_2files(cls,
                    filename_1: str,
                    filename_2: str
                    ) -> Tuple[np.ndarray, np.ndarray]:
        if not is_exist_file(filename_1):
            message = 'input file 1 does not exist: \'%s\'' % (filename_1)
            catch_error_exception(message)
        if not is_exist_file(filename_2):
            message = 'input file 1 does not exist: \'%s\'' % (filename_2)
            catch_error_exception(message)

        out_image_1 = ImageFileReader.get_image(filename_1)
        out_image_2 = ImageFileReader.get_image(filename_2)

        if out_image_1.shape != out_image_2.shape:
            message = 'input image 1 and 2 of different size: (\'%s\' != \'%s\')' % (out_image_1.shape, out_image_2.shape)
            catch_error_exception(message)

        return (out_image_1, out_image_2)

    @classmethod
    def load_1list_files(cls, list_filenames: List[str]) -> List[np.ndarray]:
        out_list_images = []
        for in_file in list_filenames:
            out_image = cls.load_1file(in_file)
            out_list_images.append(out_image)

        return out_list_images

    @classmethod
    def load_2list_files(cls,
                         list_filenames_1: List[str],
                         list_filenames_2: List[str]
                         ) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        if len(list_filenames_1) != len(list_filenames_2):
            message = 'number files in list1 (%s) and list2 (%s) are not equal' % (len(list_filenames_1), len(list_filenames_2))
            catch_error_exception(message)
                
        out_list_images_1 = []
        out_list_images_2 = []
        for in_file_1, in_file_2 in zip(list_filenames_1, list_filenames_2):
            (out_image_1, out_image_2) = cls.load_2files(in_file_1, in_file_2)
            out_list_images_1.append(out_image_1)
            out_list_images_2.append(out_image_2)

        return (out_list_images_1, out_list_images_2)


class LoadImageDataInBatchesManager(LoadImageDataManager):
    _max_num_images_batch_default = None

    def __init__(self, size_image: Tuple[int, ...]) -> None:
        self._size_image = size_image

    @staticmethod
    def _shuffle_data(in_imagedata_1: np.ndarray,
                      in_imagedata_2: np.ndarray = None
                      ) -> Tuple[np.ndarray, Any]:
        # generate random indexes to shuffle the image data
        random_indexes = np.random.choice(range(in_imagedata_1.shape[0]), size=in_imagedata_1.shape[0], replace=False)
        if in_imagedata_2 is not None:
            return (in_imagedata_1[random_indexes[:]], in_imagedata_2[random_indexes[:]])
        else:
            return (in_imagedata_1[random_indexes[:]], None)

    def load_1file(self,
                   filename: str,
                   max_num_images_batch: int = _max_num_images_batch_default,
                   is_shuffle_data: bool = True
                   ) -> np.ndarray:
        in_stack_images = super(LoadImageDataInBatchesManager, self).load_1file(filename)
        num_images_stack = in_stack_images.shape[0]

        if in_stack_images[0].shape != self._size_image:
            message = 'image size in input stack of images is different from image size in class: (\'%s\' != \'%s\'). ' \
                      'change the image size in class to be equal to the first' % (in_stack_images[0].shape, self._size_image)
            catch_error_exception(message)

        if max_num_images_batch and (num_images_stack > max_num_images_batch):
            out_batch_images = in_stack_images[0:max_num_images_batch]
        else:
            out_batch_images = in_stack_images

        if (is_shuffle_data):
            (out_batch_images, _) = self._shuffle_data(out_batch_images)

        return out_batch_images

    def load_2files(self,
                    filename_1: str,
                    filename_2: str,
                    max_num_images_batch: int = _max_num_images_batch_default,
                    is_shuffle_data: bool = True
                    ) -> Tuple[np.ndarray, np.ndarray]:
        (in_stack_images_1, in_stack_images_2) = super(LoadImageDataInBatchesManager, self).load_2files(filename_1, filename_2)
        num_images_stack = in_stack_images_1.shape[0]

        if in_stack_images_1[0].shape != self._size_image:
            message = 'image size in input stack of images is different from image size in class: (\'%s\' != \'%s\'). ' \
                      'change the image size in class to be equal to the first' % (in_stack_images_1[0].shape, self._size_image)
            catch_error_exception(message)

        if max_num_images_batch and (num_images_stack > max_num_images_batch):
            out_batch_images_1 = in_stack_images_1[0:max_num_images_batch]
            out_batch_images_2 = in_stack_images_2[0:max_num_images_batch]
        else:
            out_batch_images_1 = in_stack_images_1
            out_batch_images_2 = in_stack_images_2

        if (is_shuffle_data):
            (out_batch_images_1, out_batch_images_2) = self._shuffle_data(out_batch_images_1, out_batch_images_2)

        return (out_batch_images_1, out_batch_images_2)

    def load_1list_files(self,
                         list_filenames: List[str],
                         max_num_images_batch: int = _max_num_images_batch_default,
                         is_shuffle_data: bool = True
                         ) -> List[np.ndarray]:
        out_dtype = super(LoadImageDataInBatchesManager, self).load_1file(list_filenames[0]).dtype
        out_batch_images = np.array([], dtype=out_dtype).reshape((0,) + self._size_image)
        sumrun_out_images = 0

        for in_file in list_filenames:
            out_stack_images = super(LoadImageDataInBatchesManager, self).load_1file(in_file)
            num_images_stack = out_stack_images.shape[0]
            sumrun_out_images = sumrun_out_images + num_images_stack

            if max_num_images_batch and (sumrun_out_images > max_num_images_batch):
                num_images_rest_batch = num_images_stack - (sumrun_out_images - max_num_images_batch)
                out_stack_images = out_stack_images[0:num_images_rest_batch]

            out_batch_images = np.concatenate((out_batch_images, out_stack_images), axis=0)

        if (is_shuffle_data):
            (out_batch_images, _) = self._shuffle_data(out_batch_images)

        return out_batch_images

    def load_2list_files(self,
                         list_filenames_1: List[str],
                         list_filenames_2: List[str],
                         max_num_images_batch: int = _max_num_images_batch_default,
                         is_shuffle_data: bool = True
                         ) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        if len(list_filenames_1) != len(list_filenames_2):
            message = 'number files in list1 (%s) and list2 (%s) are not equal' % (len(list_filenames_1), len(list_filenames_2))
            catch_error_exception(message)

        out_dtype_1 = super(LoadImageDataInBatchesManager, self).load_1file(list_filenames_1[0]).dtype
        out_dtype_2 = super(LoadImageDataInBatchesManager, self).load_1file(list_filenames_2[0]).dtype
        out_batch_images_1 = np.array([], dtype=out_dtype_1).reshape((0,) + self._size_image)
        out_batch_images_2 = np.array([], dtype=out_dtype_2).reshape((0,) + self._size_image)
        sumrun_out_images = 0

        for in_file_1, in_file_2 in zip(list_filenames_1, list_filenames_2):
            (out_stack_images_1, out_stack_images_2) = super(LoadImageDataInBatchesManager, self).load_2files(in_file_1, in_file_2)
            num_images_stack = out_stack_images_1.shape[0]
            sumrun_out_images = sumrun_out_images + num_images_stack

            if max_num_images_batch and (sumrun_out_images > max_num_images_batch):
                num_images_rest_batch = num_images_stack - (sumrun_out_images - max_num_images_batch)
                out_stack_images_1  = out_stack_images_1[0:num_images_rest_batch]
                out_stack_images_2  = out_stack_images_2[0:num_images_rest_batch]

            out_batch_images_1 = np.concatenate((out_batch_images_1, out_stack_images_1), axis=0)
            out_batch_images_2 = np.concatenate((out_batch_images_2, out_stack_images_2), axis=0)

        if (is_shuffle_data):
            (out_batch_images_1, out_batch_images_2) = self._shuffle_data(out_batch_images_1, out_batch_images_2)

        return (out_batch_images_1, out_batch_images_2)