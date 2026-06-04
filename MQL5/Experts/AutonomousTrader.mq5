//+------------------------------------------------------------------+
//|                                              AutonomousTrader.mq5 |
//|                                  Copyright 2024, AI Trader Corp. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, AI Trader Corp."
#property link      "https://www.mql5.com"
#property version   "1.30"
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
input double   InpRiskPercent  = 1.0;      // Risk per trade (%) | Percentage of equity to risk per trade
input int      InpMagicNumber  = 123456;   // Magic Number | Unique identifier for trades
input int      InpStopLoss     = 200;      // Initial Stop Loss (points) | Initial protective stop in points
input int      InpTakeProfit   = 400;      // Initial Take Profit (points) | Initial target profit in points
input bool     InpTrailingSL   = true;     // Enable Trailing SL | Enable autonomous trailing stop loss
input bool     InpTrailingTP   = true;     // Enable Trailing TP | Enable autonomous trailing take profit
input int      InpTrailingStep = 50;       // Trailing Step (points) | Minimum profit movement before trailing
input bool     InpAutoCharts   = true;     // Auto-open TF Charts | Automatically open and arrange 9 timeframe charts

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

   //--- Initialize Dashboard (12 columns: Symbol + 9 TFs + Consensus + Status)
   dashboard.Create(4, 12, 10, 30, 100, 22);
   dashboard.SetHeader(0, "Symbol");
   dashboard.SetHeader(1, "M1");
   dashboard.SetHeader(2, "M5");
   dashboard.SetHeader(3, "M15");
   dashboard.SetHeader(4, "M30");
   dashboard.SetHeader(5, "H1");
   dashboard.SetHeader(6, "H4");
   dashboard.SetHeader(7, "D1");
   dashboard.SetHeader(8, "W1");
   dashboard.SetHeader(9, "MN");
   dashboard.SetHeader(10, "CONSENSUS");
   dashboard.SetHeader(11, "STATUS");

   dashboard.SetCellValue(1, 0, _Symbol);
   dashboard.SetCellValue(1, 11, "Connecting...", clrYellow);

   dashboard.SetCellValue(2, 0, "SYSTEM HEALTH:", clrCyan);
   dashboard.SetCellValue(2, 1, "OK", clrLime);
   dashboard.SetCellValue(3, 0, "REGIME:", clrCyan);

   if(InpAutoCharts)
      SetupTimeframeCharts();

   return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   Print("Deinitializing Autonomous Trader...");
   dashboard.Destroy();
  }
//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
   static datetime last_analysis = 0;

   if(!symbol_info.RefreshRates()) return;

   if(InpTrailingSL || InpTrailingTP)
      ApplyTrailingLogic();

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
   dashboard.SetCellValue(1, 11, "ANALYZING...", clrWhite);

   string request = "{\"symbol\":\"" + _Symbol + "\", " +
                    "\"balance\":" + DoubleToString(AccountInfoDouble(ACCOUNT_BALANCE), 2) + ", " +
                    "\"tick_value\":" + DoubleToString(symbol_info.TickValue(), 5) + ", " +
                    "\"tick_size\":" + DoubleToString(symbol_info.TickSize(), 8) + "}";

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

            // TF Signals
            UpdateTFCell(1, 1, response, "M1");
            UpdateTFCell(1, 2, response, "M5");
            UpdateTFCell(1, 3, response, "M15");
            UpdateTFCell(1, 4, response, "M30");
            UpdateTFCell(1, 5, response, "H1");
            UpdateTFCell(1, 6, response, "H4");
            UpdateTFCell(1, 7, response, "D1");
            UpdateTFCell(1, 8, response, "W1");
            UpdateTFCell(1, 9, response, "MN");

            dashboard.SetCellValue(1, 10, signal + "(" + DoubleToString(confidence, 0) + ")");
            dashboard.SetCellValue(3, 1, regime, (StringFind(regime, "High") != -1) ? clrRed : clrLime);

            if(verified)
              {
               dashboard.SetCellValue(1, 11, "TRADE!", clrLime);
               if(signal == "BUY") ExecuteTrade(ORDER_TYPE_BUY);
               else if(signal == "SELL") ExecuteTrade(ORDER_TYPE_SELL);
              }
            else
              {
               dashboard.SetCellValue(1, 11, "SCANNING", clrYellow);
              }
           }
        }
      socket_client.Disconnect();
     }
   else
     {
      dashboard.SetCellValue(1, 11, "CONN ERROR", clrRed);
     }
  }

