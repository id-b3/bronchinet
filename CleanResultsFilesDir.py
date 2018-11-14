#
# created by
# Antonio Garcia-Uceda Juarez
# PhD student
# Medical Informatics
#
# created on 09/02/2018
# Last update: 09/02/2018
#######################################################################################

from CommonUtil.Constants import *
from CommonUtil.ErrorMessages import *
from CommonUtil.FunctionsUtil import *


name_rel_loss_history_file     = 'lossHistory.txt'
name_link_rel_model_last_epoch = 'model_lastEpoch.hdf5'
name_link_rel_model_min_loss   = 'model_minLoss.hdf5'
name_link_rel_model_min_valoss = 'model_minValoss.hdf5'

freq_save_model_file = 10



if( len(sys.argv)<2 ):
    print("ERROR. Please input the directory to clean... EXIT")
    sys.exit(0)

results_dir = sys.argv[-1]

print("Clean the directory: '%s'..." %(results_dir))

list_all_files = listfilesDir(results_dir)

list_models_files = list(list_all_files)

name_loss_history_file     = joinpathnames(results_dir, name_rel_loss_history_file    )
name_link_model_last_epoch = joinpathnames(results_dir, name_link_rel_model_last_epoch)
name_link_model_min_loss   = joinpathnames(results_dir, name_link_rel_model_min_loss  )
name_link_model_min_valoss = joinpathnames(results_dir, name_link_rel_model_min_valoss)


list_models_files.remove(name_loss_history_file)

#remove any possible existing link
if name_link_model_last_epoch in list_all_files:
    list_models_files.remove(name_link_model_last_epoch)
if name_link_model_min_loss in list_all_files:
    list_models_files.remove(name_link_model_min_loss)
if name_link_model_min_valoss in list_all_files:
    list_models_files.remove(name_link_model_min_valoss)



# second: earmark the files to prevent from deleting
# 1) 'loss_history_file'
# 2) models corresponding to i) last epoch, ii) lowest training error, iii) lowest validation error
# 3) models with save frequency, is any

list_save_files = []
list_save_files.append(name_loss_history_file)

# find model files i) last epoch, ii) lowest training error, iii) lowest validation error
model_file_list_epochs = []
model_file_list_loss   = []
model_file_list_valoss = []

for file in list_models_files:
    attributes = basename(file).replace('model_', '').replace('.hdf5', '').split('_')
    model_file_list_epochs.append(int  (attributes[0]))
    model_file_list_loss  .append(float(attributes[1]))
    model_file_list_valoss.append(float(attributes[2]))
# endfor

model_file_maxepoch  = list_models_files[model_file_list_epochs.index(max(model_file_list_epochs))]
model_file_minloss   = list_models_files[model_file_list_loss  .index(min(model_file_list_loss  ))]
model_file_minvaloss = list_models_files[model_file_list_valoss.index(min(model_file_list_valoss))]

list_save_files.append(model_file_maxepoch)
list_save_files.append(model_file_minloss)
list_save_files.append(model_file_minvaloss)

print("model with max epoch: %s..." %(model_file_maxepoch))
print("model with min loss: %s..." %(model_file_minloss))
print("model with min valoss: %s..." %(model_file_minvaloss))


print("also save models every '%s':..." %(freq_save_model_file))

indexes_save_models = range(0, len(list_models_files), freq_save_model_file)

list_save_freq_models = []
for index in indexes_save_models:
    prefix = 'model_%s_'%(index)
    for file in list_models_files:
        if prefix in file:
            list_save_freq_models.append(file)
            list_save_files.append(file)
            continue
    #endfor
#endfor

print("list saved files: '%s'..." %(list_save_freq_models))


print("remove every other files...")
for file in list_all_files:
    if file not in list_save_files:
        removefile(file)
#endfor


# finally, link to remaining files
makelink(basename(model_file_maxepoch),  name_link_model_last_epoch)
makelink(basename(model_file_minloss),   name_link_model_min_loss)
makelink(basename(model_file_minvaloss), name_link_model_min_valoss)

print("create links: ...")
print("%s -> %s..." %(name_link_model_last_epoch, basename(model_file_maxepoch)))
print("%s -> %s..." %(name_link_model_min_loss, basename(model_file_minloss)))
print("%s -> %s..." %(name_link_model_min_valoss, basename(model_file_minvaloss)))


print("script successful...")