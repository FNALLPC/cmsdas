from ROOT import *
from utils import *
gStyle.SetOptStat(0)
fname1 = '/uscms/home/rheller/nobackup/DisappearingTracks2020/output/DYJetsToLL_pixstrips_coarse.root'
#'TagnProbeHists_DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_104_nFiles1_PixAndStrips.root'
file1 = TFile(fname1)

hist1 = file1.Get('hInvMassEl_eta0to1.4442_pt30to2500_RECOden')
hist1int = hist1.Integral()
hist1.Scale(1.0/hist1.Integral())
histoStyler(hist1, kBlack)
hist1.GetYaxis().SetRangeUser(0.001,100)
hist2 = file1.Get('hInvMassEl_eta0to1.4442_pt30to2500_DTnum')
histoStyler(hist2, kAzure)
hist2int = hist2.Integral()
hist2.Scale(1.0/hist2.Integral())
hist2.GetYaxis().SetRangeUser(0.001,100)

kappa = hist2int/hist1int
print "Kappa is",kappa

c1 = mkcanvas('c1')
leg = mklegend(x1=.22, y1=.56, x2=.69, y2=.72, color=kWhite)
hratio = FabDraw(c1,leg,hist1,[hist2],datamc='MC',lumi=35.9, title = '', LinearScale=False, fractionthing='method / truth')
hratio.GetYaxis().SetRangeUser(0,2.5)
c1.Update()
pause()
