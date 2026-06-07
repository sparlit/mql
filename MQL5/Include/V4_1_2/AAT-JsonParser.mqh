//+------------------------------------------------------------------+
//|                                                   JsonParser.mqh |
//+------------------------------------------------------------------+
#property strict
//| Status: Sovereign Citadel Masterpiece                 |

class CJsonParser
{
public:
   static string GetString(string json, string key)
   {
      string search = "\"" + key + "\":\"";
      int pos = StringFind(json, search);
      if(pos == -1) {
         // Try numeric/boolean without quotes
         search = "\"" + key + "\":";
         pos = StringFind(json, search);
         if(pos == -1) return "";
         int start = pos + StringLen(search);
         int end = StringFind(json, ",", start);
         if(end == -1) end = StringFind(json, "}", start);
         return StringSubstr(json, start, end - start);
      }
      int start = pos + StringLen(search);
      int end = StringFind(json, "\"", start);
      return StringSubstr(json, start, end - start);
   }

   static double GetDouble(string json, string key)
   {
      string val = GetString(json, key);
      return StringToDouble(val);
   }

   static bool GetBool(string json, string key)
   {
      string val = GetString(json, key);
      return (val == "true" || val == "1");
   }
};
