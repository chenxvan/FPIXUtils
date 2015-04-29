#! /usr/bin/env python

"""
Author: John Stupak (jstupak@fnal.gov)
Date: 4-9-15
Usage: python dbUpload.py <input dir>
"""

from xml.etree.ElementTree import Element, SubElement, Comment
from xml.etree import ElementTree
from xml.dom import minidom
SE=SubElement

import ROOT
ROOT.gErrorIgnoreLevel = ROOT.kWarning

from ROOT import *
gStyle.SetOptStat(0)

from glob import glob
import os
import subprocess
import sys
import zipfile

if len(sys.argv)<2:
    inputDir='/Users/jstupak/CMS/pixel/ShareTestResults/M_FR_902_ElComandanteTest_2015-04-16_15h24m_1429215874'
else:
    inputDir=sys.argv[1]

gROOT.SetBatch(1)

################################################################
################################################################
################################################################

def prettify(elem):
    roughString = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(roughString)
    return reparsed.toprettyxml(indent="  ")

#---------------------------------------------------------------

def attachName(parent):
    name=SE(parent,'NAME')
    name.text=moduleName

################################################################

def getProgramROCPlot(f, deadROCs, outputDir):
    h=f.Get('Pretest/programROC_V0')
    
    c=TCanvas()
    h.Draw()
    c.SaveAs(outputDir+'/programROC.png')

    pic=SE(top, 'PIC')
    attachName(pic)
    file=SE(pic, 'FILE')
    file.text='programROCs.png'
    txt=SE(pic, 'TXT')
    txt.text='programROC.txt'
    part=SE(pic,'PART')
    part.text='sidet_p'

    comment=open(outputDir+'/'+txt.text,'w')
    comment.write('deadROCs='+str(deadROCs))
    
    #to do:
    # -list of non-programmable ROCs needs to be searchable
    # -number of non-programmable ROCs needs to be searchable

#---------------------------------------------------------------

def getVthrCompCalDelPlot(f, VthrComps, CalDels, outputDir):
    
    c=TCanvas()
    for key in f.Get('Pretest').GetListOfKeys():
        if 'pretestVthrCompCalDel' in key.GetName():
            key.ReadObj().Draw('colz')
            c.SaveAs(outputDir+'/'+key.GetName()+'.png')

            pic=SE(top, 'PIC')
            attachName(pic)
            file=SE(pic, 'FILE')
            file.text=key.GetName()+'.png'
            txt=SE(pic, 'TXT')
            txt.text=key.GetName()+'.txt'
            part=SE(pic,'PART')
            part.text='sidet_p'

            comment=open(outputDir+'/'+txt.text,'w')
            n=int(key.GetName().split('_')[3][1:])
            comment.write('VthrComp='+str(VthrComps[n])+', CalDel='+str(CalDels[n]))

#---------------------------------------------------------------
    
def getVanaPlot(f, outputDir):
        
    h=f.Get('Pretest/VanaSettings_V0')
    c=TCanvas()
    h.Draw()
    c.SaveAs(outputDir+'/Vana.png')
    
    pic=SE(top,'PIC')
    attachName(pic)
    file=SE(pic,'FILE')
    file.text='Vana.png'
    part=SE(pic,'PART')
    part.text='sidet_p'
    
    Vana=[]
    for binNo in range(1,h.GetNbinsX()+1):
        V=int(h.GetBinContent(binNo))
        Vana.append(V)
    txt=SE(pic,'TXT')
    txt.text='Vana.txt'
    
    comment=open(outputDir+'/'+txt.text,'w')
    comment.write('Vana='+str(Vana))

#---------------------------------------------------------------

