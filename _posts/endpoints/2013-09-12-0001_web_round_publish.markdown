---
layout: endpoint
category: endpoint
title: /web/round/publish
type: WRITE
request: {"token": ROUND_TOKEN}
response:   |
            {
                "status" : 0,
                "procName" : "round_publish",
                "Round" : ROUND_DETAILS
            }
---

Mentor publishes round by calling this endpoint.

