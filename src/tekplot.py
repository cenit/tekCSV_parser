#!/usr/bin/env python

# -*- coding: utf8 -*-

import matplotlib.pyplot as plt
import csv
from pint import UnitRegistry
import argparse


# Use the default UnitRegistry instance for the entire package
u = UnitRegistry()
Q_ = u.Quantity


class tekdata():
    dt = [[], []]
    data_x = [[], []]
    data_y = [[], []]

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
        x_mag, y_mag = [], []
        with open(filename, 'rt', newline='') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                key, value, _, x, y = row[:5]
                if key:
                    info[key] = value

                x_mag.append(float(x))
                y_mag.append(float(y))

            x_units = u.parse_units(info['Horizontal Units'])
            y_units = u.parse_units(info['Vertical Units'])
            x_offset = 0.  # Not in CSV?
            y_offset = float(info['Vertical Offset'])
            x_scale = float(info['Horizontal Scale'])
            y_scale = float(info['Vertical Scale'])
            x_zero = 0.  # Not in CSV?
            y_zero = float(info['Yzero'])

            x_mag_arr = np.array(x_mag)
            y_mag_arr = np.array(y_mag)

            self.data_x = Q_((x_mag_arr - x_offset)*x_scale + x_zero, x_units)
            self.data_y = Q_((y_mag_arr - y_offset)*y_scale + y_zero, y_units)

    def save_csv(self):
        print("Not implemented")

    def show_plots(self):
        print("Not implemented")

    def run(self):
        self.load_csv()
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
