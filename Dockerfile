# Use Debian (not Alpine) because Panda3D only offers manylinux2014 (glibc) wheels
# Debian also lets us use apt to install Infisical CLI in the runtime image
FROM python:3.14-slim AS deps
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


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

COPY --from=deps /install /usr/local

COPY toontown ./toontown
COPY otp ./otp
COPY config ./config
COPY astron/dclass ./astron/dclass
COPY docker/entrypoint.sh docker/container.prc ./docker/

COPY build/resources /resources

ARG SERVER_VERSION=dev
RUN sed -i "s/^server-version SERVER_VERSION$/server-version ${SERVER_VERSION}/" \
        config/distribution/live.prc \
    && grep -qx "server-version ${SERVER_VERSION}" config/distribution/live.prc

# Unbuffered so the district's log reaches `docker logs` as it happens
ENV PYTHONUNBUFFERED=1

RUN useradd --system --create-home --uid 10001 tti && chown -R tti /app
USER tti

ENTRYPOINT ["./docker/entrypoint.sh"]

LABEL org.opencontainers.image.title="Toontown Infinite Game Server"
LABEL org.opencontainers.image.description="The official Docker image for the TTI game server (AI and UberDOG)."
LABEL org.opencontainers.image.authors="Chris/Sonder"
