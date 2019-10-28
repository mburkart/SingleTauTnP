#!/usr/bin/env python
import logging
import argparse
from copy import deepcopy

import ROOT as root


tRed     = root.TColor(3001, 1., 0., 0., "tRed"    , 0.35)  # noqa: E221,E203
tGreen   = root.TColor(3002, 0., 1., 0., "tGreen"  , 0.35)  # noqa: E221,E203
tBlue    = root.TColor(3003, 0., 0., 1., "tBlue"   , 0.35)  # noqa: E221,E203
tMagenta = root.TColor(3004, 1., 0., 1., "tMagenta", 0.35)  # noqa: E221,E203
tCyan    = root.TColor(3005, 0., 1., 1., "tCyan"   , 0.35)  # noqa: E221,E203
tYellow  = root.TColor(3006, 1., 1., 0., "tYellow" , 0.35)  # noqa: E221,E203
tOrange  = root.TColor(3007, 1., .5, 0., "tOrange" , 0.35)  # noqa: E221,E203

DM_DICT = {
        "dm0": "1 prong",
        "dm1": "1 prong + #pi^{0}'s",
        "dm10": "3 prong",
        }

OPT_DICT = {
        2016: {
            "x_range": [150, 1000],
            "lumi": "36.7 fb^{-1} (13 TeV, 2016)"},
        2017: {
            "x_range": [190, 1000],
            "lumi": "41.5 fb^{-1} (13 TeV, 2017)"},
        2018: {
            "x_range": [190, 1000],
            "lumi": "59.7 fb^{-1} (13 TeV, 2018)"},
            }


def parse_arguments():
    parser = argparse.ArgumentParser(
            description="Script to extract efficiency histograms and"
                        " uncertainties, respectively corrections.")
    parser.add_argument("-i", "--input", type=str, required=True,
                        help="Input root file.")
    parser.add_argument("-w", "--working-point", type=str,
                        default="tight", dest="wp",
                        help="Tau ID working point.")
    parser.add_argument("-e", "--era", choices=[2016, 2017, 2018], type=int,
                        help="Era used for plot labelling.")
    args = parser.parse_args()
    return args


def setup_logging(lev):
    logging.basicConfig(level=lev)
    return


def setPlotStyle():
    root.gROOT.SetStyle("Plain")
    root.gStyle.SetOptStat()
    root.gStyle.SetOptFit(0)
    root.gStyle.SetOptTitle(0)
    root.gStyle.SetFrameLineWidth(1)
    root.gStyle.SetPadBottomMargin(0.13)
    root.gStyle.SetPadLeftMargin(0.15)
    root.gStyle.SetPadTopMargin(0.06)
    root.gStyle.SetPadRightMargin(0.05)

    root.gStyle.SetLabelFont(42, "X")
    root.gStyle.SetLabelFont(42, "Y")
    root.gStyle.SetLabelSize(0.04, "X")
    root.gStyle.SetLabelSize(0.04, "Y")
    root.gStyle.SetLabelOffset(0.01, "Y")
    root.gStyle.SetTickLength(0.02, "X")
    root.gStyle.SetTickLength(0.02, "Y")
    root.gStyle.SetLineWidth(1)
    root.gStyle.SetTickLength(0.02, "Z")

    root.gStyle.SetTitleSize(1.)
    root.gStyle.SetTitleFont(42, "X")
    root.gStyle.SetTitleFont(42, "Y")
    root.gStyle.SetTitleSize(0.05, "X")
    root.gStyle.SetTitleSize(0.05, "Y")
    root.gStyle.SetTitleOffset(1.1, "X")
    root.gStyle.SetTitleOffset(1.4, "Y")
    root.gStyle.SetOptStat(0)
    root.gStyle.SetPalette(1)
    root.gStyle.SetPaintTextFormat("3.2f")
    root.gROOT.ForceStyle()
    return


