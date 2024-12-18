ARG PYTHON_VERSION=3.11.7
FROM python:${PYTHON_VERSION}-slim-bookworm

RUN apt update && \
    apt install -y curl && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

ARG USERNAME=ryeuser
RUN useradd ${USERNAME} --create-home
USER ${USERNAME}

WORKDIR /home/${USERNAME}/app

ENV RYE_HOME=/home/${USERNAME}/.rye
ENV PATH=${RYE_HOME}/shims:/home/${USERNAME}/app/.venv/bin:${PATH}

RUN curl -sSf https://rye.astral.sh/get | RYE_NO_AUTO_INSTALL=1 RYE_INSTALL_OPTION="--yes" bash

COPY . .

RUN rye sync --no-dev --no-lock

ENTRYPOINT ["python3", "main.py"]