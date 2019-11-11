#
# created by
# Antonio Garcia-Uceda Juarez
# PhD student
# Medical Informatics
#
# created on 09/02/2018
# Last update: 09/02/2018
########################################################################################

from Common.Constants import *
from Common.WorkDirsManager import *
from DataLoaders.FileReaders import *
from Preprocessing.OperationImages import *
from Preprocessing.OperationMasks import *
import argparse



def main(args):
    # ---------- SETTINGS ----------
    nameInputLumenMasksRelPath    = 'RawAirwaysLumen/'
    nameInputOutWallMasksRelPath  = 'RawAirwaysOutWall/'
    nameInputLumenMasksFiles      = '*surface0.dcm'
    nameInputOutWallMasksFiles    = '*surface1.dcm'
    nameOutputAirWallMasksRelPath = 'AirwayWall_Proc/'

    def nameOutputMasksFiles(in_name):
        in_name = in_name.replace('surface0','airwall')
        in_name = in_name.replace('surface1','airwall')
        return filenamenoextension(in_name) + '.nii.gz'
    # ---------- SETTINGS ----------


    workDirsManager        = WorkDirsManager(args.datadir)
    InputLumenMasksPath    = workDirsManager.getNameExistPath(nameInputLumenMasksRelPath)
    InputOutWallMasksPath  = workDirsManager.getNameExistPath(nameInputOutWallMasksRelPath)
    OutputAirWallMasksPath = workDirsManager.getNameNewPath  (nameOutputAirWallMasksRelPath)

    listInputLumenMasksFiles   = findFilesDirAndCheck(InputLumenMasksPath,   nameInputLumenMasksFiles)
    listInputOutWallMasksFiles = findFilesDirAndCheck(InputOutWallMasksPath, nameInputOutWallMasksFiles)



    for i, (in_lumenmask_file, in_outwallmask_file) in enumerate(zip(listInputLumenMasksFiles, listInputOutWallMasksFiles)):
        print("\nInput: \'%s\'..." % (basename(in_lumenmask_file)))
        print("And: \'%s\'..." % (basename(in_outwallmask_file)))

        (in_lumenmask_array, in_outwallmask_array, _) = FileReader.get2ImageArraysAndCheck(in_lumenmask_file, in_outwallmask_file)

        print("Original dims : \'%s\'..." % (str(in_lumenmask_array.shape)))


        in_lumenmask_array   = OperationBinaryMasks.process_masks(in_lumenmask_array)
        in_outwallmask_array = OperationBinaryMasks.process_masks(in_outwallmask_array)

        out_airwallmask_array = in_outwallmask_array - in_lumenmask_array
        # clip to bound output to limits of binary masks
        np.clip(out_airwallmask_array, 0.0, 1.0, out=out_airwallmask_array)


        out_file = joinpathnames(OutputAirWallMasksPath, nameOutputMasksFiles(basename(in_lumenmask_file)))
        print("Output: \'%s\', of dims \'%s\'..." % (basename(out_file), str(out_airwallmask_array.shape)))

        FileReader.writeImageArray(out_file, out_airwallmask_array)
    # endfor



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--datadir', type=str, default=DATADIR)
    args = parser.parse_args()

    print("Print input arguments...")
    for key, value in vars(args).iteritems():
        print("\'%s\' = %s" %(key, value))

    main(args)