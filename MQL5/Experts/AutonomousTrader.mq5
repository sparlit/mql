//+------------------------------------------------------------------+
//|                                              AutonomousTrader.mq5 |
//|                                  Copyright 2024, AI Trader Corp. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, AI Trader Corp."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict
#property description "Autonomous Autotrader with Real-time Dashboard"

//--- include files
#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\SymbolInfo.mqh>
#include <ChartObjects\ChartObjectsTxtControls.mqh>
#include <Dashboard.mqh>
#include <SocketClient.mqh>
#include <JsonParser.mqh>

//--- inputs
input double   InpRiskPercent  = 1.0;      // Risk per trade (%)
input int      InpMagicNumber  = 123456;   // Magic Number
input int      InpStopLoss     = 200;      // Initial Stop Loss (points)
input int      InpTakeProfit   = 400;      // Initial Take Profit (points)
input bool     InpTrailingSL   = true;     // Enable Trailing SL
input bool     InpTrailingTP   = true;     // Enable Trailing TP
input int      InpTrailingStep = 50;       // Trailing Step (points)

//--- global variables
CTrade         trade;
CPositionInfo  pos_info;
CSymbolInfo    symbol_info;
CDashboard     dashboard;
CSocketClient  socket_client;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
   Print("Initializing Autonomous Trader...");

   if(!symbol_info.Name(_Symbol))
     {
      Print("Error: Could not initialize symbol info");
      return(INIT_FAILED);
     }

   trade.SetExpertMagicNumber(InpMagicNumber);

   //--- Initialize Dashboard
   dashboard.Create(12, 7, 10, 30, 120, 22);
   dashboard.SetHeader(0, "Symbol");
   dashboard.SetHeader(1, "TF Analysis");
   dashboard.SetHeader(2, "Trend (H1)");
   dashboard.SetHeader(3, "Signal (Weighted)");
   dashboard.SetHeader(4, "Risk %");
   dashboard.SetHeader(5, "Market Regime");
   dashboard.SetHeader(6, "Autonomous Status");

   dashboard.SetCellValue(1, 0, _Symbol);
   dashboard.SetCellValue(1, 6, "Connecting...", clrYellow);

   return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   Print("Deinitializing Autonomous Trader...");
   //--- Cleanup Dashboard
   dashboard.Destroy();
  }
//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
   static datetime last_analysis = 0;

   //--- Refresh data
   if(!symbol_info.RefreshRates()) return;

   //--- Check for Trailing SL/TP
   if(InpTrailingSL || InpTrailingTP)
      ApplyTrailingLogic();

   //--- Run analysis every 1 minute
   if(TimeCurrent() - last_analysis >= 60)
     {
      AnalyzeMarket();
      last_analysis = TimeCurrent();
     }
  }

//+------------------------------------------------------------------+
//| Market Analysis Logic                                            |
//+------------------------------------------------------------------+
void AnalyzeMarket()
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
            string trend = CJsonParser::GetString(response, "trend");
            double confidence = CJsonParser::GetDouble(response, "confidence");
            bool verified = CJsonParser::GetBool(response, "verified");

            string regime = CJsonParser::GetString(response, "regime");

            dashboard.SetCellValue(1, 1, "M15/H1/D1");
            dashboard.SetCellValue(1, 2, trend);
            dashboard.SetCellValue(1, 3, signal + " (" + DoubleToString(confidence, 0) + ")");
            dashboard.SetCellValue(1, 4, DoubleToString(InpRiskPercent, 1) + "%");
            dashboard.SetCellValue(1, 5, regime);

            if(verified)
              {
               dashboard.SetCellValue(1, 6, "TRADE VERIFIED", clrLime);
               if(signal == "BUY") ExecuteTrade(ORDER_TYPE_BUY);
               else if(signal == "SELL") ExecuteTrade(ORDER_TYPE_SELL);
              }
            else
              {
               dashboard.SetCellValue(1, 6, "WAITING CONFIRMATION", clrYellow);
              }
           }
        }
      socket_client.Disconnect();
     }
   else
     {
      dashboard.SetCellValue(1, 6, "CONN ERROR", clrRed);
     }
  }

