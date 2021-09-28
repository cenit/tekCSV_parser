#!/usr/bin/env python

# -*- coding: utf8 -*-

import matplotlib.pyplot as plt
import csv
import os
import argparse
import numpy as np
import pandas as pd

class tekdata():
    def __init__(self, inputFileName, showPlot=False, savePlot=False, saveCSV=False):
        self.inputFileName = inputFileName.name
        self.basename = os.path.basename(inputFileName.name)
        self.basename_noext = os.path.splitext(self.basename)
        self.outputCSVFileName = self.basename_noext[0] + "_plain.csv"
        self.outputPNGFileName = self.basename_noext[0] + ".png"
        self.showPlot = showPlot
        self.savePlot = savePlot
        self.saveCSV = saveCSV

    def load_csv(self):
        """
        Load CSV data produced by a Tektronix oscilloscope.
        """
        self.info = {}
        channels = {}
        line_to_be_skipped_by_pandas = 0

        with open(self.inputFileName, 'rt', newline='') as f:
            reader = csv.reader(f, delimiter=',')
            model_key, model_value = next(reader)
            line_to_be_skipped_by_pandas += 1
            firmware_key, firmware_value = next(reader)
            line_to_be_skipped_by_pandas += 1
            _ = next(reader)  # skip empty line
            line_to_be_skipped_by_pandas += 1
            print(
                f'Reading {model_value} model file, firmware version {firmware_value}')

            while True:
                line = next(reader)
                line_to_be_skipped_by_pandas+=1
                key = line[0]
                if key == "":
                    continue
                if key:
                    for v in range(1, len(line)):
                        vkey = "CH" + str(v)
                        channels[vkey] = line[v]
                self.info[key] = channels.copy()
                if key == "Label":
                    break

        self.data = pd.read_csv(self.inputFileName, sep=',', skiprows=line_to_be_skipped_by_pandas)
        if 'Waveform Type' in self.info:
            print("File contains Waveform data")
            if self.info['Waveform Type']['CH1'] == "ANALOG":
                print("File contains analog data, renaming channels")
                self.data.rename(columns=self.info['Label'], inplace=True)

    def save_csv(self):
        print("Writing plain CSV file: ", self.outputCSVFileName)
        self.data.to_csv(self.outputCSVFileName, index=False,
                         sep='\t', float_format='%3.5f')

    def create_plots(self):
        for column in self.data.columns[1:]:
            data_x = np.asarray(self.data['TIME'])
            data_y = np.asarray(self.data[column])
            plt.plot(data_x, data_y, label=column)
        plt.legend(loc='upper right')
        if self.showPlot:
            plt.show()
        if self.savePlot:
            print("Writing png file: ", self.outputPNGFileName)
            plt.savefig(self.outputPNGFileName)

    def run(self):
        self.load_csv()
        self.create_plots()
        if self.saveCSV:
            self.save_csv()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse, rewrite as plain CSV and plot Tektronix file')
    parser.add_argument('input_file', type=argparse.FileType('r'), nargs=1, help='Input files (Tektronix CSV format)')
    parser.add_argument('--show-plot', dest='showPlot', default=False, action='store_true',
                        help='Show the plot in a windows after conversion', required=False)
    parser.add_argument('--save-plot', dest='savePlot', default=False, action='store_true',
                        help='Save the plot in a png file', required=False)
    parser.add_argument('--save-plain-csv', dest='saveCSV', default=False, action='store_true',
                        help='Show the plot in a windows after conversion', required=False)
    args = parser.parse_args()
    if args.input_file is not None:
        a = tekdata(inputFileName=args.input_file[0],
                    showPlot=args.showPlot,
                    savePlot=args.savePlot,
                    saveCSV=args.saveCSV)
    else:
        parser.print_help()
    a.run()
