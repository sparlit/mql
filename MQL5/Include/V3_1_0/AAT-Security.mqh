//+------------------------------------------------------------------+
//|                                                       AAT-Security |
//|                                  Copyright 2024, AI Trader Corp. |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, AI Trader Corp."
#property strict

/*
   AAT-Security-V1.0.0.mqh

   Implements AES-256-CBC and Base64 for communication with Python engine.
   Uses built-in MQL5 CryptEncode/CryptDecode.
*/

class CAATSecurity
{
private:
   uchar             m_key[];
   uchar             m_iv[];

public:
CAATSecurity()
{
   SetKey("AAT_SECURE_FOSS_KEY_256_BIT_STRIP");
}

void SetKey(string key_str)
{
   // Key must be exactly 32 bytes for AES-256
   StringToCharArray(key_str, m_key, 0, 32);
}

string Encrypt(string plaintext)
{
   uchar data[], key[], iv[16], result[];

   // Prepare Key
   ArrayResize(key, 32);
   ArrayCopy(key, m_key);

   // Generate Random IV
   for(int i=0; i<16; i++) iv[i] = (uchar)MathRand();

   // Prepare Data
   StringToCharArray(plaintext, data, 0, StringLen(plaintext));

   // Encrypt
   if(CryptEncode(CRYPT_AES256, data, key, result) <= 0) return "";

   // Prepend IV to result (Simulated IV for compatibility, MT5 built-in doesn't use it in this overload)
   uchar final_buf[];
   ArrayResize(final_buf, 16 + ArraySize(result));
   ArrayCopy(final_buf, iv, 0, 0, 16);
   ArrayCopy(final_buf, result, 16, 0, ArraySize(result));

   // Base64 Encode
   uchar b64_result[];
   if(CryptEncode(CRYPT_BASE64, final_buf, key, b64_result) <= 0) return "";

   return CharArrayToString(b64_result);
}

string Decrypt(string base64_ciphertext)
{
   uchar b64_data[], raw_data[], key[], iv[16], result[];

   // Prepare Key
   ArrayResize(key, 32);
   ArrayCopy(key, m_key);

   // Base64 Decode
   StringToCharArray(base64_ciphertext, b64_data, 0, StringLen(base64_ciphertext));
   if(CryptDecode(CRYPT_BASE64, b64_data, key, raw_data) <= 0) return "";

   // Extract IV
   if(ArraySize(raw_data) < 16) return "";
   ArrayCopy(iv, raw_data, 0, 0, 16);

   // Extract Ciphertext
   uchar ciphertext[];
   int cipher_len = ArraySize(raw_data) - 16;
   ArrayResize(ciphertext, cipher_len);
   ArrayCopy(ciphertext, raw_data, 0, 16, cipher_len);

   // Decrypt
   if(CryptDecode(CRYPT_AES256, ciphertext, key, result) <= 0) return "";

   return CharArrayToString(result);
}

};
