//+------------------------------------------------------------------+
//|                                                    JsonParser.mqh |
//|                                  Copyright 2024, AI Trader Corp. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, AI Trader Corp."
#property link      "https://www.mql5.com"
#property strict

/*
   Industrial-grade Minimalist JSON Parser
   Handles basic types, escaped characters, and ignores whitespace.
*/

class CJsonParser
{
public:
   static string GetString(string json, string key)
     {
      int pos = FindKey(json, key);
      if(pos == -1) return "";

      int val_start = StringFind(json, "\"", pos);
      if(val_start == -1) return "";
      val_start++;

      string result = "";
      bool escaped = false;
      for(int i = val_start; i < StringLen(json); i++)
        {
         ushort c = StringGetCharacter(json, i);
         if(escaped)
           {
            result += ShortToString(c);
            escaped = false;
            continue;
           }
         if(c == '\\')
           {
            escaped = true;
            continue;
           }
         if(c == '\"') break;
         result += ShortToString(c);
        }
      return result;
     }

   static double GetDouble(string json, string key)
     {
      int pos = FindKey(json, key);
      if(pos == -1) return 0;

      int len = StringLen(json);
      while(pos < len)
        {
         ushort c = StringGetCharacter(json, pos);
         if((c >= '0' && c <= '9') || c == '-' || c == '.') break;
         pos++;
        }

      int start = pos;
      while(pos < len)
        {
         ushort c = StringGetCharacter(json, pos);
         if(!((c >= '0' && c <= '9') || c == '-' || c == '.' || c == 'e' || c == 'E')) break;
         pos++;
        }

      if(start == pos) return 0;
      return StringToDouble(StringSubstr(json, start, pos - start));
     }

   static bool GetBool(string json, string key)
     {
      int pos = FindKey(json, key);
      if(pos == -1) return false;

      string sub = StringSubstr(json, pos, 10);
      if(StringFind(sub, "true") != -1) return true;
      return false;
     }

private:
   static int FindKey(string json, string key)
     {
      string search = "\"" + key + "\"";
      int key_pos = StringFind(json, search);
      if(key_pos == -1) return -1;

      int colon_pos = StringFind(json, ":", key_pos + StringLen(search));
      if(colon_pos == -1) return -1;

      return colon_pos + 1;
     }
};
