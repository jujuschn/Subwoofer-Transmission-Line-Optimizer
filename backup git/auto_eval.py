import os
import time 
from io import StringIO

from datetime import datetime, timedelta
import subprocess as sp


import pyautogui as ag
import pygetwindow as gw
import pandas as pd


class ABEC:
    """
    Fields: self. ->
    project_file_path
    output_file_path 
    auto_output_file_path
    process
    df

    
    """

    def __init__(self, project_file_path, output_file_path, auto_output_file_path):
        self.output_file_path = output_file_path
        self.auto_output_file_path = auto_output_file_path  # the path of the file that ABEC saves the file to when done with spectra calc
        self.project_file_path = project_file_path
        self.set_up()

    # unfinished
    def step(self):   
        # alter LEScript file 
        # -> what metrics are altered 
        # -> this should be determined from opt. algorithm 


        # run calculation 
        # is there some way of feedback that implies calc is over -> no unnecessary waiting 
        self.calc_spectra_and_safe()
        
        # extract data from file 
        self.return_data()
        print(self.df.head())
        # analyze output data and generate metrics 

    def set_up(self) :    
        self.process = sp.Popen([r'C:\Program Files\RDTeam\ABEC3\ABEC3.exe'])
        while not any("ABEC3-Demo" in w.title for w in gw.getAllWindows()):
            time.sleep(0.05)
        time.sleep(1)
        
        # set file-out to File -> see calc_spectra_and_safe()
        ag.press('alt')
        ag.press('a')
        ag.press('o')
        ag.press('down')
        ag.press('down')
        ag.press('enter')
        """
            ag.keyDown('alt')
            ag.press('tab')
            ag.keyUp('alt')
        """ 
        # open up project
        ag.keyDown('ctrl')
        ag.press('o')
        ag.keyUp('ctrl')

        time.sleep(1.5)

        ag.write(self.project_file_path)
        time.sleep(0.5)
        ag.press('enter')
        
    def calc_spectra_and_safe(self) :
        start_time = time.time()
        ag.keyDown('fn')
        ag.press('f7')
        ag.keyUp('fn')

        #check wheter output file from calculation has been updated
        mtime = start_time
        while mtime > start_time : 
            if time.time() > start_time + 10 : 
                print("calculation takes over 10 seconds")
            time.sleep(0.5)
            mtime = os.path.getmtime(self.auto_output_file_path)
        
        ag.keyDown('ctrl')
        ag.press('f7')
        ag.keyUp('ctrl')
        ag.press('enter')

    # unfinished, must be specified to the specific output data
    def return_data(self) :
        # Read the entire file into memory
        with open(self.output_file_path, "r") as f:
            lines = f.readlines()

        # Extract lines between "Data" and "Data_End"
        inside_data = False
        data_lines = []
        for line in lines:
            if line.strip() == "Data":
                inside_data = True
                continue
            elif line.strip() == "Data_End":
                break
            if inside_data:
                data_lines.append(line)

        # Create a DataFrame without header 
        data_str = ''.join(data_lines)
        self.df = pd.read_csv(StringIO(data_str), delim_whitespace=True, header=None)

        # Rename columns 
        # df.columns = ['Frequency_Hz', 'Real_Part', 'Imag_Part']



    def end(self) :
        ag.keyDown('ctrl')
        ag.press('s')
        ag.keyUp('ctrl')
        time.sleep(1)
        ag.write(self.project_file_path)
        time.sleep(0.5)
        self.process.kill()

def main():
    print("Hello from main!")
    project_file_path = r"C:\Users\julio\Documents\RDTeam\ABEC3\ABEC3 Examples\LEM\Enclosure Vented\Project.abec"
    output_file_path = r"C:\Users\julio\Documents\RDTeam\ABEC3\ABEC3 Examples\LEM\Enclosure Vented\Results\Spectrum.txt"
    auto_output_file_path = r"C:\Users\julio\Documents\RDTeam\ABEC3\ABEC3 Examples\LEM\Enclosure Vented\Results\VacsSpectrum.vips"
    abec = ABEC(project_file_path, output_file_path, auto_output_file_path)
    abec.step()
    abec.end()

if __name__ == "__main__":
    main()