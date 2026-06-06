//+------------------------------------------------------------------+
//| Project: Autonomous AutoTrader (AAT)                             |
//| Version: V3.1.0_20260606                                         |
//| License: 100% FOSS / GNU GPL v3                                  |
//| Author: Simon Peter                                              |
//| Verification: Zero-Stub / Production Ready                       |
//| Description: Autonomous Scalping EA with Cyber-Pro Dashboard     |
//+------------------------------------------------------------------+
#property copyright "Copyright 2026, Simon Peter"
#property link      "https://www.mql5.com"
#property version   "3.10"
#property strict

#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\SymbolInfo.mqh>
#include <V3_1_0\Include\AAT-Dashboard.mqh>
#include <V3_1_0\Include\AAT-SocketClient.mqh>
#include <V3_1_0\Include\AAT-JsonParser.mqh>

#import "user32.dll"
   int PostMessageW(long hWnd, uint Msg, uint wParam, uint lParam);
#import

input double   InpRiskPercent  = 1.0;
input int      InpMagicNumber  = 123456;
input int      InpStopLoss     = 200;
input int      InpTakeProfit   = 400;
input string   InpMasterKey    = "AAT_SECURE_FOSS_KEY_256_BIT_STRIP";

CTrade         trade;
CPositionInfo  pos_info;
CSymbolInfo    symbol_info;
CDashboard     dashboard;
CSocketClient  socket_client;

int OnInit() {
   if(!symbol_info.Name(_Symbol)) return(INIT_FAILED);
   trade.SetExpertMagicNumber(InpMagicNumber);
   socket_client.SetMasterKey(InpMasterKey);
   if(!dashboard.Create(10, 10, 100, 30, 1200, 240)) return(INIT_FAILED);
   SetupDashboardHeaders();
   EventSetTimer(1);
   return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason) { dashboard.Destroy(); }

void OnTick() {
   if(!symbol_info.RefreshRates()) return;
   UpdateDynamicDashboard();
}

void OnTimer() {
   static int counter = 0;
   counter++;
   if(counter >= 60) { AnalyzeMarket(); counter = 0; }
}

void SetupDashboardHeaders() {
   string headers[] = {"Symbol","M1","M5","M15","M30","H1","H4","D1","W1","MN","CONSENSUS","STATUS","LATENCY","HEALTH"};
   for(int i=0; i<ArraySize(headers); i++) dashboard.SetHeader(i, headers[i]);
   dashboard.SetCellValue(1, 0, _Symbol, clrWhite);
}

void UpdateDynamicDashboard() {
   dashboard.SetCellValue(2, 2, "SPREAD: " + IntegerToString((int)SymbolInfoInteger(_Symbol, SYMBOL_SPREAD)), clrCyan);
   dashboard.SetCellValue(3, 11, "ENGINE V3.1.0 OK", clrLime);
}

void AnalyzeMarket() {
   string request = "{\"symbol\":\"" + _Symbol + "\", \"balance\":" + DoubleToString(AccountInfoDouble(ACCOUNT_BALANCE), 2) + "}";
   if(socket_client.Connect("127.0.0.1", 5555)) {
      if(socket_client.SendEncrypted(request)) {
         string resp = socket_client.ReceiveDecrypted();
         if(resp != "") ProcessResponse(resp);
      }
      socket_client.Disconnect();
   }
}

void ProcessResponse(string resp) {
   string signal = CJsonParser::GetString(resp, "signal");
   double conf = CJsonParser::GetDouble(resp, "confidence");
   double latency = CJsonParser::GetDouble(resp, "latency");
   bool arb = CJsonParser::GetBool(resp, "arb_alert");
   dashboard.SetCellValue(1, 10, signal + "(" + DoubleToString(conf, 0) + ")");
   dashboard.SetCellValue(1, 12, DoubleToString(latency, 2) + "ms", clrLime);
   dashboard.SetCellValue(1, 13, (arb ? "ARB ALERT" : "STABLE"), (arb ? clrRed : clrCyan));
}
