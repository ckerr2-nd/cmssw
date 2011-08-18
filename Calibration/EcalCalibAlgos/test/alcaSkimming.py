import FWCore.ParameterSet.Config as cms

#IMPORTANT PRESCAlE
#prescale = 1

process = cms.Process('ZCALIB')

#process.prescaler = cms.EDFilter("Prescaler",
#                                    prescaleFactor = cms.int32(prescale),
#                                    prescaleOffset = cms.int32(0)
#                                    )
# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
#process.load('Configuration.StandardSequences.GeometryDB_cff')
#process.load('Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff')
#process.load('Configuration.StandardSequences.RawToDigi_Data_cff')
#process.load('Configuration.StandardSequences.L1Reco_cff')
#process.load('Configuration.StandardSequences.Reconstruction_cff')
#process.load('Configuration.StandardSequences.EndOfProcess_cff')
#process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load('Configuration.EventContent.EventContent_cff')

process.MessageLogger.cerr.FwkReport.reportEvery = 1000

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(10000)
)

from Calibration.EcalCalibAlgos.DoubleElectron_Jul05_ALCAELECTRON_cff import *
#from Calibration.EcalCalibAlgos.Cert_160404_172802_cff import *

process.source = cms.Source("PoolSource",
                            fileNames = readFiles
)

#process.source.inputCommands = cms.untracked.vstring("drop *", "keep *_*_*_HLT")

process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True)
)

# Other statements
#process.GlobalTag.globaltag = 'GR_R_42_V17::All' 
#process.GlobalTag.toGet = cms.VPSet(
# cms.PSet(record = cms.string("EcalIntercalibConstantsRcd"),
#          tag = cms.string("EcalIntercalibConstants_v10_offline"),
#          connect = cms.untracked.string("frontier://FrontierProd/CMS_COND_31X_ECAL")
#         )
#  ,cms.PSet(record = cms.string("EcalADCToGeVConstantRcd"),
#          tag = cms.string("EcalADCToGeVConstant_v10_offline"),
#          connect = cms.untracked.string("frontier://FrontierProd/CMS_COND_31X_ECAL")
#         )
# ,cms.PSet(record = cms.string("EcalLaserAPDPNRatiosRcd"),
##           tag = cms.string("EcalLaserAPDPNRatios_2011fit_noVPT_nolim_online"),
#           tag = cms.string("EcalLaserAPDPNRatios_test_20110625"),
#           tag = cms.string("EcalLaserAPDPNRatios_2011V3_online"),
#           tag = cms.string("EcalLaserAPDPNRatios_2011mixfit_online"),
#          connect = cms.untracked.string("frontier://FrontierPrep/CMS_COND_ECAL")
#          )
 #beam spot to arrive to very last runs after 167151
#   ,cms.PSet(record = cms.string("BeamSpotObjectsRcd"),
#          tag = cms.string("BeamSpotObjects_PCL_byLumi_v0_prompt"),
#          connect = cms.untracked.string("frontier://PromptProd/CMS_COND_31X_BEAMSPOT")
#         )


HLTPath = "HLT_Ele"
HLTProcessName = "HLT"

#electron cuts
ELECTRON_ET_CUT_MIN = 20.0
ELECTRON_CUTS = "(abs(superCluster.eta)<2.5) && (ecalEnergy*sin(superClusterPosition.theta)>" + str(ELECTRON_ET_CUT_MIN) + ")"

#mass cuts (for T&P)
MASS_CUT_MIN = 60.

##    _____ _           _                     ___    _
##   | ____| | ___  ___| |_ _ __ ___  _ __   |_ _|__| |
##   |  _| | |/ _ \/ __| __| '__/ _ \| '_ \   | |/ _` |
##   | |___| |  __/ (__| |_| | | (_) | | | |  | | (_| |
##   |_____|_|\___|\___|\__|_|  \___/|_| |_| |___\__,_|
##

