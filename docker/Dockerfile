FROM python:3.8-slim-buster as sdist

LABEL maintainer="oss@netflix.com"
LABEL org.opencontainers.image.title="Dispatch PyPI Wheel"
LABEL org.opencontainers.image.description="PyPI Wheel Builder for Dispatch"
LABEL org.opencontainers.image.url="https://dispatch.io/"
LABEL org.opencontainers.image.source="https://github.com/netflix/dispatch"
LABEL org.opencontainers.image.vendor="Netflix, Inc."
LABEL org.opencontainers.image.authors="oss@netflix.com"

RUN apt-get update && apt-get install -y --no-install-recommends \
    # Needed for GPG
    dirmngr \
    gnupg2 \
    # Needed for fetching stuff
    ca-certificates \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Fetch trusted keys
RUN for key in \
    # gosu
    B42F6819007F00F88E364FD4036A9C25BF357DD4 \
    # tini
    595E85A6B1B4779EA4DAAEC70B588DFF0527A9B7 \
    # Node - gpg keys listed at https://github.com/nodejs/node
    94AE36675C464D64BAFA68DD7434390BDBE9B9C5 \
    FD3A5288F042B6850C66B31F09FE44734EB7990E \
    71DCFD284A79C3B38668286BC97EC7A07EDE3FC1 \
    DD8F2338BAE7501E3DD5AC78C273792F7D83545D \
    C4F0DFFF4E8C1A8236409D08E73BC641CC11F4C8 \
    B9AE9905FFD7803F25714661B63B535A4C206CA9 \
    77984A986EBC2AA786BC0F66B01FBB92821C587A \
    8FCCA13FEF1D0C2E91008E09770F7A9A5AE15600 \
    4ED778F539E3634C779C87C6D7062848A1AB005C \
    A48C2BEE680E841632CD4E44F07496B3EB3C1762 \
    B9E2F5981AA6E0CD28160D9FF13993A75599653C \
    ; do \
    # Let's try several servers to ensure we get all the keys
    for server in \
    keys.openpgp.org \
    keyserver.ubuntu.com \
    hkps.pool.sks-keyservers.net \
    ; do \
    gpg2 --batch --keyserver "$server" --recv-keys "$key"; \
    done \
    done

# grab gosu for easy step-down from root
ENV GOSU_VERSION 1.12
RUN set -x \
    && dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')" \
    && wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch" \
    && wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch.asc" \
    && gpg2 --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu \
    && rm -f /usr/local/bin/gosu.asc \
    && chmod +x /usr/local/bin/gosu

# grab tini for signal processing and zombie killing
ENV TINI_VERSION 0.18.0
RUN set -x \
    && wget -O /usr/local/bin/tini "https://github.com/krallin/tini/releases/download/v$TINI_VERSION/tini" \
    && wget -O /usr/local/bin/tini.asc "https://github.com/krallin/tini/releases/download/v$TINI_VERSION/tini.asc" \
    && gpg --batch --verify /usr/local/bin/tini.asc /usr/local/bin/tini \
    && rm -f /usr/local/bin/tini.asc \
    && chmod +x /usr/local/bin/tini

# Get and set up Node for front-end asset building
COPY .nvmrc /usr/src/dispatch/
RUN cd /usr/src/dispatch \
    && export NODE_VERSION="$(cat .nvmrc)" \
    && wget "https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-x64.tar.gz" \
    && wget "https://nodejs.org/dist/v$NODE_VERSION/SHASUMS256.txt.asc" \
    && gpg --batch --verify SHASUMS256.txt.asc \
    && grep " node-v$NODE_VERSION-linux-x64.tar.gz\$" SHASUMS256.txt.asc | sha256sum -c - \
    && tar -xzf "node-v$NODE_VERSION-linux-x64.tar.gz" -C /usr/local --strip-components=1 \
    && rm -f "node-v$NODE_VERSION-linux-x64.tar.gz" SHASUMS256.txt.asc

ARG SOURCE_COMMIT
ENV DISPATCH_BUILD=${SOURCE_COMMIT:-unknown}
LABEL org.opencontainers.image.revision=$SOURCE_COMMIT
LABEL org.opencontainers.image.licenses="https://github.com/netflix/dispatch/blob/${SOURCE_COMMIT:-master}/LICENSE"

ARG DISPATCH_LIGHT_BUILD
ENV DISPATCH_LIGHT_BUILD=${DISPATCH_LIGHT_BUILD}

RUN echo "DISPATCH_LIGHT_BUILD=${DISPATCH_LIGHT_BUILD}"

COPY . /usr/src/dispatch/
RUN export YARN_CACHE_FOLDER="$(mktemp -d)" \
    && cd /usr/src/dispatch \
    && python setup.py bdist_wheel \
    && rm -r "$YARN_CACHE_FOLDER" \
    && mv /usr/src/dispatch/dist /dist

# This is the image to be run
FROM python:3.8-buster

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

COPY --from=sdist /usr/local/bin/gosu /usr/local/bin/tini /usr/local/bin/

# Sane defaults for pip
ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Dispatch config params
    DISPATCH_CONF=/etc/dispatch


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
    pkg-config postgresql-client\
    \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8000
VOLUME /var/lib/dispatch/files

ENTRYPOINT ["dispatch"]
CMD ["server", "start", "dispatch.main:app", "--host=0.0.0.0"]

ARG SOURCE_COMMIT
LABEL org.opencontainers.image.revision=$SOURCE_COMMIT
LABEL org.opencontainers.image.licenses="https://github.com/netflix/dispatch/blob/${SOURCE_COMMIT:-master}/LICENSE"
