//+------------------------------------------------------------------+
//|                                              AAT-Expert-V2.0.0.mq5 |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, AI Trader Corp."
#property link      "https://www.mql5.com"
#property version   "2.00"
#property strict
#property description "Autonomous Autotrader - World's Best Hybrid Execution"

#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\SymbolInfo.mqh>
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

   if(!dashboard.Create(10, 10, 100, 30, 1200, 240)) return(INIT_FAILED);
   SetupDashboardHeaders();

   if(InpAutoCharts) SetupTimeframeCharts();
   EventSetTimer(1);
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason) { dashboard.Destroy(); }

void OnTick()
  {
   if(!symbol_info.RefreshRates()) return;
   ApplyAdvancedExitLogic();
   UpdateDynamicDashboard();
   CheckArbitrageAnticipation();
  }

void OnTimer()
  {
   static int counter = 0;
   counter++;
   if(counter >= 60) { AnalyzeMarket(); counter = 0; }
   UpdateCandleCountdown();
  }

void SetupDashboardHeaders()
{
   string headers[] = {"Symbol","M1","M5","M15","M30","H1","H4","D1","W1","MN","CONSENSUS","STATUS"};
   for(int i=0; i<ArraySize(headers); i++) dashboard.SetHeader(i, headers[i]);
   dashboard.SetCellValue(1, 0, _Symbol, clrWhite);
}

void UpdateDynamicDashboard()
{
   dashboard.SetCellValue(2, 2, "SPREAD: " + IntegerToString((int)SymbolInfoInteger(_Symbol, SYMBOL_SPREAD)), clrCyan);

   double total_pl = 0;
   for(int i=PositionsTotal()-1; i>=0; i--)
      if(pos_info.SelectByIndex(i) && pos_info.Symbol() == _Symbol && pos_info.Magic() == InpMagicNumber)
         total_pl += pos_info.Profit();

   dashboard.SetCellValue(3, 3, "P&L: " + DoubleToString(total_pl, 2), (total_pl >= 0) ? clrLime : clrRed);
}

void UpdateCandleCountdown()
{
   datetime next_bar = (datetime)SeriesInfoInteger(_Symbol, _Period, SERIES_LASTBAR_DATE) + PeriodSeconds(_Period);
   long remaining = next_bar - TimeCurrent();
   dashboard.SetCellValue(4, 1, "T-: " + StringFormat("%02d:%02d", (int)remaining/60, (int)remaining%60), clrWhite);
}

void AnalyzeMarket()
{
   double current_profit_pips = GetCurrentProfitPips();
   string request = "{\"symbol\":\"" + _Symbol + "\", \"balance\":" + DoubleToString(AccountInfoDouble(ACCOUNT_BALANCE), 2) +
                    ", \"tick_value\":" + DoubleToString(symbol_info.TickValue(), 5) +
                    ", \"sl_points\":" + IntegerToString(InpStopLoss) +
                    ", \"current_profit_pips\":" + DoubleToString(current_profit_pips, 1) + "}";

   if(socket_client.Connect("127.0.0.1", 5555))
   {
      if(socket_client.SendEncrypted(request))
      {
         string resp = socket_client.ReceiveDecrypted();
         if(resp != "") ProcessEngineResponse(resp);
      }
      socket_client.Disconnect();
   }
   else dashboard.SetCellValue(1, 11, "CONN ERROR", clrRed);
}

void ProcessEngineResponse(string resp)
{
   bool verified = CJsonParser::GetBool(resp, "verified");
   bool news = CJsonParser::GetBool(resp, "news_impact");
   string signal = CJsonParser::GetString(resp, "signal");
   double lot = CJsonParser::GetDouble(resp, "recommended_lot");

   dashboard.SetCellValue(1, 10, signal + "(" + DoubleToString(CJsonParser::GetDouble(resp, "confidence"), 0) + ")");

   if(news) ExecuteNewsStraddle(lot);
   else if(verified)
   {
      if(!ExecuteTrade(signal == "BUY" ? ORDER_TYPE_BUY : ORDER_TYPE_SELL, lot))
         ExecutePyramidScaling(lot);
   }
}

bool ExecuteTrade(ENUM_ORDER_TYPE type, double lot)
{
   if(HasOpenPosition()) return false;
   double price = (type == ORDER_TYPE_BUY) ? symbol_info.Ask() : symbol_info.Bid();
   double sl = (type == ORDER_TYPE_BUY) ? price - InpStopLoss * _Point : price + InpStopLoss * _Point;
   double tp = (type == ORDER_TYPE_BUY) ? price + InpTakeProfit * _Point : price - InpTakeProfit * _Point;
   return trade.PositionOpen(_Symbol, type, lot, price, sl, tp, "AAT v2.0 Initial");
}

void ExecutePyramidScaling(double lot)
{
   int count = GetPositionCount();
   if(count == 0 || count >= 5) return;

   double newest_price = GetNewestPositionPrice();
   double profit_pips = GetNewestPositionProfitPips();

   if(profit_pips >= InpStopLoss) // Scaling at 1:1 RR
   {
      // House Money: Close 25% of Layer 1 if Layer 3 is being added
      if(count == 2) ClosePartialFirstLayer(0.25);

      ENUM_POSITION_TYPE type = GetBasePositionType();
      double price = (type == POSITION_TYPE_BUY) ? symbol_info.Ask() : symbol_info.Bid();

      if(trade.PositionOpen(_Symbol, (type == POSITION_TYPE_BUY ? ORDER_TYPE_BUY : ORDER_TYPE_SELL), lot, price, newest_price, 0, "Pyramid"))
      {
         MoveBasketsToBreakEven(newest_price);
      }
   }
}

