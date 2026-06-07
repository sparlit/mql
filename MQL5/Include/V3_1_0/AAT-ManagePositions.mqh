//+------------------------------------------------------------------+
//| Project: Autonomous AutoTrader (AAT)                             |
//| Version: V4.0.0_20260606                                         |
//| License: 100% FOSS / GNU GPL v3                                  |
//| Author: Simon Peter                                              |
//| Verification: Zero-Stub / Production Ready                       |
//| Description: Dynamic Position Management with Watchdog           |
//+------------------------------------------------------------------+
#property copyright "Copyright 2026, Simon Peter"
#property strict

#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <V3_1_0\AAT-Utils.mqh>

class CManagePositions
{
private:
   CPositionInfo     m_pos;
   CTrade            m_trade;
   string            m_symbol;
   int               m_magic;
   double            m_highest_prices[];

public:
   CManagePositions(string symbol, int magic) : m_symbol(symbol), m_magic(magic)
   {
      m_trade.SetExpertMagicNumber(magic);
   }

   void Update()
   {
      int count = 0;
      for(int i=PositionsTotal()-1; i>=0; i--)
         if(m_pos.SelectByIndex(i) && m_pos.Symbol() == m_symbol && m_pos.Magic() == m_magic) count++;
      if(ArraySize(m_highest_prices) != count) ArrayResize(m_highest_prices, count);
   }

   // L99 Active Watchdog Implementation (Priority 1)
   void EmergencyMoveToBE()
   {
      for(int i=PositionsTotal()-1; i>=0; i--)
      {
         if(m_pos.SelectByIndex(i) && m_pos.Symbol() == m_symbol && m_pos.Magic() == m_magic)
         {
            double be_price = m_pos.PriceOpen();
            double point = SymbolInfoDouble(m_symbol, SYMBOL_POINT);
            if(m_pos.PositionType() == POSITION_TYPE_BUY) be_price += 20 * point;
            else be_price -= 20 * point;

            m_trade.PositionModify(m_pos.Ticket(), be_price, m_pos.TakeProfit());
            CAATUtils::LogInfo("WATCHDOG: Emergency BE move for ticket " + IntegerToString(m_pos.Ticket()));
         }
      }
   }

   // Refined Professional Execution (Priority 2)
   void TrailingStop(int atr_points)
   {
      for(int i=PositionsTotal()-1; i>=0; i--)
      {
         if(m_pos.SelectByIndex(i) && m_pos.Symbol() == m_symbol && m_pos.Magic() == m_magic)
         {
            double point = SymbolInfoDouble(m_symbol, SYMBOL_POINT);
            double bid = SymbolInfoDouble(m_symbol, SYMBOL_BID);
            double ask = SymbolInfoDouble(m_symbol, SYMBOL_ASK);

            if(m_pos.PositionType() == POSITION_TYPE_BUY)
            {
               double new_sl = bid - atr_points * point;
               if(new_sl > m_pos.StopLoss() + 5 * point)
                  m_trade.PositionModify(m_pos.Ticket(), new_sl, m_pos.TakeProfit());
            }
            else
            {
               double new_sl = ask + atr_points * point;
               if(new_sl < m_pos.StopLoss() - 5 * point || m_pos.StopLoss() == 0)
                  m_trade.PositionModify(m_pos.Ticket(), new_sl, m_pos.TakeProfit());
            }
         }
      }
   }
};
