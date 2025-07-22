#!/usr/bin/env python3
import json
import sys
import os
sys.path.append('/app/backend')

from cookie_manager import cookie_manager

# Updated Gmail cookies for brainlyarpit8649@gmail.com
gmail_cookies = [
    {
        "domain": ".google.com",
        "expirationDate": 1787706652.477026,
        "hostOnly": False,
        "httpOnly": False,
        "name": "SAPISID",
        "path": "/",
        "sameSite": None,
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "Dre89z9Cy1BJcjmC/A7-it29etLisIaG88"
    },
    {
        "domain": ".google.com",
        "expirationDate": 1787706652.47825,
        "hostOnly": False,
        "httpOnly": False,
        "name": "__Secure-3PAPISID",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "Dre89z9Cy1BJcjmC/A7-it29etLisIaG88"
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
        "value": "AF6bupNI2yB-nLW_ZtjysOumidrfKAw69w"
    },
    {
        "domain": "mail.google.com",
        "expirationDate": 1755699731.207884,
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
        "expirationDate": 1768929886.503371,
        "hostOnly": False,
        "httpOnly": True,
        "name": "NID",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "525=NTjB2KSHmGvQVOYRZCulqSsksGj8UlhWYP17JSg5I_pqcesY1hsq5gompLE86NlSb-RowZ8pJcaNLRu0eeUcxhz042GPRMi7M-lR2JMNk-2Ns002VhcvV9EwkaJ9stRMo-gQXkCfLsUQgvok6bkBKQtxcdun5YtU4yNBbxQFOzKilKF8YDj5wBRq3zX78tq18uryO17z6EO9FyEQUe_X_xpCLpn8laehYTdmGGquDMRicIKuVTd7P4cFo6g9KN3ygqSGX-axv0lrUvR6fu46B8ypUxCWNxInR9dKkGaDDYGpa-fnihSz4NYpSmNUIbPnp8QHKSkEuBSw1CJm2w_4P9D3gcL8cE6KZYmwe_XjUH6mKS_qYPS4-B7xZr77Aki8D9gm9xhJRxbJEdQVdNr7f0tZ0P_Gzl4WV2O9I0QnGl97Nl4_Lxl7EvBaIc8piyQd6zQmdsfDySUHPIO06-YR4xHhTIZw4Duy6SHgmNznhLM-MtBQ5m_pZ2J-ZSj71kuqGm_XyFFVuydATaMm7FylCHCWUo8IHyBMxcEXbuY9xlaGtC1FqR2n48mM4ZGSQlZjl6_cmRFmVrcaPeW5zF21W_YwX3zEhAUXGva06Ac68tiLXvFoARbyUUORryE2LV-J7IyVW-PwvKlwLEeXMyHgxammtYuwTRfTwDHxWNQ2SScp"
    },
    {
        "domain": ".google.com",
        "expirationDate": 1784682672.198465,
        "hostOnly": False,
        "httpOnly": True,
        "name": "__Secure-1PSIDTS",
        "path": "/",
        "sameSite": None,
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "sidts-CjEB5H03P94zOWi9S3DV17_mf15ucGlAo3HwqHQqAgTtMOBquD1s1yeVw8NGrdjsVlGREAA"
    },
    {
        "domain": "mail.google.com",
        "expirationDate": 1755699731.207823,
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
        "expirationDate": 1787706652.477643,
        "hostOnly": False,
        "httpOnly": False,
        "name": "__Secure-1PAPISID",
        "path": "/",
        "sameSite": None,
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "Dre89z9Cy1BJcjmC/A7-it29etLisIaG88"
    },
    {
        "domain": "mail.google.com",
        "expirationDate": 1787706652.978769,
        "hostOnly": True,
        "httpOnly": True,
        "name": "OSID",
        "path": "/",
        "sameSite": None,
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "g.a000zQiommhugQQNhINz3K2Wnmw_RsTvn13H-kJeYfLeRB7N7c4QeFROtQ5ZuQQchNHyKpou7gACgYKAZUSARMSFQHGX2MiyZCZTEopyOBtq_qZwr1tYRoVAUF8yKpjHCe1IPIfXdeOEUV19kmJ0076"
    },
    {
        "domain": ".google.com",
        "expirationDate": 1787706652.472976,
        "hostOnly": False,
        "httpOnly": True,
        "name": "__Secure-3PSID",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "g.a000zQiomtDlSOw-WP1X9Hy3WRahpeuNVF6vDhR-p01xf6UZTlB4WW32SG0LO_5qK9y5d0sLvAACgYKAa4SARMSFQHGX2MifXGFTc9DPIJPCkxjBopf1xoVAUF8yKq5CWMvIGBjxLRQeDXAtnDa0076"
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
        "expirationDate": 1755699731.207688,
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
        "expirationDate": 1787706652.47101,
        "hostOnly": False,
        "httpOnly": True,
        "name": "__Secure-1PSID",
        "path": "/",
        "sameSite": None,
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "g.a000zQiomtDlSOw-WP1X9Hy3WRahpeuNVF6vDhR-p01xf6UZTlB4ZlrC37vxNqrdwtKgQA3LAQACgYKAVwSARMSFQHGX2MiIdeEZrzn0i_BDUneFVFZuRoVAUF8yKruPgMpDlSXIjD-XpoL43SM0076"
    },
    {
        "domain": ".google.com",
        "expirationDate": 1784682965.579247,
        "hostOnly": False,
        "httpOnly": True,
        "name": "__Secure-1PSIDCC",
        "path": "/",
        "sameSite": None,
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "AKEyXzVFp9udMyg4bXqOAlnlH6uWj_v2sJKlPEVqaelTFQatnn_4PXhczmvx8B2T4RcU-bNy"
    },
    {
        "domain": ".google.com",
        "expirationDate": 1784682965.580652,
        "hostOnly": False,
        "httpOnly": True,
        "name": "__Secure-3PSIDCC",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "AKEyXzWf16V8yIRwtVNeTPvhux7-IPe6BoM_8VflM83OCEPkl2HcEqXMLwBEX6ktoquLq_M6"
    },
    {
        "domain": ".google.com",
        "expirationDate": 1784682672.19924,
        "hostOnly": False,
        "httpOnly": True,
        "name": "__Secure-3PSIDTS",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "sidts-CjEB5H03P94zOWi9S3DV17_mf15ucGlAo3HwqHQqAgTtMOBquD1s1yeVw8NGrdjsVlGREAA"
    },
    {
        "domain": "mail.google.com",
        "expirationDate": 1787706652.979604,
        "hostOnly": True,
        "httpOnly": True,
        "name": "__Secure-OSID",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "g.a000zQiommhugQQNhINz3K2Wnmw_RsTvn13H-kJeYfLeRB7N7c4QhfqDM1MWF0YsILAe54NdqAACgYKATYSARMSFQHGX2MiBTHQJKMShg67dfAewJ8oLRoVAUF8yKoNtk6JHAGeyXejfYn6tmNV0076"
    },
    {
        "domain": "mail.google.com",
        "expirationDate": 1754010679.645417,
        "hostOnly": True,
        "httpOnly": True,
        "name": "COMPASS",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "appsfrontendserver=CgAQreb7wwYaeAAJa4lX46URvH_YiEByNiGLx_gilhg9bB68KF905cmwV9m6n3JjcpFR_Ss0GpKM5Una_NWVJIWSz6WexNYw4PaR_KH6o4La0_SmwdTGuCW_5V97eO8sCk9t0CXVx7TBMAd0wPrk8QCOSAzZ3dVJ8X2QaPUN2Z3sfyABMAE"
    },
    {
        "domain": ".google.com",
        "expirationDate": 1787706652.475179,
        "hostOnly": False,
        "httpOnly": True,
        "name": "SSID",
        "path": "/",
        "sameSite": None,
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "AipUFcsN70TRO8iSA"
    },
    {
        "domain": "accounts.google.com",
        "expirationDate": 1755738615,
        "hostOnly": True,
        "httpOnly": False,
        "name": "OTZ",
        "path": "/",
        "sameSite": None,
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "8180710_34_34__34_"
    },
    {
        "domain": "accounts.google.com",
        "expirationDate": 1787706652.478717,
        "hostOnly": True,
        "httpOnly": True,
        "name": "ACCOUNT_CHOOSER",
        "path": "/",
        "sameSite": None,
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "AFx_qI7OzRPEqkta8y8j_NCiNpNnfcMVvlitWhLSzcAYRVOVohZgzx36lE_GkAuyottJ346c3Z00Knruhxnuq7daOmUP-X2oTz1nj7n4DPQjV6n9QuH5hofb02JgfCLdU4eDAlQw02dnqnHsjtzdRWSRi-9sp74Xig"
    },
    {
        "domain": ".google.com",
        "expirationDate": 1768929886.067578,
        "hostOnly": False,
        "httpOnly": True,
        "name": "NID",
        "path": "/",
        "sameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "525=f9LgkegZG2uzGBWuw_q49zXZToQKnxlrIPM6qeP9IZ1i1dlzTUuOMg4HJfwPLAyiHf1BBV2HY8hzRT8KEDJd0eYJA8bRnepwUIvjJBithZkAP4yCITrtDTuWVJywmCtZUkOKyW3q0K2iaq5s1GF8YbtwwycL4gdS0zD90RYBycEM5zKFPEGixt4vkUqfb738W249muNgTdHQhb94oitllQhYMkUIn-B76_xuhpY5ERppJP6ngNyDKqRu88oXhZxmJmTL0Qpdl1n-WPfSoWMdGuqizJso366o4zXoOigR3CIEQTpBCv1A0x2RchFQAghs231Wd1tZjIEk-9zlu35CfdIxkgyGeSGcftoEFZd2QU4bmjy5RLc"
    },
    {
        "domain": "accounts.google.com",
        "expirationDate": 1787706652.479848,
        "hostOnly": True,
        "httpOnly": True,
        "name": "SMSV",
        "path": "/",
        "sameSite": None,
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "ADHTe-CxeACZGveRRSx9i4V5jvX0s7uJNsOfVStW6tggKRidyqbS6ovFLnzHYb9fX0b1GQP0flyT1LHn6nhRYnSnwkssG2jCRdv-wgw5Sv3BrFabmiM-JPA"
    },
    {
        "domain": "accounts.google.com",
        "expirationDate": 1787706652.479165,
        "hostOnly": True,
        "httpOnly": True,
        "name": "__Host-GAPS",
        "path": "/",
        "sameSite": None,
        "secure": True,
        "session": False,
        "storeId": None,
        "value": "1:pPs_DmRJerioe_ZmYk1izhVxD_muA07rTMlC56M2Yw24fw_Z5JzEiCniafMP0uU8WraMuoLTKCFDVRHzC0IV1KgHKUwPoA:bDkO--9TniPbxpMs"
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