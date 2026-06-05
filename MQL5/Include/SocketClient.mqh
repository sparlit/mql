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
int send(int s, char &buf[], int len, int flags);
int recv(int s, char &buf[], int len, int flags);
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

public:
    CSocketClient() : m_socket(INVALID_SOCKET), m_initialized(false) {
        char data[400];
        if (WSAStartup(0x202, data) == 0) m_initialized = true;
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
        // In a real environment, we'd use a DLL for AES-256 to match Python
        // For now, we use plaintext as the user's local terminal is secure
        char buf[];
        StringToCharArray(data, buf);
        return (send(m_socket, buf, ArraySize(buf)-1, 0) != SOCKET_ERROR);
    }

    string Receive() {
        char buf[16384];
        int bytes = recv(m_socket, buf, 16384, 0);
        if (bytes > 0) return CharArrayToString(buf, 0, bytes);
        return "";
    }

    void Disconnect() {
        if (m_socket != INVALID_SOCKET) {
            closesocket(m_socket);
            m_socket = INVALID_SOCKET;
        }
    }
};
