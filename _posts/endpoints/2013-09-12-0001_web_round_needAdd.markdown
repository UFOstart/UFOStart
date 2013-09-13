---
layout: endpoint
category: endpoint
title: /web/round/needAdd
type: WRITE
request: |
        {
            "Round" : {
                "token" : ROUND_TOKEN,
                "Needs" : [{
                        "token" : NEED_TOKEN
                    }
                ]
            }
        }

response:   |
            {
                "status" : 0,
                "procName" : "round_need_add",
                "Round" : ROUND_DETAILS
            }

---

Adds preconfigured tasks from a round template or a global task library to a round. Each task is `"status" : "PENDING"` until it gets edited.