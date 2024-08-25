# Package Structure
* eval_myo_map.py: main python script of caculating T1 and T2 mapping data
* cardiac_utils.py: helper python script providing a set of functions for performing cardiac calculations.
* image_utils.py: helper python script consisting of a set of functions for various operations related to cardiac image processing and analysis

# eval_myo_map
This is the **main python** script and is designed to process T1 and T2 mapping data labels for myocardial mapping. It takes a data path and an output CSV file path as inputs and generates a CSV file containing the mapping results.

### Prerequisites
This script requires the following dependencies to be installed:

* pandas
* nibabel
* cardiac_utils (custom module)

### Usage
**The mapping function is the main function in this script**, processing the T1 and T2 mapping data labels. It takes two parameters:

* data_path: A string representing the path where all the IDs with mapping data are stored.
* output_csv: A string representing the path of the output CSV file.

Please ensure that the name of the output CSV file contains either 't1' or 't2' so that the script can determine the type of data to process.

To use this script, modify with your desired inputs. For example:
```
if __name__ == '__main__':
    mapping('Path of mapping data','Path of csv file')
```

### Output
The script will generate a CSV file containing the mapping results. The columns of the CSV file will include the following mappings:

* Mapping_AHA_1
* Mapping_AHA_2
* Mapping_AHA_3
* Mapping_AHA_4
* Mapping_AHA_5
* Mapping_AHA_6
* Mapping_AHA_7
* Mapping_AHA_8
* Mapping_AHA_9
* Mapping_AHA_10
* Mapping_AHA_11
* Mapping_AHA_12
* Mapping_AHA_13
* Mapping_AHA_14
* Mapping_AHA_15
* Mapping_AHA_16
* Mapping_Global

Each value represents myocardial mapping values of different segments.

### Test
The demo data and output are in **test** file.

Example of T1 mapping:
Run the main function: mapping('./testdata','./ouput/t1_mapping_test.csv')
data_path: A string representing the path where all the IDs with mapping data are stored. In this case, testdata is the file containing all IDs(test1).
* output_csv: A string representing the path of the output CSV file. In this case, t1_mapping _test.csv is the name of output CSV file, instructing the script to process T1 mapping data.

Example of T1 mapping:
Run the main function: mapping('./testdata','./ouput/t2_mapping_test.csv')
data_path: A string representing the path where all the IDs with mapping data are stored. In this case, testdata is the file containing all IDs(test1).
* output_csv: A string representing the path of the output CSV file. In this case, t2_mapping _test.csv is the name of output CSV file, instructing the script to process T2 mapping data.

Output: Both output CSV files of T1 and T2 mapping data for test1 are included in output file.

### Reference
ukbb_cardic: <https://github.com/baiwenjia/ukbb_cardiac>