def get_plotting_dicts():
    mc_dict = {"markerStyle": 22,
               "markerColor": root.kRed+2,
               "lineStyle": 1,
               "fillColor": tRed,
               "fillStyle": 1001,
               "drawOption": "pl",
               "legendOption": "pl",
               # "legend": "MC efficiency"
               }
    data_dict = {"markerStyle": 22,
                 "markerColor": root.kBlue+2,
                 "lineStyle": 1,
                 "fillColor": tBlue,
                 "fillStyle": 1001,
                 "drawOption": "pl",
                 "legendOption": "pl",
                 # "legend": "Estimated efficiency in Data"
                 }
    up_dict = {"markerStyle": 22,
               "markerColor": root.kBlue+2,
               "lineStyle": 1,
               "fillColor": tBlue,
               "fillStyle": 3240,
               "drawOption": "hist bar",
               # "legendOption": "f",
               # "legend": "Data efficiency shifts"
               }
    down_dict = {"markerStyle": 22,
                 "markerColor": 10,
                 "lineStyle": 1,
                 "fillColor": 10,
                 "fillStyle": 1001,
                 "drawOption": "hist bar"
                 }
    return [up_dict, down_dict, mc_dict, data_dict]


def get_plotting_dicts_shifts():
    func_dict = {"markerStyle": 22,
                 "markerColor": root.kBlue+2,
                 "lineStyle": 1,
                 "fillColor": tBlue,
                 "fillStyle": 1001,
                 "drawOption": "hist pe",
                 }
    up_dict = {"markerStyle": 22,
               "markerColor": root.kBlue+2,
               "lineStyle": 1,
               "fillColor": tBlue,
               "fillStyle": 3240,
               "drawOption": "hist bar",
               }
    down_dict = {"markerStyle": 22,
                 "markerColor": 10,
                 "lineStyle": 1,
                 "fillColor": 10,
                 "fillStyle": 1001,
                 "drawOption": "hist bar"
                 }
    return [up_dict, down_dict, func_dict]


def derive_data_efficiency(gen_mc_hist, hist_to_multiply, denom_hist=None):
    gen_data_hist = root.TH1D(gen_mc_hist)
    gen_data_hist.SetName("")
    gen_data_hist.SetTitle(gen_data_hist.GetName())
    gen_data_hist.Multiply(hist_to_multiply)
    if denom_hist is not None:
        gen_data_hist.Divide(denom_hist)
    # Check for bin contents greater than one or less than zero.
    for i in xrange(0, gen_data_hist.GetNbinsX()+1):
        if gen_data_hist.GetBinContent(i) > 1.:
            logging.info("Bin with content greater than 1 found."
                         " Setting bin content to 1.")
            gen_data_hist.SetBinContent(i, 1.)
        if gen_data_hist.GetBinContent(i) < 0.:
            logging.info("Bin with content less than 0 found."
                         " Setting bin content to 0.")
            gen_data_hist.SetBinContent(i, 0.)
    return gen_data_hist


def plot(histos, plot_dicts, canvas_name, y_title="L1 + HLT Efficiency",
         y_axis_range=(0., 1.05), cmstext=""):
    canvas = root.TCanvas("c_"+canvas_name, canvas_name, 800, 800)
    hDummy = root.TH1F("hDummy_"+canvas_name, canvas_name, 1,
                       *OPT_DICT[args.era]["x_range"])
    y_low, y_up = y_axis_range
    hDummy.SetAxisRange(y_low, y_up, "Y")
    hDummy.SetXTitle("Offline Tau p_{T} [GeV]")
    hDummy.SetYTitle(y_title)
    # hDummy.GetXaxis().SetNdivisions(305)
    hDummy.Draw()
    legend = root.TLegend(0.54, 0.15, 0.94, 0.33)
    legend.SetTextFont(42)
    legend.SetFillColor(10)
    legend.SetTextSize(0.63*0.76*0.05)
    # legend.SetTextSize(0.9*extraTextSize)
    legend.SetBorderSize(0)
    legend.SetFillStyle(1001)
    for histo, plot_dict in zip(histos, plot_dicts):
        histo.GetXaxis().SetRangeUser(*OPT_DICT[args.era]["x_range"])
        histo.SetMarkerStyle(plot_dict["markerStyle"])
        histo.SetMarkerColor(plot_dict["markerColor"])
        histo.SetLineColor(plot_dict["markerColor"])
        histo.SetLineStyle(plot_dict["lineStyle"])
        if isinstance(plot_dict["fillColor"], int):
            histo.SetFillColor(plot_dict["fillColor"])
        else:
            histo.SetFillColor(plot_dict["fillColor"].GetNumber())
        histo.SetFillStyle(plot_dict["fillStyle"])
        histo.Draw("same "+plot_dict["drawOption"])
        if "legend" in plot_dict.keys():
            legend.AddEntry(histo, plot_dict["legend"],
                            plot_dict["legendOption"])
        cmsTextFont = 42  # font of the "CMS" label
        cmsTextSize = 0.76*0.05  # font size of the "CMS" label
        cmsTextSize2 = 0.76*0.08  # font size of the "CMS" label
        extraTextFont = 52     # for the "preliminary"
        extraTextSize = cmsTextSize  # for the "preliminary"
        # xpos  = 0.16
        # ypos  = 0.95
        xpos = 0.16
        ypos = 0.85

        CMSbox = root.TLatex(xpos, ypos, cmstext)
        CMSbox.SetNDC()
        CMSbox.SetTextSize(cmsTextSize2)
        CMSbox.SetTextFont(cmsTextFont)
        CMSbox.SetTextColor(root.kBlack)
        CMSbox.SetTextAlign(11)
    canvas.SetGrid()
    canvas.SetLogx()
    hDummy.GetXaxis().SetMoreLogLabels()
    hDummy.Draw("same axis")
    hDummy.Draw("same axig")
    # if legend.GetListOfPrimitives().GetEntries() == 0:
    #     pass
    # else:
    #     legend.Draw()
    canvas.Print("plots_prop_sfs/"+canvas_name+".pdf", "pdf")
    canvas.Print("plots_prop_sfs/"+canvas_name+".png", "png")
    return


