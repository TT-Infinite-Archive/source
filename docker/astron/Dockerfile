# astrond is built out of band by .github/workflows/build-astrond.yml, which
# pins one Astron revision, and the binary it produces is committed. Nothing is
# compiled here.
#
# Rebuilding astrond means running that workflow and committing the artifact,
# not editing this file.
FROM debian:12-slim AS runtime

# astrond carries its own libraries, so the runtime needs nothing but a
# trust store for TLS
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# x86-64, which is what the runner and the deploy host are. Building this image
# for arm64 needs an arm64 astrond committed beside it.
COPY --chmod=0755 astron/astrond-linux /usr/local/bin/astrond

ARG TZ=America/Los_Angeles
ENV TZ=${TZ}
RUN ln -snf "/usr/share/zoneinfo/$TZ" /etc/localtime && echo "$TZ" > /etc/timezone

WORKDIR /astron

COPY astron/dclass /astron/dclass
COPY docker/astron/astrond.yml /astron/config/astrond.yml

# A silent no-op here leaves astrond gating on the literal string
# SERVER_VERSION and every client is rejected at connect time.
ARG SERVER_VERSION=dev
RUN sed -i "s/\"SERVER_VERSION\"/\"${SERVER_VERSION}\"/" /astron/config/astrond.yml \
    && grep -q "version: \"${SERVER_VERSION}\"" /astron/config/astrond.yml

RUN useradd --system --create-home --uid 10002 astron \
    && mkdir -p /astron/logs && chown -R astron /astron
USER astron

ENTRYPOINT ["astrond"]
CMD ["--loglevel", "info", "/astron/config/astrond.yml"]

LABEL org.opencontainers.image.title="TTI Astron"
LABEL org.opencontainers.image.description="Astron message director for the TTI game server."
