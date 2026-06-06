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
   string            m_data[][12];
   color             m_colors[][12];
   bool              m_readonly[][12];

   bool              m_config_open;
   double            m_config_anim; // 0.0 to 1.0

public:
                     CDashboard() : m_bg_color(0xEE141414), m_text_color(clrWhite),
                                     m_neon_green(0xFF39FF14), m_neon_red(0xFFFF3131),
                                     m_neon_blue(0xFF00F3FF), m_neon_yellow(0xFFFFF000),
                                     m_neon_orange(0xFFFF9900)
   {
      m_rows = 8; m_cols = 12;
      ArrayResize(m_headers, m_cols);
      ArrayResize(m_data, m_rows);
      ArrayResize(m_colors, m_rows);
      ArrayResize(m_readonly, m_rows);
      m_config_open = false;
      m_config_anim = 0.0;
   }
                    ~CDashboard() { m_canvas.Destroy(); }

   bool Create(int x, int y, int cell_w, int cell_h, int width, int height)
   {
      m_x = x; m_y = y; m_cell_w = cell_w; m_cell_h = cell_h;
      m_width = width; m_height = height;
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

      // Draw Headers
      m_canvas.FontSet("Arial", 10, FW_BOLD);
      for(int c=0; c<m_cols; c++)
      {
         m_canvas.TextOut(c*100 + 5, 5, m_headers[c], ColorToARGB(m_neon_blue));
         m_canvas.Line(c*100, 0, c*100, 200, ColorToARGB(clrGray));
      }
      m_canvas.Line(0, 25, 1200, 25, ColorToARGB(m_neon_blue));

      // Draw Data
      m_canvas.FontSet("Arial", 9);
      for(int r=1; r<m_rows; r++)
      {
         for(int c=0; c<m_cols; c++)
         {
            m_canvas.TextOut(c*100 + 5, r*30 + 5, m_data[r][c], ColorToARGB(m_colors[r][c]));
         }
         m_canvas.Line(0, r*30 + 25, 1200, r*30 + 25, ColorToARGB(0x33FFFFFF));
      }

      // Draw Config Overlay (Sliding Animation Logic placeholder)
      if(m_config_open)
      {
         m_canvas.FillRectangle(800, 0, 1200, 400, 0xDD000000);
         m_canvas.TextOut(810, 10, "CONFIGURATION", ColorToARGB(m_neon_yellow));
         // Logic for sliders/buttons here
      }

      m_canvas.Update();
   }

   void ToggleConfig() { m_config_open = !m_config_open; Render(); }
  };
