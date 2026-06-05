//+------------------------------------------------------------------+
//|                                                SharedMemory.mqh |
//+------------------------------------------------------------------+
#property strict

struct SharedData {
    double account_risk;
    int total_positions;
    bool emergency_mode;
    char last_signal[16];
    long last_update_time; // MQL5 long is 8 bytes
};

#import "SharedMemory.dll"
bool WriteSharedData(int index, SharedData &data);
bool ReadSharedData(int index, SharedData &data);
#import
