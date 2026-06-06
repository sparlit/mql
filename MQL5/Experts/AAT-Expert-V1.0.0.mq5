//+------------------------------------------------------------------+
//|                                              AAT-Expert-V1.0.0.mq5 |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, AI Trader Corp."
#property link      "https://www.mql5.com"
#property version   "1.40"
#property strict
#property description "Autonomous Autotrader with Full-Spectrum Dashboard"

#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\SymbolInfo.mqh>
#include <ChartObjects\ChartObjectsTxtControls.mqh>
#include <AAT-Dashboard-V1.0.0.mqh>
#include <AAT-SocketClient-V1.0.0.mqh>
#include <AAT-JsonParser-V1.0.0.mqh>

#import "user32.dll"
   int PostMessageW(long hWnd, uint Msg, uint wParam, uint lParam);
#import

//--- inputs
input double   InpRiskPercent  = 1.0;      // Risk per trade (%)
input int      InpMagicNumber  = 123456;   // Magic Number
input int      InpStopLoss     = 200;      // Initial Stop Loss (points)
input int      InpTakeProfit   = 400;      // Initial Take Profit (points)
input bool     InpTrailingSL   = true;     // Enable Trailing SL
input bool     InpTrailingTP   = true;     // Enable Trailing TP
input int      InpTrailingStep = 50;       // Trailing Step (points)
input bool     InpAutoCharts   = true;     // Auto-open TF Charts
input string   InpMasterKey    = "AAT_SECURE_FOSS_KEY_256_BIT_STRIP"; // AES Master Key

//--- global variables
CTrade         trade;
CPositionInfo  pos_info;
CSymbolInfo    symbol_info;
CDashboard     dashboard;
CSocketClient  socket_client;
double         g_current_risk = InpRiskPercent;

int OnInit()
  {
   if(!symbol_info.Name(_Symbol)) return(INIT_FAILED);
   trade.SetExpertMagicNumber(InpMagicNumber);

   socket_client.SetMasterKey(InpMasterKey);

   dashboard.Create(10, 12, 10, 30, 100, 22);
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
   dashboard.SetCellValue(2, 0, "HEALTH:", clrCyan);
   dashboard.SetCellValue(2, 1, "OK", clrLime);
   dashboard.SetCellValue(2, 2, "SPREAD:", clrCyan);
   dashboard.SetCellValue(3, 0, "REGIME:", clrCyan);
   dashboard.SetCellValue(3, 2, "P&L:", clrCyan);
   dashboard.SetCellValue(4, 0, "CANDLE T-:", clrCyan);
   dashboard.SetCellValue(4, 2, "VaR:", clrCyan);
   dashboard.SetCellValue(5, 0, "CORREL:", clrCyan);
   dashboard.SetCellValue(5, 2, "POLYMARK:", clrCyan);

   dashboard.SetCellValue(6, 0, "CONFIG:", clrYellow);
   dashboard.SetCellValue(6, 1, "RISK %", clrWhite);
   dashboard.SetCellValue(7, 1, DoubleToString(InpRiskPercent, 1), clrWhite);
   dashboard.SetCellReadOnly(7, 1, false);

   if(InpAutoCharts) SetupTimeframeCharts();
   EventSetTimer(1);
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason) { dashboard.Destroy(); }

void OnTick()
  {
   if(!symbol_info.RefreshRates()) return;
   if(InpTrailingSL || InpTrailingTP) ApplyTrailingLogic();
   UpdateDynamicDashboard();
  }

void OnTimer()
  {
   static int counter = 0;
   counter++;
   if(counter >= 60) { AnalyzeMarket(); counter = 0; }
   UpdateCandleCountdown();
  }

void UpdateDynamicDashboard()
  {
   dashboard.SetCellValue(2, 3, IntegerToString((int)SymbolInfoInteger(_Symbol, SYMBOL_SPREAD)), clrWhite);

   double total_pl = 0;
   for(int i=PositionsTotal()-1; i>=0; i--)
      if(pos_info.SelectByIndex(i) && pos_info.Symbol() == _Symbol && pos_info.Magic() == InpMagicNumber)
         total_pl += pos_info.Profit();

   dashboard.SetCellValue(3, 3, DoubleToString(total_pl, 2), (total_pl >= 0) ? clrLime : clrRed);

   // Sync Risk efficiently
   string risk_val = dashboard.GetCellValue(7, 1);
   double new_risk = StringToDouble(risk_val);
   if(new_risk > 0 && new_risk < 10 && new_risk != g_current_risk)
     {
      g_current_risk = new_risk;
      GlobalVariableSet("AAT_Risk_" + _Symbol, g_current_risk);
      Print("Dynamic Config: Risk updated to ", g_current_risk);
     }
  }

