//+------------------------------------------------------------------+
//|                                                SharedMemory.mqh |
//+------------------------------------------------------------------+
#property strict

struct SharedData {
    double account_risk;
    int total_positions;
    bool emergency_mode;
    char last_signal[16];
    long last_update_time;
};

#import "SharedMemory.dll"
bool WriteSharedData(int index, SharedData &data);
bool ReadSharedData(int index, SharedData &data);
bool AES256Encrypt(uchar &data[], int data_len, uchar &key[], uchar &iv[], uchar &out[], int &out_len);
bool AES256Decrypt(uchar &data[], int data_len, uchar &key[], uchar &iv[], uchar &out[], int &out_len);
#import
