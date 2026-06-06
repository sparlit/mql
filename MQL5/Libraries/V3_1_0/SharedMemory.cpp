#include <windows.h>
#include <string>

#define SHARED_MEM_SIZE 65536

struct SharedData {
    char data[SHARED_MEM_SIZE];
};

static HANDLE hMapFile = NULL;
static SharedData* pBuf = NULL;

extern "C" __declspec(dllexport) bool WriteSharedData(const char* name, const char* value) {
    if (hMapFile == NULL) {
        hMapFile = CreateFileMapping(INVALID_HANDLE_VALUE, NULL, PAGE_READWRITE, 0, sizeof(SharedData), "AAT_Benchmark_Mem");
        pBuf = (SharedData*)MapViewOfFile(hMapFile, FILE_MAP_ALL_ACCESS, 0, 0, sizeof(SharedData));
    }
    if (pBuf) {
        // Optimized benchmark distribution (Priority 3)
        strncpy(pBuf->data, value, SHARED_MEM_SIZE);
        return true;
    }
    return false;
}

extern "C" __declspec(dllexport) const char* ReadSharedData(const char* name) {
    if (pBuf) return pBuf->data;
    return "";
}
