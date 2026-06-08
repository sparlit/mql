//+------------------------------------------------------------------+
//| Project: Autonomous AutoTrader (AAT)                             |
//| Version: V5.0.0_20260607                                         |
//| License: 100% FOSS / GNU GPL v3                                  |
//| Author: Simon Peter                                              |
//| Verification: Zero-Stub / Production Ready                       |
//| Description: V4.0 Autonomous EA with L99 Active Watchdog         |
//+------------------------------------------------------------------+
#property copyright "Copyright 2026, Simon Peter"
#property version   "4.00"
#property strict

#include <AAT-Constants.mqh>
#include <AAT-Utils.mqh>
#include <AAT-Dashboard.mqh>
#include <AAT-SocketClient.mqh>
#include <AAT-JsonParser.mqh>
#include <AAT-ManagePositions.mqh>

input string   InpMasterKey    = "AAT_SECURE_FOSS_KEY_256_BIT_STRIP";
input string   InpEngineHost   = "127.0.0.1";
input int      InpEnginePort   = 4444;
input double   InpRiskPercent  = 1.0;
input int      InpMagicScalp   = 123456;
input int      InpMagicTrade   = 654321;
input int      InpWatchdogSec  = 10; // Symmetric Heartbeat Timeout (sec)

CDashboard     dashboard;
CSocketClient  socket_client;
CManagePositions *mgr_scalp;
CManagePositions *mgr_trade;
bool           g_watchdog_active = false;
datetime       g_last_success_time = 0;
int            g_recovery_counter = 0;
int            g_trailing_points = 200;

int OnInit() {
   socket_client.SetSecurityKey(InpMasterKey);
   mgr_scalp = new CManagePositions(_Symbol, InpMagicScalp);
   mgr_trade = new CManagePositions(_Symbol, InpMagicTrade);
   if(!dashboard.Create(10, 10, 100, 30, 1200, 240)) return(INIT_FAILED);
   g_last_success_time = TimeCurrent();
   EventSetTimer(1);
   return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason) {
   delete mgr_scalp; delete mgr_trade;
   dashboard.Destroy();
}

void OnTick() {
   if(g_watchdog_active) return;
   mgr_scalp.Update();
   mgr_trade.Update();

   // Active Trailing Logic (Fix for Review)
   mgr_scalp.TrailingStop(g_trailing_points);
   mgr_trade.TrailingStop(g_trailing_points * 2);

   // Arbitrage Logic Evolution (AP 31)
   double current_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   CAATUtils::SetSharedBenchmark(_Symbol, current_price);

   double benchmark = CAATUtils::GetSharedBenchmark(_Symbol + "_REF");
   if(benchmark > 0) {
      double diff = MathAbs(current_price - benchmark) / SymbolInfoDouble(_Symbol, SYMBOL_POINT);
      if(diff > 50) { // 50 point discrepancy
         dashboard.SetCellValue(1, 14, "ARB ALERT", clrOrange);
         CAATUtils::LogInfo("Arbitrage Discrepancy detected: " + DoubleToString(diff, 1) + " points");
      } else {
         dashboard.SetCellValue(1, 14, "STABLE", clrLime);
      }
   }
}

void OnChartEvent(const int id, const long &lparam, const double &dparam, const string &sparam) {
   if(id == CHARTEVENT_CLICK) {
      int tab = dashboard.GetTabAt( (int)lparam, (int)dparam );
      if(tab >= 0) dashboard.SetTab(tab);
   }
}

void OnTimer() {
   static int counter = 0;
   counter++;

   socket_client.Update();
   if(socket_client.GetState() == STATE_COMPLETED) {
      string resp = socket_client.GetResponse();
      if(resp != "") {
         g_last_success_time = TimeCurrent();
         ProcessResponse(resp);
      }
   }

   if(counter >= 10) { AnalyzeMarket(); counter = 0; }

   CheckWatchdog();
}

