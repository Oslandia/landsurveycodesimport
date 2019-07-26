#!/usr/bin/env python3

import argparse


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='QGIS PDF generator')
    parser.add_argument('project_path', type=str,
                        help='path to the project configuration')
    parser.add_argument('layout_name', type=str,
                        help='layout name within the project')
    parser.add_argument('report_path', type=str,
                        help='generated report path')
    parser.add_argument('pyqgis_path', type=str,
                        help='syspath to pyqgis')
    args = parser.parse_args()

    if args.pyqgis_path:
        import sys
        sys.path.insert(0, args.pyqgis_path)

    from qgis.core import QgsProject, QgsLayoutExporter, QgsApplication
    
    qgs = QgsApplication([], False)
    qgs.initQgis()

    if not QgsProject.instance().read(args.project_path):
        print("Cannot open the file '{}'".format(args.project_path))
        exit(1)

    layout = QgsProject.instance().layoutManager().layoutByName(
        args.layout_name)
    if not layout:
        print("Cannot find layout '{}'".format(args.layout_name))
        exit(1)

    exporter = QgsLayoutExporter(layout)
    res = exporter.exportToPdf(args.report_path,
                               QgsLayoutExporter.PdfExportSettings())
    print(res)
    if res != QgsLayoutExporter.Success:
        print("Cannot export to pdf")
        exit(1)

    qgs.exitQgis()
