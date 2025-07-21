#!/usr/bin/env python3
import json
import sys
import os
sys.path.append('/app/backend')

from cookie_manager import cookie_manager

# Gmail cookies for brainlyarpit8649@gmail.com
gmail_cookies = [
    {
        "domain": ".google.com",
        "expirationDate": 1787641000.447148,
        "hostOnly": False,
        "httpOnly": False,
        "name": "SAPISID",
        "path": "/",
        "sameSite": None,
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "hv4zoM_HAj5XUFMi/ALZkjF57PaHdoWK-H"
    },
    {
        "domain": ".google.com",
        "expirationDate": 1787641000.447212,
        "hostOnly": False,
        "httpOnly": False,
        "name": "__Secure-3PAPISID",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "hv4zoM_HAj5XUFMi/ALZkjF57PaHdoWK-H"
    },
    {
        "domain": "mail.google.com",
        "hostOnly": True,
        "httpOnly": False,
        "name": "GMAIL_AT",
        "path": "/mail/u/0",
        "sameSite": None,
        "secure": True,
        "session": True,
        "storeId": None,
        "value": "AF6bupOZmOr5BnEGA0aS6tXucVp-Geg0jQ"
    },
    {
        "domain": "mail.google.com",
        "expirationDate": 1755672640.118824,
        "hostOnly": True,
        "httpOnly": True,
        "name": "__Host-GMAIL_SCH_GML",
        "path": "/",
        "sameSite": "lax",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "1"
    },
    {
        "domain": ".google.com",
        "expirationDate": 1768890252.446685,
        "hostOnly": False,
        "httpOnly": True,
        "name": "NID",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "525=KTRQKkP0LQ1bwmYYYb6kHVvG_e6Pkav4BQZTqtkggd1401Zm1MhJ9RDQYQflKmc3C7R2035FnyG-ZE1LVdCB90XNboHyft-56oX0ASQuhIKxf83d-8aiHd8y4q-HL1-EO9jvNR-fAiyJNqZ73BkedndwBDkT3MHfrVvc-F244MKDy2oYMANfCrMNOkLIT2c9NJ-80TUmepvgrHaNIFUvLVm1ZSSrANXU_1M_LeDGvf8_aFZR020Ib1EPhWRiksnnNTA9jQgRp9EeL5vo_uJ2y6HYiVkkR5ZhZrXzKXAb5HYg1J0h-gNllyfT8voG2dvZ06EFIRf0M4ARbjuCM_ogOsPcWCFKAyUHDjNWf92VyNCCFAh_JDwnDNq0kYYHUpka3rcL5-9j7ZsZNKtOUfaLFGn9yFO9D7wwxsgfQvYxMPyM8akXXTG-GcE_JUxSS7-CWSysuAJmc7ds_JfZ6thp3OhCI9ujfDxlQuMWd640-NNmFm_K8yzF2etVEhjRRYaFK-EviXAzORXI0WWKS2OKJq-FtiMnyV2eF0BmRyaX_EZi8BoYW-V2LK2EDZD0-kTteJYLBsqw8e0uUQK3hSnW_O9RT-GuiTA__uYm2COHnnwtidbrw6Pg-MwzWlSqaX02IZWOnOi4UwLcnS3GK026i5soa_Zu197wQtVZ2AdAIHWCVMbUW8rl-HhZ-A"
    },
    {
        "domain": ".google.com",
        "expirationDate": 1784617031.795325,
        "hostOnly": False,
        "httpOnly": True,
        "name": "__Secure-1PSIDTS",
        "path": "/",
        "sameSite": None,
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "sidts-CjEB5H03P_2UR0lzOIj0OfapEYoJskm1XEZOsxIW029V8VjZ5A0s291wrcNwMdFAPiToEAA"
    },
    {
        "domain": "mail.google.com",
        "expirationDate": 1755672640.118764,
        "hostOnly": True,
        "httpOnly": True,
        "name": "__Host-GMAIL_SCH_GMS",
        "path": "/",
        "sameSite": "strict",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "1"
    },
    {
        "domain": ".google.com",
        "expirationDate": 1787641000.44718,
        "hostOnly": False,
        "httpOnly": False,
        "name": "__Secure-1PAPISID",
        "path": "/",
        "sameSite": None,
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "hv4zoM_HAj5XUFMi/ALZkjF57PaHdoWK-H"
    },
    {
        "domain": "mail.google.com",
        "expirationDate": 1787641015.170342,
        "hostOnly": True,
        "httpOnly": True,
        "name": "OSID",
        "path": "/",
        "sameSite": None,
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "g.a000zQiomjQIIpQx2IDugECxjQx8cFJFfxMG4h60BLQRtT_jdpv4383p5h0j4EYY1raKEIBD4QACgYKAe8SARMSFQHGX2MiUc3Qt3eQLkEX7vGGybAEfhoVAUF8yKppm6FQDSU0_GOWiRVYosxx0076"
    },
    {
        "domain": ".google.com",
        "expirationDate": 1787641000.446935,
        "hostOnly": False,
        "httpOnly": True,
        "name": "__Secure-3PSID",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "g.a000zQiomkhbSrVzmOsO7YG5DNnCZHAkWNsuPG4gCGcMq_G8dQwHbuyyG8W4rQDwMd3k1Rf-qgACgYKAYESARMSFQHGX2MixdgkMXZY8Cuxnkg2yHhjXxoVAUF8yKpkw8dyfwvxUsGRHCxBef8Y0076"
    },
    {
        "domain": "mail.google.com",
        "hostOnly": True,
        "httpOnly": False,
        "name": "__Host-GMAIL_SCH",
        "path": "/",
        "sameSite": None,
        "secure": True,
        "session": True,
        "storeId": None,
        "value": "nsl"
    },
    {
        "domain": "mail.google.com",
        "expirationDate": 1755672640.118665,
        "hostOnly": True,
        "httpOnly": True,
        "name": "__Host-GMAIL_SCH_GMN",
        "path": "/",
        "sameSite": None,
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "1"
    },
    {
        "domain": ".google.com",
        "expirationDate": 1787641000.446893,
        "hostOnly": False,
        "httpOnly": True,
        "name": "__Secure-1PSID",
        "path": "/",
        "sameSite": None,
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "g.a000zQiomkhbSrVzmOsO7YG5DNnCZHAkWNsuPG4gCGcMq_G8dQwHG9RfSUFQm6nuRmFqpy9fewACgYKAd4SARMSFQHGX2MilfbS0xSCSh7p7OPLbYYPHxoVAUF8yKruEbIqC7z4vRQOdumq30tg0076"
    },
    {
        "domain": ".google.com",
        "expirationDate": 1784617046.512471,
        "hostOnly": False,
        "httpOnly": True,
        "name": "__Secure-1PSIDCC",
        "path": "/",
        "sameSite": None,
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "AKEyXzVyBbVym0MOoOZgRlMlsbcRft78hXkJZ0YMNY_EBftqDT4J-l5-wEq6ShghD-ESHze0kA"
    },
    {
        "domain": ".google.com",
        "expirationDate": 1784617046.512543,
        "hostOnly": False,
        "httpOnly": True,
        "name": "__Secure-3PSIDCC",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "AKEyXzUCABmZ9lL7JWekZ02sMP3mqL9s8SAM9uPU3iPX6gPU4CbAwIi1LPMQo-b18lF2iy9NLA"
    },
    {
        "domain": ".google.com",
        "expirationDate": 1784617031.795636,
        "hostOnly": False,
        "httpOnly": True,
        "name": "__Secure-3PSIDTS",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "sidts-CjEB5H03P_2UR0lzOIj0OfapEYoJskm1XEZOsxIW029V8VjZ5A0s291wrcNwMdFAPiToEAA"
    },
    {
        "domain": "mail.google.com",
        "expirationDate": 1787641015.170452,
        "hostOnly": True,
        "httpOnly": True,
        "name": "__Secure-OSID",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "g.a000zQiomjQIIpQx2IDugECxjQx8cFJFfxMG4h60BLQRtT_jdpv4SCcPa_5m0dtPmZkOziWP-AACgYKAVASARMSFQHGX2Mi2fwVWgA8EffvJN6B5GSuWxoVAUF8yKp_ha-luvsfnhG3KbxMMx_-0076"
    },
    {
        "domain": "mail.google.com",
        "expirationDate": 1753945041.758972,
        "hostOnly": True,
        "httpOnly": True,
        "name": "COMPASS",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "appsfrontendserver=CgAQx-X3wwYaegAJa4lXYttg4yYGU2qO-I44E96BbOFY9_z3VM74AaNyCmaysTT_WvAFs4WbwDCQQMjXvtl8tU52Xhc4H-ejBuNkrIMIVO_eVupzhQoIqW7Hkffbn_5gIByGLZ0lQ-1zBvhiVuzqiHtLYwn2xNtLIZ89s10D-sbPa1twIAEwAQ"
    },
    {
        "domain": ".google.com",
        "expirationDate": 1787641000.447081,
        "hostOnly": False,
        "httpOnly": True,
        "name": "SSID",
        "path": "/",
        "sameSite": None,
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "A4L4KfS8jC9MzCjyS"
    }
]