def getIanaPlot(f, outputDir):    

    h=f.Get('Pretest/Iana_V0')
    c=TCanvas()
    h.Draw()
    c.SaveAs(outputDir+'/Iana.png')

    pic=SE(top,'PIC')
    attachName(pic)
    file=SE(pic,'FILE')
    file.text='Iana.png'
    part=SE(pic,'PART')
    part.text='sidet_p'

    Iana=[]
    for binNo in range(1,h.GetNbinsX()+1):
        I=round(float(h.GetBinContent(binNo)),1)
        Iana.append(I)
    txt=SE(pic,'TXT')
    txt.text='Iana.txt'
    
    comment=open(outputDir+'/'+txt.text,'w')
    comment.write('Iana='+str(Iana))

#---------------------------------------------------------------

def getPixelAlivePlots(f, nDeadPixels, nMaskDefectPixels, nAddressDefectPixels, outputDir):

    c=TCanvas()
    for key in f.Get('PixelAlive').GetListOfKeys():
        if 'PixelAlive_C' in key.GetName():
            h=key.ReadObj()
            h.Draw('colz')
            c.SaveAs(outputDir+'/'+key.GetName()+'.png')
            n=int(key.GetName().split('_')[1][1:])

            deadPixels=[]
            for xBin in range(1,h.GetNbinsX()+1):
                for yBin in range(1,h.GetNbinsY()+1):
                    if h.GetBinContent(xBin, yBin)<1: deadPixels.append([xBin-1,yBin-1])

            if len(deadPixels)!=nDeadPixels[n]:
                print 'ERROR: Wrong number of dead pixels found'
                print '       From pXar log:', nDeadPixels[n]
                print '       From root file:',len(deadPixels)
                exit()

            pic=SE(top, 'PIC')
            attachName(pic)
            file=SE(pic, 'FILE')
            file.text=key.GetName()+'.png'
            txt=SE(pic, 'TXT')
            txt.text=key.GetName()+'.txt'
            part=SE(pic,'PART')
            part.text='sidet_p'

            comment=open(outputDir+'/'+txt.text,'w')
            comment.write('nDeadPixels='+str(nDeadPixels[n])+'\n')
            comment.write('deadPixels=[')
            for i in range(len(deadPixels)):
                x,y=deadPixels[i][0],deadPixels[i][1]
                comment.write('['+str(x)+','+str(y)+']')
                if i!=len(deadPixels)-1: comment.write(', ')
            comment.write(']')

        # - - - - - - - - - - - - - - - - - - - - - - - - -

        if 'MaskTest_C' in key.GetName():
            key.ReadObj().Draw('colz')
            c.SaveAs(outputDir+'/'+key.GetName()+'.png')
            n=int(key.GetName().split('_')[1][1:])

            maskDefectPixels=[]
            for xBin in range(1,h.GetNbinsX()+1):
                for yBin in range(1,h.GetNbinsY()+1):
                    if h.GetBinContent(xBin, yBin)<1: maskDefectPixels.append([xBin-1,yBin-1])

            if len(maskDefectPixels)!=nMaskDefectPixels[n]:
                print 'ERROR: Wrong number of un-maskable pixels found'
                print '       From pXar log:', nMaskDefectPixels[n]
                print '       From root file:',len(maskDefectPixels)
                exit()

            pic=SE(top, 'PIC')
            attachName(pic)
            file=SE(pic, 'FILE')
            file.text=key.GetName()+'.png'
            txt=SE(pic, 'TXT')
            txt.text=key.GetName()+'.txt'
            part=SE(pic,'PART')
            part.text='sidet_p'

            comment=open(outputDir+'/'+txt.text,'w')
            comment.write('nUnmaskable='+str(nMaskDefectPixels[n])+'\n')
            comment.write('unmaskablePixels=[')
            for i in range(len(maskDefectPixels)):
                x,y=maskDefectPixels[i][0],maskDefectPixels[i][1]
                comment.write('['+str(x)+','+str(y)+']')
                if i!=len(maskDefectPixels)-1: comment.write(', ')
            comment.write(']')

        # - - - - - - - - - - - - - - - - - - - - - - - - -   

        if 'AddressDecodingTest_C' in key.GetName():
            key.ReadObj().Draw('colz')
            c.SaveAs(outputDir+'/'+key.GetName()+'.png')
            n=int(key.GetName().split('_')[1][1:])

            addressDefectPixels=[]
            for xBin in range(1,h.GetNbinsX()+1):
                for yBin in range(1,h.GetNbinsY()+1):
                    if h.GetBinContent(xBin, yBin)<1: addressDefectPixels.append([xBin-1,yBin-1])

            if len(addressDefectPixels)!=nAddressDefectPixels[n]:
                print 'ERROR: Wrong number of un-addressable pixels found'
                print '       From pXar log:', nAddressDefectPixels[n]
                print '       From root file:',len(addressDefectPixels)
                exit()

            pic=SE(top, 'PIC')
            attachName(pic)
            file=SE(pic, 'FILE')
            file.text=key.GetName()+'.png'
            txt=SE(pic, 'TXT')
            txt.text=key.GetName()+'.txt'
            part=SE(pic,'PART')
            part.text='sidet_p'

            comment=open(outputDir+'/'+txt.text,'w')
            comment.write('nUnadressable='+str(nAddressDefectPixels[n])+'\n')
            comment.write('unaddressablePixels=[')
            for i in range(len(addressDefectPixels)):
                x,y=addressDefectPixels[i][0],addressDefectPixels[i][1]
                comment.write('['+str(x)+','+str(y)+']')
                if i!=len(addressDefectPixels)-1: comment.write(', ')
            comment.write(']')

