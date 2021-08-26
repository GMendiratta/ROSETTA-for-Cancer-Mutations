Input_Revised_locations.txt contains a vector that remaps locations from the SEER ICD03 loc data.
Input_SEER_Histology_Recode_Map.txt is a table that represents the ROSETTA recoding of SEER entries by combining ICD03 location and histology codes.
SEER_python_code_RUNME.py is the main code which uses above files as well as 'input.dic' and 'input.txt' downloaded from SEER*Stat program rate session and outputs ROSETTA recoded data. The following command can be used to run this code.
	python SEER_python_code_RUNME.py 
Output_SEER.py contains ROSETTA recoded and processed epidemiological data ready to be combined with the corresponding genomic data.
Note: input.dic and input.txt files are not provided as SEER*Stat does not allow raw data downloaded from their software to be shared publically. The data can be accessed by setting up a free account with NIH-NCI and downloading their SEER*Stat software at this link: https://seer.cancer.gov/seerstat/software/index.html