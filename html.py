
        @qgsfunction(args='auto', group='Custom')
        def tableHTMLfromAttributes(attributes, fieldname, expressionname, noattributes, feature, parent):
            """
            Returns a table from attributes
            """
            html = """
            <table style="width:100%">
                <tr>
                <th>{}</th>
                <th>{}</th>
            </tr>
            """.format(fieldname, expressionname)
            
            d = ast.literal_eval(attributes)
            if len(d) == 0:
                html +="""
                    <tr>
                        <td colspan=2><center>{}</center></td>
                    </tr>
                    """.format(noattributes)
            else:
                for k,v in dict(d).items():
                    html +="""
                    <tr>
                        <td>{}</td>
                        <td>{}</td>
                    </tr>
                    """.format(k, v)
                html += "</tr></table>"
            
            return html
