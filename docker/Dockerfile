FROM python:3.13.1-slim-bullseye as sdist

LABEL maintainer="oss@netflix.com"
LABEL org.opencontainers.image.title="Dispatch PyPI Wheel"
LABEL org.opencontainers.image.description="PyPI Wheel Builder for Dispatch"
LABEL org.opencontainers.image.url="https://dispatch.io/"
LABEL org.opencontainers.image.source="https://github.com/netflix/dispatch"
LABEL org.opencontainers.image.vendor="Netflix, Inc."
LABEL org.opencontainers.image.authors="oss@netflix.com"

SHELL ["/bin/bash", "-o", "pipefail", "-o", "errexit", "-c"]

# Get and set up Node for front-end asset building
RUN apt-get update && apt-get install -y --no-install-recommends \
  # Needed for fetching stuff
  ca-certificates \
  wget \
  && rm -rf /var/lib/apt/lists/*

RUN wget --quiet -O - https://deb.nodesource.com/setup_20.x | bash - \
  && apt-get install -y nodejs --no-install-recommends

ARG SOURCE_COMMIT
ENV DISPATCH_BUILD=${SOURCE_COMMIT:-unknown}
LABEL org.opencontainers.image.revision=$SOURCE_COMMIT
LABEL org.opencontainers.image.licenses="https://github.com/netflix/dispatch/blob/${SOURCE_COMMIT:-main}/LICENSE"

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

# Should be replaced in your build process script
ARG VITE_DISPATCH_COMMIT_HASH
ENV VITE_DISPATCH_COMMIT_HASH="Unknown"

ARG VITE_DISPATCH_COMMIT_MESSAGE
ENV VITE_DISPATCH_COMMIT_MESSAGE="Unknown"

COPY . /usr/src/dispatch/
RUN YARN_CACHE_FOLDER="$(mktemp -d)" \
  && export YARN_CACHE_FOLDER \
  && pushd /usr/src/dispatch \
  && python setup.py bdist_wheel \
  && rm -r "$YARN_CACHE_FOLDER" \
  && mv /usr/src/dispatch/dist /dist

# This is the image to be run
FROM python:3.13.1-slim-bullseye

LABEL maintainer="oss@dispatch.io"
LABEL org.opencontainers.image.title="Dispatch"
LABEL org.opencontainers.image.description="Dispatch runtime image"
LABEL org.opencontainers.image.url="https://github.com/netflix/dispatch"
LABEL org.opencontainers.image.documentation="https://github.com/netflix/dispatch"
LABEL org.opencontainers.image.source="https://github.com/netflix/dispatch"
LABEL org.opencontainers.image.vendor="Netflix, Inc."
LABEL org.opencontainers.image.authors="oss@netflix.com"

SHELL ["/bin/bash", "-o", "pipefail", "-o", "errexit", "-c"]

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

RUN echo "deb http://apt.postgresql.org/pub/repos/apt bullseye-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
  && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

RUN wget --quiet -O - https://deb.nodesource.com/setup_20.x | bash -

COPY --from=sdist /dist/*.whl /tmp/dist/
RUN buildDeps="" \
  && apt-get update \
  && apt-get install -y --no-install-recommends "$buildDeps" \
  # remove internal index when internal plugins are separated
  && pip install -U /tmp/dist/*.whl \
  && apt-get purge -y --auto-remove "$buildDeps" \
  # We install run-time dependencies strictly after
  # build dependencies to prevent accidental collusion.
  # These are also installed last as they are needed
  # during container run and can have the same deps w/
  && apt-get install -y --no-install-recommends \
  pkg-config postgresql-client-14 nodejs \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \
  # mjml has to be installed differently here because
  # after node 14, docker will install npm files at the
  # root directoy and fail, so we have to create a new
  # directory and use it for the install then copy the
  # files to the root directory to maintain backwards
  # compatibility for email generation
  && mkdir -p /mjml_install \
  # if our workdir is /, then pushd/popd doesn't work
  # for the npm install. It still tries to install in /,
  # which npm can't do
  && cd /mjml_install \
  && npm install --no-cache-dir mjml \
  && mv node_modules / \
  && cd / \
  && rm -rf /mjml_install

EXPOSE 8000
VOLUME /var/lib/dispatch/files

ENTRYPOINT ["dispatch"]
CMD ["server", "start", "dispatch.main:app", "--host=0.0.0.0"]

ARG SOURCE_COMMIT
LABEL org.opencontainers.image.revision=$SOURCE_COMMIT
LABEL org.opencontainers.image.licenses="https://github.com/netflix/dispatch/blob/${SOURCE_COMMIT:-main}/LICENSE"
