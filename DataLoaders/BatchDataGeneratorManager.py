#
# created by
# Antonio Garcia-Uceda Juarez
# PhD student
# Medical Informatics
#
# created on 09/02/2018
# Last update: 09/02/2018
########################################################################################

from Common.Constants import TYPE_DNNLIBRARY_USED

if TYPE_DNNLIBRARY_USED == 'Pytorch':
    from BatchDataGenerators.BatchDataGenerator_Pytorch import WrapperBatchGenerator_Pytorch as DNNBatchDataGenerator
elif TYPE_DNNLIBRARY_USED == 'Keras':
    from BatchDataGenerators.BatchDataGenerator_Keras import BatchDataGenerator_Keras as DNNBatchDataGenerator

from BatchDataGenerators.BatchDataGenerator import *
from Preprocessing.ImageGeneratorManager import *



def getBatchDataGeneratorWithGenerator(size_in_images,
                                       list_xData_arrays,
                                       list_yData_arrays,
                                       in_images_generator,
                                       batch_size,
                                       is_outputUnet_validconvs= False,
                                       size_output_images= None,
                                       shuffle= True,
                                       seed= None):
    batch_data_generator = DNNBatchDataGenerator(size_in_images,
                                                 list_xData_arrays,
                                                 list_yData_arrays,
                                                 in_images_generator,
                                                 batch_size=batch_size,
                                                 is_outputUnet_validconvs=is_outputUnet_validconvs,
                                                 size_output_image=size_output_images,
                                                 shuffle=shuffle,
                                                 seed=seed)

    return batch_data_generator


def getBatchDataGenerator(size_in_images,
                          list_xData_arrays,
                          list_yData_arrays,
                          use_slidingWindowImages,
                          slidewindow_propOverlap,
                          use_randomCropWindowImages,
                          numRandomPatchesEpoch,
                          use_transformationRigidImages,
                          use_transformElasticDeformImages,
                          batch_size,
                          is_outputUnet_validconvs= False,
                          size_output_images= None,
                          shuffle= True,
                          seed= None):
    if len(list_xData_arrays)==1:
        size_full_image = list_xData_arrays[0].shape
    else:
        size_full_image = 0

    images_generator = getImagesDataGenerator(size_in_images,
                                              use_slidingWindowImages,
                                              slidewindow_propOverlap,
                                              use_randomCropWindowImages,
                                              numRandomPatchesEpoch,
                                              use_transformationRigidImages,
                                              use_transformElasticDeformImages,
                                              size_full_image=size_full_image)

    return getBatchDataGeneratorWithGenerator(size_in_images,
                                              list_xData_arrays,
                                              list_yData_arrays,
                                              images_generator,
                                              batch_size,
                                              is_outputUnet_validconvs= is_outputUnet_validconvs,
                                              size_output_images= size_output_images,
                                              shuffle= shuffle,
                                              seed= seed)