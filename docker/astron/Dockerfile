FROM debian:12-slim AS build

COPY tools/build_astrond.py /tmp/build_astrond.py

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 \
    && python3 /tmp/build_astrond.py --install-deps --target linux --output /tmp \
    && mv /tmp/astrond-linux /usr/local/bin/astrond \
    && rm -rf /var/lib/apt/lists/* /tmp/build_astrond.py


FROM debian:12-slim AS runtime

# astrond carries its own libraries now, so the runtime needs nothing but a
# trust store for TLS
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /usr/local/bin/astrond /usr/local/bin/astrond

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
