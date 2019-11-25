#!/usr/bin/env python
# Plotting script for single tau trigger efficiencies
# Copied from https://github.com/tstreble/TauTagAndProbe/blob/master_HLT/TauTagAndProbe/test/fitter/results/TurnOnPlot_DATA.py

import ROOT


ROOT.gSystem.Load('libRooFit')


class TurnOn:
    def __init__(self, **args):
        self.name        = args.get("Name", "turnon")
        # self.legend      = args.get("Legend","")
        self.legend      = args.get("Legend", "Turn-on")
        self.histo       = args.get("Histo", None)
        self.fit         = args.get("Fit", None)
        self.markerColor = args.get("MarkerColor", ROOT.kBlack)
        self.markerStyle = args.get("MarkerStyle", 20)
        self.lineColor   = args.get("LineColor", ROOT.kBlack)
        self.lineStyle   = args.get("LineStyle", 1)
        self.drawOption  = args.get("drawOption", "")
        self.fillColor   = args.get("FillColor", ROOT.kBlack)
        self.fillStyle   = args.get("FillStyle", 1001)
        self.legendOptions = args.get("LegendOptions", "")
        self.histo.SetName(self.name+"_histo")
        # self.fit.SetName(self.name+"_fit")
        self.isDenom = args.get("isDenom", False)