process.goodElectrons = cms.EDFilter("GsfElectronRefSelector",
                                 src = cms.InputTag( 'gsfElectrons' ),
                                 cut = cms.string( ELECTRON_CUTS )
                             )

process.PassingWP90 = process.goodElectrons.clone(
    cut = cms.string(
        process.goodElectrons.cut.value() +
            " && (gsfTrack.trackerExpectedHitsInner.numberOfHits<=1 && !(-0.02<convDist<0.02 && -0.02<convDcot<0.02))" #wrt std WP90 allowing 1 numberOfMissingExpectedHits
            " && (ecalEnergy*sin(superClusterPosition.theta)>" + str(ELECTRON_ET_CUT_MIN) + ")"
            " && ((isEB"
            " && ( dr03TkSumPt/p4.Pt <0.12 && dr03EcalRecHitSumEt/p4.Pt < 0.09 && dr03HcalTowerSumEt/p4.Pt  < 0.1 )"
            " && (sigmaIetaIeta<0.01)"
            " && ( -0.8<deltaPhiSuperClusterTrackAtVtx<0.8 )"
            " && ( -0.007<deltaEtaSuperClusterTrackAtVtx<0.007 )"
            " && (hadronicOverEm<0.12)"
            ")"
            " || (isEE"
            " && ( dr03TkSumPt/p4.Pt <0.07 && dr03EcalRecHitSumEt/p4.Pt < 0.07 && dr03HcalTowerSumEt/p4.Pt  < 0.07 )"
            " && (sigmaIetaIeta<0.03)"
            " && ( -0.7<deltaPhiSuperClusterTrackAtVtx<0.7 )"
            " && ( -0.009<deltaEtaSuperClusterTrackAtVtx<0.009 )"
            " && (hadronicOverEm<0.1) "
            "))"
            )
    )

process.Zele_sequence = cms.Sequence(
    process.goodElectrons * process.PassingWP90
    )


import copy
from HLTrigger.HLTfilters.hltHighLevel_cfi import *
process.ZEEHltFilter = copy.deepcopy(hltHighLevel)
process.ZEEHltFilter.throw = cms.bool(False)
process.ZEEHltFilter.HLTPaths = ["HLT_Ele*"]

##    ____       _
##   |  _ \ __ _(_)_ __ ___
##   | |_) / _` | | '__/ __|
##   |  __/ (_| | | |  \__ \
##   |_|   \__,_|_|_|  |___/
##
##

process.tagGsf =  cms.EDProducer("CandViewShallowCloneCombiner",
                                 decay = cms.string("PassingWP90 PassingWP90"),
                                 checkCharge = cms.bool(False),
                                 cut   = cms.string("mass > " + str(MASS_CUT_MIN))
            )
process.tagGsfCounter = cms.EDFilter("CandViewCountFilter",
                                     src = cms.InputTag("tagGsf"),
                                     minNumber = cms.uint32(1)
                                     )

process.tagGsfFilter = cms.Sequence(process.tagGsf * process.tagGsfCounter)
process.tagGsfSeq = cms.Sequence( process.ZEEHltFilter * (process.Zele_sequence) * process.tagGsfFilter )

process.zFilterPath = cms.Path( process.tagGsfSeq )

process.ALCARECOoutput = cms.OutputModule("PoolOutputModule",
                                          splitLevel = cms.untracked.int32(0),
#                                          outputCommands = cms.untracked.vstring('keep *'),
                                          outputCommands = process.OutALCARECOEcalCalElectron.outputCommands,
                                          fileName = cms.untracked.string('zSkim.root'),
                                          SelectEvents = cms.untracked.PSet(SelectEvents = cms.vstring('zFilterPath')),
                                          dataset = cms.untracked.PSet(
    filterName = cms.untracked.string(''),
    dataTier = cms.untracked.string('ALCARECO')
    )
                                          )
process.ALCARECOoutput_step = cms.EndPath(process.ALCARECOoutput)

process.schedule = cms.Schedule(process.zFilterPath,process.ALCARECOoutput_step)
