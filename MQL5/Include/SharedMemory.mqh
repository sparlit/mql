//+------------------------------------------------------------------+
//|                                                SharedMemory.mqh |
//+------------------------------------------------------------------+
#property strict

#import "SharedMemory.dll"
bool InitSharedMemory();
void SetChartData(string symbol, double price, int signal);
int  GetChartSignal(string symbol);
void DeinitSharedMemory();
#import
