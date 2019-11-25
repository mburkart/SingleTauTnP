
import logging
import argparse

import ROOT as root

from utils import roohist_to_th1d


def parse_arguments():
    parser = argparse.ArgumentParser(
            description="Script to extract efficiency histograms and"
                        " uncertainties, respectively corrections.")
    parser.add_argument("-i", "--input", type=str, required=True,
                        help="Input root file.")
    parser.add_argument("-o", "--output", type=str, required=True,
                        help="Output root file.")
    parser.add_argument("-w", "--working-points", type=str, nargs="*", default=["tight"],
                        help="Working points the efficiencies should be computed for.")
    parser.add_argument("--mva", action="store_true",
                        help="Use MVA Tau ID algorithm.")
    args = parser.parse_args()
    return args


def setup_logging(lev):
    logging.basicConfig(level=lev)
    return


def write_SFs(dms, tau_cats, outfile, infile, wps, mva=False):
    logging.info("Calculate SF histograms and write them to %s.",
                 outfile.GetName())
    if mva:
        skeleton = "graph_{}MVAv2_{}_{}"
    else:
        skeleton = "graph_{}DeepTau_{}_{}"
    data_names = (skeleton.format(wp, dm, tau) + "_DATA"
                  for wp in wps for tau in tau_cats for dm in dms)
    mc_names = (skeleton.format(wp, dm, tau) + "_MC"
                for wp in wps for tau in tau_cats for dm in dms)
    for data, mc in zip(data_names, mc_names):
        # Get histograms from infile.
        data_hist = roohist_to_th1d(data, infile)
        print data_hist.GetName()
        print "Calculating scale factor for hist %s." % data_hist.GetName()
        mc_hist = roohist_to_th1d(mc, infile)
        print "Number of data bins: %i." % data_hist.GetNbinsX()
        print "Number of mc bins: %i." % mc_hist.GetNbinsX()
        sf_hist = root.TH1D(data_hist)
        sf_hist.Divide(data_hist, mc_hist, 1., 1., "mode b(1,1) cl=0.638")
        sf_hist.SetTitle("SF_{spec[1]}_{spec[2]}_{spec[3]}".format(spec=data.split("_")))
        sf_hist.SetName("SF_{spec[1]}_{spec[2]}_{spec[3]}".format(spec=data.split("_")))
        sf_hist.Write()
        data_graph = infile.Get(data)
        mc_graph = infile.Get(mc)
        sf_graph = create_sf_graph(data_graph, mc_graph)
        sf_graph.Write()
    return


def create_sf_graph(data, mc):
    """Create scale factors with updated uncertainties.

    Use one sigma uncertainties and propagate to the resulting graph.
    """
    sf_graph = root.TGraphAsymmErrors(data)
    sf_graph.SetName("SF_Graph_{split[1]}_{split[2]}_{split[3]}".format(
            split=data.GetName().split("_")))
    sf_graph.SetTitle(sf_graph.GetName())
    for i, x in enumerate(data.GetX()):
        try:
            sf_graph.SetPoint(i, x, data.GetY()[i]/mc.GetY()[i])
        except ZeroDivisionError:
            logging.warning("Zero division encountered while calculating "
                            "scale factor for bin at %.1f. Setting SF to 1.",
                            x)
            sf_graph.SetPoint(i, x, 1.)
        data_up = data.GetY()[i] + data.GetErrorYhigh(i)
        data_down = data.GetY()[i] - data.GetErrorYlow(i)
        mc_up = mc.GetY()[i] + mc.GetErrorYhigh(i)
        if mc_up == 0.:
            mc_up = 1.
            logging.warning("Up uncertainty for hist %s is zero."
                            " Setting to 1.",
                            sf_graph.GetName())
        mc_down = mc.GetY()[i] - mc.GetErrorYlow(i)
        if mc_down == 0.:
            mc_down = 1.
            logging.warning("MC value and uncertainty are zero."
                            " Setting down shift to one.")
        sf_graph.SetPointEYhigh(i, data_up/mc_down - data.GetY()[i])
        sf_graph.SetPointEYlow(i, sf_graph.GetY()[i] - data_down/mc_up)
    return sf_graph


def write_Effs(dms, tau_kinds, file_kinds, outfile, infile, wps, mva=False):
    logging.info("Retrieve histograms from %s and write them to %s.",
                 infile.GetName(), outfile.GetName())
    if mva:
        histnames = ("graph_{}MVAv2_{}_{}_{}".format(wp, dm, tau, fi)
                     for wp in wps for fi in file_kinds for tau in tau_kinds for dm in dms
                     if not (fi == "DATA" and tau == "genTau"))
    else:
        histnames = ("graph_{}DeepTau_{}_{}_{}".format(wp, dm, tau, fi)
                     for wp in wps for fi in file_kinds for tau in tau_kinds for dm in dms
                     if not (fi == "DATA" and tau == "genTau"))
    for name in histnames:
        logging.info("Looking for histogam %s" % name)
        histo = roohist_to_th1d(name, infile)
        histo.Write()
    return


def main(args):
    root.gROOT.SetBatch()
    eff_infile = root.TFile(args.input, "read")
    outfile = root.TFile(args.output, "recreate")
    # "inclusiveDM" not yet working because of issues calculating the
    # error for the mc turnon in one bin
    if args.mva:
        dms = ["dm0", "dm1", "dm10"]
    else:
        dms = ["dm0", "dm1", "dm10", "dm11"]
    # dms = ["dm11"]
    # taus = ["jetFakes"]
    taus = ["eFakes", "jetFakes", "genTau"]
    filetypes = ["DATA", "MC"]
    write_Effs(dms, taus, filetypes, outfile, eff_infile, args.working_points, args.mva)
    taus.pop()
    write_SFs(dms, taus, outfile, eff_infile, args.working_points, args.mva)
    return


if __name__ == "__main__":
    setup_logging(logging.INFO)
    args = parse_arguments()
    main(args)
