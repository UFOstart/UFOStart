---
layout: endpoint
category: endpoint
title: /web/pledge/create
type: WRITE
request: |
        {
            "token" : ROUND_TOKEN,
            "Pledge" : {
                "network" : SOCIAL_NETWORK,
                "networkId" : USER_NETWORK_ID,
                "picture" : PLEDGEE_PROFILE_PICTURE,
                "name" : PLEDGEE_NAME,
                "offerToken" : OFFER_TOKEN,
                "comment" : FREETEXT,
            }
        }
response:   |
            {
                "status" : 0,
                "procName" : "pledge_create",
                "Round" : ROUND_DETAILS
            }
---

Pledge to a product offer with only social network credentials.Network short codes can be LI,FB,XI,TW,AL,UFO and similar.