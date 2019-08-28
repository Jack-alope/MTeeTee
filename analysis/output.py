class OutputData():
    def writesummarycsv(self, datadict, expar):
        # Create summary file
        summaryfile = open('{0}/summary.csv'.format(expar['FOLDER']), 'w')
        # Write summary file head
        summaryfile.write('Tissue' + ',' +
                          'Pacing Freq' + ',' +
                          'Developed Force' + ',' +
                          'Developed Force STD' + ',' +
                          'Developed Stress' + ',' +
                          'Developed Stress STD' + ',' +
                          'Average Beat Rate' + ',' +
                          'Average Beat Rate STD' + ',' +
                          'Beat Rate COV' + ',' +
                          'T2PK' + ',' +
                          'T2PK STD' + ',' +
                          'T50' + ',' +
                          'T50 STD' + ',' +
                          'dfdt' + ',' +
                          'dfdt STD' + ',' +
                          'negdfdt' + ',' +
                          'negdfdt STD' + ',' +
                          'C50' + ',' +
                          'C50 STD' + ',' +
                          'R50' + ',' +
                          'R50 STD' + ',' +
                          'T2Rel90' + ',' +
                          'T2Rel90 STD' + ',' +
                          'Passive Force' + ',' +
                          'Passive Force STD' ',' +
                          'Active Force' + ',' +
                          'Active Force STD' ',' +
                          '\n'
                          )

        for i in range(len(datadict)):
            summaryfile.write(str(expar[i]['TISSUE']) + ',' +
                              str(expar[i]['PACINGFREQ']) + ',' +
                              str(datadict[i]['Developed Force']) + ',' +
                              str(datadict[i]['Developed STD']) + ',' +
                              str(datadict[i]['Developed Stress']) + ',' +
                              str(datadict[i]['Developed Stress STD']) + ',' +
                              str(datadict[i]['Beatrate']) + ',' +
                              str(datadict[i]['Beatrate STD']) + ',' +
                              str(datadict[i]['Beatrate COV']) + ',' +
                              str(datadict[i]['T2PK']) + ',' +
                              str(datadict[i]['T2PK STD']) + ',' +
                              str(datadict[i]['T50']) + ',' +
                              str(datadict[i]['T50 STD']) + ',' +
                              str(datadict[i]['dfdt']) + ',' +
                              str(datadict[i]['dfdt STD']) + ',' +
                              str(datadict[i]['-dfdt']) + ',' +
                              str(datadict[i]['-dfdt STD']) + ',' +
                              str(datadict[i]['C50']) + ',' +
                              str(datadict[i]['C50 STD']) + ',' +
                              str(datadict[i]['R50']) + ',' +
                              str(datadict[i]['R50 STD']) + ',' +
                              str(datadict[i]['T2Rel90']) + ',' +
                              str(datadict[i]['T2Rel90 STD']) + ',' +
                              str(datadict[i]['Passive Force']) + ',' +
                              str(datadict[i]['Passive STD']) + ',' +
                              str(datadict[i]['Active Force']) + ',' +
                              str(datadict[i]['Active STD']) + ',' +
                              '\n'
                              )
        summaryfile.close()
