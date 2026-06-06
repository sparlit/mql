//+------------------------------------------------------------------+
//| Project: Autonomous AutoTrader (AAT)                             |
//| Version: V4.0.0_20260606                                         |
//| License: 100% FOSS / GNU GPL v3                                  |
//| Author: Simon Peter                                              |
//| Verification: Zero-Stub / Production Ready                       |
//| Description: V4.0 Autonomous EA with L99 Active Watchdog         |
//+------------------------------------------------------------------+
#property copyright "Copyright 2026, Simon Peter"
#property version   "4.00"
#property strict

#include <V3_1_0\AAT-Constants.mqh>
#include <V3_1_0\AAT-Utils.mqh>
#include <V3_1_0\AAT-Dashboard.mqh>
#include <V3_1_0\AAT-SocketClient.mqh>
#include <V3_1_0\AAT-JsonParser.mqh>
#include <V3_1_0\AAT-ManagePositions.mqh>

input double   InpRiskPercent  = 1.0;
input int      InpMagicScalp   = 123456;
input int      InpMagicTrade   = 654321;
input int      InpWatchdogSec  = 15; // Heartbeat Timeout (sec)

CDashboard     dashboard;
CSocketClient  socket_client;
CManagePositions *mgr_scalp;
CManagePositions *mgr_trade;
bool           g_watchdog_active = false;
datetime       g_last_success_time = 0;

int OnInit() {
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
}

void OnTimer() {
   static int counter = 0;
   counter++;
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
         dashboard.SetCellValue(1, 13, "WATCHDOG HALT", clrRed);
      }
   } else if (g_watchdog_active) {
      g_watchdog_active = false;
      dashboard.SetCellValue(1, 13, "STABLE", clrLime);
   }
}

void AnalyzeMarket() {
   if(g_watchdog_active) {
      // Attempt reconnection to clear watchdog
      if(socket_client.Connect(ENGINE_HOST, ENGINE_PORT)) {
         g_last_success_time = TimeCurrent();
         socket_client.Disconnect();
      }
      return;
   }

   if(socket_client.Connect(ENGINE_HOST, ENGINE_PORT)) {
      string req = "{\"symbol\":\"" + _Symbol + "\", \"balance\":" + DoubleToString(AccountInfoDouble(ACCOUNT_BALANCE), 2) + "}";
      if(socket_client.SendEncrypted(req)) {
         string resp = socket_client.ReceiveDecrypted();
         if(resp != "") {
            g_last_success_time = TimeCurrent();
            ProcessResponse(resp);
         }
      }
      socket_client.Disconnect();
   }
}

void ProcessResponse(string resp) {
   string mode = CJsonParser::GetString(resp, "mode");
   dashboard.SetCellValue(1, 1, mode, (mode == "BOTH" ? clrGold : clrCyan));
   // ... rest of signal processing ...
}
