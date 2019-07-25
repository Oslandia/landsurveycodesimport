#!/usr/bin/env python3
import xml.etree.ElementTree as ElementTree
import csv
import argparse
import os

def jxl2csv(jxl_path, csv_path):
    e = ElementTree.parse(jxl_path).getroot()

    header = ["#name", "grid_east", "grid_north", "grid_elevation", "code", "description1", "description2", "fieldbook_id", "surveymethod", "classification", "wgs84_latitude", "wgs84_longitude", "wgs84_height", "local_latitude", "local_longitude", "local_height"] # TODO: "features", "customxmlsubrecord", "layer"

    def addElementToList(point, element):
        ret = ''
        try:
            ret = point.find(element).text
        except:
            pass
    
        return ret
    with open(csv_path, 'w') as trimbleCSV:
        csv_writer = csv.writer(trimbleCSV, delimiter=',')
        csv_writer.writerow(header)

        for point in e.findall('Reductions/Point'):
            row = []
            row.append(addElementToList(point, 'Name'))
            
            grid = point.find('Grid')
            if grid: # X/Y!!!
                row.append(grid.find('East').text)
                row.append(grid.find('North').text)
                row.append(grid.find('Elevation').text)
            else:
                row += ['', '', '']
            
            row.append(addElementToList(point, 'Code'))
            row.append(addElementToList(point, 'Description1'))
            row.append(addElementToList(point, 'Description2'))
            row.append(addElementToList(point, 'ID'))
            row.append(addElementToList(point, 'SurveyMethod'))
            row.append(addElementToList(point, 'Classification'))

            wgs84 = point.find('WGS84')
            if wgs84:
                row.append(wgs84.find('Latitude').text)
                row.append(wgs84.find('Longitude').text)
                row.append(wgs84.find('Height').text)
            else:
                row += ['', '', '']

            local = point.find('Local')
            if local:
                row.append(local.find('Latitude').text)
                row.append(local.find('Longitude').text)
                row.append(local.find('Height').text)
            else:
                row += ['', '', '']

            csv_writer.writerow(row)

def __checkFile(fnm, write=False):
    flag = os.R_OK
    if write:
        flag = os.W_OK
    if os.path.exists(fnm):
        if os.path.isfile(fnm):
            return os.access(fnm, flag)
        else:
            return False
    else:
        if not write:
            return False
    # target does not exist, check perms on parent dir
    pdir = os.path.dirname(fnm)
    if not pdir: pdir = '.'
    # target is creatable if parent dir is writable
    return os.access(pdir, flag)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Trimble JobXML to CSV')
    parser.add_argument('jxl_path', type=str,
                        help='Path to the JobXML (*.jxl) file')
    parser.add_argument('csv_path', type=str,
                        help='Path to the CSV file')
    args = parser.parse_args()

    if not __checkFile(args.jxl_path):
        print("Cannot open file {}".format(args.jxl_path))
        exit(1)

    if not __checkFile(args.csv_path, True):
        print("Cannot open file {}".format(args.csv_path))
        exit(1)

    jxl2csv(args.jxl_path, args.csv_path)
