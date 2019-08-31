import numpy as np
from analysis.output import OutputData


class PerformCalculations():
    def forcecoef(self, expar, tissue):
        # in kg/s^2 * 1000 to convert to millisecond
        radiuscalc = expar['POSTRADIUS'] ** 4
        numerator = 3 * np.pi * expar['YOUNGS'] * radiuscalc * 1000
        denom1 = (2 * (expar[tissue]['TISSUEHEIGHT1'] ** 2) *
                  ((3 * expar[tissue]['POSTHEIGHT1']) - expar[tissue]['TISSUEHEIGHT1']))
        denom2 = (2 * (expar[tissue]['TISSUEHEIGHT2'] ** 2) *
                  ((3 * expar[tissue]['POSTHEIGHT2']) - expar[tissue]['TISSUEHEIGHT2']))

        # Return force coefficient for each post, in the case of eht system they will be the same, I only use forcecoefficient1 in that case
        expar[tissue]['forcecoefficient1'] = (numerator/denom1)
        expar[tissue]['forcecoefficient2'] = (numerator/denom2)

    def populatedata(self, analyzeddf, df, expar):
        datadict = {}
        # For each tissue
        for i in range(len(analyzeddf)):
            # Creates a dict of dicts
            dummy = {}
            datadict[i] = dummy

            if expar['BIO'] == 'eht':
                (passive, passivestd) = self.passiveforce(self, expar[i]['forcecoefficient1'],
                                                          expar['MAXDISP'], analyzeddf[i]['basepoints'], df[i]['disp'])
                datadict[i]['Passive Force'] = passive
                datadict[i]['Passive STD'] = passivestd

                (active, activestd) = self.activeforce(self, expar[i]['forcecoefficient1'],
                                                       expar['MAXDISP'], analyzeddf[i]['peaks'], df[i]['disp'])
                datadict[i]['Active Force'] = active
                datadict[i]['Active STD'] = activestd

            elif expar['BIO'] == 'multitissue':
                (passive, passivestd) = self.passiveforcemt(self, expar[i]['forcecoefficient1'], expar[i]['forcecoefficient2'],
                                                            expar['MAXDISP'], analyzeddf[i]['basepoints'], df[i]['disp'])
                datadict[i]['Passive Force'] = passive
                datadict[i]['Passive STD'] = passivestd

                (active, activestd) = self.activeforcemt(self, expar[i]['forcecoefficient1'], expar[i]['forcecoefficient2'],
                                                         expar['MAXDISP'], analyzeddf[i]['peaks'], df[i]['disp'])
                datadict[i]['Active Force'] = active
                datadict[i]['Active STD'] = activestd

            (developed, developedstd) = self.developedforce(
                self, expar[i]['forcecoefficient1'], expar[i]['forcecoefficient2'], expar['MAXDISP'], analyzeddf[i]['peaks'], analyzeddf[i]['basepoints'], df[i])
            datadict[i]['Developed Force'] = developed
            datadict[i]['Developed STD'] = developedstd
            datadict[i]['Developed Stress'] = developed/expar[i]['CROSSSECT']
            datadict[i]['Developed Stress STD'] = developedstd / \
                expar[i]['CROSSSECT']

            (beatrate, beatratestd) = self.avgbeatingfreq(
                self, df[i]['time'], analyzeddf[i]['peaks'])
            datadict[i]['Beatrate'] = beatrate
            datadict[i]['Beatrate STD'] = beatratestd
            datadict[i]['Beatrate COV'] = beatratestd / beatrate

            (t2pk, t2pkstd) = self.t2pk(
                self, analyzeddf[i]['10contractedx'], analyzeddf[i]['peaks'], df[i]['time'])
            datadict[i]['T2PK'] = t2pk
            datadict[i]['T2PK STD'] = t2pkstd

            (t50, t50std) = self.t50(
                self, analyzeddf[i]['50contractedx'], analyzeddf[i]['50relaxedx'], df[i]['time'])
            datadict[i]['T50'] = t50
            datadict[i]['T50 STD'] = t50std

            (dfdt, dfdtstd) = self.dfdt(self, analyzeddf[i]['10contractedx'], analyzeddf[i]['10contractedy'],
                                        analyzeddf[i]['90contractedx'], analyzeddf[i]['90contractedy'], df[i]['time'])
            datadict[i]['dfdt'] = dfdt
            datadict[i]['dfdt STD'] = dfdtstd

            (negdfdt, negdfdtstd) = self.dfdt(self, analyzeddf[i]['90relaxedx'], analyzeddf[i]
                                              ['90relaxedy'], analyzeddf[i]['10relaxedx'], analyzeddf[i]['10relaxedy'], df[i]['time'])
            datadict[i]['-dfdt'] = negdfdt
            datadict[i]['-dfdt STD'] = negdfdtstd

            (c50, c50std) = self.c50(
                self, analyzeddf[i]['peaks'], analyzeddf[i]['50contractedx'], df[i]['time'])
            datadict[i]['C50'] = c50
            datadict[i]['C50 STD'] = c50std

            (r50, r50std) = self.r50(
                self, analyzeddf[i]['peaks'], analyzeddf[i]['50relaxedx'], df[i]['time'])
            datadict[i]['R50'] = r50
            datadict[i]['R50 STD'] = r50std

            (t2rel90, t2rel90std) = self.t2rel90(
                self, analyzeddf[i]['90relaxedx'], analyzeddf[i]['peaks'], df[i]['time'])
            datadict[i]['T2Rel90'] = t2rel90
            datadict[i]['T2Rel90 STD'] = t2rel90std

        return datadict

    def passiveforce(self, forcecoef, maxdisp, basepoints, disp):
        passiveforce = []
        for point in basepoints:
            passiveforce.append((maxdisp + disp[point]) * forcecoef/2)
        std = np.std(passiveforce)
        avg = sum(passiveforce) / len(passiveforce)
        return (avg, std)

    def activeforce(self, forcecoef, maxdisp, peaks, disp):
        activeforce = []
        for peak in peaks:
            activeforce.append((maxdisp + disp[peak]) * forcecoef/2)
        std = np.std(activeforce)
        avg = sum(activeforce) / len(activeforce)
        return (avg, std)

    def passiveforcemt(self, forcecoef1, forcecoef2, maxdisp, basepoints, disp):
        passiveforce = []
        for point in basepoints:
            dispo = maxdisp + disp[point]
            passiveforce.append(
                (dispo * forcecoef1 * forcecoef2)/(forcecoef1 + forcecoef2))
        std = np.std(passiveforce)
        avg = sum(passiveforce) / len(passiveforce)
        return (avg, std)

    def activeforcemt(self, forcecoef1, forcecoef2, maxdisp, peaks, disp):
        activeforce = []
        for peak in peaks:
            dispo = maxdisp + disp[peak]
            activeforce.append(
                (dispo * forcecoef1 * forcecoef2)/(forcecoef1 + forcecoef2))
        std = np.std(activeforce)
        avg = sum(activeforce) / len(activeforce)
        return (avg, std)

    def developedforce(self, forcecoef1, forcecoef2, maxdisp, peaks, basepoints, df):
        developedforce = []

        for i in range(len(peaks)):
            first = (df['x1'][peaks[i]], df['y1'][peaks[i]])
            second = (df['x1'][basepoints[i]], df['y1'][basepoints[i]])
            dist = np.sqrt(((second[0]-first[0])**2) + ((second[1]-first[1])**2))
            developedforce.append(dist * forcecoef1)

            first = (df['x2'][peaks[i]], df['y2'][peaks[i]])
            second = (df['x2'][basepoints[i]], df['y2'][basepoints[i]])
            dist = np.sqrt(((second[0]-first[0])**2) + ((second[1]-first[1])**2))
            developedforce.append(dist * forcecoef2)

        std = np.std(developedforce)
        avg = sum(developedforce) / len(developedforce)
        return (avg, std)

    def avgbeatingfreq(self, time, peaks):
        timediff = []
        for i in range(len(peaks) - 1):
            timediff.append(1/(time[peaks[i + 1]] - time[peaks[i]]))
        std = np.std(timediff)
        avg = sum(timediff) / len(timediff)
        return (avg, std)

    def t2pk(self, tencontracted, peaks, time):
        t2pk = []
        for i in range(len(tencontracted)):
            t2pk.append(time[peaks[i]] - tencontracted[i])
        std = np.std(t2pk)
        avg = sum(t2pk) / len(t2pk)
        return (avg, std)

    def t50(self, fiftycontract, fiftyrelax, time):
        t50 = []
        for i in range(len(fiftycontract)):
            t50.append(fiftyrelax[i] - fiftycontract[i])
        std = np.std(t50)
        avg = sum(t50) / len(t50)
        return (avg, std)

    def dfdt(self, tencontract, tencontracty, ninetycontract, ninetycontracty, time):
        dfdt = []
        for i in range(len(tencontract)):
            slope = (ninetycontracty[i] - tencontracty[i]
                     ) / (ninetycontract[i] - tencontract[i])
            dfdt.append(slope)
        std = np.std(dfdt)
        avg = sum(dfdt) / len(dfdt)
        return (avg, std)

    def c50(self, peaks, fiftypoints, time):
        c50 = []
        for i in range(len(fiftypoints)):
            timediff = time[peaks[i]] - fiftypoints[i]
            c50.append(timediff)
        std = np.std(c50)
        avg = sum(c50) / len(c50)
        return (avg, std)

    def r50(self, peaks, fiftyrelaxpoints, time):
        r50 = []
        for i in range(len(fiftyrelaxpoints)):
            timediff = fiftyrelaxpoints[i] - time[peaks[i]]
            r50.append(timediff)
        std = np.std(r50)
        avg = sum(r50) / len(r50)
        return (avg, std)

    def t2rel90(self, negtenpoints, peaks, time):
        t2rel90 = []
        for i in range(len(negtenpoints)):
            timediff = negtenpoints[i] - time[peaks[i]]
            t2rel90.append(timediff)
        std = np.std(t2rel90)
        avg = sum(t2rel90) / len(t2rel90)
        return (avg, std)
