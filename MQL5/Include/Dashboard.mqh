//+------------------------------------------------------------------+
//|                                                   Dashboard.mqh |
//|                                  Copyright 2024, AI Trader Corp. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#include <Canvas\Canvas.mqh>

class CDashboard
  {
private:
   CCanvas           m_canvas;
   int               m_width;
   int               m_height;
   int               m_x;
   int               m_y;

   color             m_bg_color;
   color             m_text_color;
   color             m_neon_green;
   color             m_neon_red;

public:
                     CDashboard() : m_bg_color(C'20,20,20'), m_text_color(clrWhite), m_neon_green(C'57,255,20'), m_neon_red(C'FF,49,49') {}
                    ~CDashboard() { m_canvas.Destroy(); }

   bool              Create(string name, int x, int y, int width, int height)
     {
      m_x = x; m_y = y; m_width = width; m_height = height;
      if(!m_canvas.CreateBitmapLabel(name, x, y, width, height, COLOR_FORMAT_ARGB_NORMALIZE)) return false;
      Render();
      return true;
     }

   void              Update(string symbol, string status, string signal, double confidence, string regime)
     {
      m_canvas.Erase(0xCC141414); // Semi-transparent charcoal

      m_canvas.FontSet("Courier New", 14, FW_BOLD);
      m_canvas.TextOut(10, 10, "AUTONOMOUS TRADER - v2.0", ColorToARGB(m_text_color));

      m_canvas.FontSet("Arial", 11);
      m_canvas.TextOut(10, 40, "SYMBOL: " + symbol, ColorToARGB(m_text_color));
      m_canvas.TextOut(10, 60, "STATUS: " + status, ColorToARGB(status == "TRADE!" ? m_neon_green : clrYellow));

      color signal_clr = (signal == "BUY") ? m_neon_green : (signal == "SELL" ? m_neon_red : clrWhite);
      m_canvas.TextOut(10, 80, "SIGNAL: " + signal + " (" + DoubleToString(confidence, 0) + ")", ColorToARGB(signal_clr));
      m_canvas.TextOut(10, 100, "REGIME: " + regime, ColorToARGB(clrCyan));

      m_canvas.Update();
     }

   void              Render()
     {
      m_canvas.Erase(0xCC141414);
      m_canvas.Update();
     }
  };
