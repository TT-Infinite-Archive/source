# Use Debian (not Alpine) because the Panda3D wheel is built against glibc
# Debian also lets us use apt to install Infisical CLI in the runtime image
FROM python:3.14-slim AS deps
WORKDIR /app

COPY requirements.txt ./
# The pinned Panda3D the client and the host add-on run too. It is not on PyPI;
# CI puts it in wheels/, and scripts/build_panda3d.py makes it anywhere else
COPY wheels/ ./wheels/
RUN wheel=$(ls wheels/panda3d-*linux*_$(uname -m).whl 2> /dev/null | head -1) \
    && if [ -z "$wheel" ]; then \
        echo "No Panda3D wheel for linux $(uname -m) in wheels/." >&2; exit 1; \
    fi \
    && pip install --no-cache-dir --prefix=/install "$wheel" -r requirements.txt


FROM python:3.14-slim AS runtime
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && curl -1sLf 'https://artifacts-cli.infisical.com/setup.deb.sh' | bash \
    && apt-get install -y --no-install-recommends infisical \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

ARG TZ=America/Los_Angeles
ENV TZ=${TZ}
RUN ln -snf "/usr/share/zoneinfo/$TZ" /etc/localtime && echo "$TZ" > /etc/timezone

RUN useradd --system --create-home --uid 10001 tti && chown tti /app

COPY --from=deps /install /usr/local

# Rarely changes, so it sits below the code and stays cached
COPY build/resources ./resources

COPY --chown=tti toontown ./toontown
COPY --chown=tti otp ./otp
COPY --chown=tti config ./config
COPY --chown=tti astron/dclass ./astron/dclass
COPY --chown=tti docker/entrypoint.sh docker/container.prc ./docker/

ARG BUILD_VERSION=dev
RUN sed -i "s/^build-version BUILD_VERSION$/build-version ${BUILD_VERSION}/" \
        config/distribution/live.prc \
    && grep -qx "build-version ${BUILD_VERSION}" config/distribution/live.prc \
    && install -d -o tti astron/databases

# Unbuffered so the district's log reaches `docker logs` as it happens
ENV PYTHONUNBUFFERED=1

USER tti

ENTRYPOINT ["./docker/entrypoint.sh"]

LABEL org.opencontainers.image.title="Toontown Infinite Game Server"
LABEL org.opencontainers.image.description="The official Docker image for the TTI game server (AI and UberDOG)."
LABEL org.opencontainers.image.authors="Chris/Sonder"
LABEL org.opencontainers.image.version="${BUILD_VERSION}"
