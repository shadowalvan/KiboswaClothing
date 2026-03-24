
sudo nmap -p- -sVC -O 10.1.1.225 -T4 -Pn   
[sudo] password for kali: 
Starting Nmap 7.95 ( https://nmap.org ) at 2026-03-23 09:03 EDT
Nmap scan report for 10.1.1.225
Host is up (0.0023s latency).
Not shown: 65519 closed tcp ports (reset)
PORT      STATE SERVICE       VERSION
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds?
2179/tcp  open  vmrdp?
3389/tcp  open  ms-wbt-server Microsoft Terminal Services
| rdp-ntlm-info: 
|   Target_Name: STADIO
|   NetBIOS_Domain_Name: STADIO
|   NetBIOS_Computer_Name: VMHOST01-WH
|   DNS_Domain_Name: ad.stadio.co.za
|   DNS_Computer_Name: VMHOST01-WH.ad.stadio.co.za
|   DNS_Tree_Name: ad.stadio.co.za
|   Product_Version: 10.0.20348
|_  System_Time: 2026-03-23T13:04:41+00:00
| ssl-cert: Subject: commonName=VMHOST01-WH.ad.stadio.co.za
| Not valid before: 2025-11-04T07:01:15
|_Not valid after:  2026-05-06T07:01:15
|_ssl-date: 2026-03-23T13:04:56+00:00; +14s from scanner time.
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
49669/tcp open  msrpc         Microsoft Windows RPC
49670/tcp open  msrpc         Microsoft Windows RPC
49671/tcp open  msrpc         Microsoft Windows RPC
49672/tcp open  msrpc         Microsoft Windows RPC
MAC Address: 04:7B:CB:7B:CD:49 (Universal Global Scientific Industrial)
Device type: general purpose
Running: Microsoft Windows 2022
OS CPE: cpe:/o:microsoft:windows_server_2022
OS details: Microsoft Windows Server 2022
Network Distance: 1 hop
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_nbstat: NetBIOS name: VMHOST01-WH, NetBIOS user: <unknown>, NetBIOS MAC: 04:7b:cb:7b:cd:49 (Universal Global Scientific Industrial)
|_clock-skew: mean: 13s, deviation: 0s, median: 12s
| smb2-time: 
|   date: 2026-03-23T13:04:41
|_  start_date: N/A
| smb2-security-mode: 
|   3:1:1: 
|_    Message signing enabled but not required

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 99.02 seconds
