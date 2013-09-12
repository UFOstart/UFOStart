---
layout: default
title: Home
---

#UFOStartApi

##APi Overview

All API endpoints are to be called with HTTPS and the following default settings.

#### Default HTTP Settings
* Method: POST
* Content-Type: application/json
* Client-Token: YOUR_CLIENT_TOKEN

#### Default JSON Request Format:

Some endpoints require a parameter JSON Document, some can be called without. If parameters are required, they must be submitted as valid JSON documents in the HTTP Body.

#### Default JSON Response Format:

The API will always return a 200 HTTP Status Code and the response as a JSON document in the body.
If the API dos return any other error code, please check that you provided all settings as above. If they are all correct, please check your API deployment.


Every valid API response document contains the following fields:

* __status__, denotes the internal error code or 0 if no error, always returned
* __procName__, name of stored procedure that got executed in the DB, this is for debugging purposes only, always returned
* __dbMessage__, contains business relevant feedback, common examples are: UNKNOWN_USER, LOGIN_FAILED, only present if business logic requires
* __errorMessage__, returned only when an unexpected error occurs, in this case the __status__ will be > 0, use this for logging/debugging purposes only


## Api Endpoint Documentation

Each endpoint section will contain Fiddler2 scratchpad code. You are highly encouraged to run those against your own API deployment to visualize the interactions.

#### Public website area endpoints

<ul id="endpoints">
  {% for post in site.posts %}
    <li>
        <h2>{{ post.title }}</h2>
        <div class="content">{{ post.request }}</div>
        <div class="content">{{ post.content }}</div>
    </li>
  {% endfor %}
</ul>