class TurnOnPlot(object):
    def __init__(self, **args):
        self.name  = ""
        self.turnons = []
        self.plotDir = "plots_singletau"
        self.xRange = (10, 120)
        self.LabelSize = 0.04
        self.TitleSize = 1.
        # self.xTitle = "Offline p_{T}^{#tau} [GeV]"
        # self.xTitle = "Nvtx"
        self.xTitle      = args.get("xTitle", "Offline Tau p_{T} [GeV]")
        # self.legendPosition = (0.6,0.2,0.9,0.4)
        self.legendPosition = (0.4, 0.2, 0.9, 0.6)
        self.setPlotStyle()
        # self.triggerName = args.get("TriggerName", "Turn-On")
        self.triggerName = args.get("TriggerName", "")
        self.lumi = args.get("lumi", "")
        self.numLegCols = args.get("numlegCols", "")
        self.year = args.get("year", "2017")
        self.cmstext = args.get("cms", "#bf{CMS} #it{Preliminary}")

    def addTurnOn(self, turnon):
        self.turnons.append(turnon)

    def plot(self):
        canvas = ROOT.TCanvas("c_"+self.name, self.name, 800, 800)
        canvas.SetGrid()
        canvas.SetLogx()
        hDummy = ROOT.TH1F("hDummy_"+self.name, self.name,
                           1, self.xRange[0], self.xRange[1])
        hDummy.SetAxisRange(0, 1.05, "Y")
        hDummy.SetXTitle(self.xTitle)
        # hDummy.SetYTitle("Test")
        hDummy.SetYTitle("L1 + HLT Efficiency")
        hDummy.GetXaxis().SetMoreLogLabels()
        hDummy.GetXaxis().ChangeLabel(1, -1., 0)
        # hDummy.GetXaxis().SetNdivisions(305)
        hDummy.Draw()

        if self.year == "2016":
            hHatch = ROOT.TH1F("hHatch_" + self.name, self.name,
                               1, self.xRange[0], 150)
        else:
            hHatch = ROOT.TH1F("hHatch_" + self.name, self.name,
                               1, self.xRange[0], 190)
        hHatch.SetBinContent(1, 1.05)
        # hHatch.SetFillColorAlpha(21, 0.85)
        hHatch.SetFillColor(21)
        hHatch.SetFillStyle(3344)
        hHatch.Draw("same l0")
        cmsTextFont     = 42  # font of the "CMS" label
        cmsTextSize   = 0.76*0.05  # font size of the "CMS" label
        cmsTextSize2   = 0.76*0.09  # font size of the "CMS" label
        extraTextFont   = 52     # for the "preliminary"
        extraTextSize   = cmsTextSize # for the "preliminary"
        # xpos  = 0.16
        # ypos  = 0.95
        xpos  = 0.20
        ypos  = 0.845

        CMSbox       = ROOT.TLatex  (xpos, ypos         , self.cmstext)
        extraTextBox = ROOT.TLatex  (xpos, ypos - 0.05 , "#it{Preliminary}")
        CMSbox.SetNDC()
        extraTextBox.SetNDC()
        CMSbox.SetTextSize(cmsTextSize2)
        CMSbox.SetTextFont(cmsTextFont)
        CMSbox.SetTextColor(ROOT.kBlack)
        CMSbox.SetTextAlign(11)
        extraTextBox.SetTextSize(extraTextSize)
        extraTextBox.SetTextFont(extraTextFont)
        extraTextBox.SetTextColor(ROOT.kBlack)
        extraTextBox.SetTextAlign(13)

        triggerNameBox = ROOT.TLatex(0.15, 0.95, self.triggerName)
        triggerNameBox.SetNDC()
        triggerNameBox.SetTextFont(42)
        triggerNameBox.SetTextSize(extraTextSize)
        triggerNameBox.SetTextColor(ROOT.kBlack)
        triggerNameBox.SetTextAlign(11)

        # lumi_num = float(cfg.readOption ("general::lumi"))
        # lumi_num = lumi_num/1000. # from pb-1 to fb-1
        # lumi = "%.1f fb^{-1} (13 TeV)" % lumi_num
        # lumi = "5.8 fb^{-1} (13 TeV, 2017)"
        lumi = self.lumi + "(13 TeV, {})".format(self.year)
        lumibox = ROOT.TLatex  (0.953, 0.95, lumi)
        lumibox.SetNDC()
        lumibox.SetTextAlign(31)
        lumibox.SetTextSize(extraTextSize*1.05)
        lumibox.SetTextFont(42)
        lumibox.SetTextColor(ROOT.kBlack)
        # Line legend
        legend = ROOT.TLegend(self.legendPosition[0], self.legendPosition[1],
                              self.legendPosition[2], self.legendPosition[3])
        legend.SetTextFont(42)
        legend.SetFillColor(10)
        legend.SetTextSize(0.63*extraTextSize)
        # legend.SetTextSize(1.2*extraTextSize)
        legend.SetBorderSize(0)
        legend.SetFillStyle(1001)
        legend.SetNColumns(self.numLegCols)
        '''legend1 = ROOT.TLegend(0.14, 0.80, 0.80, 1.02)
        legend1.SetBorderSize(0)
        legend1.SetTextFont(62)
        legend1.SetTextSize(0.025)
        legend1.SetLineColor(0)
        legend1.SetLineStyle(1)
        legend1.SetLineWidth(1)
        legend1.SetFillColor(0)
        legend1.SetFillStyle(0)
        legend1.AddEntry("NULL","CMS Preliminary:                                              #sqrt{s}=13 TeV","h")
        legend1.AddEntry("NULL","L1 Threshold : 28 GeV","h")'''

        shisto = []
        smoother = ROOT.TGraphSmooth()
        for turnon in self.turnons:
            histo = turnon.histo
            histo.SetMarkerStyle(turnon.markerStyle)
            histo.SetMarkerColor(turnon.markerColor)
            histo.SetLineColor(turnon.markerColor)
            histo.SetLineStyle(turnon.lineStyle)
            histo.SetFillColor(turnon.fillColor.GetNumber())
            histo.SetFillStyle(turnon.fillStyle)
            # fit = turnon.fit
            # fit.SetLineStyle(turnon.lineStyle)
            # fit.SetLineColor(turnon.lineColor)
            # fit.SetLineWidth(2)
            histo.Draw("same" + turnon.drawOption)
            # fit.Draw("l same")
            # legends
            legend.AddEntry(histo, turnon.legend, turnon.legendOptions)
            # legend.Draw()
            # if self.name=="turnon_Stage1_Stage2_EB":
        # triggerNameBox.Draw()
        CMSbox.Draw()
        # extraTextBox.Draw()
        lumibox.Draw()
        # print ("DEBUG: " + self.plotDir+"/"+self.name+".eps")
        canvas.Print(self.plotDir+"/"+self.name+".pdf", "pdf")
        canvas.Print(self.plotDir+"/"+self.name+".png", "png")
        return canvas

    def setPlotStyle(self):
        ROOT.gROOT.SetStyle("Plain")
        ROOT.gStyle.SetOptStat()
        ROOT.gStyle.SetOptFit(0)
        ROOT.gStyle.SetOptTitle(0)
        ROOT.gStyle.SetFrameLineWidth(1)
        ROOT.gStyle.SetPadBottomMargin(0.13)
        ROOT.gStyle.SetPadLeftMargin(0.15)
        ROOT.gStyle.SetPadTopMargin(0.06)
        ROOT.gStyle.SetPadRightMargin(0.05)

        ROOT.gStyle.SetLabelFont(42, "X")
        ROOT.gStyle.SetLabelFont(42, "Y")
        ROOT.gStyle.SetLabelSize(self.LabelSize, "X")
        ROOT.gStyle.SetLabelSize(self.LabelSize, "Y")
        ROOT.gStyle.SetLabelOffset(0.01, "Y")
        ROOT.gStyle.SetTickLength(0.02, "X")
        ROOT.gStyle.SetTickLength(0.02, "Y")
        ROOT.gStyle.SetLineWidth(1)
        ROOT.gStyle.SetTickLength(0.02, "Z")

        ROOT.gStyle.SetTitleSize(self.TitleSize)
        ROOT.gStyle.SetTitleFont(42, "X")
        ROOT.gStyle.SetTitleFont(42, "Y")
        ROOT.gStyle.SetTitleSize(0.05, "X")
        ROOT.gStyle.SetTitleSize(0.05, "Y")
        ROOT.gStyle.SetTitleOffset(1.1, "X")
        ROOT.gStyle.SetTitleOffset(1.4, "Y")
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetPalette(1)
        ROOT.gStyle.SetPaintTextFormat("3.2f")
        ROOT.gROOT.ForceStyle()


