---
layout: endpoint
category: endpoint
title: /web/funding/invest
type: WRITE
request:|
        {
            "token" : ROUND_TOKEN,
            "Funding" : {
                "Investment" : {
                    "amount" : INVESTMENT_AMOUNT_INT <b>required</b>,
                    "User" : {
                        "token" : INVESTOR_TOKEN
                    }
                }
            }
        }
response:   |
            {
                "status" : 0,
                "procName" : "round_funding_invest",
                "Round" : ROUND_DETAILS
            }

---

This endpoint adds an investment from a user to a round.
