---
layout: endpoint
category: endpoint
title: /web/company/create
type: WRITE
request:   |
            {
                "token" : FOUNDER_USER_TOKEN,
                "Company" : {
                    "name" :        COMPANY_NAME [required],
                    "logo" :        LOGO_PICTURE_URL [required],
                    "pitch" :       COMPANY_SHORT_PITCH [required],
                    "description" : COMPANY_LONG_DESCRIPTION [required],
                    "currency" :    ISO_CURRENCY_CODE (EUR/USD) [required],
                    "slideShare" :  SLIDESHARE_URL,
                    "video" :       YOUTUBE_URL_or_VIMEO_URL,
                    "Pictures" :    LIST_OF_SLIDESHOW_PICTURES,
                    "Template" : {
                        "key" : SELECTED_TEMPLATE_KEY
                    }
                }
            }
response:   |
            {
                "status" : 0,
                "procName" : "company_create",
                "User" : FULL_USER_MODEL
            }

---

Creates a company with Slug and Founder Token, returns the Founder User with all his companies.