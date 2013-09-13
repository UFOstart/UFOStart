---
layout: endpoint
category: endpoint
title: /web/user/friendscompanies
type: READ
request: {"slug": USER_SLUG}
response:   |
            {
                "status" : 0,
                "procName" : "user_friends_companies",
                "Companies" : LIST_OF_COMPANIES
            }
---

Called with a user's slug, returns a list of companies, that have at least one of user's friends as members.

