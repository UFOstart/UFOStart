---
layout: endpoint
category: endpoint
title: /web/round/sendmentor
type: WRITE
request:  {"token": ROUND_TOKEN}
response:   |
            {
                "status" : 0,
                "procName" : "round_send_to_mentor",
                "Company" : COMPANY_DETAILS
            }

---

Founder uses this endpoint to submit a round to the company's mentors for approval. All mentors will receive an approval notification.

