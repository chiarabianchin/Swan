#include <TTree.h>
#include <TH2F.h>
#include <TF2.h>
#include <TCanvas.h>
#include <TGraph.h>
#include <TLatex.h>

void draw_jobs(){
  TTree *offers = new TTree(); offers->ReadFile("offer_per_city.csv", "ID/I:latitude/F:longitude:city/I:NOffersPerCity");
  TH2F *hjobdensity = new TH2F("hjobdensity", "Number of job offers;longitude;latitude;# offers", 16, 2.3, 6.7, 12, 49., 52);
  hjobdensity->SetStats(kFALSE);

  TTree *cities = new TTree(); cities->ReadFile("cities_coord.csv", "City/C:latitude/F:longitude");
  Float_t lat, lon;
  TString cityname;
  cities->SetBranchAddress("latitude",&lat);
  cities->SetBranchAddress("longitude",&lon);
  //cities->SetBranchAddress("City",&cityname);
  Int_t n = cities->GetEntries();
  Float_t x[n], y[n];
  TString citylab[5] = {"Brussels", "Antwerp", "Namur", "Bruges", "Ghent"};
  for(Int_t i=0; i<cities->GetEntries(); i++){
    cities->GetEntry(i);

    y[i] = lat;
    x[i] = lon;
  }
  TGraph *gcities = new TGraph(n, x, y);
  gcities->SetName("gcities");
  gcities->SetMarkerStyle(kFullCircle);
  for(Int_t i=0; i<n; i++){

    TLatex *latex = new TLatex(gcities->GetX()[i], gcities->GetY()[i], citylab[i]);
    latex->SetTextSize(0.03);
    gcities->GetListOfFunctions()->Add(latex);
  }
  
  Int_t noffers;
  offers->SetBranchAddress("latitude",&lat);
  offers->SetBranchAddress("longitude",&lon);
  offers->SetBranchAddress("NOffersPerCity",&noffers);
  for(int i=0; i<offers->GetEntries(); i++){
    offers->GetEntry(i);
    hjobdensity->Fill(lon, lat, noffers);
  }
  
  //offers->Draw("latitude:longitude:NOffersPerCity>>hjobdensity", "", "colz");
  TCanvas *coffers = new TCanvas("coffers", "Number of job offers", 700, 600);
  coffers->cd();
  hjobdensity->Draw("colz");
  gcities->Draw("P");
  coffers->SaveAs("offers_per_city.jpg");
}
