#
# created by
# Antonio Garcia-Uceda Juarez
# PhD student
# Medical Informatics
#
# created on 09/02/2018
# Last update: 09/02/2018
#######################################################################################

from common.constant import *
from common.function_util import *
from common.workdir_manager import *
import subprocess
import argparse


CODEDIR                            = join_path_names(BASEDIR, 'Code/')
SCRIPT_PREDICTIONMODEL             = join_path_names(CODEDIR, 'Scripts_Experiments/PredictionModel.py')
SCRIPT_POSTPROCESSPREDICTIONS      = join_path_names(CODEDIR, 'Scripts_AirwaySegment/PostprocessPredictions.py')
SCRIPT_PROCESSPREDICTAIRWAYTREE    = join_path_names(CODEDIR, 'Scripts_AirwaySegment/ProcessPredictAirwayTree.py')
SCRIPT_EXTRACTCENTRELINESFROMMASKS = join_path_names(CODEDIR, 'Scripts_Util/ApplyOperationImages.py')
SCRIPT_CACLFIRSTCONNREGIONFROMMASKS= join_path_names(CODEDIR, 'Scripts_Util/ApplyOperationImages.py')
SCRIPT_COMPUTERESULTMETRICS        = join_path_names(CODEDIR, 'Scripts_AirwaySegment/ComputeResultMetrics.py')


def printCall(new_call):
    message = ' '.join(new_call)
    print("*" * 100)
    print("<<< Launch: %s >>>" %(message))
    print("*" * 100 +"\n")

def launchCall(new_call):
    Popen_obj = subprocess.Popen(new_call)
    Popen_obj.wait()


def create_task_replace_dirs(input_dir, input_dir_to_replace):
    new_call_1 = ['rm', '-r', input_dir]
    new_call_2 = ['mv', input_dir_to_replace, input_dir]
    return [new_call_1, new_call_2]