void CheckWatchdog() {
   if(g_last_success_time > 0 && (TimeCurrent() - g_last_success_time) > InpWatchdogSec) {
      if(!g_watchdog_active) {
         CAATUtils::LogError("Watchdog", "Heartbeat Lost! Emergency Protocol Active.");
         mgr_scalp.EmergencyMoveToBE();
         mgr_trade.EmergencyMoveToBE();
         g_watchdog_active = true;
         g_recovery_counter = 0;
         dashboard.SetCellValue(1, 13, "WATCHDOG HALT", clrRed);
         // Logging via Socket is impossible if heartbeat lost, but we will log recovery once back.
      }
   }
}

void AnalyzeMarket() {
   // If stuck in ERROR, force disconnect to reset state back to IDLE
   if(socket_client.GetState() == STATE_ERROR) socket_client.Disconnect();

   if(socket_client.GetState() != STATE_IDLE) return;

   // Get Position State for Reconciliation
   string pos_json = "";
   for(int i=PositionsTotal()-1; i>=0; i--) {
      if(PositionSelectByTicket(PositionGetTicket(i))) {
         if(pos_json != "") pos_json += ",";
         pos_json += "{\"ticket\":" + IntegerToString(PositionGetInteger(POSITION_TICKET)) +
                     ",\"type\":" + IntegerToString(PositionGetInteger(POSITION_TYPE)) + "}";
      }
   }

   // Get OHLC Data for Primary Ingress (Priority 2)
   string ohlc_json = "";
   ENUM_TIMEFRAMES tfs[] = {PERIOD_M1, PERIOD_M5, PERIOD_M15, PERIOD_H1, PERIOD_H4, PERIOD_D1};
   string tf_names[] = {"M1", "M5", "M15", "H1", "H4", "D1"};

   for(int t=0; t<ArraySize(tfs); t++) {
      double closes[];
      if(CopyClose(_Symbol, tfs[t], 0, 5, closes) == 5) {
         if(ohlc_json != "") ohlc_json += ",";
         ohlc_json += "\"" + tf_names[t] + "\":[" +
            DoubleToString(closes[0], 5) + "," +
            DoubleToString(closes[1], 5) + "," +
            DoubleToString(closes[2], 5) + "," +
            DoubleToString(closes[3], 5) + "," +
            DoubleToString(closes[4], 5) + "]";
      }
   }

   string req = "{" +
      "\"symbol\":\"" + _Symbol + "\"," +
      "\"balance\":" + DoubleToString(AccountInfoDouble(ACCOUNT_BALANCE), 2) + "," +
      "\"equity\":" + DoubleToString(AccountInfoDouble(ACCOUNT_EQUITY), 2) + "," +
      "\"tick_value\":" + DoubleToString(SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), 5) + "," +
      "\"point\":" + DoubleToString(SymbolInfoDouble(_Symbol, SYMBOL_POINT), 8) + "," +
      "\"positions\":[" + pos_json + "]," +
      "\"ohlc\":{" + ohlc_json + "}" +
   "}";
   socket_client.AsyncRequest(InpEngineHost, InpEnginePort, req);
}

void ProcessResponse(string resp) {
   string status = CJsonParser::GetString(resp, "status");
   string health = CJsonParser::GetString(resp, "health");

   if(status == "success" && health == "OK") {
      if(g_watchdog_active) {
         g_recovery_counter++;
         dashboard.SetCellValue(1, 13, "RECOVERING " + IntegerToString(g_recovery_counter) + "/3", clrYellow);
         if(g_recovery_counter >= 3) {
            g_watchdog_active = false;
            g_recovery_counter = 0;
            CAATUtils::LogInfo("Watchdog Recovered. Resuming Operations.");
            dashboard.SetCellValue(1, 13, "STABLE", clrLime);
         }
      }
   } else {
      g_recovery_counter = 0;
   }

   string mode = CJsonParser::GetString(resp, "mode");
   dashboard.SetCellValue(1, 1, mode, (mode == "BOTH" ? clrGold : clrCyan));

   g_trailing_points = (int)CJsonParser::GetDouble(resp, "trailing_points");
   if(g_trailing_points <= 0) g_trailing_points = 200;
}
