#include <windows.h>
#include <string>

#define EXPORT extern "C" __declspec(dllexport)

// Structure for shared data - using types that match MQL5 (long long = 8 bytes)
#pragma pack(push, 1)
struct SharedData {
    double account_risk;
    int total_positions;
    bool emergency_mode;
    char last_signal[16];
    long long last_update_time;
};
#pragma pack(pop)

const char* SHM_NAME = "Global\\AutonomousTrader_SharedMemory";
const int SHM_SIZE = sizeof(SharedData) * 100;

EXPORT bool WriteSharedData(int index, SharedData* data) {
    HANDLE hMapFile = CreateFileMappingA(INVALID_HANDLE_VALUE, NULL, PAGE_READWRITE, 0, SHM_SIZE, SHM_NAME);
    if (hMapFile == NULL) return false;

    void* pBuf = MapViewOfFile(hMapFile, FILE_MAP_ALL_ACCESS, 0, 0, SHM_SIZE);
    if (pBuf == NULL) {
        CloseHandle(hMapFile);
        return false;
    }

    memcpy((char*)pBuf + (index * sizeof(SharedData)), data, sizeof(SharedData));

    UnmapViewOfFile(pBuf);
    CloseHandle(hMapFile);
    return true;
}

EXPORT bool ReadSharedData(int index, SharedData* data) {
    HANDLE hMapFile = OpenFileMappingA(FILE_MAP_ALL_ACCESS, FALSE, SHM_NAME);
    if (hMapFile == NULL) return false;

    void* pBuf = MapViewOfFile(hMapFile, FILE_MAP_ALL_ACCESS, 0, 0, SHM_SIZE);
    if (pBuf == NULL) {
        CloseHandle(hMapFile);
        return false;
    }

    memcpy(data, (char*)pBuf + (index * sizeof(SharedData)), sizeof(SharedData));

    UnmapViewOfFile(pBuf);
    CloseHandle(hMapFile);
    return true;
}
