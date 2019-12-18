#!/usr/bin/env python3
import xml.etree.ElementTree as ElementTree
import csv
import argparse
import os

def jxl2csv(jxl_path, csv_path, isReduction=True, exportDeleted=False):
    e = ElementTree.parse(jxl_path).getroot()

    header = ["#name", "grid_east", "grid_north", "grid_elevation", "code", "description1", "description2", "fieldbook_id", "surveymethod", "classification", "wgs84_latitude", "wgs84_longitude", "wgs84_height", "local_latitude", "local_longitude", "local_height"] # TODO: "features", "customxmlsubrecord", "layer"

    if not isReduction:
        header += ["deleted", "precision_horizontal", "precision_vertical"]
        qc1 = ['QC1_MinimumNumberOfSatellites', 'QC1_MinGPSSVs',
               'QC1_MinGLONASSSVs', 'QC1_MinGalileoSVs', 'QC1_MinQZSSSVs',
               'QC1_MinBeiDouSVs', 'QC1_NumberOfSatellites', 'QC1_NumGPSSVs',
               'QC1_NumGLONASSSVs', 'QC1_NumGalileoSVs', 'QC1_NumQZSSSVs',
               'QC1_NumBeiDouSVs', 'QC1_RelativeDOPs', 'QC1_PDOP', 'QC1_GDOP',
               'QC1_HDOP', 'QC1_VDOP', 'QC1_PDOP_AtStore', 'QC1_GDOP_AtStore',
               'QC1_HDOP_AtStore', 'QC1_VDOP_AtStore',
               'QC1_NumberOfPositionsUsed', 'QC1_HorizontalStandardDeviation',
               'QC1_VerticalStandardDeviation']
        header += qc1
        qc2 = ['QC2_NumberOfSatellites', 'QC2_ErrorScale', 'QC2_VCVxx',
               'QC2_VCVxy', 'QC2_VCVxz', 'QC2_VCVyy', 'QC2_VCVyz', 'QC2_VCVzz']
        header += qc2

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

        points = 'Reductions/Point' if isReduction else '*/PointRecord'
        for point in e.findall(points):
            row = []
            if not isReduction and not exportDeleted and point.find('Deleted').text != 'false':
                continue

            row.append(addElementToList(point, 'Name'))
            grid = point.find('Grid') if isReduction else point.find('ComputedGrid')
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

            if not isReduction:
                row.append(addElementToList(point, 'Deleted'))

                precision = point.find('Precision')
                if precision:
                    row.append(precision.find('Horizontal').text)
                    row.append(precision.find('Vertical').text)
                else:
                    row += ['', '']

                qualityControl1 = point.find('QualityControl1')
                if qualityControl1:
                    for qc in ('MinimumNumberOfSatellites', 'MinGPSSVs',
                               'MinGLONASSSVs', 'MinGalileoSVs', 'MinQZSSSVs',
                               'MinBeiDouSVs', 'NumberOfSatellites',
                               'NumGPSSVs', 'NumGLONASSSVs', 'NumGalileoSVs',
                               'NumQZSSSVs', 'NumBeiDouSVs', 'RelativeDOPs',
                               'PDOP', 'GDOP', 'HDOP', 'VDOP', 'PDOP_AtStore',
                               'GDOP_AtStore', 'HDOP_AtStore', 'VDOP_AtStore',
                               'NumberOfPositionsUsed',
                               'HorizontalStandardDeviation',
                               'VerticalStandardDeviation'):
                        row.append(addElementToList(qualityControl1, qc))
                else:
                    row += [''] * len(qc1)

                qualityControl2 = point.find('QualityControl2')
                if qualityControl2:
                    for qc in ('NumberOfSatellites', 'ErrorScale', 'VCVxx',
                               'VCVxy', 'VCVxz', 'VCVyy', 'VCVyz', 'VCVzz'):
                        row.append(addElementToList(qualityControl2, qc))
                else:
                    row += [''] * len(qc2)

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
    parser.add_argument('--reduction', dest='reduction', action='store_true',
                        help='Use only Reductions fields (common fields)')
    parser.add_argument('--no-reduction', dest='reduction', action='store_false',
                        help="Use only FieldBook fields (all -especially precisions' -fields and all points even deleted)")
    parser.set_defaults(reduction=True)
    parser.add_argument('--export-deleted', dest='exportdeleted', action='store_true',
                        help='Export deleted points')
    parser.add_argument('--no-export-deleted', dest='exportdeleted', action='store_false',
                        help="Don't export deleted points")
    parser.set_defaults(exportdeleted=False)

    args = parser.parse_args()

    if not __checkFile(args.jxl_path):
        print("Cannot open file {}".format(args.jxl_path))
        exit(1)

    if not __checkFile(args.csv_path, True):
        print("Cannot open file {}".format(args.csv_path))
        exit(1)

    jxl2csv(args.jxl_path, args.csv_path, args.reduction, args.exportdeleted)