def main(args):
    # ---------- SETTINGS ----------
    nameTempoPosteriorsRelPath    = 'PosteriorsWorkData/'
    namePosteriorsRelPath         = 'Posteriors/'
    namePredictBinaryMasksRelPath = 'BinaryMasks/'
    namePredictCentrelinesRelPath = 'Centrelines/'
    nameReferKeysPredictionsFile  = 'referenceKeys_posteriors.npy'
    nameOutputResultsMetricsFile  = 'result_metrics.csv'

    listResultsMetrics = ['DiceCoefficient', 'AirwayVolumeLeakage']
    # ---------- SETTINGS ----------


    inputdir = dirname(args.inputmodelfile)
    in_cfgparams_file = join_path_names(inputdir, NAME_CONFIGPARAMS_FILE)

    if not is_exist_file(in_cfgparams_file):
        message = "Config params file not found: \'%s\'..." % (in_cfgparams_file)
        catch_error_exception(message)
    else:
        input_args_file = read_dictionary_configparams(in_cfgparams_file)
    #print("Retrieve BaseDir from file: \'%s\'...\n" % (in_cfgparams_file))
    #BaseDir = str(input_args_file['basedir'])
    BaseDir = currentdir()


    # OutputBaseDir = makeUpdatedir(args.outputbasedir)
    OutputBaseDir = args.outputbasedir
    makedir(OutputBaseDir)

    InOutTempoPosteriorsPath     = join_path_names(OutputBaseDir, nameTempoPosteriorsRelPath)
    InOutPosteriorsPath          = join_path_names(OutputBaseDir, namePosteriorsRelPath)
    InOutPredictBinaryMasksPath  = join_path_names(OutputBaseDir, namePredictBinaryMasksRelPath)
    InOutPredictCentrelinesPath  = join_path_names(OutputBaseDir, namePredictCentrelinesRelPath)
    InOutReferKeysPosteriorsFile = join_path_names(OutputBaseDir, nameReferKeysPredictionsFile)


    list_calls_all = []


    # 1st: Compute model predictions, and posteriors for testing work data
    new_call = ['python3', SCRIPT_PREDICTIONMODEL, args.inputmodelfile,
                '--basedir', BaseDir,
                '--nameOutputPredictionsRelPath', InOutTempoPosteriorsPath,
                '--nameOutputReferKeysFile', InOutReferKeysPosteriorsFile,
                '--cfgfromfile', in_cfgparams_file,
                '--testdatadir', args.testdatadir]
    list_calls_all.append(new_call)


    # 2nd: Compute post-processed posteriors from work predictions
    new_call = ['python3', SCRIPT_POSTPROCESSPREDICTIONS,
                '--basedir', BaseDir,
                '--nameInputPredictionsRelPath', InOutTempoPosteriorsPath,
                '--nameInputReferKeysFile', InOutReferKeysPosteriorsFile,
                '--nameOutputPosteriorsRelPath', InOutPosteriorsPath,
                '--masksToRegionInterest', str(MASKTOREGIONINTEREST),
                '--rescaleImages', str(RESCALEIMAGES),
                '--cropImages', str(CROPIMAGES)]
    list_calls_all.append(new_call)


    # 3rd: Compute the predicted binary masks from the posteriors
    new_call = ['python3', SCRIPT_PROCESSPREDICTAIRWAYTREE,
                '--basedir', BaseDir,
                '--nameInputPosteriorsRelPath', InOutPosteriorsPath,
                '--nameOutputBinaryMasksRelPath', InOutPredictBinaryMasksPath,
                '--threshold_values', ' '.join([str(el) for el in args.thresholds]),
                '--attachCoarseAirwaysMask', 'True']
    list_calls_all.append(new_call)


    if args.isconnectedmasks:
        OutTempoPredictBinaryMasksPath = set_dirname_suffix(InOutPredictBinaryMasksPath, 'Tempo')

        # Compute the first connected component from the predicted binary masks
        new_call = ['python3', SCRIPT_CACLFIRSTCONNREGIONFROMMASKS, InOutPredictBinaryMasksPath, OutTempoPredictBinaryMasksPath,
                    '--type', 'firstconreg']
        list_calls_all.append(new_call)

        # replace output folder with binary masks
        new_sublist_calls = create_task_replace_dirs(InOutPredictBinaryMasksPath, OutTempoPredictBinaryMasksPath)
        list_calls_all += new_sublist_calls


    # 4th: Compute centrelines by thinning the binary masks
    new_call = ['python3', SCRIPT_EXTRACTCENTRELINESFROMMASKS, InOutPredictBinaryMasksPath, InOutPredictCentrelinesPath,
                '--type', 'thinning']
    list_calls_all.append(new_call)


    # 5th: Compute testing metrics from predicted binary masks and centrelines
    new_call = ['python3', SCRIPT_COMPUTERESULTMETRICS, InOutPredictBinaryMasksPath,
                '--basedir', BaseDir,
                '--inputcenlinesdir', InOutPredictCentrelinesPath,
                '--outputfile', nameOutputResultsMetricsFile,
                '--removeTracheaCalcMetrics', str(REMOVETRACHEACALCMETRICS)]
    list_calls_all.append(new_call)


    # remove temporary data for posteriors not needed
    new_call = ['rm', '-r', InOutTempoPosteriorsPath]
    list_calls_all.append(new_call)
    new_call = ['rm', InOutReferKeysPosteriorsFile, InOutReferKeysPosteriorsFile.replace('.npy', '.csv')]
    list_calls_all.append(new_call)


    # move results file one basedir down
    in_resfile  = join_path_names(InOutPredictBinaryMasksPath, nameOutputResultsMetricsFile)
    out_resfile = join_path_names(OutputBaseDir, nameOutputResultsMetricsFile)

    new_call = ['mv', in_resfile, out_resfile]
    list_calls_all.append(new_call)



    # Iterate over the list and carry out call serially
    for icall in list_calls_all:
        printCall(icall)
        try:
            launchCall(icall)
        except Exception as ex:
            traceback.print_exc(file=sys.stdout)
            message = 'Call failed. Stop pipeline...'
            catch_error_exception(message)
        print('\n')
    #endfor



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('inputmodelfile', type=str)
    parser.add_argument('outputbasedir', type=str)
    parser.add_argument('--basedir', type=str, default=BASEDIR)
    parser.add_argument('--thresholds', type=str, nargs='*', default=[0.5])
    parser.add_argument('--testdatadir', type=str, default='TestingData/')
    parser.add_argument('--isconnectedmasks', type=str2bool, default=False)
    args = parser.parse_args()

    print("Print input arguments...")
    for key, value in vars(args).items():
        print("\'%s\' = %s" %(key, value))

    main(args)