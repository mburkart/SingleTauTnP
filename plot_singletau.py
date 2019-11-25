#!/usr/bin/env python
import yaml
import argparse


import ROOT

import utils.TurnOnPlot_DATA as TurnOnPlot

ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gErrorIgnoreLevel = ROOT.kError
ROOT.gROOT.SetBatch()


decayModes = ["dm0", "dm1", "dm10", "dm11"]
dm_dict = {"dmCmb": "#bf{CMS} #it{Preliminary}",
           "dm0": "1 prong",
           "dm1": "1 prong + #pi^{0}'s",
           "dm10": "3 prong",
           "dm11": "3 prong + #pi^{0}"}

# ROOT FILE CONTAINING THE DATA
col_dict = {
    "tRed"     : ROOT.TColor(3001, 1., 0., 0., "tRed"     , 0.35),  # noqa E203
    "tGreen"   : ROOT.TColor(3002, 0., 1., 0., "tGreen"   , 0.35),  # noqa E203
    "tBlue"    : ROOT.TColor(3003, 0., 0., 1., "tBlue"    , 0.35),  # noqa E203
    "tMagenta" : ROOT.TColor(3004, 1., 0., 1., "tMagenta" , 0.35),  # noqa E203
    "tCyan"    : ROOT.TColor(3005, 0., 1., 1., "tCyan"    , 0.35),  # noqa E203
    "tYellow"  : ROOT.TColor(3006, 1., 1., 0., "tYellow"  , 0.35),  # noqa E203
    "tOrange"  : ROOT.TColor(3007, 1., .5, 0., "tOrange"  , 0.35),  # noqa E203
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str,
                        help="Input file containing the histograms.")
    parser.add_argument("-e", "--era", type=str,
                        help="Era.")
    parser.add_argument("-w", "--working-point", type=str,
                        help="TauID working point.")
    parser.add_argument("--mva", action="store_true",
                        help="Use efficiencies based on MVA Tau ID algorithm.")
    return parser.parse_args()


def main(args):

    yml_dict = yaml.load(open("configs/singletau_plot_config.yaml", "r"))
    plot_dict = yml_dict["plots"]
    if not args.mva:
        for sub_dict in plot_dict.itervalues():
           sub_dict["Name"] = sub_dict["Name"].replace("MVAv2", "DeepTau")

    infile = ROOT.TFile.Open(args.input, "read")

    plots = []
    for plot in plot_dict.itervalues():
        plot["FillColor"] = col_dict[plot["FillColor"]]

    for dm in decayModes:
        turnons = []
        for plot in sorted(plot_dict.keys()):
            if dm == "dm0" and "jetFakes" in plot_dict[plot]["Name"]:
                continue
            if ((dm == "dm1" or dm == "dm10" or dm == "dm11")
                    and "eFakes" in plot_dict[plot]["Name"]):
                continue
            print "graph_" + plot_dict[plot]["Name"].format(
                    dm=dm, wp=args.working_point)
            plot_dict[plot]["Histo"] = infile.Get(
                    "graph_" + plot_dict[plot]["Name"].format(
                        dm=dm, wp=args.working_point))
            print plot_dict[plot]["Histo"]
            plot_dict[plot]["Histo"].__class__ = ROOT.RooHist
            plot_dict[plot]["Fit"] = ROOT.RooCurve()
            plot_dict[plot]["Fit"].__class__ = ROOT.RooCurve
            turnons.append(TurnOnPlot.TurnOn(**plot_dict[plot]))
        plots.append(TurnOnPlot.TurnOnPlot(TriggerName=dm + "genuine fake",
                     cms=dm_dict[dm]))
        plots[-1].name = "_".join([args.era, args.working_point, dm])
        plots[-1].xRange = yml_dict[args.era]["x_range"]
        # plots[-1].legendPosition = (0.6,0.2,0.9,0.4)
        plots[-1].legendPosition = (0.44, 0.15, 0.94, 0.33)
        plots[-1].lumi = yml_dict[args.era]["lumi"]
        plots[-1].numLegCols = 1
        plots[-1].year = args.era
        for turnon in turnons:
            plots[-1].addTurnOn(turnon)

    infile.Close()

    canvas = []
    for plot in plots:
        canvas.append(plot.plot())
    return


if __name__ == "__main__":
    args = parse_args()
    main(args)