class TurnOnPlotWithRatio(TurnOnPlot):
    def __init__(self, **args):
        super(TurnOnPlotWithRatio, self).__init__(**args)

    def plot(self):
        canvas = ROOT.TCanvas("c_"+self.name, self.name, 800, 800)
        pad = ROOT.TPad("p_"+self.name, self.name, 0.0, 0.28, 1., 1.)
        pad.Draw()
        canvas.cd()
        ratio_pad = ROOT.TPad("p_ratio_"+self.name,
                              "ratio_"+self.name,
                              0., 0., 1., 0.35)
        ratio_pad.Draw()
        pad.cd()
        pad.SetGrid()
        pad.SetLogx()
        ratio_pad.SetLogx()
        ratio_pad.SetGrid()
        scale_w_pad = (canvas.GetWw()*canvas.GetAbsWNDC())/(pad.GetWw()*pad.GetAbsWNDC())
        scale_h_pad = (canvas.GetWh()*canvas.GetAbsHNDC())/(pad.GetWh()*pad.GetAbsHNDC())
        scale_w_ratio = (canvas.GetWw()*canvas.GetAbsWNDC())/(ratio_pad.GetWw()*ratio_pad.GetAbsWNDC())
        scale_h_ratio = (canvas.GetWh()*canvas.GetAbsHNDC())/(ratio_pad.GetWh()*ratio_pad.GetAbsHNDC())
        pad.SetTopMargin(pad.GetTopMargin()*scale_h_pad)
        ratio_pad.SetBottomMargin(ratio_pad.GetBottomMargin()*scale_h_ratio)
        hDummy = ROOT.TH1F("hDummy_"+self.name, self.name,
                           1, self.xRange[0], self.xRange[1])
        hDummy.SetAxisRange(0, 1.05, "Y")
        # hDummy.SetXTitle(self.xTitle)
        # hDummy.SetYTitle("Test")
        hDummy.GetYaxis().SetTitleSize(hDummy.GetYaxis().GetTitleSize()*scale_h_pad)
        hDummy.GetYaxis().SetLabelSize(hDummy.GetYaxis().GetLabelSize()*scale_h_pad)
        hDummy.GetYaxis().SetTitleOffset(hDummy.GetYaxis().GetTitleOffset()/scale_h_pad)
        hDummy.SetYTitle("L1 + HLT Efficiency")
	hDummy.GetXaxis().SetMoreLogLabels()
        hDummy.GetXaxis().SetLabelOffset(999)
        hDummy.GetXaxis().SetLabelSize(0)
        hDummy.Draw()


        cmsTextFont     = 42  # font of the "CMS" label
        cmsTextSize   = 0.76*0.05*scale_h_pad  # font size of the "CMS" label
        extraTextFont   = 52     # for the "preliminary"
        extraTextSize   = cmsTextSize # for the "preliminary"
        xpos  = 0.16
        ypos  = 0.929

        CMSbox       = ROOT.TLatex  (xpos, ypos         , "#bf{CMS} #it{Preliminary}")
        extraTextBox = ROOT.TLatex  (xpos, ypos - 0.05 , "#it{Preliminary}")
        CMSbox.SetNDC()
        extraTextBox.SetNDC()
        CMSbox.SetTextSize(cmsTextSize)
        CMSbox.SetTextFont(cmsTextFont)
        CMSbox.SetTextColor(ROOT.kBlack)
        CMSbox.SetTextAlign(11)
        extraTextBox.SetTextSize(extraTextSize)
        extraTextBox.SetTextFont(extraTextFont)
        extraTextBox.SetTextColor(ROOT.kBlack)
        extraTextBox.SetTextAlign(13)

        triggerNameBox = ROOT.TLatex(0.15, 0.929, self.triggerName)
        triggerNameBox.SetNDC()
        triggerNameBox.SetTextFont(42)
        triggerNameBox.SetTextSize(extraTextSize)
        triggerNameBox.SetTextColor(ROOT.kBlack)
        triggerNameBox.SetTextAlign(11)

        # lumi_num = float(cfg.readOption ("general::lumi"))
        # lumi_num = lumi_num/1000. # from pb-1 to fb-1
        # lumi = "%.1f fb^{-1} (13 TeV)" % lumi_num
        # lumi = "5.8 fb^{-1} (13 TeV, 2017)"
        lumi = self.lumi + "(13 TeV, {})".format(self.year)
        lumibox = ROOT.TLatex  (0.953, 0.929, lumi)
        lumibox.SetNDC()
        lumibox.SetTextAlign(31)
        lumibox.SetTextSize(extraTextSize)
        lumibox.SetTextFont(42)
        lumibox.SetTextColor(ROOT.kBlack)
        # Line legend
        legend = ROOT.TLegend(self.legendPosition[0], self.legendPosition[1],
                              self.legendPosition[2], self.legendPosition[3])
        legend.SetTextFont(42)
        legend.SetFillColor(10)
        legend.SetTextSize(0.63*extraTextSize)
        # legend.SetTextSize(0.9*extraTextSize)
        legend.SetBorderSize(0)
        legend.SetFillStyle(1001)
        legend.SetNColumns(self.numLegCols)
        '''legend1 = ROOT.TLegend(0.14, 0.80, 0.80, 1.02)
        legend1.SetBorderSize(0)
        legend1.SetTextFont(62)
        legend1.SetTextSize(0.025)
        legend1.SetLineColor(0)
        legend1.SetLineStyle(1)
        legend1.SetLineWidth(1)
        legend1.SetFillColor(0)
        legend1.SetFillStyle(0)
        legend1.AddEntry("NULL","CMS Preliminary:                                              #sqrt{s}=13 TeV","h")
        legend1.AddEntry("NULL","L1 Threshold : 28 GeV","h")'''

        shisto = []
        smoother = ROOT.TGraphSmooth()
        for turnon in self.turnons:
            histo = turnon.histo
            histo.SetMarkerStyle(turnon.markerStyle)
            histo.SetMarkerColor(turnon.markerColor)
            histo.SetLineColor(turnon.markerColor)
            histo.SetLineStyle(turnon.lineStyle)
            histo.SetFillColor(turnon.fillColor.GetNumber())
            histo.SetFillStyle(turnon.fillStyle)
            # fit = turnon.fit
            # fit.SetLineStyle(turnon.lineStyle)
            # fit.SetLineColor(turnon.lineColor)
            # fit.SetLineWidth(2)
            histo.Draw("same" + turnon.drawOption)
            # fit.Draw("l same")
            # legends
            legend.AddEntry(histo, turnon.legend, turnon.legendOptions)
            legend.Draw()
            # if self.name=="turnon_Stage1_Stage2_EB":
        # triggerNameBox.Draw()
        CMSbox.Draw()
        # extraTextBox.Draw()
        lumibox.Draw()
        ratio_pad.cd()
        hRatioDummy = ROOT.TH1F("hRatioDummy_"+self.name, self.name,
                                1, self.xRange[0], self.xRange[1])
        hRatioDummy.SetAxisRange(0.95, 1.5, "Y")
        hRatioDummy.SetXTitle(self.xTitle)
        # hRatioDummy.SetYTitle("Test")
        hRatioDummy.SetYTitle("Ratio to Data")
	hRatioDummy.GetXaxis().SetMoreLogLabels()
        hRatioDummy.GetXaxis().SetLabelSize(hRatioDummy.GetXaxis().GetLabelSize()*scale_h_ratio)
        hRatioDummy.GetXaxis().SetTitleSize(hRatioDummy.GetXaxis().GetTitleSize()*scale_h_ratio)
        hRatioDummy.GetXaxis().SetTitleOffset(hRatioDummy.GetXaxis().GetTitleOffset()/scale_w_ratio)
        hRatioDummy.GetYaxis().SetLabelSize(hRatioDummy.GetYaxis().GetLabelSize()*scale_h_ratio)
        hRatioDummy.GetYaxis().SetTitleSize(hRatioDummy.GetYaxis().GetTitleSize()*scale_h_ratio)
        hRatioDummy.GetYaxis().SetNdivisions(305)
        hRatioDummy.GetYaxis().SetTitleOffset(hRatioDummy.GetYaxis().GetTitleOffset()/scale_h_ratio)
        hRatioDummy.Draw()
        ratio = []
        for turnon in self.turnons:
            if turnon.isDenom:
                histo0 = turnon.histo
        for turnon in self.turnons:
            if not turnon.isDenom:
                histo = turnon.histo
                ratio.append(ROOT.TGraphAsymmErrors(histo.GetN()))
                x = histo.GetX()
                y0 = histo0.GetY()
                # binomial errors used at the moment, therefore errors are symmetric
                y0_err = histo0.GetEYhigh()
                y = histo.GetY()
                y_err = histo.GetEYhigh()
                for binN, xval, ydenom, ydata, errdenom, errdata in zip(xrange(histo.GetN()),x,y0,y, y0_err, y_err):
                    try:
                        yr = ydata/ydenom
                    except ZeroDivisionError:
                        print "ZeroDivisionError encountered. Setting data to zero..."
                        yr = 0.
                    try:
                        r_yerr = yr*ROOT.TMath.Sqrt((errdata/ydata)**2+(errdenom/ydenom)**2)
                    except ZeroDivisionError:
                        r_yerr = 0.
                        print "ZeroDivisionError encountered. Setting error to zero..."
                    ratio[-1].SetPoint(binN, xval, yr)
                    x_err = histo0.GetErrorX(binN)
                    ratio[-1].SetPointError(binN, x_err, x_err, r_yerr, r_yerr)
                # ratio[-1].Draw(turnon.drawOption)
                ratio[-1].Draw("pz")
                ratio[-1].SetMarkerStyle(turnon.markerStyle)
                ratio[-1].SetMarkerColor(turnon.markerColor)
                ratio[-1].SetLineColor(turnon.markerColor)
                ratio[-1].SetLineStyle(turnon.lineStyle)
                ratio[-1].SetFillColor(turnon.fillColor.GetNumber())
                ratio[-1].SetFillStyle(turnon.fillStyle)
        # print ("DEBUG: " + self.plotDir+"/"+self.name+".eps")
        canvas.Print(self.plotDir+"/"+self.name+".pdf", "pdf")
        canvas.Print(self.plotDir+"/"+self.name+".png", "png")
        return canvas

    def setPlotStyle(self):
        super(TurnOnPlotWithRatio, self).setPlotStyle()
