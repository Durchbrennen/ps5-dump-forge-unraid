FROM python:3.13-alpine AS download
ARG FORGE_VERSION=0.5.6
COPY scripts/fetch-release.py /fetch-release.py
RUN python /fetch-release.py "$FORGE_VERSION" /out

FROM alpine:3.22
ARG FORGE_VERSION=0.5.6
LABEL org.opencontainers.image.title="PS5 Dump Forge for Unraid" \
      org.opencontainers.image.version="$FORGE_VERSION" \
      org.opencontainers.image.licenses="GPL-3.0-or-later"
RUN apk add --no-cache ca-certificates tini
COPY --from=download /out/ /opt/forge/
COPY scripts/entrypoint.sh /usr/local/bin/forge-entrypoint
RUN chmod 755 /usr/local/bin/forge-entrypoint && mkdir -p /config /games && chown 99:100 /config
ENV HOME=/config XDG_DATA_HOME=/config/data XDG_CONFIG_HOME=/config/settings
USER 99:100
EXPOSE 8095/tcp
VOLUME ["/config"]
STOPSIGNAL SIGTERM
ENTRYPOINT ["/sbin/tini", "--", "/usr/local/bin/forge-entrypoint"]
