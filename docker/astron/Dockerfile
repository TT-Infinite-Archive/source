FROM debian:12-slim AS build

ARG ASTRON_REPO=https://github.com/darktohka/Astron.git
ARG ASTRON_REV=630b2de3
ARG UVW_REPO=https://github.com/darktohka/uvw.git
ARG MONGO_C_TAG=1.27.6
ARG MONGO_CXX_TAG=r3.10.2

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential cmake git ca-certificates pkg-config python3 \
        libssl-dev libyaml-cpp-dev libboost-dev libzstd-dev \
        libsasl2-dev libsnappy-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src

ARG LIBUV_TAG=v1.51.0
RUN git clone --depth 1 --branch "$LIBUV_TAG" https://github.com/libuv/libuv.git \
    && cmake -S libuv -B build-libuv -DCMAKE_BUILD_TYPE=Release \
        -DLIBUV_BUILD_TESTS=OFF -DBUILD_TESTING=OFF \
    && cmake --build build-libuv --target install -j"$(nproc)" \
    && rm -rf libuv build-libuv \
    && ldconfig

RUN git clone --depth 1 "$UVW_REPO" uvw \
    && cmake -S uvw -B build-uvw -DCMAKE_BUILD_TYPE=Release \
        -DUVW_BUILD_LIBS=ON -DUVW_FETCH_LIBUV=OFF -DUVW_BUILD_TESTING=OFF \
    && cmake --build build-uvw --target install -j"$(nproc)" \
    && rm -rf uvw build-uvw

RUN git clone --depth 1 --branch "$MONGO_C_TAG" https://github.com/mongodb/mongo-c-driver.git \
    && cmake -S mongo-c-driver -B build-mongoc \
        -DCMAKE_BUILD_TYPE=Release -DBUILD_VERSION="${MONGO_C_TAG}" \
        -DENABLE_TESTS=OFF -DENABLE_EXAMPLES=OFF -DENABLE_STATIC=OFF \
    && cmake --build build-mongoc --target install -j"$(nproc)" \
    && rm -rf mongo-c-driver build-mongoc

# CMAKE_INSTALL_PREFIX is explicit because mongo-cxx-driver defaults it to a
# build-local install/ directory rather than /usr/local.
RUN git clone --depth 1 --branch "$MONGO_CXX_TAG" https://github.com/mongodb/mongo-cxx-driver.git \
    && cmake -S mongo-cxx-driver -B build-mongocxx \
        -DCMAKE_BUILD_TYPE=Release -DBUILD_VERSION="${MONGO_CXX_TAG#r}" \
        -DCMAKE_INSTALL_PREFIX=/usr/local \
        -DCMAKE_CXX_STANDARD=17 -DENABLE_TESTS=OFF -DBUILD_SHARED_LIBS=ON \
    && cmake --build build-mongocxx --target install -j"$(nproc)" \
    && rm -rf mongo-cxx-driver build-mongocxx \
    && ldconfig

# Astron predates mongo-cxx-driver's package rename: it calls
# find_package(libmongocxx), while 3.10 installs only mongocxx-config.cmake.
# These shims restore the LIBMONGOCXX_*/LIBBSONCXX_* variables the old package
# defined, which is all Astron's CMakeLists actually consumes.
RUN mkdir -p /usr/local/lib/cmake/libmongocxx-1 /usr/local/lib/cmake/libbsoncxx-1 \
    && printf '%s\n' \
        'set(LIBMONGOCXX_INCLUDE_DIRS /usr/local/include/mongocxx/v_noabi /usr/local/include/bsoncxx/v_noabi)' \
        'set(LIBMONGOCXX_LIBRARY_DIRS /usr/local/lib)' \
        'set(LIBMONGOCXX_LIBRARIES mongocxx)' \
        > /usr/local/lib/cmake/libmongocxx-1/libmongocxx-config.cmake \
    && printf '%s\n' \
        'set(LIBBSONCXX_INCLUDE_DIRS /usr/local/include/bsoncxx/v_noabi)' \
        'set(LIBBSONCXX_LIBRARY_DIRS /usr/local/lib)' \
        'set(LIBBSONCXX_LIBRARIES bsoncxx)' \
        > /usr/local/lib/cmake/libbsoncxx-1/libbsoncxx-config.cmake

RUN git clone "$ASTRON_REPO" astron \
    && git -C astron checkout "$ASTRON_REV" \
    && { cmake -S astron -B build-astron \
            -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_STANDARD=17 \
            -DCMAKE_CXX_FLAGS=-DUVW_AS_LIB -DBUILD_TESTS=OFF \
         > /tmp/astron-cmake.log 2>&1 || { cat /tmp/astron-cmake.log; exit 1; }; } \
    && { grep -q "MongoDB client library found" /tmp/astron-cmake.log \
         || { echo "FATAL: Astron configured without the MongoDB backend"; \
              grep -i mongo /tmp/astron-cmake.log; exit 1; }; } \
    && cmake --build build-astron -j"$(nproc)" \
    && find build-astron -name astrond -type f -exec cp {} /usr/local/bin/astrond ';' \
    && test -x /usr/local/bin/astrond


FROM debian:12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates libssl3 libyaml-cpp0.7 libzstd1 libsasl2-2 \
        libsnappy1v5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /usr/local/bin/astrond /usr/local/bin/astrond
COPY --from=build /usr/local/lib/libuv* /usr/local/lib/
COPY --from=build /usr/local/lib/libmongocxx* /usr/local/lib/
COPY --from=build /usr/local/lib/libbsoncxx* /usr/local/lib/
COPY --from=build /usr/local/lib/libmongoc* /usr/local/lib/
COPY --from=build /usr/local/lib/libbson* /usr/local/lib/
RUN ldconfig

ARG TZ=America/Los_Angeles
ENV TZ=${TZ}
RUN ln -snf "/usr/share/zoneinfo/$TZ" /etc/localtime && echo "$TZ" > /etc/timezone

WORKDIR /astron

COPY astron/dclass /astron/dclass
COPY docker/astron/astrond.yml /astron/config/astrond.yml

# The substitution is asserted rather than trusted: if the placeholder ever
# moves, a silent no-op here leaves astrond gating on the literal string
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
