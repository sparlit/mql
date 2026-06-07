//+------------------------------------------------------------------+
//|                                              AAT-Dashboard.mqh |
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
   int               m_rows;
   int               m_cols;
   int               m_cell_w;
   int               m_cell_h;

   color             m_bg_color;
   color             m_text_color;
   color             m_neon_green;
   color             m_neon_red;
   color             m_neon_blue;
   color             m_neon_yellow;
   color             m_neon_orange;

   string            m_headers[];
   string            m_data[][16];
   color             m_colors[][16];
   bool              m_readonly[][16];

   bool              m_config_open;
   int               m_active_tab; // 0: Health, 1: Analytics, 2: Settings

public:
                     CDashboard() : m_bg_color(0xEE141414), m_text_color(clrWhite),
                                     m_neon_green(0xFF39FF14), m_neon_red(0xFFFF3131),
                                     m_neon_blue(0xFF00F3FF), m_neon_yellow(0xFFFFF000),
                                     m_neon_orange(0xFFFF9900)
   {
      m_rows = 8; m_cols = 16;
      ArrayResize(m_headers, m_cols);
      ArrayResize(m_data, m_rows);
      ArrayResize(m_colors, m_rows);
      ArrayResize(m_readonly, m_rows);
      m_config_open = false;
   }
                    ~CDashboard() { m_canvas.Destroy(); }

   bool Create(int x, int y, int cell_w, int cell_h, int width, int height)
   {
      m_x = x; m_y = y; m_cell_w = cell_w; m_cell_h = cell_h;
      m_width = width; m_height = height;
      m_active_tab = 0;
      if(!m_canvas.CreateBitmapLabel("AAT_Dashboard", x, y, 1200, 400, COLOR_FORMAT_ARGB_NORMALIZE)) return false;
      Render();
      return true;
   }

   void SetHeader(int col, string text) { if(col < m_cols) m_headers[col] = text; }

   void SetCellValue(int row, int col, string value, color clr = clrWhite)
   {
      if(row < m_rows && col < m_cols) { m_data[row][col] = value; m_colors[row][col] = clr; Render(); }
   }

   string GetCellValue(int row, int col) { return (row < m_rows && col < m_cols) ? m_data[row][col] : ""; }

   void SetCellReadOnly(int row, int col, bool ro) { if(row < m_rows && col < m_cols) m_readonly[row][col] = ro; }

   void Destroy() { m_canvas.Destroy(); }

   void Render()
   {
      m_canvas.Erase(m_bg_color);

      // 1. Static Global Header (Priority 1)
      m_canvas.FillRectangle(0, 0, 1200, 30, 0xFF222222);
      m_canvas.FontSet("Verdana", 10, FW_BOLD);
      m_canvas.TextOut(10, 7, "AAT SOVEREIGN CITADEL V4.1.0", ColorToARGB(m_neon_green));

      // 2. Tab Navigation
      string tabs[] = {"[ HEALTH ]", "[ ANALYTICS ]", "[ SETTINGS ]"};
      for(int t=0; t<3; t++) {
         color clr = (m_active_tab == t) ? m_neon_yellow : clrGray;
         m_canvas.TextOut(400 + t*150, 7, tabs[t], ColorToARGB(clr));
      }

      // 3. Tab Content
      if(m_active_tab == 0) RenderHealthTab();
      else if(m_active_tab == 1) RenderAnalyticsTab();
      else RenderSettingsTab();

      m_canvas.Update();
   }

   void RenderHealthTab()
   {
      m_canvas.FontSet("Arial", 9);
      m_canvas.TextOut(10, 50, "HEARTBEAT:", ColorToARGB(clrWhite));
      m_canvas.TextOut(120, 50, m_data[1][13], ColorToARGB(m_colors[1][13]));

      m_canvas.TextOut(10, 80, "LATENCY:", ColorToARGB(clrWhite));
      m_canvas.TextOut(120, 80, m_data[1][12], ColorToARGB(m_colors[1][12]));

      m_canvas.TextOut(10, 110, "ARBITRAGE:", ColorToARGB(clrWhite));
      m_canvas.TextOut(120, 110, m_data[1][14], ColorToARGB(m_colors[1][14]));
   }

   void RenderAnalyticsTab()
   {
      m_canvas.FontSet("Arial", 9);
      m_canvas.TextOut(10, 50, "MODE:", ColorToARGB(clrWhite));
      m_canvas.TextOut(120, 50, m_data[1][1], ColorToARGB(m_colors[1][1]));
      // More analytics metrics...
   }

   void RenderSettingsTab()
   {
      m_canvas.TextOut(10, 50, "RISK PER TRADE: 1.0%", ColorToARGB(m_neon_blue));
      m_canvas.TextOut(10, 80, "VAULT STATUS: SECURE", ColorToARGB(m_neon_green));
      m_canvas.TextOut(10, 110, "AI SERVER: 127.0.0.1:8082", ColorToARGB(m_neon_yellow));
   }

   void SetTab(int tab) { m_active_tab = tab; Render(); }

   int GetTabAt(int x, int y)
   {
      // Relative coordinate detection (Institutional Grade)
      if(y < 30) {
         if(x >= 400 && x < 550) return 0;
         if(x >= 550 && x < 700) return 1;
         if(x >= 700 && x < 850) return 2;
      }
      return -1;
   }

   void ToggleConfig() { m_config_open = !m_config_open; Render(); }
  };
