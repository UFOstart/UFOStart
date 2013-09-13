---
layout: endpoint
category: endpoint
title: /web/user/lilogin
type: WRITE
request: |
        {
            "Profile" : [{
                    "type" : "LI",
                    "id" : ID_IN_NETWORK,
                    "name" : NAME_IN_NETWORK,
                    "accessToken" : ACCESS_TOKEN,
                    "email" : EMAIL_IN_NETWORK,
                    "picture" : NETWORK_PROFILE_PICTURE_URL
                }
            ]
        }
response:   |
            {
                "status" : 0,
                "procName" : "user_linkedin_login",
                "User" : USER_DETAILS
            }
---

Returns full user information from a linkedin normalized profile. Also refreshes social network information in background.


Possible dbMessage: `NO_USER_WITH_THIS_ACCOUNT`
