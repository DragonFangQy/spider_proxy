#!/bin/bash
cd app && celery --app task:celery_app worker -E -B -l INFO