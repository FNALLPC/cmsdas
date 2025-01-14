# CMSDAS @ FNAL 2020: Disappearing tracks

Welcome to the 2020 FNAL CMSDAS exercise on disappearing tracks! This long exercise will walk students through a number of steps needed to set up and implement an search for new physics at CMS. Enjoy :)

If you're doing the exercise at the school, please send an email to me so I can sign you up for Mattermost (rheller@fnal.gov)

https://mattermost.web.cern.ch/cmsdaslpc2020/channels/longexercisedisappearingtracks

Note about the samples: This exercise is built largely on pre-made ntuples, and is thus mostly independent of CMSSW. The code that generated the ntuples is contained in the repo: https://github.com/longlivedsusy/treemaker

## Introduction

Long-lived (LL) charged particles are featured in many models of physics beyond the standard model, e.g., hidden valley theories. In particular, R-parity conserving SUSY models with a wino-like LSP usually feature charginos with proper decay lengths between 1 nm and several meters, after which point the chargino would decay into a neutralino and a very soft pion or lepton. SUSY models with a light higgsino but with particularly heavy bino and wino parameters can also give rise to charginos with similar lifetimes. The known particles do not have similar lifetimes, so the potential signal events are quite distinct from the standard model background. 

The most recent public result of the search for long-lived particles with disappearing tracks at sqrt(s)=13 TeV is available [here](http://cms.cern.ch/iCMS/analysisadmin/cadilines?line=EXO-16-044). This PAS (Physics Analysis Summary) gives a good overview of the general search approach and the characteristics and difficulties one encounters when looking at this particular signature. 

The exercise is organized in sections as follows: First, the recipe for setting up a working area will be described. Then, you'll start on a track-level analysis and identify the relevant properties of disappearing tracks (DT). This DT identification is then used on event level where you study the event topology and the background contributions, which are estimated with data-driven methods.

## 1.) Set up a working area

First, [login](https://uscms.org/uscms_at_work/physics/computing/getstarted/uaf.shtml#prerequisites) to a cmslpc node

```bash
ssh -y <username>@cmslpc-sl7.fnal.gov
source /cvmfs/cms.cern.ch/cmsset_default.csh
```

Then create a CMSSW working environment in your home folder: 

```bash
mkdir longlivedLE
cd longlivedLE
SCRAM_ARCH=slc7_amd64_gcc700
cmsrel CMSSW_10_6_4
```

Change to your newly created working environment and initialize the 
CMSSW software environment (you will need to do this step every time you login): 

```bash
cd CMSSW_10_6_4/src
cmsenv
cd ../..
```

Now you need to clone the git repository which contains the analysis-specific code: 

```bash
git clone git@github.com:FNALLPC/DisappearingTracks2020
cd DisappearingTracks2020

```

## 2.) Introduction to tracking

We'll start with an introduction to using tracks for analyses in the era of large pile-up (many primary vertices). It is adapted from the [2018 tracking and vertexing short exercise](https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideCMSDataAnalysisSchoolHamburg2018TrackingAndVertexingExercise) and it will already use real data and will familiarize you with the basic track parameters and reconstructing invariant masses from tracks in CMSSW. Tracks are the detector entities that are closest to the three-vectors of particles: the curvature of the track translates directly to the transverse momentum of the charged particle itself; since we also measure |eta|, this specifies a single possible 3-momentum.

####  Accessing the data

We will be using 10.569 events from 2017 data (Run2017F_SingleMuon_AOD_17Nov2017-v1). This subset of the data is small enough to be easily accessible as a file. Set up a working area and copy the data file to your home directory: 

```bash
cd ..
mkdir tracking-intro
cd tracking-intro
```

### 2.a) The five basic track variables

![](https://raw.githubusercontent.com/LongLivedSusy/cmsdas/master/tracking/track.jpg)

One of the oldest tricks in particle physics is to put a track-measuring device in a strong, roughly uniform magnetic field so that the tracks curve with a radius proportional to their momenta (see [derivation](http://en.wikipedia.org/wiki/Gyroradius#Relativistic_case)). Apart from energy loss and magnetic field inhomogeneities, the particles' trajectories are helices. This allows us to measure a dynamic property (momentum) from a geometric property (radius of curvature).

A helical trajectory can be expressed by five parameters, but the parameterization is not unique. Given one parameterization, we can always re-express the same trajectory in another parameterization. Many of the data fields in a CMSSW reco::Track are alternate ways of expressing the same thing, and there are functions for changing the reference point from which the parameters are expressed. (For a much more detailed description, see [this page](http://www-jlc.kek.jp/subg/offl/lib/docs/helix_manip/node3.html#SECTION00210000000000000000).)

In general terms, the five parameters are:

* signed radius of curvature (units of cm), which is proportional to particle charge divided by the transverse momentum (units of GeV);
* angle of the trajectory at a given point on the helix, in the plane transverse to the beamline (usually called φ);
* angle of the trajectory at a given point on the helix with respect to the beamline (θ, or equivalently λ = π/2 - θ), which is usually expressed in terms of [pseudorapidity](http://en.wikipedia.org/wiki/Pseudorapidity) (η = −ln(tan(θ/2)));
* offset or "impact parameter" relative to some reference point (usually the beamspot), in the plane transverse to the beamline (usually called dxy);
* impact parameter relative to a reference point (beamspot or a selected primary vertex), along the beamline (usually called dz). 

The exact definitions are given in the reco::TrackBase [header file](https://github.com/cms-sw/cmssw/blob/CMSSW_8_0_10_patch2/DataFormats/TrackReco/interface/TrackBase.h). This is also where most tracking variables and functions are defined. The rest are in the reco::Track [header file](https://github.com/cms-sw/cmssw/blob/CMSSW_8_0_10_patch2/DataFormats/TrackReco/interface/Track.h), but most data fields in the latter are accessible only in [RECO](https://twiki.cern.ch/twiki/bin/view/CMS/RECO) (full data record), not [AOD](https://twiki.cern.ch/twiki/bin/view/CMS/AOD) (the subset that is available to most physics analyses). 

####  Accessing track variables

Create ```print.py``` (for example ```vim print.py```, or use your favorite text editor), then copy-paste the following code and run it (```python print.py```). The ```tracks_and_vertices.root``` data file is already referenced:

```python
import DataFormats.FWLite as fwlite
events = fwlite.Events("root://cmseos.fnal.gov//store/user/cmsdas/2020/long_exercises/DisappearingTracks/tracking/tracks_and_vertices.root")
tracks = fwlite.Handle("std::vector<reco::Track>")

for i, event in enumerate(events):
    if i >= 5: break            # only the first 5 events
    print "Event", i
    event.getByLabel("generalTracks", tracks)
    for j, track in enumerate(tracks.product()):
        print "    Track", j, track.charge()/track.pt(), track.phi(), track.eta(), track.dxy(), track.dz()
```

The first three lines load the FWLite framework, the data file, and prepare a handle for the track collection using its full C++ name (```std::vector```). In each event, we load the tracks labeled "generalTracks" and loop over them, printing out the five basic track variables for each.

####  Track quality variables

The first thing you should notice is that each event has hundreds of tracks. That is because hadronic collisions produce large numbers of particles and "generalTracks" is the broadest collection of tracks identified by CMSSW reconstruction. Some of these tracks are not real (ghosts, duplicates, noise...) and a good analysis should define quality cuts to select tracks requiring a certain quality.

Some analyses remove spurious tracks by requiring them to come from the beamspot (small dxy, dz). Some require high-momentum (usually high transverse momentum, pT), but that would be a bad idea in a search for decays with a small mass difference such as ψ' → J/ψ π+π−. In general, each analysis group should review their own needs and ask the Tracking POG about standard selections.

Some of these standard selections have been encoded into a quality flag with three categories: "loose", "tight", and "highPurity". All tracks delivered to the analyzers are at least "loose", "tight" is a subset of these that are more likely to be real, and "highPurity" is a subset of "tight" with even stricter requirements. There is a trade-off: "loose" tracks have high efficiency but also high backgrounds, "highPurity" has slightly lower efficiency but much lower backgrounds, and "tight" is in between (see also the plots below). As of CMSSW 7.4, these are all calculated using MVAs (MultiVariate Analysis techniques) for the various iterations. In addition to the status bits, it's also possible to access the MVA values directly.

![](/tracking/efficiencyVsEta.png?raw=true)
![](/tracking/efficiencyVsPt.png?raw=true)
![](/tracking/fakerateVsEta.png?raw=true)
![](/tracking/fakerateVsPt.png?raw=true)

Update the file ```print.py``` with the following lines:

Add a handle to the MVA values:

```python
MVAs   = fwlite.Handle("std::vector<float>")
```

The event loop should be updated to this: 

```python
for i, event in enumerate(events):
    if i >= 5: break            # only the first 5 events
    print "Event", i
    event.getByLabel("generalTracks", tracks)
    event.getByLabel("generalTracks", "MVAValues", MVAs)

    numTotal = tracks.product().size()
    numLoose = 0
    numTight = 0
    numHighPurity = 0

    for j, (track, mva) in enumerate(zip(tracks.product(), MVAs.product())):
        if track.quality(track.qualityByName("loose")):      numLoose      += 1
        if track.quality(track.qualityByName("tight")):      numTight      += 1
        if track.quality(track.qualityByName("highPurity")): numHighPurity += 1

        print "    Track", j,
        print track.charge()/track.pt(),
        print track.phi(),
        print track.eta(),
        print track.dxy(),
        print track.dz(),
        print track.numberOfValidHits(),
        print track.algoName(),
        print mva

    print "Event", i,
    print "numTotal:", numTotal,
    print "numLoose:", numLoose,
    print "numTight:", numTight,
    print "numHighPurity:", numHighPurity
```

To plot some track variables, use ROOT and make a python loop like in the example below (name this file ```plot_track_quantities.py```).

```python
import DataFormats.FWLite as fwlite
import ROOT

events = fwlite.Events("root://cmseos.fnal.gov//store/user/cmsdas/2020/long_exercises/DisappearingTracks/tracking/tracks_and_vertices.root")
tracks = fwlite.Handle("std::vector<reco::Track>")

hist_pt   = ROOT.TH1F("pt", "pt", 100, 0.0, 100.0)
hist_eta  = ROOT.TH1F("eta", "eta", 100, -3.0, 3.0)
hist_phi  = ROOT.TH1F("phi", "phi", 100, -3.2, 3.2)
hist_normChi2 = ROOT.TH1F("normChi2", "normChi2", 100, 0.0, 10.0)

for i, event in enumerate(events):
    event.getByLabel("generalTracks", tracks)
    for track in tracks.product():
        hist_pt.Fill(track.pt())
        hist_eta.Fill(track.eta())
        hist_phi.Fill(track.phi())
        hist_normChi2.Fill(track.normalizedChi2())
    if i > 1000: break

c = ROOT.TCanvas( "c", "c", 800, 800)

hist_pt.Draw()
c.SetLogy()
c.SaveAs("track_pt.png")
c.SetLogy(False)

hist_eta.Draw()
c.SaveAs("track_eta.png")

hist_phi.Draw()
c.SaveAs("track_phi.png")

hist_normChi2.Draw()
c.SaveAs("track_normChi2.png")
```

Run this plotting script with

```bash
python plot_track_quantities.py
``` 

#### 2.b) Tracks as particles

Unlike calorimeter showers, tracks can usually be interpreted as particle vectors without any additional corrections. Detector alignment, non-helical trajectories from energy loss, Lorentz angle corrections, and (to a much smaller extent) magnetic field inhomogeneities are important, but they are all corrections that must be applied during or before the track-reconstruction process. From an analyzer's point of view, most tracks are individual particles (depending on quality cuts) and the origin and momentum of the particle are derived from the track's geometry, with some resolution (random error). Biases (systematic offsets from the true values) are not normal: they're an indication that something went wrong in this process.

The analyzer does not even need to calculate the particle's momentum from the track parameters: there are member functions for that. Particle's transverse momentum, momentum magnitude, and all of its components can be read through the following lines (let's name this new file ```kinematics.py```):

```python
import DataFormats.FWLite as fwlite
import ROOT

events = fwlite.Events("root://cmseos.fnal.gov//store/user/cmsdas/2020/long_exercises/DisappearingTracks/tracking/tracks_and_vertices.root")
tracks = fwlite.Handle("std::vector<reco::Track>")

for i, event in enumerate(events):
    event.getByLabel("generalTracks", tracks)
    for track in tracks.product():
        print track.pt(), track.p(), track.px(), track.py(), track.pz()
    if i > 100: break
```

<b>Exercise: Now we can use this to do some kinematics. Assuming that the particle is a pion, calculate its kinetic energy.</b>
Note: Identifying the particle that made the track is difficult: the mass of some low-momentum tracks can be identified by their energy loss, called dE/dx, and electrons and muons can be identified by signatures in other subdetectors. Without any other information, the safest assumption is that a randomly chosen track is a pion, since hadron collisions produce a lot of pions.

The pion mass is 0.140 GeV (all masses in CMSSW are in GeV). You can get a square root function by typing 
```python
import math
print math.sqrt(4.0)
```

To square numbers you can use **2 (Fortran syntax). Now add all this to ```kinematics.py``` and run the script.

Once you've tried to implement this, you can take a look at the solution ![here](/tracking/solution1.md).

As a second exercise, let's compute the vector-sum momentum for all charged particles in each event. Although this neglects the momentum carried away by neutral particles, it roughly approximates the total momentum of the pp collision. Add the following to ```kinematics.py```.

```python
px_histogram = ROOT.TH1F("px", "px", 100, -1000.0, 1000.0)
py_histogram = ROOT.TH1F("py", "py", 100, -1000.0, 1000.0)
pz_histogram = ROOT.TH1F("pz", "pz", 100, -1000.0, 1000.0)

events.toBegin()                # start event loop from the beginning
for event in events:
    event.getByLabel("generalTracks", tracks)
    total_px = 0.0
    total_py = 0.0
    total_pz = 0.0
    for track in tracks.product():
        total_px += track.px()
        total_py += track.py()
        total_pz += track.pz()
    px_histogram.Fill(total_px)
    py_histogram.Fill(total_py)
    pz_histogram.Fill(total_pz)
    # no break statement; we're looping over all events

c = ROOT.TCanvas ("c" , "c", 800, 800)
px_histogram.Draw()
c.SaveAs("track_px.png")
py_histogram.Draw()
c.SaveAs("track_py.png")
pz_histogram.Draw()
c.SaveAs("track_pz.png")
```

While this is running, ask yourself what you expect the total_px, total_py, total_pz distributions should look like. (It can take a few minutes; Python is slow when used on large numbers of events.) Can you explain the relative variances of the distributions? 

Finally, let's look for resonances. Given two tracks,   

```python
one = tracks.product()[0]
two = tracks.product()[1]
```

the invariant mass may be calculated as 

```python
total_energy = math.sqrt(0.140**2 + one.p()**2) + math.sqrt(0.140**2 + two.p()**2)
total_px = one.px() + two.px()
total_py = one.py() + two.py()
total_pz = one.pz() + two.pz()
mass = math.sqrt(total_energy**2 - total_px**2 - total_py**2 - total_pz**2)
```

However, this quantity has no meaning unless the two particles are actually descendants of the same decay. Two randomly chosen tracks (out of hundreds per event) typically are not.

To increase the chances that pairs of randomly chosen tracks are descendants of the same decay, consider a smaller set of tracks: muons. Muons are identified by the fact that they can pass through meters of iron (the CMS magnet return yoke), so muon tracks extend from the silicon tracker to the muon chambers (see CMS quarter-view below), as much as 12 meters long! Muons are rare in hadron collisions. If an event contains two muons, they often (though not always) come from the same decay. 

![](https://raw.githubusercontent.com/LongLivedSusy/cmsdas/master/tracking/cms_quarterview.png) 

Normally, one would access muons through the reco::Muon object since this contains additional information about the quality of the muon hypothesis. For simplicity, we will access their track collection in the same way that we have been accessing the main track collection. We only need to replace "generalTracks" with "globalMuons". Add the following loop to ```kinematics.py```. 

```python
events.toBegin()
for i, event in enumerate(events):
    if i >= 5: break            # only the first 5 events
    print "Event", i
    event.getByLabel("globalMuons", tracks)
    for j, track in enumerate(tracks.product()):
        print "    Track", j, track.charge()/track.pt(), track.phi(), track.eta(), track.dxy(), track.dz()
```

Notice how few muon tracks there are compared to the same code executed for "generalTracks". In fact, you only see as many muons as you do because this data sample was collected with a muon trigger. (The muon definition in the trigger is looser than the "globalMuons" algorithm, which is why there are some events with fewer than two "globalMuons".)

<b>Exercise: Make a histogram of all dimuon masses from 0 to 5 GeV.</b> Exclude events that do not have exactly two muon tracks, and note that the muon mass is 0.106 GeV. Create a file ```dimuon_mass.py``` for this purpose.

Once you've implemented this, you can take a look at the solution ![here](/tracking/solution2.md).

## 3.) Track-level analysis

Now that you got your feet wet with tracking, we can start with the disappearing track search. In this section, you will take a closer look at the properies of disappearing tracks and develop a method to identify them in events.

### 3.a) Tracking variables

In the following, we will be working with ntuples which contain a selection of useful tracking variables. They have been created from AOD and miniAOD datasets which you've used in the previous section. For this section in particular, ntuples which only contain tracks are used. From each event in the considered datasets, tracks with pT>10 GeV were stored in the ntuple.

Let's start by having a look at some of the tracking variables of signal tracks:
```bash
root -l root://cmseos.fnal.gov//store/user/cmsdas/2020/long_exercises/DisappearingTracks/track-tag/tracks-pixelonly/signal.root 
root -l root://cmseos.fnal.gov//store/user/cmsdas/2020/long_exercises/DisappearingTracks/track-tag/tracks-pixelstrips/signal.root 
root [0] new TBrowser
```
With TBrowser, open the "PreSelection" tree and take a look at the variables. The tree contains variables from the track objets such as pT, eta and phi as well as variables from the hitpattern, such as nValidPixelHits or nMissingOuterHits. Also, for each track a selection of corresponding event-level properties as MET and HT are also stored.

Take some time to think about which variables could be relevant for tagging disappearing tracks. The track length is connected to the number of hits and layers with a measurement. Missing inner, middle, and outer hits indicate missing hits on the track trajectory adjacent to the interaction point, within the sequence of tracker hits, and adjacent to the ECAL, respectively. DxyVtx and dzVtx indicate the impact parameter with respect to the primary vertex.

One aspect of a disappearing track is that it has some number of missing outer hits. You can correlate this property with other variables, such as the impact parameter:
```bash
root [0] PreSelection->Draw("nMissingOuterHits")
root [0] PreSelection->Draw("nMissingOuterHits:dxyVtx", "dxyVtx<0.1", "COLZ")
root [0] PreSelection->Draw("nMissingOuterHits:dxyVtx", "dxyVtx<0.01", "COLZ")
```
You are looking at a couple of observables that are key to selecting signal disappearing tracks.

### 3.b) Plot signal and background

We will now plot the signal alongside with the stacked main MC backgrounds on track level. The script ```plot_track_variables.py``` contains some predefined plots for ```treeplotter.sh```:

```bash
$ cd tools
$ ./plot_track_variables.py
```

<b style='color:black'>Exercise: Create plots of all variables to familiarize yourself with the tracking properties.</b>

The plots will appear in the `/plots` folder.

Add your own cut (e.g. a higher cut on pT): Set

```python
my_cuts = "pt>50"
```

### 3.c) Disappearing track tag (training a BDT)

After having looked at some of the tracking variables, you now have to develop a set of criteria for selecting disappearing tracks that discriminates between such tracks and the Standard Model (SM) background. One approach is to choose a set of thresholds (cuts) to apply to the relevant track properties by hand/eye. By applying these cuts to simulated signal and background samples, one can evaluate performance of the cuts. With the large number of tracking variables available, however, it is worthwhile to consider other approaches, such as a random grid search (RGS) or a boosted decision tree (BDT). In the following, we will train a BDT for the track selection.

#### Track categorization

We define two basic track categories. Tracks which are reconstructed in the pixel tracker are classified as pixel-only tracks, while tracks in both the pixel and strips tracker are classified as pixel+strips tracks:
* pixel-only tracks: equal number of pixel and tracker layers with measurement
* pixel+strips tracks: tracker layers with measurement > pixel layers with measurement

#### Boosted decision trees

The Boosted decision tree is a rather popular type of multivariate classifier. An introduction to boosted decision trees is given [here](http://www.if.ufrj.br/~helder/20070706_hh_bdt.pdf). What most multivariant classifiers have in common, including BDTs, is that they take as input a set of properties (measurable numbers) of a signal event candidate, and output (typically a single) number that indicates how likely it is the event corresponds to true signal. We will train two separate BDTs, one for each track category, using TMVA ([Toolkit for Multivariate Analysis](https://root.cern/tmva)) included in ROOT.

In the exercise repository, change into track-selection and prepare a CMSSW 8.0.28 environment in order to use the correct TMVA version for the exercise:
```bash
$ cd track-tag
$ cmsrel CMSSW_8_0_28
$ cd CMSSW_8_0_28/src
$ cmsenv
$ cd -
```

Test your TMVA setup by running a minimal example:

```bash
$ ./run_tmva.sh <tag>
```

This will create a subdirectory named "tag" where the output of the BDT is stored. The configuration and training of the BDT is set up in a ROOT macro, tmva.cxx. If everything went well, you will see the TMVA GUI which you can use to evaluate the training and how well you did:

<center>

![](https://raw.githubusercontent.com/LongLivedSusy/cmsdas/master/etc/tmva-gui.png)
</center>

You can find the TMVA documentation [here](https://root.cern.ch/download/doc/tmva/TMVAUsersGuide.pdf). The most imporant functions accessible here are:
* 1a) View input variables
* 4a) View BDT response of the test sample
* 4b) View BDT response of both test & training sample
* 5a) View ROC curve

You can use button (1a) to take a look at the normalized signal and background plots of the input variables. In the minimal example, only the impact parameter dz with respect to the primary vertex and the number of tracker layers with measurement are used.
For each event, the BDT gives a BDT classifier ranging from -1 to 1 and indicates whether the event is background- or signal-like. A plot showing this classifier is accessible with button (4a). In this plot, we want to aim for a good separation between signal and background, which would allow us to put a cut on the BDT classifier to select disappearing tracks (signal).

By default, TMVA uses half of the input samples for training, the other half for testing. As the training should be general and not specific to one half of the dataset, the testing sample is used to verfiy no overtraining has taken place. Button (4b) shows an overlay of the BDT response plot for both the test sample and training sample, which ideally should look the same.

Button (5a) reveals the "receiver-operator curve", or ROC. For each event, the signal eff(sg) and background efficiencies eff(bg) are calculated. The background rejection efficiency is 1-eff(bg). The ROC curve is used to select a a point with high signal and high background rejection efficiency, which is linked to a cut on the BDT classifier.

Have a look at the tmva.cxx macro. On the top, you can specify whether you want to train using pixel-only or pixel+strips tracks by adjusting the path. After that, the signal and the relevant background files are added:

* (W &rightarrow; l&nu;) + jets binned in H<sub>T</sub>
* tt&#773; + jets binned in H<sub>T</sub>
* (Z/&gamma;* &rightarrow; l<sup>+</sup>l<sup>-</sup>) + jets (Drell-Yan) binned in H<sub>T</sub>

Each sample is added to TMVA with the correct weight of cross section * luminosity / number of events.

Below that, you can add/modifiy variables used for the training, with 'F' indicating float and 'I' indicating integer variables:

```c++
factory->AddVariable("dzVtx",'F');
factory->AddVariable("nValidTrackerHits",'I');
```

The configuration of the BDT is made with

```c++
factory->BookMethod(TMVA::Types::kBDT, "BDT", "NTrees=200:MaxDepth=4");
```

where we configure a BDT with 200 trees and a maximum depth of 4.

Relevant tracking variables available in the tree are:
* chargedPtSum, the sum of charged particles around a small cone around the track
* chi2perNdof, indicating the goodness of the track fit
* deDxHarmonic2, the deposited energy per distance
* dxyVtx and dzVtx, the impact parameter indicating the displacement of the track with respect to the primary vertex
* eta, phi, pt, the kinematic variables
* matchedCaloEnergy, the deposited energy in the calorimeter for a small cone around the track
* nMissing*Hits, missing hits on the track trajectory (no hits detected)
* nValid*Hits, number of hits of the track
* pixel/trackerLayersWithMeasurement, number of tracker layers with measurement
* ptErrOverPt2, the error on pT divided by pT^2
* trackQuality*, a set of track quality criteria. High purity tracks are recommended
* trkRelIso, the track isolation

<b style='color:black'>Exercise: Find the best combination of input variables and the best BDT configuration. Compare different ROCs and check for overtraining to get the maximum in signal and background rejection efficiency.</b>

##### Some hints:
The TCut variables "mycuts" and "mycutb" can be used to apply cuts before the BDT training. This can be useful to exclude certain ranges of input parameters to improve BDT performance, as well as to set the number of signal and background events used for training and testing. The latter may become necessary when exploring many different TMVA configurations. For example, to consider only tracks with pT>50 GeV and 100 events for training and testing in total, write:

```c++
TCut mycuts = ("pt>50 && event<100");
TCut mycutb = ("pt>50 && event<100");
```

Note that by changing the number of events, you need to adjust the "Nev" variable for each signal and background sample as well in order to use the correct weighting.

##### Comparing TMVA results

TMVA stores the output by default in "output.root" and a folder containing the weights of the BDT along with a C helper class to apply the weights to a given event. You can use tmva_comparison.py to overlay different ROC curves, which you can specify in the last line: 
Add a line for each BDT you'd like to compare, with the appropriate directory defined by the tag provided earlier.
```python
cfg_dict = {
    "configuration 1": ["./path/to/tmva/output.root", "/eos/uscms/store/user/cmsdas/2020/long_exercises/DisappearingTracks/track-tag/tracks-pixelonly/*.root", "samples.cfg"],
   }
```

Run it with

```bash
$ python tmva_comparison.py
```

##### Selecting a lower cut on the BDT classifier

After you have decided on a BDT configuration, you need to select a lower cut on the BDT classifier to separate signal tracks. One possible way to do this is to calculate the significance Z = S/sqrt(S+B) for each combination of signal and background efficiency, and then to determine the BDT classifier value with the highest significance:
First update the last line of best_tmva_significance.py to point to your output root file.

```bash
$ python best_tmva_significance.py
```

This script will produce a similar plot as when accessing button (5a), but gives you greater flexibility and considers the total amount of signal and background tracks used in the training.

We will provide two BDTs for pixel-only and pixel+strips tracks which you can compare your performance against. You can later include your best BDTs in the Friday presentation.

You have now learned how to train a BDT with signal and background samples and to come up with a first track tag for disppearing tracks. A similar track tag is used in the skims provided in the following sections.

## 4.) Event-based analysis

Background skim files have been Let's make some distributions of various event-level quantities, 
comparing signal and background events. 

### 4.a) Background events

```bash
python tools/CharacterizeEvents.py
```

This script created histograms with a minimal set of selection, 
and saved them in a new file called canvases.root. Open up canvases.root 
and have a look at the canvases stored there. 

```
root -l canvases.root
[inside ROOT command prompt]: TBrowser b
```

After clicking through a few plots, can you identify which are the 
main backgrounds? 

<b style='color:black'>Question 1: What is the main background in 
events with low missing transverse momentum, MHT?</b>

<b style='color:black'>Question 2: What is the main background in 
events with at least 2 b-tagged jets?</b>

### 4.b) Skimming signal events 

We'd like to overlay some signal distributions onto these plots, 
but there are currently no skims for the signal. We are interested in a wide range of 
signal models, but we will consider the important example of gluino pair production,
with a small mass splitting between the gluino and LSP, called T1qqqqLL(1800,1400,30); 
where 1800 GeV is the gluino mass, 1400 is the LSP mass, and the chargino proper decay 
length is 30 cm. Have a look  in the pre-made pyroot script to skim signal events, 
tools/SkimTreeMaker.py, and after a quick glance, run the script:

```bash
python tools/SkimTreeMaker.py /eos/uscms/store/user/cmsdas/2020/long_exercises/DisappearingTracks/Ntuples/g1800_chi1400_27_200970_step4_30.root
```


<b style='color:black'>Question 3: How many skimmed events are there?</b>

Create a directory called Signal for the new file, move the new file into Signal/ 
and re-run the plot maker:

```bash
mkdir Signal
mv skim_g1800_chi1400_27_200970_step4_30.root Signal/
python tools/CharacterizeEvents.py
root -l canvases.root
```

This folder you created is special and is recognized by name by the code. Clicking around on the canvases, you will now be able to see the signal overlaid (not stacked). Can you identify any observables/kinematic regions where the signal-to-background ratio looks more favorable? Look at several observables and try to come up with a set of cuts that improves the sensitivity. Your selection can be tested by adding elements to the python dictionary called ```cutsets``` in ```tools/CharacterizeEvents.py.``` Hint: the most useful observables have distributions that are different in shape between signal and background.

<b style='color:black'>When you have a decent set of selection and nice looking plots, you can save the canvases as pdfs for the record. </b>

You just performed a so-called eyeball optimization. Can you count the total weighted signal and background events that pass your selection? Write these numbers down in a safe place; we can use them later.

<b style='color:black'>Question 4: How many weighted signal and background events were there passing your selection? What was the expected significance, in terms of s/sqrt(s+b)</b>

## 4.c) Cut-based optimization (RGS)

Let's get systematic with the optimization. Many tools exist that help to select events with a good sensitivity. The main challenge is that an exaustive scan over all possible cut values on all observables in an n-dimensional space of observables becomes computationally intensive or prohibitive for n>3. 

One interesting tool that seeks to overcome this curse of dimensionality is called a random grid search (RGS), which is documented in the publication, "Optimizing Event Selection with the Random Grid Search" https://arxiv.org/abs/1706.09907. RGS performs a scan over the observable hyperplane, using a set of available simulated signal (or background) events to define steps in the scan. For each step in the scan (each simulated event), a proposed selection set is defined taking the cut values to be the values of the observables of the event. We are going to run RGS on the signal/background samples, and compare the sensitivity of the selection to the hand-picked cuts you obtained previously.  


```bash
#git clone https://github.com/hbprosper/RGS.git
git clone https://github.com/sbein/RGS.git
cd RGS/
make
source setup.sh #whenever intending to use RGS
cd ../
pwd
```
Note: Harrison Prosper's repo is the master and has a nice readme; but for some reason does not work with the exercise at the moment. 

The first script to run is tools/rgs_train.py. Open this script up, edit the lumi appropriately (to 35900/pb), give the path to the signal event file you just created, and tweak anything else as you see fit. When finished, save and open tools/LLSUSY.cuts. This file specifies the observables you want RGS to scan over and cut on, as well as the type of cut to apply (greater than, less than, equal to, etc.). Run the (first) training RGS script:

```bash
python tools/rgs_train.py
```
This creates the file LLSUSY.root which contains a tree of signal and background counts for each possible selection set in the scan. To determine the most optimal cut set, run the (second) analysis RGS script:

```bash
python tools/rgs_analysis.py
```
This will print the optimum set of thresholds to the screen, as well as the signal and background count corresponding to each set of cuts, and an estimate of the signal significance, z.  How does the RGS optimal selection compare to your hand-picked selection? Hopefully better - if not, you are pretty darn good at eyeball optimization!

You'll have noticed the script also draws a canvas. The scatter plot depicts the ROC cloud, which shows the set of signal and background efficiencies corresponding to each step of the scan. The color map in the background indicates the highest value of the significance of the various cut sets falling into each bin. 

Open up tools/rgs_analysis.py and have a look. You'll notice the significance measure is the simplified z = s/sqrt(b+db^2), where the user can specify the systematic uncertainty (SU) db. The fractional SU is currently set to 0.05. Try changing this value to something larger and rerunning rgs_analysis.py script. 

<b style='color:black'>Question 5. What happened to the optimum thresholds after doubling the SU? How about the expected significance? </b>

<b style='color:black'>Question 6. What value of the systematic uncertainty would correspond to a significance of 2 sigma? This is the worst case uncertainty that would allow us to exclude this signal model. </b>

## 5.) Background estimation

There are two main sources of backgrounds contributing to the search, *prompt* and *fake* background. The prompt background is due to charged leptons which failed the lepton reconstruction, but leave a track in the tracker and are thus not included in the ParticleFlow candidates. Fake tracks originate from pattern recogniction errors, which produce tracks not originating from real particles.

A trustworthy determination for these types of backgrounds requires a data-diven method. A general introduction to data-diven methods is given [here](http://www.desy.de/~csander/Talks/120223_SFB_DataDrivenBackgrounds.pdf).
 
### 5.a) Prompt background

The prompt background is the name given to SM events with a disappearing track that arises because of the presence of a true electron. The method for estimating this background is based on there being a relationship between the single-lepton control region and the single-disappearing track region. Transfer factors (kappa factors) are derived that relate the count in the single lepton control region to the count in the signal region. 

The single-lepton control region is defined as being analogous to the signal region, but where the requirement of there being 1 disappearing track is replaced by the requirement of there being one well-reconstructed lepton:

n(bkg in SR) = kappa * n(single lepton)

Kappa factors are derived using a data-driven tag and probe method. A well-reconstructed lepton is identified as the tag, and the event is checked for an isolated track (probe) that can be paired with the tag such that the invariant mass of the pair falls within 20 GeV of the Z mass, 90 GeV. In such a case, the track is identified as either being a well-reconstructed lepton, a disappearing track, or neither. The ratio of probes that are disappearing tracks to probes that are well-reconstructed leptons is taken as the estimate of kappa. 

#### step 1. Create histograms for deriving kappa factors

The following command will run a script that generates histograms for the numberator (disappearing tracks) and denominator (prompt leptons) that are needed compute kappa:

```bash
python tools/TagNProbeHistMaker.py --fnamekeyword Summer16.DYJetsToLL_M-50_Tune --dtmode PixAndStrips
```

When the script has finished running, you can run the fairly generic script,
```bash
python tools/OverlayTwoHists.py
```

, which, as the name suggests, overlays two histograms and creates a ratio plot - in this case, it is taking actual histograms from your file. You'll notice that the statistics are very low. **Question: What are you looking at? What is its relevance to the analysis?** There is one bug in the tag and probe script. The tag lepton pT is too small small to be realistic in real data. For this part of the analysis in data, we'll use a single electron and single muon trigger with online thresholds of around 20-27 GeV. You should update the pT threshold on the tag.  

One of you (maybe not all) can proceed to do a larger submission on the condor batch system, which will generate a higher statistics version of these plots. The script SubmitJobs_condor.py creates one job per input file, running the script specified in the first argument over each respective file. The output file for each job will be delivered to your Output directory. 
```bash
mkdir output/
mkdir jobs/

python tools/SubmitJobs_fnal.py --analyzer tools/TagNProbeHistMaker.py --fnamekeyword DYJetsToLL --dtmode PixAndStrips
python tools/SubmitJobs_fnal.py --analyzer tools/TagNProbeHistMaker.py --fnamekeyword DYJetsToLL --dtmode PixOnly

```
After the jobs are submitted, the status of the jobs can be checked by:
```bash
condor_q | <your user name> 
#or simply
condor_q 
```

When the jobs are finished, merge the files using an hadd (pronounced like "H"-add) command, After that, we'll proceed to computing the kappa factors from the merged histogram file: 

```bash
mkdir RawKappaMaps
python tools/mergeMcHists.py "RawKappaMaps/RawKapps_DYJets_PixOnly.root" "output/DYJetsToLL/TagnProbeHists_Summer16.DYJetsToLL_M-50_HT-600to800_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_*PixOnly*.root"
python tools/mergeMcHists.py "RawKappaMaps/RawKapps_DYJets_PixAndStrips.root" "output/DYJetsToLL/TagnProbeHists_Summer16.DYJetsToLL_M-50_HT-600to800_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_*PixAndStrips*.root"
```

You should now have some higher statistics versions of your invariant mass plots. You can modify the OverlayTwoHists.py to draw the new plots.

It is recommended to backup your files in RawKappaMaps:
```bash
mv RawKappaMaps RawKappaMaps_backup
cp -r /uscms_data/d3/sbein/RawKappaMaps .
```

You now have access to the tag and probe histograms from MC and data. Too see the tag and probe invariant mass distributions in data and MC, you can do:

```bash
mkdir pdfs
mkdir pdfs/tagandprobe/
python tools/CompareInvariantMass.py
```

You can scp and browse through your new files and look at the distributions of the invariant masses. For a given plot, what is the meaning of each histogram?
#### step 2. Compute the kappa factors



To compute kappas from the merged histograms, and then proceed to view those kappa factors, create pdfs folders and run the following two scripts in sequence:
```bash
mkdir pdfs/closure
mkdir pdfs/closure/tpkappa
source bashscripts/doKappFitting.sh
python tools/PlotKappaClosureAndData.py PixOnly && python tools/PlotKappaClosureAndData.py PixAndStrips
```
The script doKappFitting.sh calls the same python code python/ComputeKappa.py for the various tag and probe categories (electron, muon, long, short, barrel, endcap). It creates pdfs files which you can scp locally and look at. If you're curious about the fitting, have a look in ComputeKappa.py to see the functional form; it can be changed and tweaked if necessary to see how the pdfs change. The current choice is purly emperical. You might find it useful to use a log scale when answering the next question.
<b style='color:black'>Question 7. How do the fit functions perform? You can modify them in the script that computes kappa. Do you notice anything distinct about the shape of kappa as a function of pT? Eta?</b>


#### step 3. peform closure test
Step 3 : Construct a **single lepton CR** and weight each event by the corresponding kappa factor. The result is the **background prediction in the SR** for the prompt electrons. The script called PromptBkgHistMaker.py creates histograms of these two populations, as well as the **"true" distributions**, which of course consist of events with a disappearing track in the signal region:

```bash
python tools/PromptBkgHistMaker.py --fnamekeyword Summer16.WJetsToLNu_HT-800To1200
```

If the script runs ok, edit it and add your new signal region from the RGS optimization, and then do another test run to ensure there is no crash. Then, again please just one of you, can proceed to submit a large number of jobs:

```bash
python tools/SubmitJobs_fnal.py --analyzer tools/PromptBkgHistMaker.py --fnamekeyword Summer16.WJetsToLNu
```

After a few jobs accrue a bit in the Output directory, an hadd of the output files is in order, as done previously. Again, I realize it is likely that one of your group mates did the submission so be sure to get the full path to their Output directory. 

Step 4: The histograms generated by this script are sufficient to generate a so-called *closure test.* Closure is a consistency check between the data-driven prediction and the truth in the signal region, all performed in simulation. 

```bash
mkdir pdfs/closure/prompt-bkg/
python tools/mergeMcHists.py output/totalweightedbkgsDataDrivenMC.root "output/Summer16.WJetsToLNu/PromptBkgHists_*Tune*.root"
#python tools/closurePromptBkg.py <inputFile.root> <outputFile.root>
python tools/closurePromptBkg.py output/totalweightedbkgsDataDrivenMC.root outputClosure.root
```

You can also copy the real data versions of the control region histograms:

```bash
cp /eos/uscms/store/user/cmsdas/2020/long_exercises/DisappearingTracks/totalweightedbkgs*.root output/
cp -r /eos/uscms/store/user/cmsdas/2020/long_exercises/DisappearingTracks/mergedRoots .

Actually do:
xrdcp root://cmseos.fnal.gov//store/user/cmsdas/2020/long_exercises/DisappearingTracks/totalweightedbkgsDataDrivenMC.root output/
xrdcp root://cmseos.fnal.gov//store/user/cmsdas/2020/long_exercises/DisappearingTracks/totalweightedbkgsTrueFit.root
mkdir mergedRoots
for i in `eosls /eos/uscms/store/user/cmsdas/2020/long_exercises/DisappearingTracks/mergedRoots`; do xrdcp root://cmseos.fnal.gov//store/user/cmsdas/2020/long_exercises/DisappearingTracks/mergedRoots/$i .;  done

```

It is also important to validate the procedure in the real data. A good test region is a ttbar-enhanced control region, where we select one good muon or electron and at least one b-tagged jet. The test is made in the low MHT sideband from 100-250:

```bash
mkdir pdfs/closure/prompt-bkg-validation/
python tools/closureDataValidation.py
```

### 5.b) Fake track background

Another source of background are fake tracks, which are not from real particles but originate from pattern recognition errors in the tracking algorithm. Such tracks are also expected to have higher impact parameters (dxy, dz) as they do not necessarily seem to originate from the primary vertex.

#### Identifying fake tracks

The following figure shows a (somewhat extreme) example how pattern recognition errors might occur, with hits in the tracking layers indicated as red and valid tracks marked as black. A large number of possible tracks corresponding to hits in the tracker poses a combinatorial problem and can cause fake tracks (violet) to occur:

<center>

![](https://raw.githubusercontent.com/LongLivedSusy/cmsdas/master/tools/EstimateBackground/FakeBkg/fakes.png)
</center>

In addition, the hits marked in red can be valid hits or hits due to detector noise, thus providing another (connected) source of fake tracks.

#### Fake rate

We need to determine the expected number of disappearing tracks in a given kinematic region due to fakes. For each signal region (SR), we construct one control region (CR), which has the exact same selection as usual but with zero disappearing tracks. We can then apply a fake rate as weights to the control region events, where the fake rate is the probability for an event to contain a fake disappearing track:

fake rate = # events with n(DT)≥1 / # events with n(DT)≥0 ≈  # events with n(DT)≥1 / # events with n(DT)=0

The number of events due to fake disappearing tracks is then

N(SR, fakes) = fake rate * N(CR)

#### Drell-Yan event cleaning

There are different approaches to measure the fake rate. One approach is to use clean Drell-Yan events with low MET. Any track of such events which passes the disappearing track tag can be considered as a fake track. Our signal region has zero leptons, thus we imitate Z→νν events by removing the leptons (referred to as *event cleaning*). We will recalculate HT, missing HT and the number of jets per event without the leptons. Any jet connected to one of the two leptons is then ignored as well.

<b>Exercise: Loops over the nutples and select events with exactly two reconstructed leptons with an invariant mass compatible with that of the Z mass (±10 GeV). Plot the invariant dilepton distribution for electrons and muons.</b> What requirements can you add to improve the event selection?

Some tips: You can use ```fakerate_loop.py``` to loop over the events of the ntuples. In the event loop, you can add the dilepton selection. Test the script with

```bash
./fakerate_loop.py root://cmseos.fnal.gov//store/user/lpcsusyhad/sbein/cmsdas19/Ntuples/Summer16.WJetsToLNu_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_163_RA2AnalysisTree.root test.root
```

Once you are ready to run over the complete set of ntuples using condor submission, first create a gridpack:

```bash
cd $CMSSW_BASE/..
tar -czf gridpack.tgz CMSSW_10_6_4
mkdir CMSSW_10_6_4/src/2020/tools/submission
mv gridpack.tgz CMSSW_10_6_4/src/2020/tools/submission/
cd -
```

Then submit your condor jobs:

```bash
./fakerate_submit.py
```

Afterwards, use ```fakerate_analyze.py``` to plot the dilepton invariant mass distribution. You should obtain a Z mass peak with only little QCD contribution.

Now, add the event cleaning in the main event loop:

```python
    # clean event (recalculate HT, MHT, n_Jets without the two reconstructed leptons):
    csv_b = 0.8838
    metvec = TLorentzVector()
    metvec.SetPtEtaPhiE(event.MET, 0, event.METPhi, event.MET)
    mhtvec = TLorentzVector()
    mhtvec.SetPtEtaPhiE(0, 0, 0, 0)
    jets = []
    n_btags_cleaned = 0
    HT_cleaned = 0
    
    for ijet, jet in enumerate(event.Jets):
        
        if not (abs(jet.Eta()) < 5 and jet.Pt() > 30): continue
        
        # check if lepton is in jet, and veto jet if that is the case
        lepton_is_in_jet = False
        for leptons in [event.Electrons, event.Muons]:
            for lepton in leptons:
                if jet.DeltaR(lepton) < 0.05:
                    lepton_is_in_jet = True
        if lepton_is_in_jet: continue
        
        mhtvec-=jet
        jets.append(jet)
        HT_cleaned+=jet.Pt()        
        if event.Jets_bDiscriminatorCSV[ijet] > csv_b: n_btags_cleaned+=1
        
    n_jets_cleaned = len(jets)
    MHT_cleaned = mhtvec.Pt()

    MinDeltaPhiMhtJets_cleaned = 9999   
    for jet in jets: 
        if abs(jet.DeltaPhi(mhtvec)) < MinDeltaPhiMhtJets_cleaned:
            MinDeltaPhiMhtJets_cleaned = abs(jet.DeltaPhi(mhtvec))
```

<b>Exercise: Add branches which contain the number of disappearing tracks per event and the number of disappearing tracks per event due to fake tracks. Apply your signal region cuts as well. Then, plot these new branches and calculate the fake rate.</b>

There is likely a prompt background contamination in the selected events, which you can measure in the following.

<b>Exercise: Check the generator information (MC truth) to verify that a disappearing track is not due to a charged genParticle.</b> For each track, loop over the generator particles and do a ΔR matching with a small cone (ΔR<0.01). Save the number of disappearing tracks per event which are not due to a genParticle in a new branch.

Now you can determine the fake rate in your signal region with and without the MC truth information. The difference between the two rates is then the prompt background contribution, which you can express as a factor.

## 7) Limit 

Congratulations, you've made it! We can now put exlusion limits on the production cross section of the signal process. Since the data is still blinded for this analysis, we will calculate 95% CL expected limits.

First, let's install the [Higgs combine](https://cms-hcomb.gitbooks.io/combine/content/) tool. It is recommended to run ``combine`` in a CMSSW 8.1.0 environment. Change to the parent directory of your CMSSW_10_1_0 folder, then do:

```bash
export SCRAM_ARCH=slc6_amd64_gcc530
cmsrel CMSSW_8_1_0
cd CMSSW_8_1_0/src 
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v7.0.10
scramv1 b clean; scramv1 b # always make a clean build
```

Prepare an example datacard file called ``test``, which contains a single "tthhad" bin and a single nuisance parameter (an uncertainty of the luminosity measurement of 2.5%). For signal and background, the event count is entered into the datacard:

```
------------------------------------
imax 1 number of bins
jmax 1 number of backgrounds
kmax 1 number of nuisance parameters
------------------------------------
bin          tthhad
observation  368
------------------------------------
bin          tthhad          tthhad
process      SIG             BKG
process      0               1
rate         0.6562          368
------------------------------------
lumi  lnN    1.025       1.025
```

Save this example datacard and run:

```bash
combine test
```

Now, let's calculate an expected limit for our analysis. Modify the datacard with the event counts you have determined and add the systematic uncertainties.