#---------------------------------------------------------------

def getBumpBondingPlots(f, badBumpsPreTrim, badBumpsPostTrim, bbCutPreTrim, bbCutPostTrim, outputDir):

    c=TCanvas()
    for key in f.Get('BumpBonding').GetListOfKeys():

        if 'dist_thr_calSMap_VthrComp_C' in key.GetName():
            key.ReadObj().Draw()
            c.SaveAs(outputDir+'/'+key.GetName()+'.png')

            pic=SE(top, 'PIC')
            attachName(pic)
            file=SE(pic, 'FILE')
            file.text=key.GetName()+'.png'
            part=SE(pic,'PART')
            part.text='sidet_p'

        # - - - - - - - - - - - - - - - - - - - - - - - - -
        
        elif 'thr_calSMap_VthrComp_C' in key.GetName():
            h=key.ReadObj()
            h.Draw('colz')
            c.SaveAs(outputDir+'/'+key.GetName()+'.png')
            n=int(key.GetName().split('_')[3][1:])
            print n, len(bbCutPreTrim), len(bbCutPostTrim)
                        
            if 'V0' in key.GetName(): preTrim=True
            elif 'V1' in key.GetName(): preTrim=False
            else:
                print 'ERROR: Unexpected bump bonding results'
                exit()

            badBumps=[]
            for xBin in range(1, h.GetNbinsX()+1):
                for yBin in range(1, h.GetNbinsY()+1):
                    if h.GetBinContent(xBin,yBin)+1>=(preTrim*bbCutPreTrim[n])+((not preTrim)*bbCutPostTrim[n]):
                        badBumps.append([xBin-1,yBin-1])

            if len(badBumps)!=(preTrim*badBumpsPreTrim[n])+((not preTrim)*badBumpsPostTrim[n]):
                print 'ERROR: Wrong number of bad bump bonds found'
                print '       From pXar log:', (preTrim*badBumpsPreTrim[n])+((not preTrim)*badBumpsPostTrim[n])
                print '       From root file:',len(badBumps)
                exit()                        

            pic=SE(top, 'PIC')
            attachName(pic)
            file=SE(pic, 'FILE')
            file.text=key.GetName()+'.png'
            txt=SE(pic, 'TXT')
            txt.text=key.GetName()+'.txt'
            part=SE(pic,'PART')
            part.text='sidet_p'

            comment=open(outputDir+'/'+txt.text,'w')
            n=int(key.GetName().split('_')[3][1:])
            if preTrim: comment.write('nBadBumpsPreTrim='+str(badBumpsPreTrim[n])+'\n')
            else:       comment.write('nBadBumpsPostTrim='+str(badBumpsPostTrim[n])+'\n')
            comment.write('badBumps=[')
            for i in range(len(badBumps)):
                x,y=badBumps[i][0],badBumps[i][1]
                comment.write('['+str(x)+','+str(y)+']')
                if i!=len(badBumps)-1: comment.write(', ')
            comment.write(']')