void UpdateCandleCountdown()
  {
   datetime next_bar = (datetime)SeriesInfoInteger(_Symbol, _Period, SERIES_LASTBAR_DATE) + PeriodSeconds(_Period);
   long remaining = next_bar - TimeCurrent();
   if(remaining < 0) remaining = 0;
   dashboard.SetCellValue(4, 1, StringFormat("%02d:%02d", (int)remaining/60, (int)remaining%60), clrWhite);
  }

void AnalyzeMarket()
  {
   dashboard.SetCellValue(1, 11, "ANALYZING...", clrWhite);
   double current_profit_pips = 0;
   for(int i=PositionsTotal()-1; i>=0; i--)
      if(pos_info.SelectByIndex(i) && pos_info.Symbol() == _Symbol && pos_info.Magic() == InpMagicNumber)
        {
         current_profit_pips = ((pos_info.PositionType() == POSITION_TYPE_BUY) ? (symbol_info.Bid() - pos_info.PriceOpen()) : (pos_info.PriceOpen() - symbol_info.Ask())) / _Point;
         break;
        }

   string request = "{\"symbol\":\"" + _Symbol + "\", \"balance\":" + DoubleToString(AccountInfoDouble(ACCOUNT_BALANCE), 2) +
                    ", \"tick_value\":" + DoubleToString(symbol_info.TickValue(), 5) +
                    ", \"tick_size\":" + DoubleToString(symbol_info.TickSize(), 8) +
                    ", \"sl_points\":" + IntegerToString(InpStopLoss) +
                    ", \"current_profit_pips\":" + DoubleToString(current_profit_pips, 1) + "}";

   if(socket_client.Connect("127.0.0.1", 5555))
     {
      if(socket_client.SendEncrypted(request))
        {
         string resp = socket_client.ReceiveDecrypted();
         if(resp != "")
           {
            bool verified = CJsonParser::GetBool(resp, "verified");
            bool news = CJsonParser::GetBool(resp, "news_impact");
            string signal = CJsonParser::GetString(resp, "signal");
            double lot = CJsonParser::GetDouble(resp, "recommended_lot");

            dashboard.SetCellValue(3, 1, CJsonParser::GetString(resp, "regime"));
            dashboard.SetCellValue(4, 3, DoubleToString(CJsonParser::GetDouble(resp, "var"), 4));
            dashboard.SetCellValue(5, 1, DoubleToString(CJsonParser::GetDouble(resp, "correlation"), 2));
            dashboard.SetCellValue(5, 3, CJsonParser::GetString(resp, "polymarket"));
            dashboard.SetCellValue(1, 10, signal + "(" + DoubleToString(CJsonParser::GetDouble(resp, "confidence"), 0) + ")");
            dashboard.SetCellValue(2, 1, "OK", clrLime);

            string tfs[] = {"M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN"};
            for(int i=0; i<ArraySize(tfs); i++)
              {
               double score = CJsonParser::GetDouble(resp, tfs[i]);
               color c = (score > 0) ? clrLime : (score < 0 ? clrRed : clrWhite);
               dashboard.SetCellValue(1, i+1, DoubleToString(score, 0), c);
              }

            if(news)
              {
               dashboard.SetCellValue(1, 11, "NEWS STRADDLE", clrOrange);
               ExecuteNewsStraddle(lot);
              }
            else if(verified)
              {
               dashboard.SetCellValue(1, 11, "TRADE!", clrLime);
               if(!ExecuteTrade(signal == "BUY" ? ORDER_TYPE_BUY : ORDER_TYPE_SELL, lot))
                  CheckPyramidScaling(lot);
              }
            else
              {
               dashboard.SetCellValue(1, 11, "SCANNING", clrYellow);
               CheckPyramidScaling(lot);
              }
           }
        }
      socket_client.Disconnect();
     }
   else
     {
      dashboard.SetCellValue(1, 11, "CONN ERROR", clrRed);
      dashboard.SetCellValue(2, 1, "OFFLINE", clrRed);
     }
  }

bool ExecuteTrade(ENUM_ORDER_TYPE type, double lot)
  {
   for(int i=PositionsTotal()-1; i>=0; i--)
      if(pos_info.SelectByIndex(i) && pos_info.Symbol() == _Symbol && pos_info.Magic() == InpMagicNumber) return false;

   double price = (type == ORDER_TYPE_BUY) ? symbol_info.Ask() : symbol_info.Bid();
   double sl = (type == ORDER_TYPE_BUY) ? price - InpStopLoss * _Point : price + InpStopLoss * _Point;
   double tp = (type == ORDER_TYPE_BUY) ? price + InpTakeProfit * _Point : price - InpTakeProfit * _Point;

   if(lot <= 0) lot = 0.01;
   return trade.PositionOpen(_Symbol, type, lot, price, sl, tp, "AAT Initial");
  }

