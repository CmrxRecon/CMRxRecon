# Package Structure
* Data_check.py: python script giving 'CMRxRecon_check.xlsx' excel containing the structure of CMRxRecon folder
* Compare_excel.py: python script that compares two excel files 'CMRxRecon.xlsx' and 'CMRxRecon_check.xlsx'.

# Prerequisites
This script requires the following dependencies to be installed:

* os
* openpyxl
* mat73

# Usage
### 1.Run the python scripit, Data_check.py.
* directory_path: A string representing the path where all the folder, 'CMRxRecon', is stored.
* output_file: A string representing the path of the excel, 'CMRxRecon_check.xlsx'.

    **Ouput:**
    **'CMRxRecon.xlsx' consits of:**
    Level_number: represent the folder level
    Dimensions: represent the dimension of .mat file (not included other types' dimensions)

### 2.Run the python scripit, Compare_excel.py.
* file_a: A string representing the path of the excel, 'CMRxRecon.xlsx'. (You can download the excel from the website: [https://www.synapse.org/#!Synapse:syn51476561/files/](https://www.synapse.org/#!Synapse:syn51476561/files/))
* file_b: A string representing the path of the excel, 'CMRxRecon_check.xlsx'. (generated from Data_check.py)
* output_file: A string representing the path of the output excel, 'Comparison_Result.xlsx'.

    **Ouput:**
    **'CMRxRecon.xlsx' consits of:**
    The cell filled with red represents the file is downloaded incompletely or is missing.