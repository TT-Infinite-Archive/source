FROM debian:12-slim AS build

ARG ASTRON_REPO=https://github.com/darktohka/Astron.git
ARG ASTRON_REV=630b2de3
ARG UVW_REPO=https://github.com/darktohka/uvw.git
ARG MONGO_C_TAG=1.27.6
ARG MONGO_CXX_TAG=r3.10.2
ARG LIBUV_TAG=v1.51.0
ARG YAML_CPP_TAG=yaml-cpp-0.9.0

# yaml-cpp is built from source rather than taken from apt
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential cmake git ca-certificates pkg-config python3 \
        libssl-dev libboost-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src

# Everything static. Only glibc stays dynamic. Linking it statically breaks
# getaddrinfo, and astrond has to resolve the MongoDB host by name.
ARG STATIC="-DBUILD_SHARED_LIBS=OFF -DCMAKE_POSITION_INDEPENDENT_CODE=ON"

RUN git clone --depth 1 --branch "$YAML_CPP_TAG" https://github.com/jbeder/yaml-cpp.git \
    && cmake -S yaml-cpp -B build-yaml-cpp -DCMAKE_BUILD_TYPE=Release $STATIC \
        -DYAML_BUILD_SHARED_LIBS=OFF -DYAML_CPP_BUILD_TESTS=OFF \
        -DYAML_CPP_BUILD_TOOLS=OFF -DYAML_CPP_BUILD_CONTRIB=OFF \
    && cmake --build build-yaml-cpp --target install -j"$(nproc)" \
    && rm -rf yaml-cpp build-yaml-cpp

# Astron's Findlibuv searches by bare name
RUN git clone --depth 1 --branch "$LIBUV_TAG" https://github.com/libuv/libuv.git \
    && cmake -S libuv -B build-libuv -DCMAKE_BUILD_TYPE=Release $STATIC \
        -DLIBUV_BUILD_SHARED=OFF -DLIBUV_BUILD_TESTS=OFF -DBUILD_TESTING=OFF \
    && cmake --build build-libuv --target install -j"$(nproc)" \
    && rm -rf libuv build-libuv

RUN git clone --depth 1 "$UVW_REPO" uvw \
    && cmake -S uvw -B build-uvw -DCMAKE_BUILD_TYPE=Release $STATIC \
        -DUVW_BUILD_LIBS=ON -DUVW_FETCH_LIBUV=OFF -DUVW_BUILD_TESTING=OFF \
    && cmake --build build-uvw --target install -j"$(nproc)" \
    && rm -rf uvw build-uvw

# OpenSSL is linked statically too
RUN git clone --depth 1 --branch "$MONGO_C_TAG" https://github.com/mongodb/mongo-c-driver.git \
    && cmake -S mongo-c-driver -B build-mongoc \
        -DCMAKE_BUILD_TYPE=Release -DBUILD_VERSION="${MONGO_C_TAG}" $STATIC \
        -DENABLE_STATIC=ON -DENABLE_TESTS=OFF -DENABLE_EXAMPLES=OFF \
        -DENABLE_SSL=OPENSSL -DOPENSSL_USE_STATIC_LIBS=TRUE -DENABLE_SASL=OFF \
        -DENABLE_ZSTD=OFF -DENABLE_SNAPPY=OFF -DENABLE_ZLIB=BUNDLED \
    && cmake --build build-mongoc --target install -j"$(nproc)" \
    && rm -rf mongo-c-driver build-mongoc

# CMAKE_INSTALL_PREFIX is explicit because mongo-cxx-driver defaults it to a
# build-local install/ directory rather than /usr/local.
RUN git clone --depth 1 --branch "$MONGO_CXX_TAG" https://github.com/mongodb/mongo-cxx-driver.git \
    && cmake -S mongo-cxx-driver -B build-mongocxx \
        -DCMAKE_BUILD_TYPE=Release -DBUILD_VERSION="${MONGO_CXX_TAG#r}" $STATIC \
        -DCMAKE_INSTALL_PREFIX=/usr/local -DBUILD_SHARED_AND_STATIC_LIBS=OFF \
        -DMONGOCXX_LINK_WITH_STATIC_MONGOC=ON \
        -DCMAKE_CXX_STANDARD=17 -DENABLE_TESTS=OFF \
    && cmake --build build-mongocxx --target install -j"$(nproc)" \
    && rm -rf mongo-cxx-driver build-mongocxx

