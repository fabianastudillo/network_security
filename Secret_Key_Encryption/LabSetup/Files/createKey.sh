#!/bin/bash

echo {a..z} | tr ' ' '\n' | shuf | tr '\n' ' ' | sed 's/ //g'

echo ""

