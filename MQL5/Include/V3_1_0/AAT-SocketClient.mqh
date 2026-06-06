//+------------------------------------------------------------------+
//|                                              AAT-SocketClient.mqh |
//+------------------------------------------------------------------+
#property strict

#define INVALID_SOCKET 0xFFFFFFFF
#define SOCKET_ERROR   -1

#import "ws2_32.dll"
int socket(int af, int type, int protocol);
int connect(uint s, sockaddr_in &name, int namelen);
int send(uint s, char &buf[], int len, int flags);
int recv(uint s, char &buf[], int len, int flags);
int closesocket(uint s);
int WSAStartup(ushort wVersionRequested, char &lpWSAData[]);
int WSACleanup();
uint inet_addr(string cp);
ushort htons(ushort hostshort);
#import

#include <AAT-Security-V1.0.0.mqh>

struct sockaddr_in {
    short sin_family;
    ushort sin_port;
    uint sin_addr;
    char sin_zero[8];
};

class CSocketClient
{
private:
   uint              m_socket;
   bool              m_initialized;
   CAATSecurity      m_security;

public:
   CSocketClient() : m_socket(INVALID_SOCKET), m_initialized(false)
   {
      char data[400];
      if(WSAStartup(0x202, data) == 0) m_initialized = true;
      else Print("AAT-SocketClient: WSAStartup failed");
   }

   ~CSocketClient()
   {
      Disconnect();
      if(m_initialized) WSACleanup();
   }

   void SetMasterKey(string key) { m_security.SetKey(key); }

   bool Connect(string ip, int port)
   {
      if(!m_initialized) return false;

      m_socket = socket(2, 1, 6); // AF_INET, SOCK_STREAM, IPPROTO_TCP
      if(m_socket == INVALID_SOCKET) return false;

      sockaddr_in server;
      server.sin_family = 2;
      server.sin_port = htons((ushort)port);
      server.sin_addr = inet_addr(ip);

      if(connect(m_socket, server, sizeof(server)) == SOCKET_ERROR)
      {
         closesocket(m_socket);
         m_socket = INVALID_SOCKET;
         return false;
      }
      return true;
   }

   bool SendEncrypted(string message)
   {
      if(m_socket == INVALID_SOCKET) return false;

      string encrypted = m_security.Encrypt(message);
      if(encrypted == "") return false;

      encrypted += "\n"; // Newline as terminator
      char buf[];
      StringToCharArray(encrypted, buf);
      int len = ArraySize(buf) - 1; // Exclude null terminator

      return (send(m_socket, buf, len, 0) != SOCKET_ERROR);
   }

   string ReceiveDecrypted()
   {
      if(m_socket == INVALID_SOCKET) return "";

      string result = "";
      char buf[4096];

      while(true)
      {
         ArrayInitialize(buf, 0);
         int res = recv(m_socket, buf, 4096, 0);
         if(res > 0)
         {
            result += CharArrayToString(buf, 0, res);
            if(StringFind(result, "\n") != -1) break;
         }
         else break;
      }

      if(result == "") return "";

      int pos = StringFind(result, "\n");
      if(pos != -1) result = StringSubstr(result, 0, pos);

      return m_security.Decrypt(result);
   }

   void Disconnect()
   {
      if(m_socket != INVALID_SOCKET)
      {
         closesocket(m_socket);
         m_socket = INVALID_SOCKET;
      }
   }
};
