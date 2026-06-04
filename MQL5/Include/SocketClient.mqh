//+------------------------------------------------------------------+
//|                                                       SocketClient.mqh |
//|                                  Copyright 2024, AI Trader Corp. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, AI Trader Corp."
#property link      "https://www.mql5.com"
#property strict

#include <WinAPI\WinAPI.mqh>

#define INVALID_SOCKET  (uint)-1
#define SOCKET_ERROR    -1
#define AF_INET         2
#define SOCK_STREAM     1
#define IPPROTO_TCP     6

struct sockaddr_in {
    short          sin_family;
    unsigned short sin_port;
    unsigned int   sin_addr;
    char           sin_zero[8];
};

// Import Winsock functions
#import "ws2_32.dll"
   uint socket(int af, int type, int protocol);
   int connect(uint s, sockaddr_in &name, int namelen);
   int send(uint s, char &buf[], int len, int flags);
   int recv(uint s, char &buf[], int len, int flags);
   int closesocket(uint s);
   int WSAStartup(ushort wVersionRequested, char &lpWSAData[]);
   int WSACleanup();
   uint inet_addr(string cp);
   ushort htons(ushort hostshort);
#import

class CSocketClient
{
private:
   uint              m_socket;
   string            m_host;
   int               m_port;
   bool              m_initialized;

public:
                     CSocketClient(void) : m_socket(INVALID_SOCKET), m_host("127.0.0.1"), m_port(5555), m_initialized(false) {}
                    ~CSocketClient(void) { Disconnect(); if(m_initialized) WSACleanup(); }

   bool              Init()
     {
      char data[512];
      if(WSAStartup(0x0202, data) != 0) return false;
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

      sockaddr_in addr;
      addr.sin_family = AF_INET;
      addr.sin_port = htons((ushort)m_port);
      addr.sin_addr = inet_addr(m_host);

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
      StringToCharArray(message, buf);
      return (send(m_socket, buf[0], ArraySize(buf), 0) != SOCKET_ERROR);
     }

   string            Receive()
     {
      if(m_socket == INVALID_SOCKET) return "";
      char buf[4096];
      ArrayInitialize(buf, 0);
      int res = recv(m_socket, buf, 4096, 0);
      if(res > 0)
        {
         return CharArrayToString(buf);
        }
      return "";
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
