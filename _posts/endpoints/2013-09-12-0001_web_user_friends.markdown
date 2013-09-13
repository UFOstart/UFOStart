---
layout: endpoint
category: endpoint
title: /web/user/friends
type: READ
request: {"slug": USER_SLUG}
response:   |
            {
                "status" : 0,
                "procName" : "user_friends",
                "User" : {
                    "Users" : LIST_OF_FRIEND_USERS
                }
            }
---

Called with a user's slug, returns a list of this user's friends who also use {{ site.project_name }} plattform.