void UpdateTFCell(int row, int col, string json, string tf)
  {
   double score = CJsonParser::GetDouble(json, tf);
   string text = (score > 0) ? "BUY" : (score < 0 ? "SELL" : "NEUT");
   color clr = (score > 0) ? clrLime : (score < 0 ? clrRed : clrWhite);
   dashboard.SetCellValue(row, col, text, clr);
  }

//+------------------------------------------------------------------+
//| Trade Execution Logic                                            |
//+------------------------------------------------------------------+
void ExecuteTrade(ENUM_ORDER_TYPE type)
  {
   if(!symbol_info.RefreshRates()) return;

   // Check if we already have an open position
   for(int i=PositionsTotal()-1; i>=0; i--)
     {
      if(pos_info.SelectByIndex(i))
        {
         if(pos_info.Symbol() == _Symbol && pos_info.Magic() == InpMagicNumber)
            return;
        }
     }

   double price = (type == ORDER_TYPE_BUY) ? symbol_info.Ask() : symbol_info.Bid();
   double sl = (type == ORDER_TYPE_BUY) ? price - InpStopLoss * _Point : price + InpStopLoss * _Point;
   double tp = (type == ORDER_TYPE_BUY) ? price + InpTakeProfit * _Point : price - InpTakeProfit * _Point;

   // Precise Position Sizing
   double risk_amount = AccountInfoDouble(ACCOUNT_BALANCE) * (InpRiskPercent / 100.0);
   double tick_value = symbol_info.TickValue();

   if(tick_value <= 0)
     {
      Print("CRITICAL: TickValue is zero for ", _Symbol, ". Aborting trade for safety.");
      return;
     }

   // Volume = Risk Amount / (Price Risk in Points * Tick Value)
   double volume = risk_amount / (InpStopLoss * tick_value);

   // Standardize volume
   double step = symbol_info.LotsStep();
   if(step > 0)
      volume = MathFloor(volume / step) * step;

   if(volume < symbol_info.LotsMin()) volume = symbol_info.LotsMin();
   if(volume > symbol_info.LotsMax()) volume = symbol_info.LotsMax();

   if(trade.PositionOpen(_Symbol, type, volume, price, sl, tp, "Autonomous Zero-Flaw EA"))
     {
      Print("Trade executed: ", EnumToString(type), " Vol: ", volume);
     }
   else
     {
      Print("Execution Error: ", trade.ResultRetcodeDescription());
     }
  }

//+------------------------------------------------------------------+
//| Setup TF Charts                                                  |
//+------------------------------------------------------------------+
void SetupTimeframeCharts()
  {
   ENUM_TIMEFRAMES tfs[] = {PERIOD_M1, PERIOD_M5, PERIOD_M15, PERIOD_M30, PERIOD_H1, PERIOD_H4, PERIOD_D1, PERIOD_W1, PERIOD_MN1};
   for(int i=0; i<ArraySize(tfs); i++)
     {
      long chart_id = ChartOpen(_Symbol, tfs[i]);
      if(chart_id > 0)
         ChartApplyTemplate(chart_id, "default.tpl");
     }
   ChartTile(CHART_TILE_VERTICAL);
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
               if(InpTrailingSL)
                 {
                  double target_sl = NormalizeDouble(bid - InpStopLoss * point, _Digits);
                  if(target_sl > current_sl + step) new_sl = target_sl;
                 }
               if(InpTrailingTP)
                 {
                  double target_tp = NormalizeDouble(bid + InpTakeProfit * point, _Digits);
                  if(target_tp > current_tp + step) new_tp = target_tp;
                 }
              }
            else if(pos_info.PositionType() == POSITION_TYPE_SELL)
              {
               if(InpTrailingSL)
                 {
                  double target_sl = NormalizeDouble(ask + InpStopLoss * point, _Digits);
                  if(target_sl < current_sl - step || current_sl == 0) new_sl = target_sl;
                 }
               if(InpTrailingTP)
                 {
                  double target_tp = NormalizeDouble(ask - InpTakeProfit * point, _Digits);
                  if(target_tp < current_tp - step || current_tp == 0) new_tp = target_tp;
                 }
              }

            if(new_sl != current_sl || new_tp != current_tp)
               trade.PositionModify(pos_info.Ticket(), new_sl, new_tp);
           }
        }
     }
  }
//+------------------------------------------------------------------+
