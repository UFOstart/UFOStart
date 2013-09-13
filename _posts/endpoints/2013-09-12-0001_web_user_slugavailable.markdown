---
layout: endpoint
category: endpoint
title: /web/user/slugavailable
type: READ
request:  {"slug": SOME_SLUG}
response:   |
            {
                "status" : 0,
                "procName" : "user_check_slug_available"
            }

---

Checks if slug still available.

Possible dbMessage: `SLUG_TAKEN`