def plot_with_ratio(histos, plot_dicts, canvas_name,
                    y_title="L1 + HLT Efficiency",
                    y_axis_range=(0., 1.05), cmstext=""):
    canvas = root.TCanvas("c_"+canvas_name, canvas_name, 800, 800)
    pad = root.TPad("p_"+canvas_name, canvas_name, 0.0, 0.28, 1., 1.)
    pad.Draw()
    canvas.cd()
    ratio_pad = root.TPad("p_ratio_"+canvas_name, "ratio_"+canvas_name,
                          0., 0., 1., 0.35)
    ratio_pad.Draw()
    pad.cd()

    scale_w_pad = ((canvas.GetWw()*canvas.GetAbsWNDC())
                   / (pad.GetWw()*pad.GetAbsWNDC()))
    scale_h_pad = ((canvas.GetWh()*canvas.GetAbsHNDC())
                   / (pad.GetWh()*pad.GetAbsHNDC()))
    scale_w_ratio = ((canvas.GetWw()*canvas.GetAbsWNDC())
                     / (ratio_pad.GetWw()*ratio_pad.GetAbsWNDC()))
    scale_h_ratio = ((canvas.GetWh()*canvas.GetAbsHNDC())
                     / (ratio_pad.GetWh()*ratio_pad.GetAbsHNDC()))
    pad.SetTopMargin(pad.GetTopMargin()*scale_h_pad)
    ratio_pad.SetBottomMargin(ratio_pad.GetBottomMargin()*scale_h_ratio)

    hDummy = root.TH1F("hDummy_"+canvas_name, canvas_name, 1, 190, 1000)
    y_low, y_up = y_axis_range
    hDummy.SetAxisRange(y_low, y_up, "Y")
    hDummy.GetYaxis().SetTitleSize(
            hDummy.GetYaxis().GetTitleSize()*scale_h_pad)
    hDummy.GetYaxis().SetLabelSize(
            hDummy.GetYaxis().GetLabelSize()*scale_h_pad)
    hDummy.GetYaxis().SetTitleOffset(
            hDummy.GetYaxis().GetTitleOffset()/scale_h_pad)
    hDummy.GetXaxis().SetMoreLogLabels()
    hDummy.GetXaxis().SetLabelOffset(999)
    hDummy.GetXaxis().SetLabelSize(0)
    hDummy.SetXTitle("Offline Tau p_{T} [GeV]")
    hDummy.SetYTitle(y_title)
    # hDummy.GetXaxis().SetNdivisions(305)
    hDummy.Draw()
    legend = root.TLegend(0.49, 0.15, 0.94, 0.33)
    legend.SetTextFont(42)
    legend.SetFillColor(10)
    legend.SetTextSize(0.63*0.76*0.06*scale_h_pad)
    # legend.SetTextSize(0.9*extraTextSize)
    legend.SetBorderSize(0)
    legend.SetFillStyle(1001)
    for histo, plot_dict in zip(histos, plot_dicts):
        histo.GetXaxis().SetRangeUser(190, 1000)
        histo.SetMarkerStyle(plot_dict["markerStyle"])
        histo.SetMarkerColor(plot_dict["markerColor"])
        histo.SetLineColor(plot_dict["markerColor"])
        histo.SetLineStyle(plot_dict["lineStyle"])
        if isinstance(plot_dict["fillColor"], int):
            histo.SetFillColor(plot_dict["fillColor"])
        else:
            histo.SetFillColor(plot_dict["fillColor"].GetNumber())
        histo.SetFillStyle(plot_dict["fillStyle"])
        histo.Draw("same "+plot_dict["drawOption"])
        if "legend" in plot_dict.keys():
            legend.AddEntry(histo, plot_dict["legend"],
                            plot_dict["legendOption"])
    if legend.GetListOfPrimitives().GetEntries() == 0:
        pass
    else:
        legend.Draw()
    cmsTextFont = 42  # font of the "CMS" label
    cmsTextSize = 0.76*0.05*scale_h_pad  # font size of the "CMS" label
    cmsTextSize2 = 0.76*0.08*scale_h_pad  # font size of the "CMS" label
    extraTextFont = 52     # for the "preliminary"
    extraTextSize = cmsTextSize  # for the "preliminary"
    # xpos  = 0.16
    # ypos  = 0.929
    # xpos  = 0.17
    xpos = 0.175
    # ypos  = 0.809
    ypos = 0.839

    CMSbox = root.TLatex(xpos, ypos, cmstext)
    CMSbox.SetNDC()
    CMSbox.SetTextSize(cmsTextSize2)
    CMSbox.SetTextFont(cmsTextFont)
    CMSbox.SetTextColor(root.kBlack)
    CMSbox.SetTextAlign(11)
    CMSbox.Draw()
    lumi = OPT_DICT[args.era]["lumi"]
    lumibox = root.TLatex(0.953, 0.929, lumi)
    lumibox.SetNDC()
    lumibox.SetTextAlign(31)
    lumibox.SetTextSize(extraTextSize)
    lumibox.SetTextFont(42)
    lumibox.SetTextColor(root.kBlack)
    lumibox.Draw()
    pad.SetGrid()
    pad.SetLogx()
    hDummy.GetXaxis().SetMoreLogLabels()
    hDummy.Draw("same axis")
    hDummy.Draw("same axig")

    ratio_pad.cd()
    hRatioDummy = root.TH1F("hRatioDummy_"+canvas_name, canvas_name,
                            1, *OPT_DICT[args.era]["x_range"])
    hRatioDummy.SetAxisRange(0.75, 1.15, "Y")
    hRatioDummy.SetXTitle("Offline Tau p_{T} [GeV]")
    # hRatioDummy.SetYTitle("Test")
    hRatioDummy.SetYTitle("Scale factor")
    hRatioDummy.GetXaxis().SetMoreLogLabels()
    hRatioDummy.GetXaxis().SetLabelSize(
            hRatioDummy.GetXaxis().GetLabelSize()*scale_h_ratio)
    hRatioDummy.GetXaxis().SetTitleSize(
            hRatioDummy.GetXaxis().GetTitleSize()*scale_h_ratio)
    hRatioDummy.GetXaxis().SetTitleOffset(
            hRatioDummy.GetXaxis().GetTitleOffset()/scale_w_ratio)
    hRatioDummy.GetYaxis().SetLabelSize(
            hRatioDummy.GetYaxis().GetLabelSize()*scale_h_ratio)
    hRatioDummy.GetYaxis().SetTitleSize(
            hRatioDummy.GetYaxis().GetTitleSize()*scale_h_ratio)
    hRatioDummy.GetYaxis().SetNdivisions(305)
    hRatioDummy.GetYaxis().SetTitleOffset(
            hRatioDummy.GetYaxis().GetTitleOffset()/scale_h_ratio)
    hRatioDummy.Draw()
    mc_hist = deepcopy(histos[2])
    data_hists = [deepcopy(h) for i, h in enumerate(histos) if i != 2]
    styles = [deepcopy(d) for i, d in enumerate(plot_dicts) if i != 2]
    for histo, plot_dict in zip(data_hists, styles):
        histo.Divide(mc_hist)
        histo.GetXaxis().SetRangeUser(*OPT_DICT[args.era]["x_range"])
        histo.SetMarkerStyle(plot_dict["markerStyle"])
        histo.SetMarkerColor(plot_dict["markerColor"])
        histo.SetLineColor(plot_dict["markerColor"])
        histo.SetLineStyle(plot_dict["lineStyle"])
        if isinstance(plot_dict["fillColor"], int):
            histo.SetFillColor(plot_dict["fillColor"])
        else:
            histo.SetFillColor(plot_dict["fillColor"].GetNumber())
        histo.SetFillStyle(plot_dict["fillStyle"])
        histo.Draw("same "+plot_dict["drawOption"])
    ratio_pad.SetGrid()
    ratio_pad.SetLogx()
    hRatioDummy.Draw("same axis")
    hRatioDummy.Draw("same axig")
    canvas.Print("plots_prop_sfs/"+canvas_name+".pdf", "pdf")
    canvas.Print("plots_prop_sfs/"+canvas_name+".png", "png")
    return canvas


