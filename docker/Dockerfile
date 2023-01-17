FROM python:3.9.7-slim-buster as sdist

LABEL maintainer="oss@netflix.com"
LABEL org.opencontainers.image.title="Dispatch PyPI Wheel"
LABEL org.opencontainers.image.description="PyPI Wheel Builder for Dispatch"
LABEL org.opencontainers.image.url="https://dispatch.io/"
LABEL org.opencontainers.image.source="https://github.com/netflix/dispatch"
LABEL org.opencontainers.image.vendor="Netflix, Inc."
LABEL org.opencontainers.image.authors="oss@netflix.com"

# Get and set up Node for front-end asset building
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Needed for fetching stuff
    ca-certificates \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN set -x \
    && wget --quiet -O - https://deb.nodesource.com/setup_16.x | bash - \
    && apt-get install -y nodejs

ARG SOURCE_COMMIT
ENV DISPATCH_BUILD=${SOURCE_COMMIT:-unknown}
LABEL org.opencontainers.image.revision=$SOURCE_COMMIT
LABEL org.opencontainers.image.licenses="https://github.com/netflix/dispatch/blob/${SOURCE_COMMIT:-master}/LICENSE"

ARG DISPATCH_LIGHT_BUILD
ENV DISPATCH_LIGHT_BUILD=${DISPATCH_LIGHT_BUILD}

RUN echo "DISPATCH_LIGHT_BUILD=${DISPATCH_LIGHT_BUILD}"

# Allow build time variables via --build-arg
ARG VITE_DISPATCH_AUTH_REGISTRATION_ENABLED
ARG VITE_DISPATCH_AUTHENTICATION_PROVIDER_PKCE_CLIENT_ID
ARG VITE_DISPATCH_AUTHENTICATION_PROVIDER_PKCE_OPEN_ID_CONNECT_URL
ARG VITE_DISPATCH_AUTHENTICATION_PROVIDER_SLUG
ARG VITE_DISPATCH_AUTHENTICATION_PROVIDER_USE_ID_TOKEN
ARG VITE_SENTRY_DSN
ARG VITE_SENTRY_APP_KEY
ARG VITE_SENTRY_ENABLED

COPY . /usr/src/dispatch/
RUN export YARN_CACHE_FOLDER="$(mktemp -d)" \
    && cd /usr/src/dispatch \
    && python setup.py bdist_wheel \
    && rm -r "$YARN_CACHE_FOLDER" \
    && mv /usr/src/dispatch/dist /dist

# This is the image to be run
FROM python:3.9.7-slim-buster

LABEL maintainer="oss@dispatch.io"
LABEL org.opencontainers.image.title="Dispatch"
LABEL org.opencontainers.image.description="Dispatch runtime image"
LABEL org.opencontainers.image.url="https://github.com/netflix/dispatch"
LABEL org.opencontainers.image.documentation="https://github.com/netflix/dispatch"
LABEL org.opencontainers.image.source="https://github.com/netflix/dispatch"
LABEL org.opencontainers.image.vendor="Netflix, Inc."
LABEL org.opencontainers.image.authors="oss@netflix.com"


# add our user and group first to make sure their IDs get assigned consistently
RUN groupadd -r dispatch && useradd -r -m -g dispatch dispatch

# Sane defaults for pip
ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Dispatch config params
    DISPATCH_CONF=/etc/dispatch

RUN apt-get update && apt-get install -y --no-install-recommends \
    # Needed for fetching stuff
    ca-certificates \
    wget gnupg \
    && rm -rf /var/lib/apt/lists/*

RUN set -x \
    && echo "deb http://apt.postgresql.org/pub/repos/apt buster-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

RUN set -x \
    && wget --quiet -O - https://deb.nodesource.com/setup_12.x | bash -

COPY --from=sdist /dist/*.whl /tmp/dist/
RUN set -x \
    && buildDeps="" \
    && apt-get update \
    && apt-get install -y --no-install-recommends $buildDeps \
    # remove internal index when internal plugins are seperated
    && pip install -U /tmp/dist/*.whl \
    && apt-get purge -y --auto-remove $buildDeps \
    # We install run-time dependencies strictly after
    # build dependencies to prevent accidental collusion.
    # These are also installed last as they are needed
    # during container run and can have the same deps w/
    && apt-get install -y --no-install-recommends \
    pkg-config postgresql-client-12 nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && npm install mjml

EXPOSE 8000
VOLUME /var/lib/dispatch/files

ENTRYPOINT ["dispatch"]
CMD ["server", "start", "dispatch.main:app", "--host=0.0.0.0"]

ARG SOURCE_COMMIT
LABEL org.opencontainers.image.revision=$SOURCE_COMMIT
LABEL org.opencontainers.image.licenses="https://github.com/netflix/dispatch/blob/${SOURCE_COMMIT:-master}/LICENSE"
