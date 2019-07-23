#!-*- coding:utf-8 -*-

def verifyCodification(code_file):
    assert(all([x in code_file for x in
                ['AllPoints', 'ErrorPoints',
                 'ParameterSeparator', 'CodeSeparator',
                 'Codification']]))

    for c in ['CodeSeparator', 'ParameterSeparator']:
        sep = code_file[c]
        # TODO: Code and Parameter check in a predefined list?
        assert(isinstance(sep, str) and len(sep) == 1)

    for c in ['AllPoints', 'ErrorPoints']:
        dict_points = code_file[c]
        assert('Layer' in dict_points and
               isinstance(dict_points['Layer'], str) and
               # TODO: check if layer exists
               'isChecked' in dict_points and
               isinstance(dict_points['isChecked'], bool)
               )

    codif = code_file['Codification']
    assert(isinstance(codif, dict))
    # assert(len(codif.keys()) > 0)
    for k in codif.keys():
        c = codif[k]
        assert(all([x in c for x in
                    ['Attributes', 'Description',
                     'GeometryType', 'Layer']]))
        assert(isinstance(c['Attributes'], list))
        assert(isinstance(c['Description'], str))
        assert(isinstance(c['GeometryType'], str) and
           c['GeometryType'] in [v["code"] for v in AVAILABLE_CODE])
        assert(isinstance(c['Layer'], str)
               # TODO: check if layer exists
               )


