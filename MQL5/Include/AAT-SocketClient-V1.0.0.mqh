//+------------------------------------------------------------------+
//|                                                       SocketClient.mqh |
//|                                  Copyright 2024, AI Trader Corp. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, AI Trader Corp."
#property link      "https://www.mql5.com"
#property strict

#define INVALID_SOCKET  (uint)-1
#define SOCKET_ERROR    -1
#define AF_INET         2
#define SOCK_STREAM     1
#define IPPROTO_TCP     6
#define SOL_SOCKET      0xFFFF
#define SO_RCVTIMEO     0x1006
#define SO_SNDTIMEO     0x1005

struct sockaddr_in {
    short          sin_family;
    unsigned short sin_port;
    unsigned int   sin_addr;
    char           sin_zero[8];
};

#import "ws2_32.dll"
   uint socket(int af, int type, int protocol);
   int connect(uint s, sockaddr_in &name, int namelen);
   int send(uint s, uchar &buf[], int len, int flags);
   int recv(uint s, char &buf[], int len, int flags);
   int closesocket(uint s);
   int WSAStartup(ushort wVersionRequested, uchar &lpWSAData[]);
   int WSACleanup();
   uint inet_addr(uchar &cp[]);
   ushort htons(ushort hostshort);
   int setsockopt(uint s, int level, int optname, int &optval, int optlen);
#import

class CSocketClient
{
private:
   uint              m_socket;
   string            m_host;
   int               m_port;
   bool              m_initialized;
   int               m_timeout;

public:
                     CSocketClient(void) : m_socket(INVALID_SOCKET), m_host("127.0.0.1"), m_port(5555), m_initialized(false), m_timeout(5000) {}
                    ~CSocketClient(void) { Disconnect(); if(m_initialized) WSACleanup(); }

   bool              Init()
     {
      uchar data[512];
      if(WSAStartup(0x0202, data) != 0)
        {
         Print("SocketClient: WSAStartup failed");
         return false;
        }
      m_initialized = true;
      return true;
     }

   bool              Connect(string host, int port)
     {
      if(!m_initialized && !Init()) return false;
      m_host = host;
      m_port = port;

      m_socket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
      if(m_socket == INVALID_SOCKET) return false;

      // Set Timeouts
      setsockopt(m_socket, SOL_SOCKET, SO_RCVTIMEO, m_timeout, 4);
      setsockopt(m_socket, SOL_SOCKET, SO_SNDTIMEO, m_timeout, 4);

      sockaddr_in addr;
      addr.sin_family = AF_INET;
      addr.sin_port = htons((ushort)m_port);

      uchar host_buf[];
      StringToCharArray(m_host, host_buf);
      addr.sin_addr = inet_addr(host_buf);

      if(connect(m_socket, addr, sizeof(addr)) == SOCKET_ERROR)
        {
         closesocket(m_socket);
         m_socket = INVALID_SOCKET;
         return false;
        }
      return true;
     }

   bool              Send(string message)
     {
      if(m_socket == INVALID_SOCKET) return false;
      uchar buf[];
      int len = StringToCharArray(message, buf);
      if(len <= 1) return false;

      int total_sent = 0;
      int to_send = len - 1;
      while(total_sent < to_send)
        {
         uchar chunk[];
         ArrayCopy(chunk, buf, 0, total_sent, to_send - total_sent);
         int res = send(m_socket, chunk, ArraySize(chunk), 0);
         if(res == SOCKET_ERROR) return false;
         total_sent += res;
        }
      return true;
     }

   string            Receive()
     {
      if(m_socket == INVALID_SOCKET) return "";
      string result = "";
      char buf[4096];
      int res;

      while(true)
        {
         ArrayInitialize(buf, 0);
         res = recv(m_socket, buf, 4096, 0);
         if(res > 0)
           {
            result += CharArrayToString(buf, 0, res);
           }
         else if(res == 0) // Graceful shutdown
           {
            break;
           }
         else // Error or timeout
           {
            break;
           }
        }
      return result;
     }

   void              Disconnect()
     {
      if(m_socket != INVALID_SOCKET)
        {
         closesocket(m_socket);
         m_socket = INVALID_SOCKET;
        }
     }
};