def calculate_uncertainty(gen_tau_mc, fake_tau_mc, fake_tau_data):
    sf_corr_hist = fake_tau_mc.Clone()
    sf_corr_hist.Add(fake_tau_data, -1.)
    sf_corr_hist.Multiply(sf_corr_hist)
    sf_corr_hist.Scale(1./4.)

    tf_corr_hist = gen_tau_mc.Clone()
    tf_corr_hist.Add(fake_tau_mc, -1.)
    tf_corr_hist.Multiply(tf_corr_hist)
    tf_corr_hist.Scale(1./4.)

    uncertainty_hist_tmp = sf_corr_hist.Clone()
    uncertainty_hist_tmp.Add(tf_corr_hist)
    uncertainty_hist = get_sqrt(uncertainty_hist_tmp)
    uncertainty_hist.Multiply(
            derive_data_efficiency(
                gen_tau_mc, fake_tau_data,
                denom_hist=fake_tau_mc)
            )
    return uncertainty_hist


def create_function_and_shift(h_num, h_denom):
    h_function = h_num.Clone()
    h_function.Divide(h_denom)
    h_shift = h_num.Clone()
    h_shift.Add(h_denom, -1.)
    h_shift = abs_hist(h_shift)
    h_shift.Scale(1./2.)
    h_shift.Multiply(h_function)
    h_function_up = h_function.Clone()
    h_function_up.Add(h_shift)
    h_function_down = h_function.Clone()
    h_function_down.Add(h_shift, -1.)
    return h_function_up, h_function_down, h_function