# Astron predates mongo-cxx-driver's package rename: it calls
# find_package(libmongocxx-static), while 3.10 installs only
# mongocxx-config.cmake
RUN mkdir -p /usr/local/lib/cmake/libmongocxx-static-1 /usr/local/lib/cmake/libbsoncxx-static-1 \
    && printf '%s\n' \
        'find_package(mongocxx REQUIRED CONFIG)' \
        'set(LIBMONGOCXX_STATIC_INCLUDE_DIRS "")' \
        'set(LIBMONGOCXX_STATIC_LIBRARY_DIRS "")' \
        'set(LIBMONGOCXX_STATIC_LIBRARIES mongo::mongocxx_static)' \
        > /usr/local/lib/cmake/libmongocxx-static-1/libmongocxx-static-config.cmake \
    && printf '%s\n' \
        'find_package(bsoncxx REQUIRED CONFIG)' \
        'set(LIBBSONCXX_STATIC_INCLUDE_DIRS "")' \
        'set(LIBBSONCXX_STATIC_LIBRARY_DIRS "")' \
        'set(LIBBSONCXX_STATIC_LIBRARIES mongo::bsoncxx_static)' \
        > /usr/local/lib/cmake/libbsoncxx-static-1/libbsoncxx-static-config.cmake

# Astron links libuv before uvw, and GNU ld resolves static archives in strict
# command-line order, so uvw's references to libuv find nothing
RUN git clone "$ASTRON_REPO" astron \
    && git -C astron checkout "$ASTRON_REV" \
    && { cmake -S astron -B build-astron \
            -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_STANDARD=17 \
            -DCMAKE_CXX_FLAGS=-DUVW_AS_LIB -DBUILD_TESTS=OFF \
            -DCMAKE_EXE_LINKER_FLAGS="-static-libstdc++ -static-libgcc" \
            -DCMAKE_CXX_STANDARD_LIBRARIES=/usr/local/lib/libuv.a \
            -DCMAKE_NO_SYSTEM_FROM_IMPORTED=ON \
            -DOPENSSL_USE_STATIC_LIBS=TRUE \
            -DUVW_INCLUDE_DIR=/usr/local/include -DUVW_LIBRARY=/usr/local/lib/libuvw.a \
            -DLIBUV_INCLUDE_DIR=/usr/local/include -DLIBUV_LIBRARY=/usr/local/lib/libuv.a \
         > /tmp/astron-cmake.log 2>&1 || { cat /tmp/astron-cmake.log; exit 1; }; } \
    && { grep -q "MongoDB client library found" /tmp/astron-cmake.log \
         || { echo "FATAL: Astron configured without the MongoDB backend"; \
              grep -i mongo /tmp/astron-cmake.log; exit 1; }; } \
    && cmake --build build-astron -j"$(nproc)" \
    && find build-astron -name astrond -type f -exec cp {} /usr/local/bin/astrond ';' \
    && test -x /usr/local/bin/astrond

# Anything here beyond glibc is a file the player
# would have to be shipped separately
RUN strays="$(ldd /usr/local/bin/astrond \
        | grep -oE '(lib[a-zA-Z0-9_.+-]+\.so[0-9.]*)' \
        | grep -vE '^(libc|libm|libdl|librt|libpthread|libresolv|libgcc_s|ld-linux)' || true)"; \
    if [ -n "$strays" ]; then \
        echo "FATAL: astrond still depends on libraries the player would not have:"; \
        echo "$strays"; ldd /usr/local/bin/astrond; exit 1; \
    fi; \
    echo "Single-file astrond:"; ldd /usr/local/bin/astrond


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
