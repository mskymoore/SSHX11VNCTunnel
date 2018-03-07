#!/bin/bash

ssh -t -L 5900:localhost:5900 $1 'x11vnc -ncache -localhost -display :0'
