#include <windows.h>
#include <map>
#include <string>

#define EXPORT __declspec(dllexport)

// Shared memory structure for inter-chart communication
struct ChartData {
    double price;
    int signal;
    long long timestamp;
};

std::map<std::string, ChartData>* shared_map = nullptr;
HANDLE hMutex = NULL;

extern "C" {
    EXPORT bool __stdcall InitSharedMemory() {
        if (!shared_map) {
            shared_map = new std::map<std::string, ChartData>();
            hMutex = CreateMutex(NULL, FALSE, "AAT_SharedMemory_Mutex");
        }
        return true;
    }

    EXPORT void __stdcall SetChartData(const char* symbol, double price, int signal) {
        if (!shared_map) return;
        WaitForSingleObject(hMutex, INFINITE);
        ChartData data = { price, signal, GetTickCount64() };
        (*shared_map)[symbol] = data;
        ReleaseMutex(hMutex);
    }

    EXPORT int __stdcall GetChartSignal(const char* symbol) {
        if (!shared_map) return 0;
        WaitForSingleObject(hMutex, INFINITE);
        int signal = 0;
        if (shared_map->count(symbol)) {
            signal = (*shared_map)[symbol].signal;
        }
        ReleaseMutex(hMutex);
        return signal;
    }

    EXPORT void __stdcall DeinitSharedMemory() {
        if (shared_map) {
            delete shared_map;
            shared_map = nullptr;
            CloseHandle(hMutex);
        }
    }
}
