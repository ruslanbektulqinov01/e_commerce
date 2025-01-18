#!/bin/bash

if [ ! -d "alembic" ]; then
  alembic init alembic
else

  read -r -p "Enter the revision message: " message
  alembic revision --autogenerate -m "$message"
fi

alembic upgrade head
