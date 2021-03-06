#! /usr/bin/env python

"""
Author: John Stupak (jstupak@fnal.gov)
Date: 5-2-15
Usage: ./checkTest.py <test>
"""

from Comparison import *
from sys import argv
from config import *
from glob import glob

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

if len(argv)>1:
    testName=argv[1]
else:
    raise Exception("You must specify which test to check")

testFiles=[]
for module in moduleNames:
    print '/home/fnalpix2/ShareTestResults/'+module+'_ElComandanteTest_*/*_'+testName+'_*/commander_'+testName+'.root'
    testFiles.append(sorted(glob('/home/fnalpix2/ShareTestResults/'+module+'_ElComandanteTest_*/*_'+testName+'_*/commander_'+testName+'.root'))[-1])

"""
testFiles=['/Users/jstupak/CMS/pixel/ShareTestResults/M_LL_922_ElComandanteTest_2015-04-28_10h33m_1430235234/001_Pretest_p17/commander_Pretest.root',
'/Users/jstupak/CMS/pixel/ShareTestResults/M_TT_915_ElComandanteTest_2015-04-28_10h33m_1430235234/001_Pretest_p17/commander_Pretest.root',
'/Users/jstupak/CMS/pixel/ShareTestResults/P-A-03-42_ElComandanteTest_2015-04-28_10h33m_1430235234/001_Pretest_p17/commander_Pretest.root',
'/Users/jstupak/CMS/pixel/ShareTestResults/M_FR_902_ElComandanteTest_2015-04-16_15h24m_1429215874/001_Pretest_p17/commander_Pretest.root'
]
"""

referenceFile='/home/fnalpix2/ShareTestResults/M_TT_915_ElComandanteTest_2015-05-14_10h23m_1431617010/001_FPIXTest_p17/commander_FPIXTest.root'

outputDir='/home/fnalpix2/forExperts'

if testName=='Pretest':
    theComparisons=[Comparison('Pretest/programROC_V0','Pretest/programROC_V0',referenceFile,outputDir,'All y values should be greater than 0'),
                    Comparison('Pretest/Iana_V0','Pretest/Iana_V0',referenceFile,outputDir,'All y values should be approximately 24')]
    #theComparisons+=[Comparison('Pretest/pretestVthrCompCalDel_c12_r22_C'+str(i)+'_V0','Pretest/pretestVthrCompCalDel_c12_r22_C0_V0',referenceFile,outputDir) for i in range(16)]

if testName=='FPIXTest':
    theComparisons=[Comparison('Trim/dist_thr_TrimThrFinal_vcal_C'+str(i)+'_V0','Trim/dist_thr_TrimThrFinal_vcal_C0_V0',referenceFile,outputDir,'Distribution should be sharply peaked around 35') for i in range(16)]
    theComparisons+=[Comparison('Scurves/dist_thr_scurveVthrComp_VthrComp_C'+str(i)+'_V0','Scurves/dist_thr_scurveVthrComp_VthrComp_C0_V0',referenceFile,outputDir,'Distribution should be sharply peaked around 100') for i in range(16)]
    theComparisons+=[Comparison('Scurves/dist_thr_scurveVcal_Vcal_C'+str(i)+'_V0','Scurves/dist_thr_scurveVcal_Vcal_C0_V0',referenceFile,outputDir,'Distribution should be sharply peaked around 35') for i in range(16)]
    theComparisons+=[Comparison('Scurves/dist_sig_scurveVcal_Vcal_C'+str(i)+'_V0','Scurves/dist_sig_scurveVcal_Vcal_C0_V0',referenceFile,outputDir,'Distribution should peak above 2') for i in range(16)]
    #theComparisons+=[Comparison('PhOptimization/',referenceFile,outputDir,'') for i in range(16)]
    theComparisons+=[Comparison('GainPedestal/gainPedestalNonLinearity_C'+str(i)+'_V0','GainPedestal/gainPedestalNonLinearity_C0_V0',referenceFile,outputDir,'Distribution should be sharply peaked just below 1') for i in range(16)]
    theComparisons+=[Comparison('PixelAlive/PixelAlive_C'+str(i)+'_V0','PixelAlive/PixelAlive_C0_V0',referenceFile,outputDir,'Plot should be almost entirely red') for i in range(16)]
    theComparisons+=[Comparison('BumpBonding/dist_thr_calSMap_VthrComp_C'+str(i)+'_V0','BumpBonding/dist_thr_calSMap_VthrComp_C0_V0',referenceFile,outputDir,'Less than ~5% of the entries should be at larger x values than the arrow') for i in range(16)]
    

################################################################
################################################################
################################################################

if __name__=='__main__':

    results=[]
    i=0
    badModules=[]
    while i<len(theComparisons):
        result=theComparisons[i].do(testFiles)
        
        #go back one test
        if result==-1: i=max(i-1,0)

        if type(result)==type([]):
            try: results[i]=result
            except: results.append(result)
            i+=1

    badModules=set([])
    for result in results:
        badModules=badModules|set(result)
    badModules=list(badModules)
    if len(badModules)>0:
        print 'Replace the following module(s) and repeat pre-test:'
        for m in badModules:
            print '    - '+str(m)
    else:
        print 'Rock on'
        
