---
layout: endpoint
category: endpoint
title: /web/company/acceptInvite
type: WRITE
request:    |
            {
                "inviteToken" : INVITE_TOKEN,
                "userToken" : INVITEE_USER_TOKEN
            }
response:   |
            {
                "status" : 0,
                "procName" : "invite_accept"
            }

---

A user can accept an invitation if and only they possess a `userToken`  (i.e. are logged in) and an `inviteToken` (i.e. received their notification).