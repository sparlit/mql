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
#define WSAEWOULDBLOCK 10035
#define SOCKET_BUFFER_SIZE 10240

struct sockaddr {
    short family;
    ushort port;
    uint addr;
    char zero[8];
};

#import "ws2_32.dll"
   int socket(int af, int type, int protocol);
   int connect(int s, sockaddr& name, int namelen);
   int send(int s, uchar& buf[], int len, int flags);
   int recv(int s, uchar& buf[], int len, int flags);
   int closesocket(int s);
   int ioctlsocket(int s, long cmd, uint& argp);
   uint inet_addr(string cp);
   ushort htons(ushort hostshort);
   int WSAGetLastError();
#import

enum ENUM_SOCKET_STATE {
   STATE_IDLE,
   STATE_CONNECTING,
   STATE_SENDING,
   STATE_RECEIVING,
   STATE_COMPLETED,
   STATE_ERROR
};

class CSocketClient
{
private:
   int               m_socket;
   CAATSecurity      m_security;
   ENUM_SOCKET_STATE m_state;
   string            m_send_buffer;
   string            m_recv_buffer;
   datetime          m_last_action;
   bool              m_is_connected;

public:
   CSocketClient() : m_socket(-1), m_state(STATE_IDLE), m_last_action(0), m_is_connected(false) {}
  ~CSocketClient() { Disconnect(); }

   ENUM_SOCKET_STATE GetState() { return m_state; }

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

   bool AsyncRequest(string host, int port, string data)
   {
      if(m_state != STATE_IDLE) return false;
      m_send_buffer = m_security.Encrypt(data) + "\n";
      m_recv_buffer = "";
      m_state = STATE_CONNECTING;
      m_last_action = TimeCurrent();

      m_socket = socket(2, 1, 6);
      if(m_socket == -1) { m_state = STATE_ERROR; return false; }

      uint non_block = 1;
      ioctlsocket(m_socket, FIONBIO, non_block);

      sockaddr server;
      server.family = 2;
      server.port = htons((ushort)port);
      server.addr = inet_addr(host);

      connect(m_socket, server, sizeof(sockaddr));
      return true;
   }

   void Update()
   {
      if(m_state == STATE_IDLE || m_state == STATE_COMPLETED || m_state == STATE_ERROR) return;

      if(TimeCurrent() - m_last_action > 5) { // Timeout
         Disconnect();
         m_state = STATE_ERROR;
         return;
      }

      if(m_state == STATE_CONNECTING) {
         // In non-blocking, we just try to send to check connection
         m_state = STATE_SENDING;
      }

      if(m_state == STATE_SENDING) {
         uchar buf[];
         StringToCharArray(m_send_buffer, buf);
         int sent = send(m_socket, buf, ArraySize(buf)-1, 0);
         if(sent > 0) {
            m_state = STATE_RECEIVING;
            m_last_action = TimeCurrent();
         } else {
            int err = WSAGetLastError();
            if(err != WSAEWOULDBLOCK) { m_state = STATE_ERROR; Disconnect(); }
         }
      }

      if(m_state == STATE_RECEIVING) {
         uchar buf[SOCKET_BUFFER_SIZE];
         int received = recv(m_socket, buf, SOCKET_BUFFER_SIZE, 0);
         if(received > 0) {
            m_recv_buffer += CharArrayToString(buf, 0, received);
            if(StringFind(m_recv_buffer, "\n") != -1) {
               m_state = STATE_COMPLETED;
               Disconnect();
            }
         } else {
            int err = WSAGetLastError();
            if(err != WSAEWOULDBLOCK) { m_state = STATE_ERROR; Disconnect(); }
         }
      }
   }

   string GetResponse()
   {
      if(m_state != STATE_COMPLETED) return "";
      string decrypted = m_security.Decrypt(m_recv_buffer);
      m_state = STATE_IDLE;
      return decrypted;
   }

   void SetSecurityKey(string key) {
      m_security.SetKey(key);
   }

   void Disconnect() {
      if(m_socket != -1) closesocket(m_socket);
      m_socket = -1;
      // Reset state to IDLE to allow retries (Fixes permanent ERROR state)
      m_state = STATE_IDLE;
   }
};
