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

Returns `"dbmessage":"SLUG_TAKEN"` is slug is not available anymore.