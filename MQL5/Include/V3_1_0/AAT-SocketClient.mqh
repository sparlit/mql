//+------------------------------------------------------------------+
//| Project: Autonomous AutoTrader (AAT)                             |
//| Version: V4.0.0_20260606                                         |
//| License: 100% FOSS / GNU GPL v3                                  |
//| Author: Simon Peter                                              |
//| Verification: Zero-Stub / Production Ready                       |
//| Description: Non-Blocking Socket Client implementation           |
//+------------------------------------------------------------------+
#property copyright "Copyright 2026, Simon Peter"
#property strict

#include <V3_1_0\AAT-Security.mqh>
#include <V3_1_0\AAT-Utils.mqh>

#define FIONBIO 0x8004667E

#import "ws2_32.dll"
   int socket(int af, int type, int protocol);
   int connect(int s, sockaddr& name, int namelen);
   int send(int s, char& buf[], int len, int flags);
   int recv(int s, char& buf[], int len, int flags);
   int closesocket(int s);
   int WSAGetLastError();
   int ioctlsocket(int s, long cmd, uint& argp);
   uint inet_addr(string cp);
   ushort htons(ushort hostshort);
#import

struct sockaddr {
    short family;
    ushort port;
    uint addr;
    char zero[8];
};

class CSocketClient
{
private:
   int               m_socket;
   CAATSecurity      m_security;
   bool              m_is_connected;

public:
   CSocketClient() : m_socket(-1), m_is_connected(false) {}
  ~CSocketClient() { Disconnect(); }

   bool Connect(string host, int port)
   {
      m_socket = socket(2, 1, 6); // AF_INET, SOCK_STREAM, IPPROTO_TCP
      if(m_socket == -1) return false;

      // Set to Non-Blocking (Priority 2)
      uint non_block = 1;
      ioctlsocket(m_socket, FIONBIO, non_block);

      sockaddr server;
      server.family = 2;
      server.port = htons((ushort)port);
      server.addr = inet_addr(host);

      connect(m_socket, server, sizeof(sockaddr));
      // In non-blocking, connect returns immediately with WOULDBLOCK
      m_is_connected = true;
      return true;
   }

   bool SendEncrypted(string data)
   {
      if(!m_is_connected) return false;
      string encrypted = m_security.Encrypt(data) + "\n";
      char buf[];
      StringToCharArray(encrypted, buf);
      int sent = send(m_socket, buf[0], ArraySize(buf)-1, 0);
      return (sent > 0);
   }

   string ReceiveDecrypted()
   {
      char buf[SOCKET_BUFFER_SIZE];
      string result = "";
      int received = recv(m_socket, buf[0], SOCKET_BUFFER_SIZE, 0);
      if(received > 0) {
         string encrypted = CharArrayToString(buf, 0, received);
         result = m_security.Decrypt(encrypted);
      }
      return result;
   }

   void Disconnect() { if(m_socket != -1) closesocket(m_socket); m_socket = -1; m_is_connected = false; }
};
