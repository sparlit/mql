#include <windows.h>
#include <string>
#include <mutex>
#include <vector>

#define SHARED_MEM_SIZE 65536
#define MAX_ENTRIES 512
#define KEY_SIZE 32
#define VAL_SIZE 32
#define MUTEX_NAME "Global\\AAT_SharedMem_Mutex"
#define MAP_NAME "Global\\AAT_Benchmark_Mem"
#define LOCK_TIMEOUT 500

struct Entry {
    char key[KEY_SIZE];
    char value[VAL_SIZE];
};

struct SharedData {
    Entry entries[MAX_ENTRIES];
    int count;
};

static HANDLE hMapFile = NULL;
static SharedData* pBuf = NULL;
static HANDLE hMutex = NULL;

void Initialize() {
    if (hMapFile == NULL) {
        hMapFile = CreateFileMappingA(INVALID_HANDLE_VALUE, NULL, PAGE_READWRITE, 0, sizeof(SharedData), MAP_NAME);
        if (hMapFile) {
            bool isNew = (GetLastError() != ERROR_ALREADY_EXISTS);
            pBuf = (SharedData*)MapViewOfFile(hMapFile, FILE_MAP_ALL_ACCESS, 0, 0, sizeof(SharedData));
            if (isNew && pBuf) {
                pBuf->count = 0;
                memset(pBuf->entries, 0, sizeof(pBuf->entries));
            }
        }
    }
    if (hMutex == NULL) {
        hMutex = CreateMutexA(NULL, FALSE, MUTEX_NAME);
    }
}

extern "C" __declspec(dllexport) bool WriteSharedData(const char* name, const char* value) {
    Initialize();
    if (pBuf && hMutex) {
        if (WaitForSingleObject(hMutex, LOCK_TIMEOUT) == WAIT_OBJECT_0) {
            bool found = false;
            for (int i = 0; i < pBuf->count; i++) {
                if (_stricmp(pBuf->entries[i].key, name) == 0) {
                    strncpy_s(pBuf->entries[i].value, VAL_SIZE, value, _TRUNCATE);
                    found = true;
                    break;
                }
            }
            if (!found && pBuf->count < MAX_ENTRIES) {
                strncpy_s(pBuf->entries[pBuf->count].key, KEY_SIZE, name, _TRUNCATE);
                strncpy_s(pBuf->entries[pBuf->count].value, VAL_SIZE, value, _TRUNCATE);
                pBuf->count++;
            }
            ReleaseMutex(hMutex);
            return true;
        }
    }
    return false;
}

extern "C" __declspec(dllexport) const char* ReadSharedData(const char* name) {
    Initialize();
    static char local_buf[VAL_SIZE];
    local_buf[0] = '\0';
    if (pBuf && hMutex) {
        if (WaitForSingleObject(hMutex, LOCK_TIMEOUT) == WAIT_OBJECT_0) {
            for (int i = 0; i < pBuf->count; i++) {
                if (_stricmp(pBuf->entries[i].key, name) == 0) {
                    strncpy_s(local_buf, VAL_SIZE, pBuf->entries[i].value, _TRUNCATE);
                    break;
                }
            }
            ReleaseMutex(hMutex);
        }
    }
    return local_buf;
}