#---------------------------------------------------------------

def getSCurvePlots(f, outputDir):
    
    goodPlots=['adjustVcal_C',
               'thr_scurveVthrComp_VthrComp_C','sig_scurveVthrComp_VthrComp_C','thn_scurveVthrComp_VthrComp_C',
               'dist_thr_scurveVthrComp_VthrComp_C','dist_sig_scurveVthrComp_VthrComp_C','dist_thn_scurveVthrComp_VthrComp_C',
               'thr_scurveVcal_Vcal_C','sig_scurveVcal_Vcal_C',
               'dist_thr_scurveVcal_Vcal_C','dist_sig_scurveVcal_Vcal_C']

    c=TCanvas()
    for key in f.Get('Scurves').GetListOfKeys():
        for plot in goodPlots:
            if plot in key.GetName():
                if 'dist' in key.GetName(): key.ReadObj().Draw()
                else: key.ReadObj().Draw('COLZ')
                c.SaveAs(outputDir+'/'+key.GetName()+'.png')
                
                pic=SE(top, 'PIC')
                attachName(pic)
                file=SE(pic, 'FILE')
                file.text=key.GetName()+'.png'
                part=SE(pic,'PART')
                part.text='sidet_p'

#---------------------------------------------------------------

def getTrimPlots(f, outputDir):
    
    goodPlots=['TrimMap_C','dist_TrimMap_C',
               'thr_TrimThrFinal_vcal_C','dist_thr_TrimThrFinal_vcal_C']

    c=TCanvas()
    for key in f.Get('Trim').GetListOfKeys():
        for plot in goodPlots:
            if plot in key.GetName():
                if 'dist' in key.GetName(): key.ReadObj().Draw()
                else: key.ReadObj().Draw('COLZ')
                c.SaveAs(outputDir+'/'+key.GetName()+'.png')

                pic=SE(top, 'PIC')
                attachName(pic)
                file=SE(pic, 'FILE')
                file.text=key.GetName()+'.png'
                part=SE(pic,'PART')
                part.text='sidet_p'

#---------------------------------------------------------------

def getPulseHeightOptPlots(f, outputDir):

    goodPlots=['PH_mapHiVcal_C','dist_PH_mapHiVcal_C',
               'PH_mapLowVcal_C','dist_PH_mapLowVcal_C']

    c=TCanvas()
    for key in f.Get('PhOptimization').GetListOfKeys():
        for plot in goodPlots:
            if plot in key.GetName():
                if 'dist' in key.GetName(): key.ReadObj().Draw()
                else: key.ReadObj().Draw('COLZ')
                c.SaveAs(outputDir+'/'+key.GetName()+'.png')

                pic=SE(top, 'PIC')
                attachName(pic)
                file=SE(pic, 'FILE')
                file.text=key.GetName()+'.png'
                part=SE(pic,'PART')
                part.text='sidet_p'

#---------------------------------------------------------------

def getGainPedestalPlots(f,outputDir):

    goodPlots=['gainPedestalP1_C']

    c=TCanvas()
    for key in f.Get('GainPedestal').GetListOfKeys():
        for plot in goodPlots:
            if plot in key.GetName():
                if 'dist' in key.GetName(): key.ReadObj().Draw()
                else: key.ReadObj().Draw('COLZ')
                c.SaveAs(outputDir+'/'+key.GetName()+'.png')

                pic=SE(top, 'PIC')
                attachName(pic)
                file=SE(pic, 'FILE')
                file.text=key.GetName()+'.png'
                part=SE(pic,'PART')
                part.text='sidet_p'

