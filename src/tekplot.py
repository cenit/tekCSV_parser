#!/usr/bin/env python

# -*- coding: utf8 -*-

import matplotlib.pyplot as plt
import csv
from pint import UnitRegistry, Quantity
import argparse
import numpy as np
import pandas as pd
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    Quantity([])

# Use the default UnitRegistry instance for the entire package
u = UnitRegistry()
Q_ = u.Quantity


class tekdata():
    def __init__(self, inputFileName, outputFileName, showPlot=False):
        self.inputFileName = inputFileName
        self.outputFileName = outputFileName
        self.showPlot = showPlot

    def load_csv(self):
        """
        Load CSV data produced by a Tektronix oscilloscope.
        """
        filename = self.inputFileName
        info = {}
        x_mag, y1_mag, y2_mag = [], [], []
        with open(filename, 'rt', newline='') as f:
            reader = csv.reader(f, delimiter=',')
            model_key, model_value = next(reader)
            firmware_key, firmware_value = next(reader)
            _ = next(reader)  # skip empty line
            print(
                f'Reading {model_value} model file, firmware version {firmware_value}')

            for x in range(0, 12):
                key, value, _, _, _ = next(reader)
                if key:
                    info[key] = value
            x_units = u.parse_units(info['Horizontal Units'])
            y_units = u.parse_units(info['Vertical Units'])
            x_offset = 0.  # Not in CSV?
            y_offset = float(info['Vertical Offset'])
            x_scale = float(info['Horizontal Scale'])
            y_scale = float(info['Vertical Scale'])

            print(
                f'Horizontal Units: {x_units}, Vertical Units: {y_units}')
            print(
                f'Horizontal Offset: {x_offset}, Vertical Offset: {y_offset}')
            print(
                f'Horizontal Scale: {x_scale}, Vertical Scale: {y_scale}')

            self.x_axis_label, self.y1_axis_label, _, self.y2_axis_label, _ = next(
                reader)

            for row in reader:
                if len(row) != 5:
                    continue
                x, y1, _, y2, _ = row[:5]

                try:
                    xf = float(x)
                except ValueError:
                    # print("Not a float: ", x)
                    xf = 0
                try:
                    y1f = float(y1)
                except ValueError:
                    # print("Not a float: ", y1)
                    y1f = 0
                try:
                    y2f = float(y2)
                except ValueError:
                    # print("Not a float: ", y2)
                    y2f = 0

                x_mag.append(xf)
                y1_mag.append(y1f)
                y2_mag.append(y2f)

            self.x_mag_arr = np.array(x_mag)
            self.y1_mag_arr = np.array(y1_mag)
            self.y2_mag_arr = np.array(y2_mag)

            #hard_fixes
            x_scale = 1
            y_scale = 1

            self.data_x = Q_((self.x_mag_arr - x_offset)*x_scale, x_units)
            self.data_y1 = Q_((self.y1_mag_arr - y_offset)*y_scale, y_units)
            self.data_y2 = Q_((self.y2_mag_arr - y_offset)*y_scale, y_units)

            print(self.data_x[0])
            print(self.data_x[1])

    def save_csv(self):
        df = pd.DataFrame({self.x_axis_label: self.data_x, self.y1_axis_label: self.data_y1, self.y2_axis_label: self.data_y2})
        df.to_csv(self.outputFileName, index=False, sep='\t', float_format='%3.5f', columns=[self.x_axis_label, self.y1_axis_label, self.y2_axis_label])

    def show_plots(self):
        plt.plot(self.data_x, self.data_y1, label=self.y1_axis_label)
        plt.plot(self.data_x, self.data_y2, label=self.y2_axis_label)
        plt.legend(loc='upper left')
        plt.show()

    def run(self):
        self.load_csv()
        print(self.data_x, self.data_y1, self.data_y2)
        self.save_csv()
        if self.showPlot:
            self.show_plots()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse, rewrite as plain CSV and plot Tektronix file')
    parser.add_argument('input_file', help='Input file (Tektronix CSV format)')
    parser.add_argument('output_file', help='Output file (plain CSV format)')
    parser.add_argument('--showPlot', dest='showPlot', default=False, action='store_true',
                        help='Show the plot in a windows after conversion', required=False)
    args = parser.parse_args()
    if args.input_file is not None and args.output_file is not None:
        a = tekdata(inputFileName=args.input_file,
                    outputFileName=args.output_file,
                    showPlot=args.showPlot)
    else:
        parser.print_help()
    a.run()