//+------------------------------------------------------------------+
//| Trade Execution Logic                                            |
//+------------------------------------------------------------------+
void ExecuteTrade(ENUM_ORDER_TYPE type)
  {
   // Check if we already have an open position for this magic number
   bool already_open = false;
   for(int i=PositionsTotal()-1; i>=0; i--)
     {
      if(pos_info.SelectByIndex(i))
        {
         if(pos_info.Symbol() == _Symbol && pos_info.Magic() == InpMagicNumber)
           {
            already_open = true;
            break;
           }
        }
     }
   if(already_open) return;

   double price = (type == ORDER_TYPE_BUY) ? symbol_info.Ask() : symbol_info.Bid();
   double sl = (type == ORDER_TYPE_BUY) ? price - InpStopLoss * _Point : price + InpStopLoss * _Point;
   double tp = (type == ORDER_TYPE_BUY) ? price + InpTakeProfit * _Point : price - InpTakeProfit * _Point;

   // Position Sizing based on risk
   double risk_amount = AccountInfoDouble(ACCOUNT_BALANCE) * (InpRiskPercent / 100.0);
   double tick_value = symbol_info.TickValue();
   double volume = risk_amount / (InpStopLoss * tick_value);

   volume = NormalizeDouble(volume, 2);
   if(volume < symbol_info.LotsMin()) volume = symbol_info.LotsMin();
   if(volume > symbol_info.LotsMax()) volume = symbol_info.LotsMax();

   if(trade.PositionOpen(_Symbol, type, volume, price, sl, tp, "Autonomous Trader"))
     {
      Print("Trade executed: ", EnumToString(type), " Volume: ", volume);
     }
   else
     {
      Print("Trade failed: ", trade.ResultRetcodeDescription());
     }
  }

//+------------------------------------------------------------------+
//| Trailing SL and TP Logic                                         |
//+------------------------------------------------------------------+
void ApplyTrailingLogic()
  {
   for(int i=PositionsTotal()-1; i>=0; i--)
     {
      if(pos_info.SelectByIndex(i))
        {
         if(pos_info.Symbol() == _Symbol && pos_info.Magic() == InpMagicNumber)
           {
            double bid = symbol_info.Bid();
            double ask = symbol_info.Ask();
            double point = symbol_info.Point();
            double step = InpTrailingStep * point;

            double current_sl = pos_info.StopLoss();
            double current_tp = pos_info.TakeProfit();
            double new_sl = current_sl;
            double new_tp = current_tp;

            if(pos_info.PositionType() == POSITION_TYPE_BUY)
              {
               // Trailing SL
               if(InpTrailingSL)
                 {
                  double target_sl = NormalizeDouble(bid - InpStopLoss * point, _Digits);
                  if(target_sl > current_sl + step) new_sl = target_sl;
                 }
               // Trailing TP
               if(InpTrailingTP)
                 {
                  double target_tp = NormalizeDouble(bid + InpTakeProfit * point, _Digits);
                  if(target_tp > current_tp + step) new_tp = target_tp;
                 }
              }
            else if(pos_info.PositionType() == POSITION_TYPE_SELL)
              {
               // Trailing SL
               if(InpTrailingSL)
                 {
                  double target_sl = NormalizeDouble(ask + InpStopLoss * point, _Digits);
                  if(target_sl < current_sl - step || current_sl == 0) new_sl = target_sl;
                 }
               // Trailing TP
               if(InpTrailingTP)
                 {
                  double target_tp = NormalizeDouble(ask - InpTakeProfit * point, _Digits);
                  if(target_tp < current_tp - step || current_tp == 0) new_tp = target_tp;
                 }
              }

            if(new_sl != current_sl || new_tp != current_tp)
              {
               trade.PositionModify(pos_info.Ticket(), new_sl, new_tp);
              }
           }
        }
     }
  }
//+------------------------------------------------------------------+