################################################################

def analyzePreTest(inputDir, outputDir, log, data):
    log=log['pretest']
    data=TFile(data['pretest'])

    f=iter(open(log,'r'))
    for line in f:

        if 'No good timings found' in line: canTime=False
        elif 'Default timings are good' in line or 'Good Timings Found' in line: canTime=True

        if 'ROCs are all programmable' in line: deadROCs=[]
        elif 'cannot be programmed! Error' in line: deadROCs=[int(i) for i in line[line.find('ROCs')+len('ROCs'):line.find('cannot')].split()]
    
        if 'PixTestPretest::setVthrCompCalDel() done' in line:
            line=next(f)
            calDels=[int(i) for i in line.split('CalDel:')[1].split()]
            line=next(f)
            VthrComps=[int(i) for i in line.split('VthrComp:')[1].split()]
            
    ct=SE(test,'CAN_TIME')
    ct.text=str(int(canTime))

    getProgramROCPlot(data, deadROCs, outputDir)
    getVanaPlot(data, outputDir)
    getIanaPlot(data, outputDir)
    getVthrCompCalDelPlot(data, calDels, VthrComps, outputDir)

    dr=SE(test,'DEAD_ROCS')
    for n in deadROCs: SE(dr,'ROC').text=str(n)
    
    lr=SE(test,'LIVE_ROCS')
    for n in range(16): 
        if n not in deadROCs: SE(lr,'ROC').text=str(n)
        
################################################################

def analyzeIV(inputDir, outputDir, log, data):
    inputName=glob(inputDir+'/*_IV_p*/ivCurve.log')[0]
    input=open(inputName, 'r')
    outputName=outputDir+'/'+moduleName+'_IV.xml'
    output=open(outputName,'w')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #scan header
    
    t=Element('ROOT')
    t.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')

    header=SE(t,'HEADER')
    type=SE(header,'TYPE')

    extension_table_name=SE(type,'EXTENSION_TABLE_NAME')
    extension_table_name.text='PH1_FPIX_ASSEMBLED_IV'
    name=SE(type,'NAME')
    name.text='Ph1 FNAL assembled module IV Test Data'

    run=SE(header,'RUN')
    run_name=SE(run,'RUN_NAME')
    run_name.text='Ph1 FNAL assembled module '+moduleName+' IV'

    run_begin_timestamp=SE(run,'RUN_BEGIN_TIMESTAMP')

    for line in input:
        if 'LOG from' in line:
            run_begin_timestamp.text=' '.join(line.split()[2:-1])
            break

    location=SE(run,'LOCATION')
    location.text='FNAL'
    comment_description=SE(run,'COMMENT_DESCRIPTION')
    comment_description.text=run_name.text

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #scan data

    data_set=SE(t,'DATA_SET')
    part=SE(data_set,'PART')
    serial_number=SE(part,'SERIAL_NUMBER')
    serial_number.text=moduleName
    kind_of_part=SE(part,'KIND_OF_PART')
    kind_of_part.text='Ph1 FPix 2x8 Sensor'

    values=[]
    for line in input:
        if line[0]=='#': continue
        data=SE(data_set,'DATA')
        voltage_volt=SE(data,'VOLTAGE_VOLT')
        voltage_volt.text=str(abs(float(line.split()[0])))
        tot_current_amp=SE(data,'TOT_CURRENT_AMP')
        tot_current_amp.text=str(abs(float(line.split()[1])))

        values.append([abs(float(line.split()[0])),float(line.split()[1])])

    output.write(prettify(t))
    output.close()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #main xml content

    scan=SE(top,'SCAN')
    attachName(scan)
    level=SE(scan,'LEVEL')
    level.text='ASSEMBLED'
    type=SE(scan,'TYPE')
    type.text='IV'
    file=SE(scan,'FILE')
    file.text=os.path.basename(outputName)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #until DB has field, upload the png
    
    nBins=len(values)
    xMin=values[0][0]
    xMax=values[-1][0]
    binWidth=float(xMax-xMin)/(nBins-1)
    xMin-=binWidth/2
    xMax+=binWidth/2

    h=TH1F('IV',';-U [V];-I [#muA]',nBins,xMin,xMax)
    for i in range(len(values)): h.SetBinContent(i+1, -1*values[i][1])
    h.SetMaximum(5*h.GetMaximum())

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    b=getBreakdown(h)
    breakdown=SE(scan,'BREAKDOWN')
    breakdown.text=str(int(round(b,0)))
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
    c=TCanvas()
    c.SetLogy()
    h.Draw()
    l=TLine(b,h.GetYaxis().GetXmin(),b,h.GetMaximum())
    l.Draw('same')
    c.SaveAs(outputName.replace('xml','png'))

    pic=SE(top,'PIC')
    attachName(pic)
    file=SE(pic,'FILE')
    file.text=os.path.basename(outputName.replace('xml','png'))
    txt=SE(pic,'TXT')
    txt.text=os.path.basename(outputName).replace('xml','txt')
    part=SE(pic,'PART')
    part.text='sidet_p'
    comment=open(outputDir+'/'+txt.text,'w')
    comment.write('IV scan')

    #to do:
    # -V(100uA)