def shift_plots(genTau_mc, fakeTau_mc, fakeTau_data, dm):
    plot(create_function_and_shift(fakeTau_data, fakeTau_mc),
         get_plotting_dicts_shifts(),
         str(args.era) + "_" + dm+"_scalefactor_shift",
         y_axis_range=(0.75, 1.2), y_title="Scale factor")
    plot(create_function_and_shift(genTau_mc, fakeTau_mc),
         get_plotting_dicts_shifts(),
         str(args.era) + "_" + dm+"_transferfunction_shift",
         y_axis_range=(0.75, 1.2), y_title="Transfer function")
    return


def sanity_check(unc_hist):
    # Sanity check. If bin content takes unphysical value set it back.
    for i in xrange(0, unc_hist.GetNbinsX()+1):
        if unc_hist.GetBinContent(i) > 1.:
            logging.info("Bin with content greater than 1 found in unc hist."
                         " Setting bin content to 1.")
            unc_hist.SetBinContent(i, 1.)
        if unc_hist.GetBinContent(i) < 0.:
            logging.info("Bin with content less than 0 found in unc hist."
                         " Setting bin content to 0.")
            unc_hist.SetBinContent(i, 0.)
    return unc_hist


def abs_hist(input_hist):
    for i in xrange(0, input_hist.GetNbinsX()+1):
        if input_hist.GetBinContent(i) < 0.:
            input_hist.SetBinContent(i, -input_hist.GetBinContent(i))
    return input_hist


def get_sqrt(hist):
    for i in xrange(0, hist.GetNbinsX()+1):
        bin_cont = hist.GetBinContent(i)
        hist.SetBinContent(i, root.TMath.Sqrt(bin_cont))
    return hist