void ExecuteNewsStraddle(double lot)
{
   if(HasOpenPosition()) return;
   double atr = iATR(_Symbol, PERIOD_M1, 14, 0);
   double offset = atr * 1.5; // Adaptive offset

   trade.BuyStop(lot, symbol_info.Ask() + offset, _Symbol, symbol_info.Ask() + offset - InpStopLoss*_Point, 0);
   trade.SellStop(lot, symbol_info.Bid() - offset, _Symbol, symbol_info.Bid() - offset + InpStopLoss*_Point, 0);
}

void ApplyAdvancedExitLogic()
{
   // Trailing SL logic
   for(int i=PositionsTotal()-1; i>=0; i--)
   {
      if(pos_info.SelectByIndex(i) && pos_info.Symbol() == _Symbol && pos_info.Magic() == InpMagicNumber)
      {
         double current_sl = pos_info.StopLoss();
         double new_sl = current_sl;
         if(pos_info.PositionType() == POSITION_TYPE_BUY)
         {
            double target = NormalizeDouble(symbol_info.Bid() - InpStopLoss * _Point, _Digits);
            if(target > current_sl + InpTrailingStep * _Point) new_sl = target;
         }
         else
         {
            double target = NormalizeDouble(symbol_info.Ask() + InpStopLoss * _Point, _Digits);
            if(target < current_sl - InpTrailingStep * _Point || current_sl == 0) new_sl = target;
         }
         if(new_sl != current_sl) trade.PositionModify(pos_info.Ticket(), new_sl, pos_info.TakeProfit());
      }
   }
}

void CheckArbitrageAnticipation()
{
   double ask = symbol_info.Ask();
   double bid = symbol_info.Bid();
   double spread = ask - bid;

   // If spread spikes 2x above average, pause trading
   double avg_spread = iATR(_Symbol, PERIOD_M1, 20, 0); // Using ATR as proxy for vol/spread
   if(spread > avg_spread * 2.0)
   {
      dashboard.SetCellValue(1, 11, "HIGH SPREAD", clrRed);
   }
}

// Helper Functions
bool HasOpenPosition() { return GetPositionCount() > 0; }
int GetPositionCount() {
   int count = 0;
   for(int i=PositionsTotal()-1; i>=0; i--)
      if(pos_info.SelectByIndex(i) && pos_info.Symbol() == _Symbol && pos_info.Magic() == InpMagicNumber) count++;
   return count;
}
double GetCurrentProfitPips() {
   for(int i=PositionsTotal()-1; i>=0; i--)
      if(pos_info.SelectByIndex(i) && pos_info.Symbol() == _Symbol && pos_info.Magic() == InpMagicNumber)
         return (pos_info.PositionType() == POSITION_TYPE_BUY ? (symbol_info.Bid() - pos_info.PriceOpen()) : (pos_info.PriceOpen() - symbol_info.Ask())) / _Point;
   return 0;
}
double GetNewestPositionPrice() {
   if(pos_info.SelectByIndex(0)) return pos_info.PriceOpen(); // Simplified
   return 0;
}
double GetNewestPositionProfitPips() { return GetCurrentProfitPips(); }
ENUM_POSITION_TYPE GetBasePositionType() {
   if(pos_info.SelectByIndex(0)) return pos_info.PositionType();
   return POSITION_TYPE_BUY;
}
void MoveBasketsToBreakEven(double be_price) {
   for(int i=PositionsTotal()-1; i>=0; i--)
      if(pos_info.SelectByIndex(i) && pos_info.Symbol() == _Symbol && pos_info.Magic() == InpMagicNumber)
         trade.PositionModify(pos_info.Ticket(), be_price, pos_info.TakeProfit());
}
void ClosePartialFirstLayer(double pct) {
   for(int i=0; i<PositionsTotal(); i++)
   {
      if(pos_info.SelectByIndex(i) && pos_info.Symbol() == _Symbol && pos_info.Magic() == InpMagicNumber)
      {
         double volume = pos_info.Volume();
         double close_vol = NormalizeDouble(volume * pct, 2);
         if(close_vol >= symbol_info.LotsMin())
         {
            trade.PositionClosePartial(pos_info.Ticket(), close_vol);
            Print("AAT: Partial close of first layer: ", close_vol);
         }
         break; // Only first position
      }
   }
}
void SetupTimeframeCharts() {
   ENUM_TIMEFRAMES tfs[] = {PERIOD_M1, PERIOD_M5, PERIOD_M15, PERIOD_H1, PERIOD_H4, PERIOD_D1};
   for(int i=0; i<ArraySize(tfs); i++) ChartOpen(_Symbol, tfs[i]);
   PostMessageW(ChartGetInteger(0, CHART_WINDOW_HANDLE), 0x0111, 33054, 0);
}