def main():
    # Convert Chrome cookie format to Playwright format
    playwright_cookies = []
    for cookie in gmail_cookies:
        playwright_cookie = {
            "name": cookie["name"],
            "value": cookie["value"],
            "domain": cookie["domain"],
            "path": cookie["path"],
            "secure": cookie["secure"],
            "httpOnly": cookie["httpOnly"]
        }
        
        # Handle expiration dates
        if not cookie.get("session", False) and "expirationDate" in cookie:
            # Convert to Playwright format (seconds since epoch)
            playwright_cookie["expires"] = int(cookie["expirationDate"])
        
        # Handle sameSite
        if cookie.get("sameSite"):
            sameSite = cookie["sameSite"]
            if sameSite == "no_restriction":
                playwright_cookie["sameSite"] = "None"
            elif sameSite == "lax":
                playwright_cookie["sameSite"] = "Lax" 
            elif sameSite == "strict":
                playwright_cookie["sameSite"] = "Strict"
        
        playwright_cookies.append(playwright_cookie)
    
    # Save cookies using the cookie manager
    success = cookie_manager.save_cookies(
        service_name="gmail",
        user_identifier="brainlyarpit8649@gmail.com", 
        cookies=playwright_cookies
    )
    
    if success:
        print("✅ Successfully saved Gmail cookies for brainlyarpit8649@gmail.com")
        print(f"📊 Total cookies saved: {len(playwright_cookies)}")
        
        # Verify cookies were saved
        loaded_cookies = cookie_manager.load_cookies("gmail", "brainlyarpit8649@gmail.com")
        if loaded_cookies:
            print(f"✅ Verification successful: {len(loaded_cookies)} cookies loaded")
        else:
            print("❌ Verification failed: Could not load saved cookies")
            
    else:
        print("❌ Failed to save Gmail cookies")

if __name__ == "__main__":
    main()