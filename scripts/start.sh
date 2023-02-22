#!/bin/bash
poetry run uvicorn --app-dir ./src/ main:app
