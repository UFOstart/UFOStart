---
layout: endpoint
category: endpoint
title: /web/user/profile
type: READ
request: {"slug": USER_SLUG}
response:   |
            {
                "status" : 0,
                "procName" : "user_profile",
                "User" : USER_DETAILS
            }

---

Returns all profile information for a given user.