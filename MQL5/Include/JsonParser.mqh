//+------------------------------------------------------------------+
//|                                                    JsonParser.mqh |
//|                                  Copyright 2024, AI Trader Corp. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, AI Trader Corp."
#property link      "https://www.mql5.com"
#property strict

// A simple manual JSON parser to extract key values from the engine's response
class CJsonParser
{
public:
   static string GetString(string json, string key)
     {
      string search = "\"" + key + "\":\"";
      int start = StringFind(json, search);
      if(start == -1) return "";
      start += StringLen(search);
      int end = StringFind(json, "\"", start);
      if(end == -1) return "";
      return StringSubstr(json, start, end - start);
     }

   static double GetDouble(string json, string key)
     {
      string search = "\"" + key + "\":";
      int start = StringFind(json, search);
      if(start == -1) return 0;
      start += StringLen(search);
      int end = StringFind(json, ",", start);
      if(end == -1) end = StringFind(json, "}", start);
      if(end == -1) return 0;
      return StringToDouble(StringSubstr(json, start, end - start));
     }

   static bool GetBool(string json, string key)
     {
      string search = "\"" + key + "\":";
      int start = StringFind(json, search);
      if(start == -1) return false;
      start += StringLen(search);
      if(StringSubstr(json, start, 4) == "true") return true;
      return false;
     }
};
