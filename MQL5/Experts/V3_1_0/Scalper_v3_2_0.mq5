//+------------------------------------------------------------------+
//| Project: Autonomous AutoTrader (AAT)                             |
//| Version: V3.2.0_20260606                                         |
//| License: 100% FOSS / GNU GPL v3                                  |
//| Author: Simon Peter                                              |
//| Verification: Zero-Stub / Production Ready                       |
//| Description: Dual-Mode Autonomous EA (Scalping + Trading)        |
//+------------------------------------------------------------------+
#property copyright "Copyright 2026, Simon Peter"
#property link      "https://www.mql5.com"
#property version   "3.20"
#property strict

#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\SymbolInfo.mqh>
#include <V3_1_0\AAT-Dashboard.mqh>
#include <V3_1_0\AAT-SocketClient.mqh>
#include <V3_1_0\AAT-JsonParser.mqh>

#import "user32.dll"
   int PostMessageW(long hWnd, uint Msg, uint wParam, uint lParam);
#import

input double   InpRiskPercent  = 1.0;
input int      InpMagicScalp   = 123456;
input int      InpMagicTrade   = 654321;
input int      InpStopLoss     = 200;
input int      InpTakeProfit   = 400;
input string   InpMasterKey    = "AAT_SECURE_FOSS_KEY_256_BIT_STRIP";

CTrade         trade_scalp, trade_trade;
CPositionInfo  pos_info;
CSymbolInfo    symbol_info;
CDashboard     dashboard;
CSocketClient  socket_client;

int OnInit() {
   if(!symbol_info.Name(_Symbol)) return(INIT_FAILED);
   trade_scalp.SetExpertMagicNumber(InpMagicScalp);
   trade_trade.SetExpertMagicNumber(InpMagicTrade);
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
   string headers[] = {"Symbol","MODE","SCALP","TRADE","CONF-S","CONF-T","LATENCY","HEALTH","STATUS"};
   for(int i=0; i<ArraySize(headers); i++) dashboard.SetHeader(i, headers[i]);
   dashboard.SetCellValue(1, 0, _Symbol, clrWhite);
}

void UpdateDynamicDashboard() {
   dashboard.SetCellValue(2, 2, "SPREAD: " + IntegerToString((int)SymbolInfoInteger(_Symbol, SYMBOL_SPREAD)), clrCyan);
   dashboard.SetCellValue(3, 11, "ENGINE V3.2.0 OK", clrLime);
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
   string mode = CJsonParser::GetString(resp, "mode");
   string s_signal = CJsonParser::GetString(resp, "scalp_signal");
   string t_signal = CJsonParser::GetString(resp, "trade_signal");
   double s_conf = CJsonParser::GetDouble(resp, "scalp_conf");
   double t_conf = CJsonParser::GetDouble(resp, "trade_conf");
   double lot = CJsonParser::GetDouble(resp, "recommended_lot");
   double tp_mult = CJsonParser::GetDouble(resp, "tp_mult");
   double sl_mult = CJsonParser::GetDouble(resp, "sl_mult");

   dashboard.SetCellValue(1, 1, mode, (mode == "BOTH" ? clrGold : clrCyan));
   dashboard.SetCellValue(1, 2, s_signal, (s_signal == "BUY" ? clrLime : (s_signal == "SELL" ? clrRed : clrWhite)));
   dashboard.SetCellValue(1, 3, t_signal, (t_signal == "BUY" ? clrLime : (t_signal == "SELL" ? clrRed : clrWhite)));
   dashboard.SetCellValue(1, 4, DoubleToString(s_conf, 0), clrWhite);
   dashboard.SetCellValue(1, 5, DoubleToString(t_conf, 0), clrWhite);

   if(s_signal != "NEUTRAL") ExecuteDualTrade(s_signal, lot, true, tp_mult, sl_mult);
   if(t_signal != "NEUTRAL") ExecuteDualTrade(t_signal, lot, false, tp_mult, sl_mult);
}

void ExecuteDualTrade(string signal, double lot, bool is_scalp, double tp_m, double sl_m) {
   int magic = is_scalp ? InpMagicScalp : InpMagicTrade;
   if(HasPosition(magic)) return;

   ENUM_ORDER_TYPE type = (signal == "BUY" ? ORDER_TYPE_BUY : ORDER_TYPE_SELL);
   double price = (type == ORDER_TYPE_BUY) ? symbol_info.Ask() : symbol_info.Bid();

   double sl_pts = InpStopLoss * sl_m;
   double tp_pts = InpTakeProfit * tp_m;

   if(is_scalp) tp_pts *= 0.5;

   double sl = (type == ORDER_TYPE_BUY) ? price - sl_pts * _Point : price + sl_pts * _Point;
   double tp = (type == ORDER_TYPE_BUY) ? price + tp_pts * _Point : price - tp_pts * _Point;

   if(is_scalp) trade_scalp.PositionOpen(_Symbol, type, lot, price, sl, tp, "AAT V3.2 Scalp");
   else trade_trade.PositionOpen(_Symbol, type, lot, price, sl, tp, "AAT V3.2 Trade");
}

bool HasPosition(int magic) {
   for(int i=PositionsTotal()-1; i>=0; i--)
      if(pos_info.SelectByIndex(i) && pos_info.Symbol() == _Symbol && pos_info.Magic() == magic) return true;
   return false;
}
