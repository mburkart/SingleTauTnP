#!/usr/bin/env python
import argparse
import re

import ROOT as root


# graph_tightMVAv2_dm1_genTau_MC -> singletau_$WPMVAv2_dm1_MC
# graph_tightMVAv2_dm1_genTau_DATA -> singletau_tightMVAv2_dm1_DATA
# graph_tightMVAv2_dm1_genTau_upShift -> singletau_tightMVAv2_dm1_DATA_errorBand
# graph_tightMVAv2_dm1_genTau_downShift -> singletau_tightMVAv2_dm1_DATA_errorBand


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", dest="in_filename",
                        help="Input root file")
    parser.add_argument("-o", "--output",
                        help="Output root file")
    parser.add_argument("--mva", action="store_true",
                        help="Use MVA Tau ID algorithm.")
    return parser.parse_args()


def get_matches(to_match, expression):
    prog = re.compile(expression)
    matches = filter(lambda x: prog.match(x) is not None, to_match)
    return matches


def copy_histogram(key, infile):
    hist = infile.Get(key)
    new_key = key.replace("graph", "singletau") \
                 .replace("genTau_", "") \
                 .replace("upShift", "Up") \
                 .replace("downShift", "Down")
    hist.SetName(new_key)
    hist.SetTitle(new_key)
    hist.Write()
    return


# def build_histogram(key, in_file):
#     hist = in_file.Get(key)
#     new_key = key.replace("graph", "singletau") \
#                  .replace("genTau_", "")
#     new_key += "_errorBand"
#     up_hist = in_file.Get(key.replace("DATA", "upShift"))
#     down_hist = in_file.Get(key.replace("DATA", "downShift"))
#     for i in range(0, hist.GetNbinsX()+2):
#         hist.SetBinErrorUp(i, up_hist.GetBinContent(i) - hist.GetBinContent(i))
#         hist.SetBinErrorLow(i, hist.GetBinContent(i) - down_hist.GetBinContent(i))
#     hist.SetName(new_key)
#     hist.SetTitle(new_key)
#     hist.Write()
#     return


def main():
    root.gROOT.SetBatch()
    args = parse_args()
    inp_file = root.TFile(args.in_filename, "read")
    keys = [key.GetName() for key in inp_file.GetListOfKeys()]
    out_file = root.TFile(args.output, "recreate")
    tauid = "MVAv2" if args.mva else "DeepTau"
    for key in get_matches(keys, "^graph_.*{}.*genTau_(MC|DATA)".format(tauid)):
        copy_histogram(key, inp_file)
        # if "DATA" in key:
        #     build_histogram(key, inp_file)
    out_file.Close()
    return
# Get list of keys from root file
# filter keys to obtain only keys that are of interest
# get interesting objects from file, change their name and write them to a new file
# get shifted hists from file and build new histogram with entries as errors


if __name__ == "__main__":
    main()
