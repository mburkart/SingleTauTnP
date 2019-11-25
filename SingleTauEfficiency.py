#!/usr/bin/env python
# -*- coding: utf-8 -*-
import yaml
import logging
import re
import os


import numpy as np


import ROOT as root
root.gROOT.SetBatch()
root.ROOT.EnableImplicitMT(10)

logger = logging.getLogger(__name__)


class SingleTauEfficiency(object):

    era_map = {
               "2016": {
                  "DATA": "2016",
                  "MC": "Summer16v3"},
               "2017": {
                  "DATA": "2017",
                  "MC": "Fall17v2"},
               "2018": {
                  "DATA": "2018",
                  "MC": "Autumn18"},
               }

    def __init__(self, era, tauid_wps, input_dir, tau_type, sample_type,
                 save_hists=False, use_mva=False, bin_by_wp=False):
        self._era = era
        self.tauid_wps = tauid_wps
        self._inp_dir = input_dir
        self._tau_type = tau_type
        self._sample_type = sample_type
        self._config = yaml.load(open("configs/settings_singletau.yaml", "r"))
        self._mod_th1d_pT = {}
        self._hists = []
        self._directory = self.era_map[self.era][self._sample_type]
        self._dataframes = []
        self._save_hists = save_hists
        self._bin_by_wp = bin_by_wp
        self._use_mva = use_mva
        self._create_histogram_model()
        root.TH1.SetDefaultSumw2()

    @property
    def era(self):
        return self._era

    @property
    def tauid_wps(self):
        return self._tauid_wps

    @tauid_wps.setter
    def tauid_wps(self, wp_list):
        if not isinstance(wp_list, list):
            raise ValueError("The working points of the tau id criteria "
                             "must be supplied as list.")
        self._tauid_wps = wp_list

    def _create_histogram_model(self):
        if self._bin_by_wp:
            binning = self._config["binning_per_wp"][self.era]
            for wp, bins_dict in binning.iteritems():
                self._mod_th1d_pT[wp] = {}
                for dm, bins in bins_dict.iteritems():
                    self._mod_th1d_pT[wp][dm] = root.RDF.TH1DModel(
                            "mod_th1d_pT", "mod_th1d_pT",
                            len(bins["pT"])-1, np.array(bins["pT"], dtype=float))
        else:
            binning = self._config["binning"][self.era]
            for dm, bins in binning.iteritems():
                self._mod_th1d_pT[dm] = root.RDF.TH1DModel(
                        "mod_th1d_pT", "mod_th1d_pT",
                        len(bins["pT"])-1, np.array(bins["pT"], dtype=float))
        return

    def _build_dataframe(self):
        for sel, sel_config \
                in self._config[self._tau_type][self._sample_type].iteritems():
            logger.debug("Setting up hists for selection %s" % sel)
            hist_dict = {}
            self._dataframes.append(
                    root.RDataFrame("Ntuplizer/TagAndProbe",
                                    self._get_file_list(sel_config["files"])))
            self._dataframes.append(
                    self._dataframes[-1].Filter(
                        "(" + ")&&(".join(sel_config["selection"]) + ")"))
            for idwp in self.tauid_wps:
                hist_dict[idwp] = {}
                if self._use_mva:
                    for dm in ["0", "1", "10"]:
                        if self._bin_by_wp:
                            hist_dict[idwp]["dm"+dm] = {}
                            hist_dict[idwp]["dm"+dm]["total"] = self._dataframes[-1] \
                                .Filter(self._config["tau_wps"]["MVATau"][idwp]
                                    if sel == "MuTauSelection"
                                    else "tauBy" + idwp.capitalize()
                                    + "IsolationMVArun2017v2DBoldDMwLT2017") \
                                .Filter("tauDM == {}".format(dm)) \
                                .Histo1D(self._mod_th1d_pT[idwp]["dm"+dm], "tauPt")
                            hist_dict[idwp]["dm"+dm]["pass"] = self._dataframes[-1] \
                                .Filter(self._config["tau_wps"]["MVATau"][idwp]
                                    if sel == "MuTauSelection"
                                    else "tauBy" + idwp.capitalize()
                                    + "IsolationMVArun2017v2DBoldDMwLT2017") \
                                .Filter("tauDM == {}".format(dm)) \
                                .Filter(sel_config["trg_name"][self.era]) \
                                .Histo1D(self._mod_th1d_pT[idwp]["dm"+dm], "tauPt")
                        else:
                            hist_dict[idwp]["dm"+dm] = {}
                            hist_dict[idwp]["dm"+dm]["total"] = self._dataframes[-1] \
                                .Filter(self._config["tau_wps"]["MVATau"][idwp]
                                    if sel == "MuTauSelection"
                                    else "tauBy" + idwp.capitalize()
                                    + "IsolationMVArun2017v2DBoldDMwLT2017") \
                                .Filter("tauDM == {}".format(dm)) \
                                .Histo1D(self._mod_th1d_pT["dm"+dm], "tauPt")
                            hist_dict[idwp]["dm"+dm]["pass"] = self._dataframes[-1] \
                                .Filter(self._config["tau_wps"]["MVATau"][idwp]
                                    if sel == "MuTauSelection"
                                    else "tauBy" + idwp.capitalize()
                                    + "IsolationMVArun2017v2DBoldDMwLT2017") \
                                .Filter("tauDM == {}".format(dm)) \
                                .Filter(sel_config["trg_name"][self.era]) \
                                .Histo1D(self._mod_th1d_pT["dm"+dm], "tauPt")
                else:
                    if self._bin_by_wp:
                        for dm in ["0", "1", "10", "11"]:
                            hist_dict[idwp]["dm"+dm] = {}
                            hist_dict[idwp]["dm"+dm]["total"] = self._dataframes[-1] \
                                .Filter(self._config["tau_wps"]["DeepTau"][idwp]) \
                                .Filter("tauDM == {}".format(dm)) \
                                .Histo1D(self._mod_th1d_pT[idwp]["dm"+dm], "tauPt")
                            hist_dict[idwp]["dm"+dm]["pass"] = self._dataframes[-1] \
                                .Filter(self._config["tau_wps"]["DeepTau"][idwp]) \
                                .Filter("tauDM == {}".format(dm)) \
                                .Filter(sel_config["trg_name"][self.era]) \
                                .Histo1D(self._mod_th1d_pT[idwp]["dm"+dm], "tauPt")
                    else:
                        for dm in ["0", "1", "10", "11"]:
                            hist_dict[idwp]["dm"+dm] = {}
                            hist_dict[idwp]["dm"+dm]["total"] = self._dataframes[-1] \
                                .Filter(self._config["tau_wps"]["DeepTau"][idwp]) \
                                .Filter("tauDM == {}".format(dm)) \
                                .Histo1D(self._mod_th1d_pT["dm"+dm], "tauPt")
                            hist_dict[idwp]["dm"+dm]["pass"] = self._dataframes[-1] \
                                .Filter(self._config["tau_wps"]["DeepTau"][idwp]) \
                                .Filter("tauDM == {}".format(dm)) \
                                .Filter(sel_config["trg_name"][self.era]) \
                                .Histo1D(self._mod_th1d_pT["dm"+dm], "tauPt")
            self._hists.append(hist_dict)
        return

    def _get_file_list(self, file_regex):
        file_vect = root.vector("string")()
        exp = re.compile(file_regex)
        match_files = [os.path.join(self._inp_dir, self._directory, f)
                       for f in os.listdir(os.path.join(self._inp_dir,
                                                        self._directory))
                       if exp.search(f) is not None]
        for f in match_files:
            logger.info("Using sample %s", f)
            file_vect.push_back(f)
        if file_vect.size() == 0:
            logger.error("No matching files found in directory {} "
                         "for expression {}".format(
                            os.path.join([self._inp_dir, self._directory]),
                            file_regex))
            raise Exception
        return file_vect

    def _get_restructured_dict(self):
        # Combine pass and total histograms for different selections.
        comb_dict = self._hists[0].copy()
        for wp, dm_dict in self._hists[0].iteritems():
            for dm, hists in dm_dict.iteritems():
                for h_type in hists.iterkeys():
                    comb_dict[wp][dm][h_type] = [di[wp][dm][h_type]
                                                 for di in self._hists]
        return comb_dict

    def determine_efficiencies(self):
        self._build_dataframe()
        if not root.TH1.GetDefaultSumw2():
            logger.warning("Sum of weights method is not used for newly "
                           "created histograms. This may result in "
                           "wrong results.")
        for wp, dm_dict in self._get_restructured_dict().iteritems():
            for dm, h_dict in dm_dict.iteritems():
                h_eff = root.TH1D(h_dict["pass"][0].GetValue())
                if len(h_dict["pass"]) > 1:
                    h_tot = root.TH1D(h_dict["total"][0].GetValue())
                    h_tot.Draw()
                    h_dict["total"][1].GetValue().Draw("same")
                    for h_p, h_t in zip(h_dict["pass"][1:], h_dict["total"][1:]):  # noqa: E501
                        h_eff.Add(h_p.GetValue())
                        h_tot.Add(h_t.GetValue())
                    h_pass = h_eff.Clone()
                    h_eff.Divide(h_pass, h_tot, 1., 1., "b(1,1) cl=0.683 mode")

                    h_fail = root.TH1D(h_tot)
                    h_fail.Add(h_pass, -1.)
                    g_eff = root.RooHist(h_pass, h_fail,
                                         0, 1., root.RooAbsData.Poisson, 1.,
                                         root.kTRUE, 1.)
                else:
                    h_eff.Divide(h_dict["pass"][0].GetValue(),
                                 h_dict["total"][0].GetValue(),
                                 1., 1., "b(1,1) cl=0.683 mode")

                    h_fail = root.TH1D(h_dict["total"][0].GetValue())
                    h_fail.Add(h_dict["pass"][0].GetValue(), -1.)
                    g_eff = root.RooHist(h_dict["pass"][0].GetValue(), h_fail,
                                         0, 1., root.RooAbsData.Poisson, 1.,
                                         root.kTRUE, 1.)
                if self._use_mva:
                    nm_temp = "{}_{}MVAv2_{}_{}_{}"
                else:
                    nm_temp = "{}_{}DeepTau_{}_{}_{}"
                form_opt = [wp, dm, self._tau_type, self._sample_type]
                self._save_root_object(
                        h_eff, nm_temp.format("hist", *form_opt))
                self._save_root_object(
                        g_eff, nm_temp.format("graph", *form_opt))
        return

    def _save_root_object(self, root_obj, name):
        root_obj.SetName(name)
        root_obj.SetTitle(name)
        root_obj.Write()
        return
