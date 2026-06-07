//+------------------------------------------------------------------+
//| Project: Autonomous AutoTrader (AAT)                             |
//| Version: V4.1.2_20260607                                         |
//| License: 100% FOSS / GNU GPL v3                                  |
//| Status: Sovereign Citadel Masterpiece                 |
//| Author: Simon Peter                                              |
//| Verification: Zero-Stub / Production Ready                       |
//| Description: Centralized Utilities and Error Logging              |
//+------------------------------------------------------------------+
#property copyright "Copyright 2026, Simon Peter"
#property strict

#import "V4_1_2\SharedMemory.dll"
   bool WriteSharedData(string name, string value);
   string ReadSharedData(string name);
#import

class CAATUtils
{
public:
   static void LogError(string source, string message)
   {
      string full_msg = StringFormat("AAT ERROR [%s]: %s (Code: %d)", source, message, GetLastError());
      Print(full_msg);
   }

   static void LogInfo(string message)
   {
      Print("AAT INFO: ", message);
   }

   static double PipToPoint(string symbol)
   {
      int digits = (int)SymbolInfoInteger(symbol, SYMBOL_DIGITS);
      return (digits == 3 || digits == 5) ? 0.0001 : 0.01;
   }

   static bool ValidateInputs(double risk, int sl, int tp)
   {
      if(risk <= 0 || risk > 10) { LogError("Init", "Invalid Risk %"); return false; }
      if(sl <= 0 || tp <= 0) { LogError("Init", "Invalid SL/TP points"); return false; }
      return true;
   }

   static void SetSharedBenchmark(string symbol, double price)
   {
      WriteSharedData(symbol, DoubleToString(price, 5));
   }

   static double GetSharedBenchmark(string symbol)
   {
      string val = ReadSharedData(symbol);
      if(val == "") return 0;
      return StringToDouble(val);
   }
};
