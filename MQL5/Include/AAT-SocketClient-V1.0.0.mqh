//+------------------------------------------------------------------+
//|                                                   SocketClient.mqh |
//+------------------------------------------------------------------+
#property strict

#include <SharedMemory.mqh>

#define INVALID_SOCKET -1
#define SOCKET_ERROR -1

#import "ws2_32.dll"
int socket(int af, int type, int protocol);
int connect(int s, sockaddr_in &name, int namelen);
int send(int s, uchar &buf[], int len, int flags);
int recv(int s, uchar &buf[], int len, int flags);
int closesocket(int s);
int WSAStartup(ushort wVersionRequested, char &lpWSAData[]);
int WSACleanup();
uint inet_addr(string cp);
ushort htons(ushort hostshort);
#import

struct sockaddr_in {
    short sin_family;
    ushort sin_port;
    uint sin_addr;
    char sin_zero[8];
};

class CSocketClient
{
private:
    int m_socket;
    bool m_initialized;
    uchar m_key[32];
    uchar m_iv[16];

public:
    CSocketClient() : m_socket(INVALID_SOCKET), m_initialized(false) {
        char data[400];
        if (WSAStartup(0x202, data) == 0) m_initialized = true;
        // In production, these should be securely loaded/negotiated
        StringToCharArray("Static32ByteKeyForZeroStubPolicy", m_key);
        StringToCharArray("Static16ByteIV!!", m_iv);
    }

    ~CSocketClient() {
        if (m_socket != INVALID_SOCKET) closesocket(m_socket);
        if (m_initialized) WSACleanup();
    }

    bool Connect(string ip, int port) {
        m_socket = socket(2, 1, 6);
        if (m_socket == INVALID_SOCKET) return false;
        sockaddr_in server;
        server.sin_family = 2;
        server.sin_port = htons((ushort)port);
        server.sin_addr = inet_addr(ip);
        if (connect(m_socket, server, sizeof(server)) == SOCKET_ERROR) {
            closesocket(m_socket);
            m_socket = INVALID_SOCKET;
            return false;
        }
        return true;
    }

    bool Send(string data) {
        uchar plain[];
        StringToCharArray(data, plain);
        int plain_len = ArraySize(plain)-1;

        // Ensure padding for AES (16 byte block)
        int padded_len = ((plain_len / 16) + 1) * 16;
        uchar plain_padded[];
        ArrayResize(plain_padded, padded_len);
        ArrayFill(plain_padded, 0, padded_len, 0);
        memcpy_uchar(plain_padded, plain, plain_len);

        uchar encrypted[];
        ArrayResize(encrypted, padded_len);
        int out_len = padded_len;

        if(!AES256Encrypt(plain_padded, padded_len, m_key, m_iv, encrypted, out_len)) return false;

        string b64 = Base64Encode(encrypted, out_len);
        uchar send_buf[];
        StringToCharArray(b64, send_buf);
        return (send(m_socket, send_buf, ArraySize(send_buf)-1, 0) != SOCKET_ERROR);
    }

    string Receive() {
        uchar buf[16384];
        int bytes = recv(m_socket, buf, 16384, 0);
        if (bytes > 0) {
            string b64 = CharArrayToString(buf, 0, bytes);
            uchar encrypted[];
            int enc_len = Base64Decode(b64, encrypted);

            uchar decrypted[];
            ArrayResize(decrypted, enc_len);
            int out_len = enc_len;

            if(!AES256Decrypt(encrypted, enc_len, m_key, m_iv, decrypted, out_len)) return "";
            return CharArrayToString(decrypted, 0, out_len);
        }
        return "";
    }

    void Disconnect() {
        if (m_socket != INVALID_SOCKET) {
            closesocket(m_socket);
            m_socket = INVALID_SOCKET;
        }
    }

    void memcpy_uchar(uchar &dst[], uchar &src[], int count) {
        for(int i=0; i<count; i++) dst[i] = src[i];
    }

    string Base64Encode(uchar &data[], int len) {
        static const string base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
        string ret = "";
        int i = 0;
        uchar char_array_3[3], char_array_4[4];
        for (int n=0; n<len; n++) {
            char_array_3[i++] = data[n];
            if (i == 3) {
                char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
                char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
                char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
                char_array_4[3] = char_array_3[2] & 0x3f;
                for(i = 0; i <4 ; i++) ret += StringSubstr(base64_chars, char_array_4[i], 1);
                i = 0;
            }
        }
        if (i) {
            for(int j = i; j < 3; j++) char_array_3[j] = '\0';
            char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
            char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
            char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
            for (int j = 0; j < i + 1; j++) ret += StringSubstr(base64_chars, char_array_4[j], 1);
            while((i++ < 3)) ret += "=";
        }
        return ret;
    }

    int Base64Decode(string base64, uchar &data[]) {
        static const string base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
        int len = StringLen(base64);
        int i = 0, j = 0, in_ = 0;
        uchar char_array_4[4], char_array_3[3];
        ArrayResize(data, len);
        int out_len = 0;
        while (len-- && (base64[in_] != '=') && is_base64(base64[in_])) {
            char_array_4[i++] = (uchar)StringFind(base64_chars, StringSubstr(base64, in_++, 1));
            if (i == 4) {
                char_array_3[0] = (char_array_4[0] << 2) + ((char_array_4[1] & 0x30) >> 4);
                char_array_3[1] = ((char_array_4[1] & 0xf) << 4) + ((char_array_4[2] & 0x3c) >> 2);
                char_array_3[2] = ((char_array_4[2] & 0x3) << 6) + char_array_4[3];
                for (i = 0; i < 3; i++) data[out_len++] = char_array_3[i];
                i = 0;
            }
        }
        if (i) {
            for (j = i; j < 4; j++) char_array_4[j] = 0;
            char_array_3[0] = (char_array_4[0] << 2) + ((char_array_4[1] & 0x30) >> 4);
            char_array_3[1] = ((char_array_4[1] & 0xf) << 4) + ((char_array_4[2] & 0x3c) >> 2);
            for (j = 0; j < i - 1; j++) data[out_len++] = char_array_3[j];
        }
        ArrayResize(data, out_len);
        return out_len;
    }
    bool is_base64(char c) { return (isalnum(c) || (c == '+') || (c == '/')); }
};
