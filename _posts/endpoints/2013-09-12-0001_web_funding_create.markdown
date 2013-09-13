---
layout: endpoint
category: endpoint
title: /web/funding/create
type: WRITE
request:    |
            {
                "token" : ROUND_TOKEN,
                "Funding" : {
                    "amount" : FUNDING_AMOUNT_INT <b>required</b>,
                    "valuation" : VALUATION_AMOUNT_INT <b>required</b>,
                    "description" : FUNDING_TEXT <b>required</b>,
                    "contract" : CONTRACT_DOWNLOAD_URL
                }
            }
response:   |
            {
                "status" : 0,
                "procName" : "round_funding_target", ,
                "Round" : ROUND_DETAILS
            }

---

Sets up funding for a round.