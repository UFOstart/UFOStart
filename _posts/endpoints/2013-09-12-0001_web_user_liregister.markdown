---
layout: endpoint
category: endpoint
title: /web/user/liregister
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
                "procName" : "user_linkedin_register",
                "User" : USER_DETAILS
            }
---

Registers a user with linkedin normalized profile information.


Possible dbMessage: `USER_ALREADY_REGISTERED`
