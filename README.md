# Apple Watch HR Export Collection Tool

## Usage

1. First export the xml data from the apple health app by going into the profile and select export all health data.  
2. Then open the zip file as you see fit and get the move the hr_export.xml file into this folder.
3. run `python3 hr_xml_to_csv.py` 
4. (optional) run the process data to generate the breakdown and partition based on month and annual parameter. 
Example `python3 process_data.py --file hr_export.csv -p yearly -b daily -o output_folder`
