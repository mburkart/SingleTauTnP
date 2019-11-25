from array import array
import logging
import math

import ROOT as root

logger = logging.getLogger(__name__)


def roohist_to_th1d(roohistname, fileobject):
    """Convert RooHist to TH1D object.

    Taken from workspaceTools.py script.
    """
    roohist = fileobject.Get(roohistname)
    # Get array of bin centers and bin widths.
    nbins = roohist.GetN()
    bin_edges = []
    for i in xrange(0, nbins):
        bin_edges.append(roohist.GetX()[i] - roohist.GetEXlow()[i])
    bin_edges.append(roohist.GetX()[i] + roohist.GetEXhigh()[i])
    # Create empty histogram.
    th1f = root.TH1D(roohist.GetName(), roohist.GetTitle(),
                     nbins, array("d", bin_edges))
    # Get and set bin contents according to RooHists bin contents
    for i in xrange(1, nbins+1):
        logger.debug("Content of bin number %s is %s.", i, roohist.GetY()[i-1])
        th1f.SetBinContent(i, roohist.GetY()[i-1]
                           if not math.isnan(roohist.GetY()[i-1]) else 0.)
        logger.debug("Uncertainty of bin number %s is %s.", i,
                     (roohist.GetEYhigh()[i-1] + roohist.GetEYlow()[i-1])/2.)
        th1f.SetBinError(
                i, (roohist.GetEYhigh()[i-1] + roohist.GetEYlow()[i-1])/2.
                if not math.isnan(roohist.GetY()[i-1]) else 0.)
    return th1f


def test():
    fi = root.TFile.Open("fitOutput_VBFTrigger_JetMeasurement.root")
    hist = roohist_to_th1d(
            "histo_MC_HLT_VBF_DoubleLooseChargedIsoPFTau20_eta2p1_Reg_v_leadJetPt",  # noqa: E501
            fi)
    return hist


if __name__ == "__main__":
    test()
