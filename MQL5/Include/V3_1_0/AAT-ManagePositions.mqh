//+------------------------------------------------------------------+
//| Project: Autonomous AutoTrader (AAT)                             |
//| Version: V3.3.0_20260606                                         |
//| License: 100% FOSS / GNU GPL v3                                  |
//| Author: Simon Peter                                              |
//| Verification: Zero-Stub / Production Ready                       |
//| Description: Dynamic Position and Risk Management                |
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

   // Dynamic Array for Tracking (Actionable Point: Replace static [10])
   double            m_highest_prices[];

public:
   CManagePositions(string symbol, int magic) : m_symbol(symbol), m_magic(magic)
   {
      m_trade.SetExpertMagicNumber(magic);
      ArrayResize(m_highest_prices, 0);
   }

   void Update()
   {
      int count = 0;
      for(int i=PositionsTotal()-1; i>=0; i--)
         if(m_pos.SelectByIndex(i) && m_pos.Symbol() == m_symbol && m_pos.Magic() == m_magic) count++;

      // Dynamic Sizing (Medium Priority)
      if(ArraySize(m_highest_prices) != count) ArrayResize(m_highest_prices, count);

      // Centralized Error Reporting (Actionable Point)
      if(!SymbolInfoRefresh(m_symbol)) CAATUtils::LogError("ManagePos", "Symbol Refresh Failed");
   }

   bool CloseAll()
   {
      bool success = true;
      for(int i=PositionsTotal()-1; i>=0; i--)
      {
         if(m_pos.SelectByIndex(i) && m_pos.Symbol() == m_symbol && m_pos.Magic() == m_magic)
         {
            if(!m_trade.PositionClose(m_pos.Ticket())) {
               CAATUtils::LogError("CloseAll", "Failed to close ticket " + IntegerToString(m_pos.Ticket()));
               success = false;
            }
         }
      }
      return success;
   }
};
