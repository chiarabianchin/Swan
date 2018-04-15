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

  TString prov_wl[5] = {"WNA", "WLX", "WBR", "WHT", "WLG"};
  TString prov_fl[5] = {"VAN", "VWV", "VLI", "VOV", "VBR"};
  Int_t id_prov[11];
  for (Int_t i=0; i<11; i++){
    id_prov[i]=i;
  }
  Int_t pop_br = 1187890;
  Int_t pop_wl[5] = {489204,  280327,  396840, 1337157,1098688};
  Int_t pop_fl[5] = {1824136, 1181828,  863725,1486722, 1121693};
  Float_t pop_fl_tot = 0;
  Float_t pop_wl_tot = 0;
  Float_t pop_tot = 0;
  //TGraph *g_pop = new TGraph(11, id_prov, inhab);
  TH1I *h_pop_fl = new TH1I("h_pop_fl","Population Fl", 5, -0.5, 4.5);
  h_pop_fl->SetFillColor(kPink+9);
  TH1I *h_pop_wl = new TH1I("h_pop_wl","Population Wal", 5, 4.5, 9.5);
  h_pop_wl->SetFillColor(kOrange-1);
  TH1I  *h_pop_br= new TH1I("h_pop_br","Population per province; province; population", 11, -0.5, 10.5);
  h_pop_br->SetFillColor(kCyan-6);
  for (Int_t i=0; i<5; i++){
    h_pop_fl->SetBinContent(i+1, pop_fl[i]);
    h_pop_br->GetXaxis()->SetBinLabel(i+1, prov_fl[i]);
    pop_fl_tot+=pop_fl[i];
    h_pop_wl->SetBinContent(i+1, pop_wl[i]);
    h_pop_br->GetXaxis()->SetBinLabel(i+6, prov_wl[i]);
    pop_wl_tot+=pop_wl[i];
  }
  pop_tot = pop_wl_tot + pop_fl_tot + pop_br;
  h_pop_br->SetBinContent(11, pop_br);
  h_pop_br->GetXaxis()->SetBinLabel(11, "BRU");
  
  cout<<"Pop fl "<< pop_fl_tot<< " ->  "<< pop_fl_tot/pop_tot << endl;
  cout<<"Pop wl "<< pop_wl_tot << " ->  "<< pop_wl_tot/pop_tot << endl;
  cout<<"Pop br "<< pop_br << " ->  "<< pop_br/pop_tot << endl;
  
  
  //g_pop->SetNameTitle("gpop", "Population per province; province; population");
  //g_pop->SetMarkerStyle(kFullSquare);
  TCanvas *c_pop = new TCanvas("c_pop","Population per province");
  c_pop->cd();
  h_pop_br->Draw();
  h_pop_fl->Draw("sames");
  h_pop_wl->Draw("sames");

}
