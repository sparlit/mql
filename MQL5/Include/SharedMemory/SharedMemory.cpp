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

/**
 * @brief Writes a SharedData record into the globally named shared memory at the specified index.
 *
 * Stores the contents of `data` into the shared memory region reserved by this module at position
 * `index`. The function expects `data` to point to a valid SharedData instance and the mapped
 * shared memory to be large enough to contain an entry at `index`.
 *
 * @param index Zero-based slot index within the shared memory region where the record will be written.
 *               Valid indices are 0 through 99 (inclusive) for the current mapping size.
 * @param data Pointer to the SharedData to write; must not be null.
 * @return `true` if the record was written successfully, `false` on any failure.
 */
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

/**
 * @brief Reads a SharedData entry from the global shared memory region into the provided buffer.
 *
 * Copies the SharedData record located at the given zero-based index from the named memory-mapped region into `data`.
 * Note: the function does not validate that `index` is within bounds of the mapping.
 *
 * @param index Zero-based slot index of the SharedData entry to read.
 * @param data Pointer to a caller-provided buffer that receives the copied SharedData (must be at least sizeof(SharedData)).
 * @return bool `true` if the entry was successfully read, `false` on failure (e.g., shared memory unavailable).
 */
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

/**
 * @brief Encrypts a buffer using AES-256 in CBC mode.
 *
 * Performs AES-256-CBC encryption of the input buffer and writes the ciphertext to the provided output buffer.
 *
 * @param data Pointer to the plaintext input bytes.
 * @param data_len Length of the plaintext in bytes.
 * @param key Pointer to the 32-byte (256-bit) encryption key.
 * @param iv Pointer to the 16-byte initialization vector.
 * @param out Buffer that receives the ciphertext; must have at least the size provided via `*out_len` on entry.
 * @param out_len On entry, the capacity of `out` in bytes; on return, the number of bytes written to `out`.
 * @return bool `true` if encryption succeeds, `false` otherwise.
 */
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

/**
 * @brief Decrypts AES-256-CBC ciphertext into the provided output buffer.
 *
 * Decrypts `data` (ciphertext) using a 32-byte AES-256 key and a 16-byte IV in CBC mode.
 *
 * @param data Pointer to the ciphertext bytes to decrypt.
 * @param data_len Length of the ciphertext in bytes.
 * @param key Pointer to a 32-byte AES-256 key.
 * @param iv Pointer to a 16-byte initialization vector (IV).
 * @param out Pointer to the buffer that will receive the decrypted plaintext; buffer must be at least `data_len` bytes.
 * @param out_len Pointer to an integer that will be set to the resulting plaintext length in bytes on success.
 * @return true if decryption succeeds and `out`/`out_len` are populated, false on failure.
 */
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