void CheckPyramidScaling(double lot)
  {
   int pos_count = 0;
   double newest_open = 0;
   ENUM_POSITION_TYPE type = POSITION_TYPE_BUY;

   // Correctly find the newest position and count total
   for(int i=PositionsTotal()-1; i>=0; i--)
      if(pos_info.SelectByIndex(i) && pos_info.Symbol() == _Symbol && pos_info.Magic() == InpMagicNumber)
        {
         if(pos_count == 0) { newest_open = pos_info.PriceOpen(); type = pos_info.PositionType(); }
         pos_count++;
        }

   if(pos_count == 0 || pos_count >= 5) return;

   double profit = ((type == POSITION_TYPE_BUY) ? (symbol_info.Bid() - newest_open) : (newest_open - symbol_info.Ask())) / _Point;

   if(profit >= InpStopLoss) // Add every 1:1 RR distance
     {
      double price = (type == POSITION_TYPE_BUY) ? symbol_info.Ask() : symbol_info.Bid();
      double sl = newest_open; // Move to BE (newest_open)

      if(lot <= 0) lot = 0.01;

      if(trade.PositionOpen(_Symbol, (type == POSITION_TYPE_BUY ? ORDER_TYPE_BUY : ORDER_TYPE_SELL), lot, price, sl, 0, "Pyramid"))
        {
         // On success, update ALL positions of this symbol to the BE stop loss
         for(int i=PositionsTotal()-1; i>=0; i--)
            if(pos_info.SelectByIndex(i) && pos_info.Symbol() == _Symbol && pos_info.Magic() == InpMagicNumber)
               trade.PositionModify(pos_info.Ticket(), newest_open, pos_info.TakeProfit());
        }
     }
  }

void ExecuteNewsStraddle(double lot)
  {
   for(int i=PositionsTotal()-1; i>=0; i--)
      if(pos_info.SelectByIndex(i) && pos_info.Symbol() == _Symbol && pos_info.Magic() == InpMagicNumber) return;

   if(lot <= 0) lot = 0.01;
   trade.PositionOpen(_Symbol, ORDER_TYPE_BUY, lot, symbol_info.Ask(), symbol_info.Ask() - InpStopLoss*_Point, 0, "Straddle B");
   trade.PositionOpen(_Symbol, ORDER_TYPE_SELL, lot, symbol_info.Bid(), symbol_info.Bid() + InpStopLoss*_Point, 0, "Straddle S");
  }

void ApplyTrailingLogic()
  {
   for(int i=PositionsTotal()-1; i>=0; i--)
      if(pos_info.SelectByIndex(i) && pos_info.Symbol() == _Symbol && pos_info.Magic() == InpMagicNumber)
        {
         double point = _Point;
         double current_sl = pos_info.StopLoss();
         double new_sl = current_sl;
         if(pos_info.PositionType() == POSITION_TYPE_BUY)
           {
            double target = NormalizeDouble(symbol_info.Bid() - InpStopLoss * point, _Digits);
            if(target > current_sl + InpTrailingStep * point) new_sl = target;
           }
         else
           {
            double target = NormalizeDouble(symbol_info.Ask() + InpStopLoss * point, _Digits);
            if(target < current_sl - InpTrailingStep * point || current_sl == 0) new_sl = target;
           }
         if(new_sl != current_sl) trade.PositionModify(pos_info.Ticket(), new_sl, pos_info.TakeProfit());
        }
  }

void SetupTimeframeCharts()
  {
   ENUM_TIMEFRAMES tfs[] = {PERIOD_M1, PERIOD_M5, PERIOD_M15, PERIOD_M30, PERIOD_H1, PERIOD_H4, PERIOD_D1, PERIOD_W1, PERIOD_MN1};
   for(int i=0; i<ArraySize(tfs); i++) ChartOpen(_Symbol, tfs[i]);

   // Tile windows vertically using WinAPI (MT5 doesn't have a native ChartTile function)
   // 0x0111 = WM_COMMAND, 33054 = ID_WINDOW_TILE_VERT
   long main_hwnd = ChartGetInteger(0, CHART_WINDOW_HANDLE);
   PostMessageW(main_hwnd, 0x0111, 33054, 0);
  }
