FROM gmag11/metatrader5_vnc:1.0

LABEL build_version="Metatrader5 Docker:- ${VERSION} Build-date:- ${BUILD_DATE}"
LABEL maintainer="hadi fathi"

ENV CUSTOM_USER=admin
ENV PASSWORD=admin


COPY ./config_mini/ /config/
RUN chown -R abc:abc /config/.config
RUN chown -R abc:abc /config/.wine
RUN usermod -a -G root abc
#RUN chown -R abc:abc /config/

EXPOSE 3000 8001

