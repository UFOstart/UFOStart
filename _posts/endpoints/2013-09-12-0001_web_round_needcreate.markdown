---
layout: endpoint
category: endpoint
title: /web/round/needCreate
type: WRITE
request:    |
            {
                "Needs" : [{
                    "name" : NEED_NAME <b>required</b>,
                    "Tags" : LIST_OF_TAGS <b>required</b>,
                    "cash" : CASH_AMOUNT_INT <b>required</b>,
                    "equity" : EQUITY_AMOUNT <b>required</b>,
                    "customText" : USER_ENTERED_NEED_DESCRIPTION <b>required</b>,
                    "picture" : NEED_PICTURE_URL
                }],
                "token" : ROUND_TOKEN
            }
response:   |
            {
                "status" : 0,
                "procName" : "round_need_create",
                "Need" : NEED_DETAILS
            }

---

Creates a new task inside this round. Newly created tasks always have `"status":"CUSTOMISED"`.
