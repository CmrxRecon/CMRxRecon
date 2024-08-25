import sys

import os
import argparse
import pandas as pd
import nibabel as nib
from cardiac_utils import evaluate_myo_AHA_mapping


def mapping(data_path, output_csv):
    # data_path is a string containing the path where all IDs are stored with mapping data.
    # ouput_csv is a string containing the path of the ouput csv.
    # Note: Please include 't1' or 't2' in the name so that the code could recognize the type of data to process
    
    data_list = sorted(os.listdir(data_path)) # all IDs
    print(data_list)
    table = []
    processed_list = []
    for data in data_list:

        data_dir = os.path.join(data_path,data)

        # Evaluate myocardial mapping values

        # t1 or t2
        if 't1' in output_csv:
            mapping_type = 'T1'

            # Quality control for segmentation at ED
            # If the segmentation quality is low, evaluation of wall thickness may fail.
            mapping_sa_name = '{0}/t1map_short_t1_MOCO_T1.nii.gz'.format(data_dir)
            seg_sa_name = '{0}/label_t1map.nii.gz'.format(data_dir)
            if not os.path.exists(seg_sa_name):
                print('check')
                continue
            # if not sa_pass_quality_control(seg_sa_name):
            #     continue

            df = evaluate_myo_AHA_mapping(seg_sa_name,
                                          mapping_sa_name,
                                          mapping_type, part=None)
        elif 't2' in output_csv:
            mapping_type = 'T2'

            # Quality control for segmentation at ED
            # If the segmentation quality is low, evaluation of wall thickness may fail.
            mapping_sa_name = '{0}/t2map_flash_MOCO_T2.nii.gz'.format(data_dir)
            seg_sa_name = '{0}/label_t2map.nii.gz'.format(data_dir)
            if not os.path.exists(seg_sa_name):
                continue
            # if not sa_pass_quality_control(seg_sa_name):
            #     continue

            df = evaluate_myo_AHA_mapping(seg_sa_name,
                                          mapping_sa_name,
                                          mapping_type, part=None)
        else:
            print('Error: wrong mapping_type')
    #         exit(0)

        line = df['Mapping'].values
        table += [line]
        processed_list += [data]

    # Save wall thickness for all the subjects
    columns_list = ['Mapping_AHA_1', 'Mapping_AHA_2', 'Mapping_AHA_3',
               'Mapping_AHA_4', 'Mapping_AHA_5', 'Mapping_AHA_6',
               'Mapping_AHA_7', 'Mapping_AHA_8', 'Mapping_AHA_9',
               'Mapping_AHA_10', 'Mapping_AHA_11', 'Mapping_AHA_12',
               'Mapping_AHA_13', 'Mapping_AHA_14', 'Mapping_AHA_15', 'Mapping_AHA_16',
               'Mapping_Global']
    columns_list = [mapping_type+'_'+s for s in columns_list]

    df = pd.DataFrame(table, index=processed_list,
                      columns=columns_list
                      )
    df.to_csv(output_csv)


if __name__ == '__main__':
    #example
    mapping('Path of mapping data','Path of csv file')


