#include <windows.h>
#include <string>
#include <vector>
#include <wincrypt.h>

#define EXPORT extern "C" __declspec(dllexport)

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
    if (pBuf == NULL) { CloseHandle(hMapFile); return false; }
    memcpy((char*)pBuf + (index * sizeof(SharedData)), data, sizeof(SharedData));
    UnmapViewOfFile(pBuf);
    CloseHandle(hMapFile);
    return true;
}

EXPORT bool ReadSharedData(int index, SharedData* data) {
    HANDLE hMapFile = OpenFileMappingA(FILE_MAP_ALL_ACCESS, FALSE, SHM_NAME);
    if (hMapFile == NULL) return false;
    void* pBuf = MapViewOfFile(hMapFile, FILE_MAP_ALL_ACCESS, 0, 0, SHM_SIZE);
    if (pBuf == NULL) { CloseHandle(hMapFile); return false; }
    memcpy(data, (char*)pBuf + (index * sizeof(SharedData)), sizeof(SharedData));
    UnmapViewOfFile(pBuf);
    CloseHandle(hMapFile);
    return true;
}

// AES-256 CBC using Windows CryptoAPI
EXPORT bool AES256Encrypt(unsigned char* data, int data_len, unsigned char* key, unsigned char* iv, unsigned char* out, int* out_len) {
    HCRYPTPROV hProv = 0;
    HCRYPTKEY hKey = 0;
    HCRYPTHASH hHash = 0;

    if (!CryptAcquireContext(&hProv, NULL, MS_ENH_RSA_AES_PROV, PROV_RSA_AES, CRYPT_VERIFYCONTEXT)) return false;

    struct KeyBlob {
        BLOBHEADER header;
        DWORD cbKeySize;
        BYTE rgbKeyData[32];
    } blob;

    blob.header.bType = PLAINTEXTKEYBLOB;
    blob.header.bVersion = CUR_BLOB_VERSION;
    blob.header.reserved = 0;
    blob.header.aiKeyAlg = CALG_AES_256;
    blob.cbKeySize = 32;
    memcpy(blob.rgbKeyData, key, 32);

    if (!CryptImportKey(hProv, (BYTE*)&blob, sizeof(blob), 0, 0, &hKey)) {
        CryptReleaseContext(hProv, 0);
        return false;
    }

    CryptSetKeyParam(hKey, KP_IV, iv, 0);
    DWORD mode = CRYPT_MODE_CBC;
    CryptSetKeyParam(hKey, KP_MODE, (BYTE*)&mode, 0);

    DWORD dwLen = data_len;
    memcpy(out, data, data_len);
    if (!CryptEncrypt(hKey, 0, TRUE, 0, out, &dwLen, *out_len)) {
        CryptDestroyKey(hKey);
        CryptReleaseContext(hProv, 0);
        return false;
    }

    *out_len = dwLen;
    CryptDestroyKey(hKey);
    CryptReleaseContext(hProv, 0);
    return true;
}

EXPORT bool AES256Decrypt(unsigned char* data, int data_len, unsigned char* key, unsigned char* iv, unsigned char* out, int* out_len) {
    HCRYPTPROV hProv = 0;
    HCRYPTKEY hKey = 0;

    if (!CryptAcquireContext(&hProv, NULL, MS_ENH_RSA_AES_PROV, PROV_RSA_AES, CRYPT_VERIFYCONTEXT)) return false;

    struct KeyBlob {
        BLOBHEADER header;
        DWORD cbKeySize;
        BYTE rgbKeyData[32];
    } blob;

    blob.header.bType = PLAINTEXTKEYBLOB;
    blob.header.bVersion = CUR_BLOB_VERSION;
    blob.header.reserved = 0;
    blob.header.aiKeyAlg = CALG_AES_256;
    blob.cbKeySize = 32;
    memcpy(blob.rgbKeyData, key, 32);

    if (!CryptImportKey(hProv, (BYTE*)&blob, sizeof(blob), 0, 0, &hKey)) {
        CryptReleaseContext(hProv, 0);
        return false;
    }

    CryptSetKeyParam(hKey, KP_IV, iv, 0);
    DWORD mode = CRYPT_MODE_CBC;
    CryptSetKeyParam(hKey, KP_MODE, (BYTE*)&mode, 0);

    DWORD dwLen = data_len;
    memcpy(out, data, data_len);
    if (!CryptDecrypt(hKey, 0, TRUE, 0, out, &dwLen)) {
        CryptDestroyKey(hKey);
        CryptReleaseContext(hProv, 0);
        return false;
    }

    *out_len = dwLen;
    CryptDestroyKey(hKey);
    CryptReleaseContext(hProv, 0);
    return true;
}
