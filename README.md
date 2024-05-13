# AppearanceUI
A basic framework for stitching together prebuilt python web applications


The goal of AppearanceUI is to have a basic local web interface that may serve simple 'applications' through your browser.

## Why the quotes around 'applications'?

Individual applications that may be attached and served through AppearanceUI are not meant to be large scale applications. 
An example would be a file browser or a simple database frontend. These are not meant to function like something like Visual
Studio Code, which would be served through Electron or a dedicated server.

Imagine a docker-compose environment with a simple GUI behind an nginx container. Through that GUI, you can say 'Install
Application A along path `/path/to/app`. It would download the image, spin it up in the overlay network, update the nginx config,
then reset the nginx instance so that "Application A" may be reached via the `/path/to/app` url.

## Why not use the docker + nginx + gui approach explained above?

Docker is not available on many environments, but python is. Further more, setting up Dockerfiles along what are supposed to 
be simple applications adds an extra layer of complexity.

## How are the 'applications' served via AppearanceUI supposed to be structured?

The applications just need to be basic asyncio web apps. Need a gui? Include a view that'll ship out HTML with js that'll return to
the server for websocket connections and REST requests as needed. Include many HTML views. Include none. It's all up to the 'application'
developer. The applications need to be simple enough that a novice programmer may put one together.

An example of what _could_ be an AppearanceUI app would be [Yanv](https://github.com/christophertubbs/Yanv).
