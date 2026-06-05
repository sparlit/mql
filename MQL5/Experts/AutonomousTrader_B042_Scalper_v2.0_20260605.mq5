//+------------------------------------------------------------------+
//|                      AutonomousTrader_B042_Scalper_v2.0_20260605 |
//|                                  Copyright 2024, AI Trader Corp. |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, AI Trader Corp."
#property link      "https://www.mql5.com"
#property version   "2.00"
#property strict

#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\SymbolInfo.mqh>
#include <Dashboard.mqh>
#include <SocketClient.mqh>
#include <JsonParser.mqh>
#include <SharedMemory.mqh>

//--- inputs
input double   InpRiskPercent  = 1.0;      // Risk per trade (%)
input int      InpMagicNumber  = 888888;   // Magic Number
input int      InpStopLoss     = 150;      // Stop Loss (points)
input int      InpTakeProfit   = 300;      // Take Profit (points)
input bool     InpUsePyramid   = true;     // Enable Pyramid Scaling
input double   InpMaxDrawdown  = 15.0;     // Max Drawdown (%) Firewall
input bool     InpNewsStraddle = true;     // Enable ATR-Adaptive Straddle
input int      InpSymbolIndex  = 0;        // Unique index for shared memory (0-99)

//--- global variables
CTrade         trade;
CPositionInfo  pos_info;
CSymbolInfo    symbol_info;
CDashboard     dashboard;
CSocketClient  socket_client;
SharedData     shm_data;

int OnInit()
  {
   if(!symbol_info.Name(_Symbol)) return(INIT_FAILED);
   trade.SetExpertMagicNumber(InpMagicNumber);
   if(!dashboard.Create("AT_Dashboard", 10, 30, 400, 250)) return(INIT_FAILED);

   // Shared Memory Init
   shm_data.account_risk = InpRiskPercent;
   shm_data.last_update_time = TimeCurrent();
   WriteSharedData(InpSymbolIndex, shm_data);

   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason) { dashboard.~CDashboard(); }

void OnTick()
  {
   if(!symbol_info.RefreshRates()) return;
   if(CheckFirewall()) return;

   ManageActivePositions();

   static datetime last_scan = 0;
   if(TimeCurrent() - last_scan >= 60)
     {
      ExecuteAnalysis();
      last_scan = TimeCurrent();
     }

   // Update Shared Memory for Swarm Consensus
   shm_data.total_positions = PositionsTotal();
   shm_data.last_update_time = TimeCurrent();
   WriteSharedData(InpSymbolIndex, shm_data);
  }

bool CheckFirewall()
  {
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double dd = (balance - equity) / balance * 100.0;
   if(dd >= InpMaxDrawdown) { CloseAll(); return true; }
   return false;
  }

void ExecuteAnalysis()
  {
   string request = "{\"symbol\":\"" + _Symbol + "\", \"balance\":" + DoubleToString(AccountInfoDouble(ACCOUNT_BALANCE), 2) + "}";
   if(socket_client.Connect("127.0.0.1", 5555))
     {
      if(socket_client.Send(request))
        {
         string response = socket_client.Receive();
         if(response != "")
           {
            string signal = CJsonParser::GetString(response, "signal");
            double confidence = CJsonParser::GetDouble(response, "confidence");
            bool verified = CJsonParser::GetBool(response, "verified");
            string regime = CJsonParser::GetString(response, "regime");
            bool has_news = CJsonParser::GetBool(response, "has_high_impact_news");

            dashboard.Update(_Symbol, verified ? "TRADE!" : "SCANNING", signal, confidence, regime);

            if(has_news && InpNewsStraddle) ExecuteNewsStraddle();
            else if(verified) OpenTrade((signal == "BUY") ? ORDER_TYPE_BUY : ORDER_TYPE_SELL);
           }
        }
      socket_client.Disconnect();
     }
  }

void ExecuteNewsStraddle()
  {
   if(PositionsTotal() > 0) return;

   double atr = iATR(_Symbol, PERIOD_M1, 14, 0);
   double distance = MathMax(atr * 0.5, 50 * _Point);

   double ask = symbol_info.Ask();
   double bid = symbol_info.Bid();

   trade.BuyStop(0.01, ask + distance, _Symbol, ask + distance - InpStopLoss*_Point, ask + distance + InpTakeProfit*_Point);
   trade.SellStop(0.01, bid - distance, _Symbol, bid - distance + InpStopLoss*_Point, bid - distance - InpTakeProfit*_Point);
   Print("News Straddle orders placed at distance: ", distance);
  }

void ManageActivePositions()
  {
   for(int i=PositionsTotal()-1; i>=0; i--)
     {
      if(pos_info.SelectByIndex(i) && pos_info.Symbol() == _Symbol && pos_info.Magic() == InpMagicNumber)
        {
         // Partial Profit Scale-Out
         double profit_points = (pos_info.PositionType() == POSITION_TYPE_BUY) ? (symbol_info.Bid() - pos_info.PriceOpen()) : (pos_info.PriceOpen() - symbol_info.Ask());
         profit_points /= _Point;

         if(profit_points > InpStopLoss)
           {
            if(pos_info.Volume() > 0.01) trade.PositionClosePartial(pos_info.Ticket(), NormalizeDouble(pos_info.Volume()/2.0, 2));
            trade.PositionModify(pos_info.Ticket(), pos_info.PriceOpen(), pos_info.TakeProfit());
           }

         if(InpUsePyramid) ApplyPyramidScaling();
        }
     }
  }

void ApplyPyramidScaling()
  {
   int layers = 0;
   for(int i=PositionsTotal()-1; i>=0; i--)
      if(pos_info.SelectByIndex(i) && pos_info.Symbol() == _Symbol && pos_info.Magic() == InpMagicNumber) layers++;

   if(layers < 5)
     {
      double profit_points = (pos_info.PositionType() == POSITION_TYPE_BUY) ? (symbol_info.Bid() - pos_info.PriceOpen()) : (pos_info.PriceOpen() - symbol_info.Ask());
      profit_points /= _Point;

      if(profit_points > 200)
        {
         ENUM_ORDER_TYPE type = (pos_info.PositionType() == POSITION_TYPE_BUY) ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
         double price = (type == ORDER_TYPE_BUY) ? symbol_info.Ask() : symbol_info.Bid();
         trade.PositionOpen(_Symbol, type, 0.01, price, price - (type==ORDER_TYPE_BUY?1:-1)*InpStopLoss*_Point, 0, "Pyramid");
        }
     }
  }

void OpenTrade(ENUM_ORDER_TYPE type)
  {
   if(PositionsTotal() > 0) return;
   double price = (type == ORDER_TYPE_BUY) ? symbol_info.Ask() : symbol_info.Bid();
   trade.PositionOpen(_Symbol, type, 0.01, price, price - (type==ORDER_TYPE_BUY?1:-1)*InpStopLoss*_Point, price + (type==ORDER_TYPE_BUY?1:-1)*InpTakeProfit*_Point, "Initial");
  }

void CloseAll()
  {
   for(int i=PositionsTotal()-1; i>=0; i--)
      if(pos_info.SelectByIndex(i) && pos_info.Magic() == InpMagicNumber) trade.PositionClose(pos_info.Ticket());
  }