#---------------------------------------------------------------

def getBreakdown(h):
    tolerance=1./10000
    width=max(1,int(round(25./h.GetBinWidth(1),0)))
    
    
    h0=h.Clone('h0')

    lastFilledBin=0
    for binNo in range(h0.GetNbinsX()+1):
        if h0.GetBinContent(binNo)>0: lastFilledBin=binNo
        
        if h0.GetBinContent(binNo)<=0: h0.SetBinContent(binNo,0)
        else: h0.SetBinContent(binNo,log10(h0.GetBinContent(binNo)))
        
    h1=h0.Clone('h1')
    h1.Reset()
    for binNo in range(width+1,lastFilledBin-width):
        h1.SetBinContent(binNo,(h0.GetBinContent(binNo+width)-h0.GetBinContent(binNo-width))/(2*width*h0.GetBinWidth(binNo)))

    h2=h1.Clone('h2')
    h2.Reset()
    for binNo in range(width+2,lastFilledBin-width):
        h2.SetBinContent(binNo,(h1.GetBinContent(binNo+1)-h1.GetBinContent(binNo-1))/(2*h0.GetBinWidth(binNo)))

    depletion=0
    breakdown=0

    firstBin=0
    lastBin=0
    for binNo in range(width+2,lastFilledBin-width):
        if abs(h2.GetBinContent(binNo))<tolerance:
            if not firstBin:
                if h0.GetBinCenter(binNo)<200:
                    firstBin=binNo
            else:            lastBin =binNo
        elif firstBin:
            if lastBin-firstBin>breakdown-depletion:
                depletion=firstBin
                breakdown=lastBin
            firstBin=0
            lastBin=0
    depletion-=width-1
    breakdown+=width+1

    return h0.GetBinCenter(breakdown)

#---------------------------------------------------------------

