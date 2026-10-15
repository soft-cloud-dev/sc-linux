ARG BASE_IMAGE=debian:trixie-slim
FROM ${BASE_IMAGE}
ARG SNAPSHOT=20261014T000000Z
ARG MKOSI_PACKAGE=25.3-7
ENV DEBIAN_FRONTEND=noninteractive LC_ALL=C.UTF-8 TZ=UTC
RUN rm -f /etc/apt/sources.list /etc/apt/sources.list.d/* \
 && printf 'deb [check-valid-until=no] http://snapshot.debian.org/archive/debian/%s/ trixie main\ndeb [check-valid-until=no] http://snapshot.debian.org/archive/debian/%s/ trixie-updates main\ndeb [check-valid-until=no] http://snapshot.debian.org/archive/debian-security/%s/ trixie-security main\n' "$SNAPSHOT" "$SNAPSHOT" "$SNAPSHOT" > /etc/apt/sources.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends "mkosi=${MKOSI_PACKAGE}" ca-certificates \
      git make xorriso zstd gdisk qemu-system-x86 qemu-utils ovmf swtpm \
      openssh-client python3-yaml sbsigntool \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /src
