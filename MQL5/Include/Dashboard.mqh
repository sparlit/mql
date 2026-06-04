//+------------------------------------------------------------------+
//|                                                   Dashboard.mqh |
//|                                  Copyright 2024, AI Trader Corp. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, AI Trader Corp."
#property link      "https://www.mql5.com"
#property strict

#include <ChartObjects\ChartObjectsTxtControls.mqh>

//+------------------------------------------------------------------+
//| CDashboard Class                                                 |
//+------------------------------------------------------------------+
class CDashboard
  {
private:
   int               m_rows;
   int               m_cols;
   int               m_x_start;
   int               m_y_start;
   int               m_cell_width;
   int               m_cell_height;
   color             m_header_bg;
   color             m_cell_bg;
   color             m_text_color;

   CChartObjectEdit  m_cells[][10]; // Fixed max columns for simplicity in this version

public:
                     CDashboard(void);
                    ~CDashboard(void);

   void              Create(int rows, int cols, int x, int y, int width, int height);
   void              SetHeader(int col, string text);
   void              SetCellValue(int row, int col, string value, color clr = clrWhite);
   void              Destroy(void);
  };

//+------------------------------------------------------------------+
//| Constructor                                                      |
//+------------------------------------------------------------------+
CDashboard::CDashboard(void) : m_rows(0), m_cols(0), m_x_start(10), m_y_start(30), m_cell_width(100), m_cell_height(20)
  {
   m_header_bg = C'50,50,50';
   m_cell_bg = C'30,30,30';
   m_text_color = clrWhite;
  }

//+------------------------------------------------------------------+
//| Destructor                                                       |
//+------------------------------------------------------------------+
CDashboard::~CDashboard(void)
  {
   Destroy();
  }

//+------------------------------------------------------------------+
//| Create the grid                                                  |
//+------------------------------------------------------------------+
void CDashboard::Create(int rows, int cols, int x, int y, int width, int height)
  {
   m_rows = rows;
   m_cols = cols;
   m_x_start = x;
   m_y_start = y;
   m_cell_width = width;
   m_cell_height = height;

   ArrayResize(m_cells, m_rows);

   for(int r=0; r<m_rows; r++)
     {
      for(int c=0; c<m_cols; c++)
        {
         string name = "DB_Cell_" + IntegerToString(r) + "_" + IntegerToString(c);
         m_cells[r][c].Create(0, name, 0, m_x_start + c*m_cell_width, m_y_start + r*m_cell_height, m_cell_width, m_cell_height);
         m_cells[r][c].BackColor(r == 0 ? m_header_bg : m_cell_bg);
         m_cells[r][c].Color(m_text_color);
         m_cells[r][c].FontSize(8);
         m_cells[r][c].TextAlign(ALIGN_CENTER);
         m_cells[r][c].ReadOnly(true);
        }
     }
  }

//+------------------------------------------------------------------+
//| Set Header Text                                                  |
//+------------------------------------------------------------------+
void CDashboard::SetHeader(int col, string text)
  {
   if(col >= 0 && col < m_cols)
      m_cells[0][col].Description(text);
  }

//+------------------------------------------------------------------+
//| Set Cell Value                                                   |
//+------------------------------------------------------------------+
void CDashboard::SetCellValue(int row, int col, string value, color clr = clrWhite)
  {
   if(row >= 0 && row < m_rows && col >= 0 && col < m_cols)
     {
      m_cells[row][col].Description(value);
      m_cells[row][col].Color(clr);
     }
  }

//+------------------------------------------------------------------+
//| Destroy Dashboard                                                |
//+------------------------------------------------------------------+
void CDashboard::Destroy(void)
  {
   for(int r=0; r<m_rows; r++)
     {
      for(int c=0; c<m_cols; c++)
        {
         m_cells[r][c].Delete();
        }
     }
  }