def analyzeFullTest(inputDir, outputDir, log, data):

    log=log['fulltest']
    data=TFile(data['fulltest'])

    badBumpsPreTrim=[]
    badBumpsPostTrim=[]

    bbCutPreTrim=[]
    bbCutPostTrim=[]

    f=iter(open(log,'r'))
    for line in f:

        if 'number of dead pixels (per ROC)' in line:
            deadPixels=[int(x) for x in line.split()[-16:]]

        if 'number of mask-defect pixels (per ROC)' in line:
            maskDefectPixels=[int(x) for x in line.split()[-16:]]

        if 'number of address-decoding pixels (per ROC)' in line:
            addressDefectPixels=[int(x) for x in line.split()[-16:]]

        if 'number of dead bumps (per ROC)' in line:
            badBumps=[int(x) for x in line.split()[-16:]]
            if not badBumpsPreTrim: badBumpsPreTrim=badBumps
            else: badBumpsPostTrim=badBumps
            
        if 'separation cut       (per ROC):' in line:
            if not bbCutPreTrim: bbCutPreTrim=[int(x) for x in line.split()[-16:]]
            else: bbCutPostTrim=[int(x) for x in line.split()[-16:]]
    
    n=0
    for i in deadPixels: n+=i
    dead_pix=SE(test,'DEAD_PIX')
    dead_pix.text=str(n)

    n=0
    for i in badBumpsPostTrim: n+=i
    dead_bumps_elec=SE(test,'DEAD_BUMPS_ELEC')
    dead_bumps_elec.text=str(n)

    getPixelAlivePlots(data, deadPixels, maskDefectPixels, addressDefectPixels, outputDir)
    getBumpBondingPlots(data, badBumpsPreTrim, badBumpsPostTrim, bbCutPreTrim, bbCutPostTrim, outputDir)
    getSCurvePlots(data,outputDir)
    getTrimPlots(data,outputDir)
    getPulseHeightOptPlots(data,outputDir)
    getGainPedestalPlots(data,outputDir)
    
#---------------------------------------------------------------

def getConfigs(inputDir, outputDir, log, data):
    for config in ['configParameters.dat', 
                   'tbParameters.dat', 
                   'tbmParameters_C*a.dat','tbmParameters_C*b.dat', 
                   'testParameters.dat', 
                   'testPatterns.dat', 
                   'defaultMaskFile.dat', 
                   'SCurveData_C*.dat', 
                   'trimParameters35_C*.dat', 
                   'phCalibration_C*.dat', 
                   'phCalibrationFitErr35_C*.dat', 
                   'dacParameters_C*.dat']:

        if len(glob(inputDir+'/*_Fulltest_p*/'+config))==0: 
            print 'ERROR: no config files found:', config
            #exit()

        for file in glob(inputDir+'/*_Fulltest_p*/'+config):
            subprocess.call(['cp', file, outputDir])
            
            c=SE(top,'CONFIG')

            attachName(c)
            f=SE(c,'FILE')
            f.text=os.path.basename(file)

################################################################

def makeXML(inputDir):
    
    global moduleName
    moduleName='_'.join(inputDir.split('/')[-1].split('_')[:3])

    outputDir=moduleName
    if os.path.exists(outputDir):
        print 'WARNING: outputDir exists'
        #exit()
    else:
        os.makedirs(outputDir)

    log={}
    data={}
    
    log['pretest']=inputDir+'/*_Pretest_p*/commander_Pretest.log'
    data['pretest']=log['pretest'].replace('.log','.root')
    
    log['fulltest']=log['pretest'].replace('Pretest','Fulltest')
    data['fulltest']=log['fulltest'].replace('.log','.root')
    
    log['iv']=inputDir+'/*_IV_p*/ivCurve.log' #log['pretest'].replace('Pretest','IV')
    #data['iv']=log['iv'].replace('.log','.root')
    
    for key in log.keys():
        try:
            log[key]=glob(log[key])[0]
            if key!='iv': data[key]=glob(data[key])[0]
        except:
            print 'Missing log:',key
            print

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    global top
    top=Element('ROOT')
    top.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')

    global test
    test=SE(top,'TEST')
    attachName(test)

    for f in [analyzeIV,
              analyzePreTest,
              analyzeFullTest,
              getConfigs,
              ]:
        f(inputDir, outputDir, log, data)
    
    output=open(outputDir+'/master.xml','w')
    output.write(prettify(top))
    output.close()

    #print
    #print prettify(top)
    #print

    os.chdir(outputDir)
    zip=zipfile.ZipFile('../'+moduleName+'.zip', mode='w')
    for file in glob('*'):
        zip.write(file)
    zip.close()

################################################################
################################################################
################################################################

if __name__=='__main__':
    xml=makeXML(inputDir)