//+------------------------------------------------------------------+
//|                                                    JsonParser.mqh |
//|                                  Copyright 2024, AI Trader Corp. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, AI Trader Corp."
#property link      "https://www.mql5.com"
#property strict

class CJsonParser
{
public:
   static string GetString(string json, string key)
     {
      string search = "\"" + key + "\"";
      int key_start = StringFind(json, search);
      if(key_start == -1) return "";

      int colon_pos = StringFind(json, ":", key_start + StringLen(search));
      if(colon_pos == -1) return "";

      int val_start = StringFind(json, "\"", colon_pos);
      if(val_start == -1) return "";
      val_start++;

      int val_end = StringFind(json, "\"", val_start);
      if(val_end == -1) return "";

      return StringSubstr(json, val_start, val_end - val_start);
     }

   static double GetDouble(string json, string key)
     {
      string search = "\"" + key + "\"";
      int key_start = StringFind(json, search);
      if(key_start == -1) return 0;

      int colon_pos = StringFind(json, ":", key_start + StringLen(search));
      if(colon_pos == -1) return 0;

      int val_start = colon_pos + 1;
      while(val_start < StringLen(json) && (StringSubstr(json, val_start, 1) == " " || StringSubstr(json, val_start, 1) == "\t"))
         val_start++;

      int val_end = val_start;
      while(val_end < StringLen(json) &&
            StringFind("0123456789.-", StringSubstr(json, val_end, 1)) != -1)
         val_end++;

      if(val_start == val_end) return 0;
      return StringToDouble(StringSubstr(json, val_start, val_end - val_start));
     }

   static bool GetBool(string json, string key)
     {
      string search = "\"" + key + "\"";
      int key_start = StringFind(json, search);
      if(key_start == -1) return false;

      int colon_pos = StringFind(json, ":", key_start + StringLen(search));
      if(colon_pos == -1) return false;

      int val_start = colon_pos + 1;
      while(val_start < StringLen(json) && (StringSubstr(json, val_start, 1) == " " || StringSubstr(json, val_start, 1) == "\t"))
         val_start++;

      if(StringSubstr(json, val_start, 4) == "true") return true;
      return false;
     }
};
