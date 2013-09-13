---
layout: endpoint
category: endpoint
title: /web/product/create
type: WRITE
request: |
        {
            "token" : ROUND_TOKEN,
            "Product" : {
                "name" : PRODUCT_NAME,
                "description" : FREETEXT_DESCRIPTION,
                "video" :       YOUTUBE_URL_or_VIMEO_URL,
                "Pictures" :    LIST_OF_SLIDESHOW_PICTURES,
            }
        }
response:   |
            {
                "status" : 0,
                "procName" : "company_product_set",
                "Round" : ROUND_DETAILS
            }


---

Creates and updates a product inside a round.