def main(args):
    root.gROOT.SetBatch(1)
    turnons = []
    setPlotStyle()
    infile = root.TFile(args.input, "update")
    # "inclusiveDM" not yet working because of issues calculating the error
    # for the mc turnon in one bin
    dms = ["dm0", "dm1", "dm10"]
    # dms = ["dm10"]
    for dm in dms:
        gen_mc_turnon = infile.Get(
                "graph_{wp}MVAv2_{dm}_genTau_MC".format(wp=args.wp, dm=dm))
        if dm == "dm0":
            fake_sf = infile.Get("SF_{dm}_eFakes".format(dm=dm))
            fake_data = infile.Get(
                    "graph_{wp}MVAv2_{dm}_eFakes_DATA".format(
                        wp=args.wp, dm=dm))
            fake_mc = infile.Get(
                    "graph_{wp}MVAv2_{dm}_eFakes_MC".format(
                        wp=args.wp, dm=dm))
        else:
            fake_sf = infile.Get("SF_{dm}_jetFakes".format(dm=dm))
            fake_data = infile.Get(
                    "graph_{wp}MVAv2_{dm}_jetFakes_DATA".format(
                        wp=args.wp, dm=dm))
            fake_mc = infile.Get(
                    "graph_{wp}MVAv2_{dm}_jetFakes_MC".format(
                        wp=args.wp, dm=dm))
        gen_data_turnon = derive_data_efficiency(gen_mc_turnon, fake_sf)

        # Get the latest version of the uncertainties using error propagation.
        # Data = fakeMC * SF * TF = GenTauMC * SF
        # s_data = Data * sqrt((fakeMC-fakeData)**2/4 + (GenTauMC-fakeMC)**2/4
        # Data = GenTauMC * SF (1 +- sqrt((fakeMC-fakeData)**2/4 + (GenTauMC-fakeMC)**2/4)  # noqa: E501
        unc_hist = calculate_uncertainty(gen_mc_turnon, fake_mc, fake_data)
        gen_data_up = derive_data_efficiency(gen_mc_turnon, fake_sf)
        gen_data_up.Add(unc_hist, 1.)
        gen_data_up = sanity_check(gen_data_up)

        gen_data_down = derive_data_efficiency(gen_mc_turnon, fake_sf)
        gen_data_down.Add(unc_hist, -1.)
        gen_data_down = sanity_check(gen_data_down)

        plot_with_ratio([gen_data_up, gen_data_down,
                        gen_mc_turnon, gen_data_turnon],
                        get_plotting_dicts(),
                        str(args.era) + "_" + dm+"_latestUncertainty",
                        y_axis_range=(0., 1.1),
                        cmstext=DM_DICT[dm])

        turnons.extend([gen_mc_turnon, fake_mc, fake_data])
        shift_plots(gen_mc_turnon, fake_mc, fake_data, dm)
        # Write back shifts to efficiency file.
        gen_data_turnon.SetName(
                "graph_{wp}MVAv2_{dm}_genTau_DATA".format(wp=args.wp, dm=dm))
        gen_data_turnon.SetTitle(
                "graph_{wp}MVAv2_{dm}_genTau_DATA".format(wp=args.wp, dm=dm))
        gen_data_turnon.Write("", root.TObject.kOverwrite)

        gen_data_up.SetName(
                "graph_{wp}MVAv2_{dm}_genTau_DATA_upShift".format(
                    wp=args.wp, dm=dm))
        gen_data_up.SetTitle(
                "graph_{wp}MVAv2_{dm}_genTau_DATA_upShift".format(
                    wp=args.wp, dm=dm))
        gen_data_up.Write("", root.TObject.kOverwrite)

        gen_data_down.SetName(
                "graph_{wp}MVAv2_{dm}_genTau_DATA_downShift".format(
                    wp=args.wp, dm=dm))
        gen_data_down.SetTitle(
                "graph_{wp}MVAv2_{dm}_genTau_DATA_downShift".format(
                    wp=args.wp, dm=dm))
        gen_data_down.Write("", root.TObject.kOverwrite)

    # test_fitting(infile)
    infile.Close()
    return


if __name__ == "__main__":
    setup_logging(logging.INFO)
    args = parse_arguments()
    main(args)
